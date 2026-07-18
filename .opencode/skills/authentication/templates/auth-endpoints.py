"""
Authentication Endpoints — FastAPI login, refresh, and logout with Keycloak.

This module provides ready-to-use FastAPI router endpoints for:
- POST /auth/login      — Direct grant (password) flow via Keycloak token endpoint.
- POST /auth/refresh    — Refresh token grant.
- POST /auth/logout     — Server-side logout (ends Keycloak session + revokes tokens).
- GET  /auth/me         — Returns current user info from the validated JWT.

All endpoints return a standardized ApiResponse envelope.

Usage:
    from templates.auth_endpoints import router as auth_router
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from templates.auth_middleware import KeycloakConfig, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# ──────────────────────────────────────────────
# DTOs (Request / Response)
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Credentials for password grant login."""

    username: str = Field(..., min_length=1, description="Username or email")
    password: str = Field(..., min_length=1, description="User password")

    class Config:
        json_schema_extra = {
            "example": {"username": "jane.doe@example.com", "password": "s3cret!"}
        }


class LoginResponse(BaseModel):
    """Token payload returned on successful login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
    session_state: Optional[str] = None
    scope: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGci...",
                "refresh_token": "eyJhbGci...",
                "token_type": "bearer",
                "expires_in": 300,
                "refresh_expires_in": 1800,
                "session_state": "abc123",
                "scope": "openid profile email",
            }
        }


class RefreshRequest(BaseModel):
    """A refresh token to obtain a new access token."""

    refresh_token: str = Field(..., min_length=1, description="Valid refresh token")

    class Config:
        json_schema_extra = {"example": {"refresh_token": "eyJhbGci..."}}


class LogoutRequest(BaseModel):
    """Tokens to revoke on logout."""

    refresh_token: str = Field(..., min_length=1, description="Refresh token to revoke")
    access_token: Optional[str] = Field(None, description="Access token to revoke (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGci...",
                "access_token": "eyJhbGci...",
            }
        }


class ApiResponse(BaseModel):
    """Standardized API response envelope."""

    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


# ──────────────────────────────────────────────
# Keycloak HTTP client helper
# ──────────────────────────────────────────────

def _get_keycloak_config() -> KeycloakConfig:
    """Lazily create and return KeycloakConfig (uses env vars)."""
    return KeycloakConfig()


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@router.post("/login", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def login(body: LoginRequest) -> ApiResponse:
    """Authenticate user via direct grant (password) flow.

    Exchanges username + password for an access token + refresh token pair.

    Returns:
        ApiResponse with LoginResponse as data.
    """
    cfg = _get_keycloak_config()

    payload: Dict[str, str] = {
        "grant_type": "password",
        "client_id": cfg.client_id,
        "username": body.username,
        "password": body.password,
        "scope": "openid profile email",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # If client is confidential, include secret
    if cfg.client_secret:
        payload["client_secret"] = cfg.client_secret

    async with httpx.AsyncClient(verify=cfg.verify_ssl, timeout=15) as client:
        resp = await client.post(cfg.token_endpoint, data=payload, headers=headers)

    if resp.status_code != 200:
        logger.warning("Login failed for user '%s': %s", body.username, resp.text)
        return ApiResponse(
            success=False,
            error={
                "code": "AUTH_LOGIN_FAILED",
                "message": _extract_keycloak_error(resp),
                "details": {"keycloak_status": resp.status_code},
            },
        )

    data = resp.json()
    return ApiResponse(
        success=True,
        data=LoginResponse(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "bearer"),
            expires_in=data["expires_in"],
            refresh_expires_in=data["refresh_expires_in"],
            session_state=data.get("session_state"),
            scope=data.get("scope", ""),
        ).model_dump(),
    )


@router.post("/refresh", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def refresh_token(body: RefreshRequest) -> ApiResponse:
    """Refresh an access token using a valid refresh token.

    This extends the user's session without requiring re-authentication.

    Returns:
        ApiResponse with a new LoginResponse (new access + refresh tokens).
    """
    cfg = _get_keycloak_config()

    payload: Dict[str, str] = {
        "grant_type": "refresh_token",
        "client_id": cfg.client_id,
        "refresh_token": body.refresh_token,
    }
    if cfg.client_secret:
        payload["client_secret"] = cfg.client_secret

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient(verify=cfg.verify_ssl, timeout=15) as client:
        resp = await client.post(cfg.token_endpoint, data=payload, headers=headers)

    if resp.status_code != 200:
        logger.warning("Token refresh failed: %s", resp.text)
        return ApiResponse(
            success=False,
            error={
                "code": "AUTH_REFRESH_FAILED",
                "message": _extract_keycloak_error(resp),
                "details": {"keycloak_status": resp.status_code},
            },
        )

    data = resp.json()
    return ApiResponse(
        success=True,
        data=LoginResponse(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", body.refresh_token),
            token_type=data.get("token_type", "bearer"),
            expires_in=data["expires_in"],
            refresh_expires_in=data.get("refresh_expires_in", data["expires_in"] * 6),
            session_state=data.get("session_state"),
            scope=data.get("scope", ""),
        ).model_dump(),
    )


@router.post("/logout", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def logout(
    body: LogoutRequest,
    user: dict = Depends(get_current_user),
) -> ApiResponse:
    """Log out the current user.

    Revokes the refresh token (and optionally the access token) on the Keycloak
    server, effectively ending the session.

    Requires a valid access token in the Authorization header.
    """
    cfg = _get_keycloak_config()

    payload: Dict[str, str] = {
        "client_id": cfg.client_id,
        "refresh_token": body.refresh_token,
    }
    if cfg.client_secret:
        payload["client_secret"] = cfg.client_secret

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    errors: list[str] = []

    # 1. Revoke refresh token
    async with httpx.AsyncClient(verify=cfg.verify_ssl, timeout=15) as client:
        resp = await client.post(
            f"{cfg.server_url}/realms/{cfg.realm}/protocol/openid-connect/revoke",
            data={**payload, "token": body.refresh_token, "token_type_hint": "refresh_token"},
            headers=headers,
        )
        if resp.status_code != 200:
            errors.append(f"refresh_revoke_failed({resp.status_code})")

    # 2. Optionally revoke access token
    if body.access_token:
        async with httpx.AsyncClient(verify=cfg.verify_ssl, timeout=15) as client:
            resp = await client.post(
                f"{cfg.server_url}/realms/{cfg.realm}/protocol/openid-connect/revoke",
                data={**payload, "token": body.access_token, "token_type_hint": "access_token"},
                headers=headers,
            )
            if resp.status_code != 200:
                errors.append(f"access_revoke_failed({resp.status_code})")

    # 3. Call end-session endpoint (best-effort)
    async with httpx.AsyncClient(verify=cfg.verify_ssl, timeout=15) as client:
        try:
            end_resp = await client.get(
                cfg.end_session_endpoint,
                params={
                    "client_id": cfg.client_id,
                    "refresh_token": body.refresh_token,
                },
            )
            if end_resp.status_code not in (200, 204, 302):
                errors.append(f"end_session_failed({end_resp.status_code})")
        except Exception as exc:
            logger.warning("End-session call failed: %s", exc)

    if errors:
        logger.warning("Logout partially completed for sub='%s': %s", user.get("sub"), errors)
        return ApiResponse(
            success=False,
            error={
                "code": "AUTH_LOGOUT_PARTIAL",
                "message": "Logout partially completed",
                "details": {"errors": errors},
            },
        )

    logger.info("User logged out: sub='%s'", user.get("sub"))
    return ApiResponse(
        success=True,
        data={"message": "Logged out successfully"},
    )


@router.get("/me", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def me(user: dict = Depends(get_current_user)) -> ApiResponse:
    """Return the current authenticated user's profile from the JWT.

    Requires a valid access token in the Authorization header.
    """
    return ApiResponse(
        success=True,
        data={
            "sub": user.get("sub"),
            "preferred_username": user.get("preferred_username"),
            "email": user.get("email"),
            "email_verified": user.get("email_verified"),
            "given_name": user.get("given_name"),
            "family_name": user.get("family_name"),
            "realm_access": user.get("realm_access"),
            "resource_access": user.get("resource_access"),
            "scope": user.get("scope"),
        },
    )


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _extract_keycloak_error(resp: httpx.Response) -> str:
    """Extract a human-readable error message from a Keycloak error response."""
    try:
        body = resp.json()
        return body.get("error_description", body.get("error", "Unknown error"))
    except Exception:
        return f"Keycloak returned status {resp.status_code}"
