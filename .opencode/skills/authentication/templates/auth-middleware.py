"""
Authentication Middleware — FastAPI JWT validation with Keycloak JWKS.

This module provides a FastAPI middleware and dependency for validating
Keycloak-issued JWT tokens using the JWKS (JSON Web Key Set) endpoint.

Usage:
    from templates.auth_middleware import AuthMiddleware, get_current_user

    app.add_middleware(AuthMiddleware)

    @app.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        return {"user": user}
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import PyJWK

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

@dataclass
class KeycloakConfig:
    """Keycloak connection configuration.

    All values can be overridden via environment variables.

    Environment Variables:
        KEYCLOAK_SERVER_URL:      e.g., https://auth.example.com
        KEYCLOAK_REALM:           e.g., my-realm
        KEYCLOAK_CLIENT_ID:       e.g., my-api
        KEYCLOAK_CLIENT_SECRET:   Client secret (if confidential client)
        KEYCLOAK_AUDIENCE:        Expected audience claim (defaults to client_id)
        KEYCLOAK_VERIFY_SSL:      Whether to verify SSL certs (default True)
        KEYCLOAK_JWKS_CACHE_TTL:  Seconds to cache JWKS (default 3600)
    """

    server_url: str = field(default_factory=lambda: os_getenv("KEYCLOAK_SERVER_URL", ""))
    realm: str = field(default_factory=lambda: os_getenv("KEYCLOAK_REALM", ""))
    client_id: str = field(default_factory=lambda: os_getenv("KEYCLOAK_CLIENT_ID", ""))
    client_secret: str = field(default_factory=lambda: os_getenv("KEYCLOAK_CLIENT_SECRET", ""), repr=False)
    audience: str = field(default_factory=lambda: os_getenv("KEYCLOAK_AUDIENCE", os_getenv("KEYCLOAK_CLIENT_ID", "")))
    verify_ssl: bool = field(default_factory=lambda: os_getenv("KEYCLOAK_VERIFY_SSL", "true").lower() in ("1", "true", "yes"))
    jwks_cache_ttl: int = field(default_factory=lambda: int(os_getenv("KEYCLOAK_JWKS_CACHE_TTL", "3600")))

    # Internal — derived
    _openid_config: Dict[str, Any] = field(default_factory=dict, init=False, repr=False)
    _fetched: bool = field(default=False, init=False, repr=False)

    @property
    def issuer(self) -> str:
        return f"{self.server_url}/realms/{self.realm}"

    @property
    def authorization_endpoint(self) -> str:
        return self._resolve("authorization_endpoint")

    @property
    def token_endpoint(self) -> str:
        return self._resolve("token_endpoint")

    @property
    def jwks_uri(self) -> str:
        return self._resolve("jwks_uri")

    @property
    def end_session_endpoint(self) -> str:
        return self._resolve("end_session_endpoint")

    def _resolve(self, key: str) -> str:
        """Lazily fetch and resolve an OpenID configuration property."""
        if not self._fetched:
            self._refresh_openid_config()
        return self._openid_config.get(key, "")

    def _refresh_openid_config(self) -> None:
        """Fetch the OpenID Connect Discovery document synchronously (for bootstrap)."""
        url = f"{self.server_url}/realms/{self.realm}/.well-known/openid-configuration"
        try:
            with httpx.Client(verify=self.verify_ssl, timeout=10) as client:
                resp = client.get(url)
                resp.raise_for_status()
                self._openid_config = resp.json()
                self._fetched = True
        except Exception as exc:
            logger.error("Failed to fetch OIDC config from %s: %s", url, exc)
            raise RuntimeError(f"Failed to fetch OIDC config: {exc}") from exc


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

import os as _os


def os_getenv(key: str, default: str = "") -> str:
    """Thin wrapper so @dataclass default_factory calls work cleanly."""
    return _os.environ.get(key, default)


# ──────────────────────────────────────────────
# JWKS Cache & Token Validation
# ──────────────────────────────────────────────

class JWKSCache:
    """In-memory cache for JSON Web Key Sets with TTL-based expiration.

    Keys are fetched lazily on first validation; subsequent validations
    use cached keys until they expire (configured by KEYCLOAK_JWKS_CACHE_TTL).
    """

    def __init__(self, config: KeycloakConfig) -> None:
        self._config = config
        self._keys: Dict[str, Any] = {}
        self._last_fetch: Optional[datetime] = None

    @property
    def _ttl_seconds(self) -> int:
        return self._config.jwks_cache_ttl

    def get_key(self, kid: str) -> Optional[Dict[str, Any]]:
        """Return the JWK dict for the given key ID, fetching if stale."""
        if self._is_stale():
            self._fetch_jwks()
        return self._keys.get(kid)

    def _is_stale(self) -> bool:
        if self._last_fetch is None:
            return True
        elapsed = (datetime.now(timezone.utc) - self._last_fetch).total_seconds()
        return elapsed >= self._ttl_seconds

    def _fetch_jwks(self) -> None:
        """Fetch the JWKS from Keycloak and index keys by kid."""
        url = self._config.jwks_uri
        with httpx.Client(verify=self._config.verify_ssl, timeout=10) as client:
            resp = client.get(url)
            resp.raise_for_status()
            keys_list = resp.json().get("keys", [])
        self._keys = {k["kid"]: k for k in keys_list}
        self._last_fetch = datetime.now(timezone.utc)
        logger.info("JWKS refreshed — %d keys loaded", len(self._keys))


class TokenValidator:
    """Validates JWT access tokens against Keycloak's JWKS and claims."""

    def __init__(self, config: KeycloakConfig) -> None:
        self._config = config
        self._jwks = JWKSCache(config)

    def validate(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return its decoded payload.

        Args:
            token: Raw JWT access token string (without 'Bearer ' prefix).

        Returns:
            Decoded token payload as a dictionary.

        Raises:
            HTTPException: 401 if the token is invalid, expired, or missing claims.
        """
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError as exc:
            raise self._unauthorized("Invalid token header") from exc

        kid = unverified_header.get("kid")
        if not kid:
            raise self._unauthorized("Token header missing 'kid'")

        jwk_data = self._jwks.get_key(kid)
        if not jwk_data:
            raise self._unauthorized(f"Unknown key ID: {kid}")

        try:
            public_key = PyJWK(jwk_data)
        except Exception as exc:
            raise self._unauthorized("Failed to construct JWK") from exc

        try:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self._config.audience,
                issuer=self._config.issuer,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                },
            )
        except jwt.ExpiredSignatureError as exc:
            raise self._unauthorized("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise self._unauthorized(f"Token validation failed: {exc}") from exc

        return payload

    @staticmethod
    def _unauthorized(detail: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# ──────────────────────────────────────────────
# FastAPI Dependency & Middleware
# ──────────────────────────────────────────────

# Singleton instances (lazy init)
_config: Optional[KeycloakConfig] = None
_validator: Optional[TokenValidator] = None
_bearer_scheme = HTTPBearer(auto_error=False)


def _get_validator() -> TokenValidator:
    global _config, _validator
    if _validator is None:
        _config = KeycloakConfig()
        _validator = TokenValidator(_config)
    return _validator


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> dict:
    """FastAPI dependency: extract and validate the JWT from the Authorization header.

    Usage:
        @app.get("/me")
        async def me(user: dict = Depends(get_current_user)):
            return {"sub": user["sub"], "preferred_username": user.get("preferred_username")}

    Returns:
        Decoded JWT payload (dict).

    Raises:
        HTTPException: 401 if no valid token is present.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _get_validator().validate(credentials.credentials)


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Optional[dict]:
    """FastAPI dependency: optionally extract the JWT, returning None if absent.

    Usage:
        @app.get("/items")
        async def items(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                return {"owner": user["sub"], "items": [...]}
            return {"items": [...]}  # public view
    """
    if credentials is None:
        return None
    try:
        return _get_validator().validate(credentials.credentials)
    except HTTPException:
        return None
