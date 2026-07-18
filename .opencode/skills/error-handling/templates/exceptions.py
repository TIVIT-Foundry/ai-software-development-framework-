"""
Application Exception Hierarchy — Centralized exception classes.

This module defines a clean, extensible exception hierarchy for the entire
application. Every custom exception inherits from AppException, which carries:

- HTTP status_code
- application error_code
- structured error details
- optional logging level override
- optional debug context (sanitized for production)

Usage:
    raise NotFoundException("User not found", resource="user", resource_id="abc-123")
    raise ValidationException("Email is required", field="email")
    raise AuthException("Invalid credentials", reason="token_expired")
    raise SystemException("Database connection failed", retryable=True)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import status as http_status

# ──────────────────────────────────────────────
# Error severity (controls logging level)
# ──────────────────────────────────────────────

class ErrorSeverity(int, Enum):
    """Maps application errors to Python logging levels."""

    DEBUG = logging.DEBUG       # 10
    INFO = logging.INFO         # 20
    WARNING = logging.WARNING   # 30
    ERROR = logging.ERROR       # 40
    CRITICAL = logging.CRITICAL # 50

    @property
    def log_level(self) -> int:
        return self.value


# ──────────────────────────────────────────────
# Error detail helper
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class ErrorDetail:
    """Structured representation of a single validation or domain error."""

    field: Optional[str] = None
    message: str = ""
    code: Optional[str] = None
    value: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"message": self.message}
        if self.field is not None:
            d["field"] = self.field
        if self.code is not None:
            d["code"] = self.code
        if self.value is not None:
            d["value"] = self.value
        return d


# ──────────────────────────────────────────────
# AppException — Base for all application errors
# ──────────────────────────────────────────────

class AppException(Exception):
    """Base class for all application-level exceptions.

    Subclasses set defaults for status_code, error_code, severity, etc.

    Attributes:
        status_code:    HTTP status code (default 500).
        error_code:     Machine-readable error code (e.g., "NOT_FOUND").
        message:        Human-readable error message.
        details:        Structured error details (list of ErrorDetail or raw dicts).
        severity:       Controls logging level (default ERROR).
        retryable:      Hint for retry logic (default False).
        debug_context:  Additional debug info (sanitized before being sent to clients).
    """

    status_code: int = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    severity: ErrorSeverity = ErrorSeverity.ERROR
    retryable: bool = False

    def __init__(
        self,
        message: str = "",
        *,
        details: Optional[List[Union[ErrorDetail, Dict[str, Any]]]] = None,
        debug_context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.message = message or self.__class__.__doc__ or "An application error occurred"
        self.details: List[ErrorDetail] = self._normalize_details(details)
        self.debug_context = debug_context or {}
        self.cause = cause

    def _normalize_details(
        self, raw: Optional[List[Union[ErrorDetail, Dict[str, Any]]]]
    ) -> List[ErrorDetail]:
        """Ensure all details are ErrorDetail instances."""
        if not raw:
            return []
        result: List[ErrorDetail] = []
        for item in raw:
            if isinstance(item, ErrorDetail):
                result.append(item)
            elif isinstance(item, dict):
                result.append(ErrorDetail(
                    field=item.get("field"),
                    message=item.get("message", ""),
                    code=item.get("code"),
                    value=item.get("value"),
                ))
            else:
                result.append(ErrorDetail(message=str(item)))
        return result

    def to_dict(self, include_debug: bool = False) -> Dict[str, Any]:
        """Serialize the exception to a dictionary (safe for API responses).

        Args:
            include_debug: If True, include debug_context (NEVER True in production).
        """
        d: Dict[str, Any] = {
            "code": self.error_code,
            "message": self.message,
        }
        if self.details:
            d["details"] = [detail.to_dict() for detail in self.details]
        if self.retryable:
            d["retryable"] = True
        if include_debug and self.debug_context:
            d["debug"] = self._sanitize_debug(self.debug_context)
        if self.cause and include_debug:
            d["debug_cause"] = repr(self.cause)
        return d

    @staticmethod
    def _sanitize_debug(ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Remove potentially sensitive keys from debug context."""
        sensitive_keys = {"password", "secret", "token", "api_key", "authorization", "cookie"}
        sanitized: Dict[str, Any] = {}
        for k, v in ctx.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = "***REDACTED***"
            elif isinstance(v, dict):
                sanitized[k] = AppException._sanitize_debug(v)
            else:
                sanitized[k] = v
        return sanitized

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status={self.status_code}, "
            f"code='{self.error_code}', "
            f"message='{self.message}')"
        )


# ──────────────────────────────────────────────
# Concrete Exception Classes
# ──────────────────────────────────────────────

class ValidationException(AppException):
    """Input validation failed (invalid data, missing fields, format errors)."""

    status_code = http_status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    severity = ErrorSeverity.WARNING

    def __init__(
        self,
        message: str = "Validation failed",
        *,
        field: Optional[str] = None,
        code: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[List[Union[ErrorDetail, Dict[str, Any]]]] = None,
        **kwargs: Any,
    ) -> None:
        if field and not details:
            details = [ErrorDetail(field=field, message=message, code=code, value=value)]
        super().__init__(message, details=details, **kwargs)


