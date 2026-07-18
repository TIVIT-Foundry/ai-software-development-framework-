"""
Permission Checker — FastAPI dependency for RBAC with require_roles.

This module provides FastAPI dependencies that enforce role-based access control
(RBAC). It integrates with the JWT payload produced by the authentication layer
(Keycloak tokens) and supports:

- Realm-level roles    (from `realm_access.roles`)
- Client-level roles   (from `resource_access.<client_id>.roles`)
- Composite role checks (AND / OR logic)
- Tenant-scoped roles  (for multi-tenant applications)

Usage:
    from templates.permission_checker import require_roles, require_any_role

    @app.get("/admin")
    async def admin_route(user: dict = Depends(require_roles("admin"))):
        ...

    @app.get("/dashboard")
    async def dashboard(user: dict = Depends(require_any_role("admin", "viewer"))):
        ...
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from fastapi import Depends, HTTPException, Request, status

from templates.auth_middleware import get_current_user

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Constants & Enums
# ──────────────────────────────────────────────

class RoleSource(str, Enum):
    """Where to look for roles in the JWT payload."""

    REALM = "realm"     # realm_access.roles
    CLIENT = "client"   # resource_access.<client_id>.roles
    ANY = "any"         # Search both realm and client roles

    @classmethod
    def _missing_(cls, value: object) -> "RoleSource":
        """Fallback: treat unknown values as ANY."""
        return cls.ANY


class RoleCheckMode(str, Enum):
    """How to combine multiple required roles."""

    ALL = "all"  # User must have ALL specified roles (AND)
    ANY = "any"  # User must have AT LEAST ONE specified role (OR)


# ──────────────────────────────────────────────
# Role extraction from JWT payload
# ──────────────────────────────────────────────

def _extract_realm_roles(payload: dict) -> Set[str]:
    """Extract realm-level roles from a Keycloak token payload."""
    realm_access: dict = payload.get("realm_access", {})
    return set(realm_access.get("roles", []))


def _extract_client_roles(payload: dict, client_id: Optional[str] = None) -> Set[str]:
    """Extract client-level roles from a Keycloak token payload.

    If client_id is None, roles from ALL clients are merged.
    """
    resource_access: dict = payload.get("resource_access", {})
    if client_id:
        client_entry = resource_access.get(client_id, {})
        return set(client_entry.get("roles", []))
    # Merge roles from every client
    roles: Set[str] = set()
    for client_roles in resource_access.values():
        roles.update(client_roles.get("roles", []))
    return roles


def get_user_roles(payload: dict, client_id: Optional[str] = None) -> Set[str]:
    """Return the full set of roles for a user from a JWT payload.

    By default merges realm roles and all client roles.
    Pass client_id to restrict to a specific client's roles.

    Args:
        payload:   Decoded JWT payload (from get_current_user).
        client_id: Optional Keycloak client ID to filter client roles.

    Returns:
        Set of role names (strings).
    """
    realm = _extract_realm_roles(payload)
    client = _extract_client_roles(payload, client_id)
    return realm | client


# ──────────────────────────────────────────────
# Permission rule definition
# ──────────────────────────────────────────────

class PermissionRule:
    """Defines a single permission/role check against the JWT payload.

    This can be extended to support:
    - Attribute-based checks (e.g., user.tenant == resource.tenant)
    - Scope checks             (e.g., scope "write:items")
    - Custom predicates         (e.g., user.group in resource.allowed_groups)
    """

    def __init__(
        self,
        roles: Union[str, List[str], Set[str]],
        source: RoleSource = RoleSource.ANY,
        mode: RoleCheckMode = RoleCheckMode.ALL,
        client_id: Optional[str] = None,
        tenant_id_param: Optional[str] = None,
    ) -> None:
        """
        Args:
            roles:           Single role name, list, or set of role names.
            source:          Where to look for the roles (realm, client, any).
            mode:            Whether ALL roles or ANY role is required.
            client_id:       If source is CLIENT, which client's roles to check.
            tenant_id_param: Optional query/path param name to extract tenant_id
                             for tenant-scoped role checks.
        """
        if isinstance(roles, str):
            self.roles: Set[str] = {roles}
        elif isinstance(roles, (list, set)):
            self.roles = set(roles)
        else:
            raise TypeError(f"roles must be str, list, or set; got {type(roles)}")

        self.source = RoleSource(source)
        self.mode = RoleCheckMode(mode)
        self.client_id = client_id
        self.tenant_id_param = tenant_id_param

    def check(self, payload: dict, request: Optional[Request] = None) -> bool:
        """Evaluate this rule against a user's JWT payload and optional request.

        Returns True if the user satisfies the rule.
        """
        # Gather applicable roles
        user_roles: Set[str] = set()
        if self.source in (RoleSource.REALM, RoleSource.ANY):
            user_roles |= _extract_realm_roles(payload)
        if self.source in (RoleSource.CLIENT, RoleSource.ANY):
            user_roles |= _extract_client_roles(payload, self.client_id)

        # --- Tenant-scoped roles (optional) ---
        if self.tenant_id_param and request is not None:
            tenant_id = request.query_params.get(self.tenant_id_param) or request.path_params.get(self.tenant_id_param)
            if tenant_id:
                # Check tenant-specific roles: "admin:tenant-<id>" or "admin@<id>"
                tenant_roles: Set[str] = set()
                for role in user_roles:
                    if ":" in role:
                        _, tid = role.split(":", 1)
                        if tid == tenant_id:
                            tenant_roles.add(role)
                # Also check if user has a general tenant admin role
                if not tenant_roles:
                    user_roles = set()  # No tenant access ⇒ fail
                else:
                    user_roles = tenant_roles

        # --- Role matching ---
        if self.mode == RoleCheckMode.ALL:
            return self.roles.issubset(user_roles)
        else:  # ANY
            return bool(self.roles & user_roles)

    def __repr__(self) -> str:
        return (
            f"PermissionRule(roles={self.roles}, source={self.source.value}, "
            f"mode={self.mode.value})"
        )


# ──────────────────────────────────────────────
# FastAPI Dependencies (factory functions)
# ──────────────────────────────────────────────

def require_roles(
    *roles: str,
    source: Union[str, RoleSource] = RoleSource.ANY,
    client_id: Optional[str] = None,
    tenant_id_param: Optional[str] = None,
) -> Callable:
    """Create a FastAPI dependency that requires the user to have ALL specified roles.

    Args:
        roles:            One or more role names (strings) — user must have ALL.
        source:           'realm', 'client', or 'any' (default: 'any').
        client_id:        Keycloak client ID (required if source is 'client').
        tenant_id_param:  If set, roles are scoped to a tenant extracted from this
                          query/path parameter.

    Returns:
        A FastAPI dependency callable.

    Raises:
        HTTPException 403 if the user lacks the required roles.

    Example:
        @app.get("/admin/users")
        async def admin_users(user: dict = Depends(require_roles("admin"))):
            ...

        @app.get("/orgs/{org_id}/settings")
        async def org_settings(
            org_id: str,
            user: dict = Depends(require_roles("admin", tenant_id_param="org_id")),
        ):
            ...
    """
    if not roles:
        raise ValueError("require_roles requires at least one role name")

    rule = PermissionRule(
        roles=list(roles),
        source=source,
        mode=RoleCheckMode.ALL,
        client_id=client_id,
        tenant_id_param=tenant_id_param,
    )

    async def dependency(
        request: Request,
        user: dict = Depends(get_current_user),
    ) -> dict:
        if not rule.check(user, request):
            logger.warning(
                "Access denied for sub='%s' — required roles: %s, source: %s, mode: ALL",
                user.get("sub", "?"),
                rule.roles,
                rule.source.value,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency


def require_any_role(
    *roles: str,
    source: Union[str, RoleSource] = RoleSource.ANY,
    client_id: Optional[str] = None,
    tenant_id_param: Optional[str] = None,
) -> Callable:
    """Create a FastAPI dependency that requires the user to have AT LEAST ONE of the specified roles.

    Args:
        roles:            One or more role names — user must have AT LEAST ONE.
        source:           'realm', 'client', or 'any' (default: 'any').
        client_id:        Keycloak client ID (required if source is 'client').
        tenant_id_param:  If set, roles are scoped to a tenant.

    Returns:
        A FastAPI dependency callable.

    Raises:
        HTTPException 403 if the user lacks ALL specified roles.

    Example:
        @app.get("/content")
        async def content(user: dict = Depends(require_any_role("editor", "viewer"))):
            ...
    """
    if not roles:
        raise ValueError("require_any_role requires at least one role name")

    rule = PermissionRule(
        roles=list(roles),
        source=source,
        mode=RoleCheckMode.ANY,
        client_id=client_id,
        tenant_id_param=tenant_id_param,
    )

    async def dependency(
        request: Request,
        user: dict = Depends(get_current_user),
    ) -> dict:
        if not rule.check(user, request):
            logger.warning(
                "Access denied for sub='%s' — required (any): %s, source: %s",
                user.get("sub", "?"),
                rule.roles,
                rule.source.value,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency


def require_permission(rule: PermissionRule) -> Callable:
    """Create a FastAPI dependency from a pre-built PermissionRule.

    This is the low-level factory — use require_roles / require_any_role for
    common cases, or build a custom PermissionRule for advanced scenarios.

    Example:
        rule = PermissionRule(roles={"admin", "superadmin"}, source=RoleSource.REALM)
        @app.get("/system", dependencies=[Depends(require_permission(rule))])
        async def system():
            ...
    """
    async def dependency(
        request: Request,
        user: dict = Depends(get_current_user),
    ) -> dict:
        if not rule.check(user, request):
            logger.warning(
                "Access denied for sub='%s' — rule: %s",
                user.get("sub", "?"),
                rule,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency
