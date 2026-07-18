"""
Exception Handlers — FastAPI exception handlers with ApiResponse wrapper.

This module registers global exception handlers on a FastAPI app to ensure
every error response follows the standardized ApiResponse envelope:

    {
        "success": false,
        "error": {
            "code": "NOT_FOUND",
            "message": "User not found",
            "details": [...]
        },
        "data": null,
        "meta": {
            "trace_id": "abc-123",
            "timestamp": "2026-07-17T12:00:00Z"
        }
    }

Supported handlers:
- AppException & subclasses     → mapped to their status_code
- HTTPException                 → converted to AppException shape
- RequestValidationError       → 422 with field-level details
- Starlette HTTPException       → generic HTTP error
- Exception (catch-all)         → 500 with sanitized message

Usage:
    from fastapi import FastAPI
    from templates.exception_handlers import register_exception_handlers

    app = FastAPI()
    register_exception_handlers(app)
"""

from __future__ import annotations

import logging
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from templates.exceptions import (
    AppException,
    ErrorSeverity,
    ValidationException,
    SystemException,
)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# ApiResponse builder
# ──────────────────────────────────────────────

def build_error_response(
    status_code: int,
    error_code: str,
    message: str,
    *,
    details: Optional[list] = None,
    trace_id: Optional[str] = None,
    retryable: bool = False,
    headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    """Build a standardized error JSONResponse.

    Args:
        status_code: HTTP status code.
        error_code:  Machine-readable error code.
        message:     Human-readable error message.
        details:     Optional structured error details.
        trace_id:    Correlation ID for tracing (auto-generated if None).
        retryable:   Whether the client may retry.
        headers:     Additional response headers.

    Returns:
        JSONResponse with the ApiResponse envelope.
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    body: Dict[str, Any] = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        },
        "data": None,
        "meta": {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }

    if details:
        body["error"]["details"] = jsonable_encoder(details)
    if retryable:
        body["error"]["retryable"] = True

    response_headers: Dict[str, str] = {"X-Trace-Id": trace_id}
    if headers:
        response_headers.update(headers)

    return JSONResponse(
        status_code=status_code,
        content=body,
        headers=response_headers,
    )


# ──────────────────────────────────────────────
# Individual handlers
# ──────────────────────────────────────────────

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all AppException subclasses.

    Logs at the severity level defined by the exception class.
    """
    log_message = f"[{exc.error_code}] {exc.message}"
    extra = {
        "trace_id": str(uuid.uuid4()),
        "path": request.url.path,
        "method": request.method,
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "debug_context": exc.debug_context,
    }

    # Log at the appropriate level
    log_method = {
        ErrorSeverity.DEBUG: logger.debug,
        ErrorSeverity.INFO: logger.info,
        ErrorSeverity.WARNING: logger.warning,
        ErrorSeverity.ERROR: logger.error,
        ErrorSeverity.CRITICAL: logger.critical,
    }.get(exc.severity, logger.error)

    if exc.cause:
        log_method(log_message, extra=extra, exc_info=exc.cause)
    else:
        log_method(log_message, extra=extra)

    # Build details
    details = [
        {"field": d.field, "message": d.message, "code": d.code, "value": d.value}
        for d in exc.details
    ] if exc.details else None

    headers: Dict[str, str] = {}
    if hasattr(exc, "retry_after_seconds") and exc.retry_after_seconds:
        headers["Retry-After"] = str(exc.retry_after_seconds)

    return build_error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=details,
        trace_id=extra["trace_id"],
        retryable=exc.retryable,
        headers=headers,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette/FastAPI HTTPException.

    Converts generic HTTP exceptions into the ApiResponse envelope.
    """
    trace_id = str(uuid.uuid4())

    # Map HTTP status code → error code
    error_code_map: Dict[int, str] = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        406: "NOT_ACCEPTABLE",
        408: "TIMEOUT",
        409: "CONFLICT",
        410: "GONE",
        413: "PAYLOAD_TOO_LARGE",
        414: "URI_TOO_LONG",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        501: "NOT_IMPLEMENTED",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }

    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")

    # If the detail is already a structured dict, use it
    if isinstance(exc.detail, dict):
        detail_message = exc.detail.get("message", str(exc.detail))
        detail_code = exc.detail.get("code", error_code)
    else:
        detail_message = str(exc.detail)
        detail_code = error_code

    logger.warning(
        "[%s] %s — %s %s",
        detail_code,
        detail_message,
        request.method,
        request.url.path,
        extra={"trace_id": trace_id, "status_code": exc.status_code},
    )

    return build_error_response(
        status_code=exc.status_code,
        error_code=detail_code,
        message=detail_message,
        trace_id=trace_id,
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic request validation errors (422).

    Converts field-level errors into structured details.
    """
    trace_id = str(uuid.uuid4())
    details = []

    for error in exc.errors():
        # error shape: {"loc": [...], "msg": "...", "type": "..."}
        loc = error.get("loc", [])
        msg = error.get("msg", "Invalid value")
        error_type = error.get("type", "type_error")

        field = ".".join(str(part) for part in loc if part != "body")

        details.append({
            "field": field or "unknown",
            "message": msg,
            "code": f"VALIDATION_{error_type.upper()}",
            "value": error.get("input"),
        })

    logger.warning(
        "Validation error on %s %s — %d errors",
        request.method,
        request.url.path,
        len(details),
        extra={"trace_id": trace_id, "details": details},
    )

    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details=details,
        trace_id=trace_id,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions (500).

    Logs the full traceback but returns a sanitized message to the client
    to avoid leaking internal details.
    """
    trace_id = str(uuid.uuid4())

    logger.critical(
        "Unhandled exception: %s — %s %s",
        exc.__class__.__name__,
        request.method,
        request.url.path,
        extra={
            "trace_id": trace_id,
            "exception_type": exc.__class__.__name__,
            "exception_message": str(exc),
        },
        exc_info=True,
    )

    # In production, NEVER expose the real error message
    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        trace_id=trace_id,
    )


# ──────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on a FastAPI application.

    Call this once during app startup (after creating the FastAPI instance).

    Args:
        app: The FastAPI application instance.

    Example:
        from fastapi import FastAPI
        from templates.exception_handlers import register_exception_handlers

        app = FastAPI(title="My API", version="1.0.0")
        register_exception_handlers(app)

        # Now every unhandled exception will produce a clean ApiResponse.
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info(
        "Registered exception handlers: AppException, HTTPException, "
        "RequestValidationError, Exception (catch-all)"
    )