class NotFoundException(AppException):
    """Requested resource was not found."""

    status_code = http_status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    severity = ErrorSeverity.INFO

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        resource: Optional[str] = None,
        resource_id: Optional[Any] = None,
        details: Optional[List[Union[ErrorDetail, Dict[str, Any]]]] = None,
        **kwargs: Any,
    ) -> None:
        if resource and not details:
            details = [ErrorDetail(
                field=resource,
                message=message,
                code="RESOURCE_NOT_FOUND",
                value=resource_id,
            )]
        super().__init__(message, details=details, **kwargs)
        self.resource = resource
        self.resource_id = resource_id


class BadRequestException(AppException):
    """The request is malformed or cannot be processed."""

    status_code = http_status.HTTP_400_BAD_REQUEST
    error_code = "BAD_REQUEST"
    severity = ErrorSeverity.WARNING


class ConflictException(AppException):
    """The request conflicts with the current state (e.g., duplicate key)."""

    status_code = http_status.HTTP_409_CONFLICT
    error_code = "CONFLICT"
    severity = ErrorSeverity.WARNING


class AuthException(AppException):
    """Authentication or authorization failed.

    Use for:
    - Invalid credentials
    - Expired tokens
    - Insufficient permissions (when not using the RBAC layer directly)
    """

    status_code = http_status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"
    severity = ErrorSeverity.WARNING

    def __init__(
        self,
        message: str = "Authentication failed",
        *,
        reason: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if reason and (reason in ("token_expired", "token_invalid", "forbidden")):
            self.error_code = f"AUTH_{reason.upper()}"
            if reason == "forbidden":
                self.status_code = http_status.HTTP_403_FORBIDDEN
                self.error_code = "FORBIDDEN"
        super().__init__(message, **kwargs)


class ForbiddenException(AppException):
    """The authenticated user lacks permission for this action."""

    status_code = http_status.HTTP_403_FORBIDDEN
    error_code = "FORBIDDEN"
    severity = ErrorSeverity.WARNING


class RateLimitException(AppException):
    """Too many requests — rate limit exceeded."""

    status_code = http_status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"
    severity = ErrorSeverity.WARNING
    retryable = True

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after_seconds: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after_seconds = retry_after_seconds


class SystemException(AppException):
    """Internal system error (database, network, external service failure).

    These errors are typically retryable and should NOT expose internal
    details to the client.
    """

    status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "INTERNAL_ERROR"
    severity = ErrorSeverity.ERROR
    retryable = True

    def __init__(
        self,
        message: str = "An internal error occurred",
        *,
        service: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.service = service


class ServiceUnavailableException(AppException):
    """A downstream service is unavailable.

    Used for circuit-breaker open states, connection failures, etc.
    """

    status_code = http_status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"
    severity = ErrorSeverity.ERROR
    retryable = True

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        *,
        service: Optional[str] = None,
        retry_after_seconds: Optional[int] = 30,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.service = service
        self.retry_after_seconds = retry_after_seconds


class TimeoutException(AppException):
    """An operation timed out."""

    status_code = http_status.HTTP_504_GATEWAY_TIMEOUT
    error_code = "TIMEOUT"
    severity = ErrorSeverity.ERROR
    retryable = True


# ──────────────────────────────────────────────
# Domain-specific exceptions (extensible)
# ──────────────────────────────────────────────

class BusinessRuleException(AppException):
    """A business rule was violated (domain-level validation).

    Use this when a business invariant is broken, e.g.:
    - Cannot cancel an order already shipped
    - User already has an active subscription
    - Wallet balance insufficient

    These typically map to 422 or 409 depending on semantics.
    """

    status_code = http_status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "BUSINESS_RULE_VIOLATION"
    severity = ErrorSeverity.WARNING


class TenantException(AppException):
    """Multi-tenancy related error (wrong tenant, tenant not found, etc.)."""

    status_code = http_status.HTTP_403_FORBIDDEN
    error_code = "TENANT_ERROR"
    severity = ErrorSeverity.WARNING

    def __init__(
        self,
        message: str = "Tenant error",
        *,
        tenant_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.tenant_id = tenant_id


class DataIntegrityException(AppException):
    """Data integrity violation (foreign key, unique constraint, check constraint)."""

    status_code = http_status.HTTP_409_CONFLICT
    error_code = "DATA_INTEGRITY_ERROR"
    severity = ErrorSeverity.ERROR


# ──────────────────────────────────────────────
# Registry: map exception class → HTTP status
# ──────────────────────────────────────────────

EXCEPTION_REGISTRY: Dict[type, int] = {}

def _populate_registry() -> None:
    """Auto-populate the registry from all AppException subclasses."""
    for subclass in AppException.__subclasses__():
        EXCEPTION_REGISTRY[subclass] = subclass.status_code

_populate_registry()

# ──────────────────────────────────────────────
# Exception factory (convenience)
# ──────────────────────────────────────────────

def raise_not_found(resource: str, resource_id: Any) -> None:
    """Convenience: raise a NotFoundException."""
    raise NotFoundException(
        message=f"{resource} not found",
        resource=resource,
        resource_id=resource_id,
    )


def raise_validation(field: str, message: str, code: Optional[str] = None) -> None:
    """Convenience: raise a ValidationException."""
    raise ValidationException(message=message, field=field, code=code)
