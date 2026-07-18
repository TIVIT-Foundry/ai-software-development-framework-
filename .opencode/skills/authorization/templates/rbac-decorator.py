"""
RBAC Decorator — Decorator for endpoints with permission verification.

This module provides a Python decorator `@rbac` that wraps FastAPI endpoints
to enforce RBAC permission checks. It supports:

- Role-based checks   (realm roles, client roles, or both)
- Permission strings   (e.g., "users:write", "reports:export")
- Composite rules     (AND / OR logic)
- Tenant-scoped rules

The decorator works with both sync and async endpoint functions and integrates
with the JWT payload produced by get_current_user.

Usage:
    from templates.rbac_decorator import rbac, R

    @app.get("/items")
    @rbac(R.any("viewer", "editor"))
    async def list_items(user: dict = Depends(get_current_user)):
        ...

    @app.post("/items")
    @rbac(R.all("editor"))
    async def create_item(user: dict = Depends(get_current_user)):
        ...
"""

from __future__ import annotations

import asyncio
import functools
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Permission DSL (Domain-Specific Language)
# ──────────────────────────────────────────────

class _Operator(str, Enum):
    AND = "AND"
    OR = "OR"


@dataclass(frozen=True)
class Permission:
    """A single permission node in the permission tree.

    Attributes:
        value:          Permission string (e.g., "users:write") or role name.
        operator:       AND or OR (used when combining permissions).
        children:       Sub-permissions (for composite checks).
        source:         Where to look: 'realm', 'client', 'any'.
        client_id:      Keycloak client ID for client-level checks.
        tenant_param:   Query/path parameter name for tenant-scoped checks.
        description:    Human-readable description for audit/error messages.
    """

    value: str
    operator: _Operator = _Operator.AND
    children: List["Permission"] = field(default_factory=list)
    source: str = "any"
    client_id: Optional[str] = None
    tenant_param: Optional[str] = None
    description: str = ""

    def __post_init__(self) -> None:
        # Validate source
        if self.source not in ("realm", "client", "any"):
            raise ValueError(f"Invalid source '{self.source}': must be 'realm', 'client', or 'any'")

    def __repr__(self) -> str:
        return f"Permission('{self.value}', op={self.operator.value})"

    # ─── Combinators ──────────────────────────

    def __and__(self, other: "Permission") -> "Permission":
        """Combine two permissions with AND logic."""
        return Permission(
            value="(composite)",
            operator=_Operator.AND,
            children=[self, other],
        )

    def __or__(self, other: "Permission") -> "Permission":
        """Combine two permissions with OR logic."""
        return Permission(
            value="(composite)",
            operator=_Operator.OR,
            children=[self, other],
        )

    def with_tenant(self, param: str) -> "Permission":
        """Scope this permission to a tenant extracted from a path/query parameter."""
        return Permission(
            value=self.value,
            operator=self.operator,
            children=self.children,
            source=self.source,
            client_id=self.client_id,
            tenant_param=param,
            description=self.description,
        )


# ─── Convenience constructors ──────────────────────────────────────────

class R:
    """Fluent factory for building Permission trees.

    Usage:
        R.any("viewer", "editor")                     # OR: viewer or editor
        R.all("admin", "writer")                      # AND: admin AND writer
        R.perm("users:write")                         # Single permission
        (R.perm("admin") | R.perm("superadmin"))      # OR with |
        (R.perm("write") & R.perm("read"))            # AND with &
        R.client("my-app", "admin")                   # Client-level role
        R.realm("org_admin")                          # Realm-level role
        R.perm("admin").with_tenant("org_id")         # Tenant-scoped
    """

    @staticmethod
    def perm(value: str, description: str = "") -> Permission:
        """Create a single permission."""
        return Permission(value=value, description=description)

    @staticmethod
    def any(*values: str) -> Permission:
        """Create an OR-group of permissions."""
        if len(values) == 1:
            return Permission(value=values[0])
        return Permission(
            value="(any)",
            operator=_Operator.OR,
            children=[Permission(value=v) for v in values],
        )

    @staticmethod
    def all(*values: str) -> Permission:
        """Create an AND-group of permissions."""
        if len(values) == 1:
            return Permission(value=values[0])
        return Permission(
            value="(all)",
            operator=_Operator.AND,
            children=[Permission(value=v) for v in values],
        )

    @staticmethod
    def realm(role: str, description: str = "") -> Permission:
        """A realm-level role check."""
        return Permission(value=role, source="realm", description=description)

    @staticmethod
    def client(client_id: str, role: str, description: str = "") -> Permission:
        """A client-level role check."""
        return Permission(value=role, source="client", client_id=client_id, description=description)


# ──────────────────────────────────────────────
# Permission evaluator
# ──────────────────────────────────────────────

def _extract_roles(payload: dict, source: str, client_id: Optional[str] = None) -> Set[str]:
    """Extract roles from a JWT payload based on source."""
    roles: Set[str] = set()

    if source in ("realm", "any"):
        realm_access: dict = payload.get("realm_access", {})
        roles.update(realm_access.get("roles", []))

    if source in ("client", "any"):
        resource_access: dict = payload.get("resource_access", {})
        if client_id:
            client_entry = resource_access.get(client_id, {})
            roles.update(client_entry.get("roles", []))
        else:
            for client_roles in resource_access.values():
                roles.update(client_roles.get("roles", []))

    return roles


def _evaluate_permission(
    perm: Permission,
    payload: dict,
    request: Optional[Request] = None,
) -> bool:
    """Recursively evaluate a Permission tree against a JWT payload.

    Args:
        perm:    The Permission tree to evaluate.
        payload: Decoded JWT payload dictionary.
        request: Optional FastAPI Request (for tenant param extraction).

    Returns:
        True if the permission is granted.
    """
    # --- Tenant-scoped check ---
    user_roles = _extract_roles(payload, perm.source, perm.client_id)

    if perm.tenant_param and request is not None:
        tenant_id = (
            request.query_params.get(perm.tenant_param)
            or request.path_params.get(perm.tenant_param)
        )
        if tenant_id:
            scoped: Set[str] = set()
            for role in user_roles:
                if ":" in role:
                    _, tid = role.split(":", 1)
                    if tid == tenant_id:
                        scoped.add(role)
            user_roles = scoped if scoped else set()
        else:
            user_roles = set()  # No tenant found → fail

    # --- Composite (AND/OR children) ---
    if perm.children:
        if perm.operator == _Operator.AND:
            return all(
                _evaluate_permission(child, payload, request)
                for child in perm.children
            )
        else:  # OR
            return any(
                _evaluate_permission(child, payload, request)
                for child in perm.children
            )

    # --- Leaf: check the role/permission string ---
    return perm.value in user_roles


# ──────────────────────────────────────────────
# The @rbac decorator
# ──────────────────────────────────────────────

def rbac(
    permission: Permission,
    *,
    user_param: str = "user",
    error_message: Optional[str] = None,
    error_code: str = "FORBIDDEN",
    status_code: int = status.HTTP_403_FORBIDDEN,
    audit: bool = True,
) -> Callable:
    """Decorator to enforce RBAC on a FastAPI endpoint.

    Extracts a `request` and the JWT payload (from a named parameter) and
    evaluates the permission tree before allowing the endpoint to execute.

    Args:
        permission:     A Permission tree (built with R.* constructors).
        user_param:     Name of the endpoint parameter holding the JWT dict
                        (default: "user" — as produced by get_current_user).
        error_message:  Custom 403 detail message. Defaults to a description
                        of the required permission.
        error_code:     Application error code returned in the response.
        status_code:    HTTP status code (default 403).
        audit:          If True, log an audit event on denial.

    Usage:
        @app.get("/items")
        @rbac(R.any("viewer", "editor"))
        async def list_items(user: dict = Depends(get_current_user)):
            ...

        @app.post("/items")
        @rbac(R.all("admin", "editor"), user_param="current_user")
        async def create_item(current_user: dict = Depends(get_current_user)):
            ...
    """
    if error_message is None:
        error_message = f"Required permission: {permission}"

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Resolve the JWT payload and request from kwargs
            payload = kwargs.get(user_param)
            request_obj = None
            for v in kwargs.values():
                if isinstance(v, Request):
                    request_obj = v
                    break

            if payload is None:
                logger.error("rbac: user_param '%s' not found in kwargs", user_param)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication context not available",
                )

            if not _evaluate_permission(permission, payload, request_obj):
                if audit:
                    logger.warning(
                        "rbac DENIED — sub='%s', permission='%s', endpoint='%s'",
                        payload.get("sub", "?"),
                        permission,
                        func.__name__,
                    )
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        "code": error_code,
                        "message": error_message,
                        "required": str(permission),
                    },
                )

            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Resolve the JWT payload and request from kwargs
            payload = kwargs.get(user_param)
            request_obj = None
            for v in kwargs.values():
                if isinstance(v, Request):
                    request_obj = v
                    break

            if payload is None:
                logger.error("rbac: user_param '%s' not found in kwargs", user_param)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication context not available",
                )

            if not _evaluate_permission(permission, payload, request_obj):
                if audit:
                    logger.warning(
                        "rbac DENIED — sub='%s', permission='%s', endpoint='%s'",
                        payload.get("sub", "?"),
                        permission,
                        func.__name__,
                    )
                raise HTTPException(
                    status_code=status_code,
                    detail={
                        "code": error_code,
                        "message": error_message,
                        "required": str(permission),
                    },
                )

            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# ──────────────────────────────────────────────
# Convenience: class-based decorator
# ──────────────────────────────────────────────

class RBACDecorator:
    """Class-based RBAC decorator that can be instantiated with shared config.

    Useful when you want to reuse the same audit/log settings across endpoints.

    Usage:
        rbac_check = RBACDecorator(audit=True)

        @app.get("/items")
        @rbac_check(R.any("viewer", "editor"))
        async def list_items(user: dict = Depends(get_current_user)):
            ...
    """

    def __init__(
        self,
        user_param: str = "user",
        error_code: str = "FORBIDDEN",
        status_code: int = status.HTTP_403_FORBIDDEN,
        audit: bool = True,
    ) -> None:
        self.user_param = user_param
        self.error_code = error_code
        self.status_code = status_code
        self.audit = audit

    def __call__(self, permission: Permission) -> Callable:
        return rbac(
            permission,
            user_param=self.user_param,
            error_code=self.error_code,
            status_code=self.status_code,
            audit=self.audit,
        )
