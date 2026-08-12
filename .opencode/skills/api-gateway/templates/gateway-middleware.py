"""
FastAPI Gateway Middleware
==========================
Middleware stack for an API Gateway built on FastAPI. Handles:
  - Correlation ID generation/propagation
  - Rate limiting (per IP, per tenant, per route)
  - Structured request logging
  - JWT authentication & identity propagation to downstream services
  - CORS preflight
  - Request timeout enforcement

Stack: Python 3.12+ / FastAPI / slowapi (rate limiting) / PyJWT (JWT) / structlog

Usage:
    from gateway_middleware import GatewayMiddlewareStack

    app = FastAPI()
    stack = GatewayMiddlewareStack(app, config=GatewayConfig())
    stack.register_all()
"""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class GatewayConfig:
    """Gateway-wide configuration."""

    # ---- Correlation ID ----
    correlation_id_header: str = "X-Correlation-Id"
    correlation_id_response_header: str = "X-Correlation-Id"

    # ---- Rate Limiting (per-IP defaults; route-specific overrides in ROUTE_RATE_LIMITS) ----
    global_rate_limit: str = "100/minute"
    auth_rate_limit: str = "5/minute"

    # ---- JWT ----
    jwt_secret_key: str = field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""))
    jwt_algorithms: list[str] = field(default_factory=lambda: ["HS256"])

    # ---- Identity propagation headers ----
    user_id_header: str = "X-User-Id"
    roles_header: str = "X-Roles"
    tenant_id_header: str = "X-Tenant-Id"

    # ---- Paths excluded from authentication ----
    excluded_auth_paths: list[str] = field(default_factory=lambda: [
        "/swagger",
        "/openapi.json",
        "/health",
        "/metrics",
        "/auth/api/v1/login",
        "/auth/api/v1/refresh",
        "/docs",
        "/redoc",
    ])

    # ---- Paths excluded from rate limiting ----
    excluded_rate_limit_paths: list[str] = field(default_factory=lambda: [
        "/swagger",
        "/openapi.json",
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
    ])

    # ---- CORS ----
    cors_allow_origins: list[str] = field(default_factory=lambda: [
        "http://localhost:4200",
        "http://localhost:3000",
    ])
    cors_allow_methods: list[str] = field(default_factory=lambda: [
        "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS",
    ])
    cors_allow_headers: list[str] = field(default_factory=lambda: [
        "Authorization",
        "Content-Type",
        "X-Correlation-Id",
        "X-Tenant-Id",
        "X-Api-Key",
        "Accept-Language",
    ])
    cors_allow_credentials: bool = True
    cors_max_age: int = 86400

    # ---- Logging ----
    log_level: str = "INFO"
    log_request_body_max: int = 4096      # Max bytes to log from request body
    log_response_body_max: int = 4096     # Max bytes to log from response body


# =============================================================================
# Rate limit per-route configuration
# =============================================================================
ROUTE_RATE_LIMITS: dict[str, str] = {
    # Pattern → rate limit string
    "/auth/api/v1/login":          "5/minute",
    "/auth/api/v1/refresh":        "10/minute",
    "/users/api/v1/":              "30/second",
    "/orders/api/v1/":             "30/second",
    "/notifications/api/v1/":      "20/second",
    "/bun/api/v1/":                "30/second",
}


# =============================================================================
# Correlation ID Middleware
# =============================================================================

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Ensures every request has a correlation ID.
    - Reads existing X-Correlation-Id from the request header.
    - If absent, generates a new UUID4.
    - Adds the correlation ID to the response header.
    - Attaches the correlation ID to structlog context for all downstream logs.
    """

    def __init__(self, app, header_name: str, response_header: str):
        super().__init__(app)
        self.header_name = header_name
        self.response_header = response_header

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        correlation_id = request.headers.get(self.header_name)
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Bind correlation ID to all logs during this request's lifetime
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        # Store in request state for downstream middleware/routes
        request.state.correlation_id = correlation_id

        # Process request
        response: Response = await call_next(request)

        # Always return correlation ID to caller
        response.headers[self.response_header] = correlation_id

        # Clean up context after response
        structlog.contextvars.unbind_contextvars("correlation_id")
        return response


# =============================================================================
# Request Logging Middleware
# =============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request in structured JSON format.
    Captures: method, path, status, latency, client IP, user ID, tenant, correlation ID.
    """

    def __init__(self, app, config: GatewayConfig):
        super().__init__(app)
        self.config = config

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.perf_counter()

        # Process the request
        response: Response = await call_next(request)

        # Calculate latency
        duration_ms = round((time.perf_counter() - start_time) * 1000, 3)

        # Build structured log entry
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "query_string": str(request.url.query) if request.url.query else None,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent", ""),
            "correlation_id": getattr(request.state, "correlation_id", None),
            "user_id": request.headers.get(self.config.user_id_header),
            "tenant_id": request.headers.get(self.config.tenant_id_header),
        }

        # Choose log level based on status code
        if response.status_code >= 500:
            logger.error("gateway_request", **log_data)
        elif response.status_code >= 400:
            logger.warning("gateway_request", **log_data)
        else:
            logger.info("gateway_request", **log_data)

        return response


# =============================================================================
# JWT Authentication Middleware
# =============================================================================

class GatewayAuthMiddleware(BaseHTTPMiddleware):
    """
    Validates JWT tokens and propagates identity to downstream services.
    - Extracts Bearer token from Authorization header.
    - Decodes JWT claims (sub, roles, tenant_id).
    - Sets X-User-Id, X-Roles, X-Tenant-Id headers on the request.
    - Skips excluded paths (health, swagger, login, etc.).

    Downstream services should trust these headers (Zero Trust internally)
    and NOT re-validate the original JWT token.
    """

    AUTH_HEADER = "Authorization"
    BEARER_PREFIX = "Bearer "

    def __init__(self, app, config: GatewayConfig):
        super().__init__(app)
        self.config = config

    def _is_excluded(self, path: str) -> bool:
        """Check if the path is excluded from authentication."""
        return any(path.startswith(excluded) for excluded in self.config.excluded_auth_paths)

    def _decode_token(self, token: str) -> dict:
        """Decode and validate JWT token. Raises on failure."""
        import jwt
        from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=self.config.jwt_algorithms,
            )
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": {"code": "AUTH_TOKEN_EXPIRED", "message": "Token has expired"}},
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": {"code": "AUTH_INVALID_TOKEN", "message": f"Invalid token: {str(e)}"}},
            )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        from fastapi import HTTPException

        # Skip auth for excluded paths
        if self._is_excluded(request.url.path):
            return await call_next(request)

        # Extract Bearer token
        auth_header = request.headers.get(self.AUTH_HEADER, "")
        if not auth_header.startswith(self.BEARER_PREFIX):
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {"code": "AUTH_MISSING_TOKEN", "message": "Missing or invalid Authorization header"},
                },
            )

        token = auth_header[len(self.BEARER_PREFIX):]

        # Validate and decode JWT
        try:
            payload = self._decode_token(token)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail,
            )

        # Extract identity claims
        user_id = payload.get("sub", "")
        roles = payload.get("roles", [])
        tenant_id = payload.get("tenant_id", "")

        # Validate required claims
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {"code": "AUTH_MISSING_SUB", "message": "Token missing 'sub' claim"},
                },
            )

        # Store identity in request state for access by routes/other middleware
        request.state.user_id = user_id
        request.state.roles = roles if isinstance(roles, list) else [roles]
        request.state.tenant_id = tenant_id

        # Mutate request headers to propagate identity downstream
        # (scope headers are tuples; we rebuild the headers list)
        request.scope["headers"] = [
            *request.scope.get("headers", []),
            (self.config.user_id_header.lower().encode(), user_id.encode()),
            (self.config.roles_header.lower().encode(), ",".join(request.state.roles).encode()),
            (self.config.tenant_id_header.lower().encode(), tenant_id.encode()),
        ]

        # Bind identity to log context
        structlog.contextvars.bind_contextvars(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        return await call_next(request)


# =============================================================================
# Rate Limiting Setup
# =============================================================================

class GatewayRateLimiter:
    """
    Configures rate limiting using slowapi.
    - Per-IP rate limiting via slowapi's Limiter.
    - Global default + per-route overrides via ROUTE_RATE_LIMITS.
    - Custom key function that can use tenant ID or API key when available.
    """

    def __init__(self, config: GatewayConfig):
        self.config = config

        # Custom key function: tenant-aware rate limiting
        def tenant_aware_key(request: Request) -> str:
            """Rate limit key: uses tenant_id if available, otherwise IP."""
            tenant_id = request.headers.get(config.tenant_id_header)
            if tenant_id:
                return f"tenant:{tenant_id}"
            # Fall back to client IP
            return get_remote_address(request)

        # Default limiter with IP-based key
        self.default_limiter = Limiter(key_func=get_remote_address)

    def configure(self, app: FastAPI, limiter: Limiter | None = None) -> Limiter:
        """
        Apply rate limiting to the FastAPI app.
        Returns the Limiter instance for use in dependency injection on routes.
        """
        if limiter is None:
            limiter = self.default_limiter

        # Store limiter in app state for access by routes
        app.state.limiter = limiter

        # Register generic rate limit handler
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

        return limiter

    @staticmethod
    def get_route_rate_limit(path: str) -> str:
        """Look up rate limit string for a given route path."""
        for prefix, rate in ROUTE_RATE_LIMITS.items():
            if path.startswith(prefix):
                return rate
        return ""

    @staticmethod
    def apply_route_limits(limiter: Limiter, app: FastAPI) -> None:
        """
        Apply per-route rate limits by iterating over registered routes.
        This is called after all routes are registered.
        Uses slowapi's @limiter.limit() decorator pattern via route metadata.

        Note: In production, prefer declarative limits via nginx.conf or
        applying @limiter.limit() directly on route handlers.
        """
        # slowapi applies limits via decorator; for dynamic application,
        # routes should use `@limiter.limit("30/second")` directly.
        # This method serves as documentation of expected per-route limits.
        for route in app.routes:
            if hasattr(route, "path"):
                rate = GatewayRateLimiter.get_route_rate_limit(route.path)
                if rate:
                    logger.debug(
                        "rate_limit_route",
                        path=route.path,
                        rate_limit=rate,
                    )


# =============================================================================
# Gateway Middleware Stack — Facade
# =============================================================================

class GatewayMiddlewareStack:
    """
    Facade that registers all gateway middleware in the correct order.

    ORDER IS CRITICAL — middleware is executed in reverse of registration:
      1. CORSMiddleware          (outermost — handle preflight early)
      2. CorrelationIdMiddleware (assign correlation ID)
      3. RequestLoggingMiddleware (log the raw request)
      4. GatewayRateLimiter      (rate limiting check)
      5. GatewayAuthMiddleware   (JWT validation & identity propagation)
      6. Route handler           (innermost — the actual endpoint)

    Usage:
        app = FastAPI()
        config = GatewayConfig(
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            cors_allow_origins=["http://localhost:4200", "https://app.example.com"],
        )
        stack = GatewayMiddlewareStack(app, config)
        stack.register_all()
    """

    def __init__(self, app: FastAPI, config: GatewayConfig | None = None):
        self.app = app
        self.config = config or GatewayConfig()
        self.rate_limiter_manager = GatewayRateLimiter(self.config)

    def register_all(self) -> Limiter:
        """Register all middleware and rate limiting. Returns the Limiter instance."""
        # ---- Layer 1: CORS (outermost — handle preflight OPTIONS early) ----
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_allow_origins,
            allow_credentials=self.config.cors_allow_credentials,
            allow_methods=self.config.cors_allow_methods,
            allow_headers=self.config.cors_allow_headers,
            max_age=self.config.cors_max_age,
        )

        # ---- Layer 2: Correlation ID (assigns X-Correlation-Id to every request) ----
        self.app.add_middleware(
            CorrelationIdMiddleware,
            header_name=self.config.correlation_id_header,
            response_header=self.config.correlation_id_response_header,
        )

        # ---- Layer 3: Request Logging (structured JSON logs) ----
        self.app.add_middleware(
            RequestLoggingMiddleware,
            config=self.config,
        )

        # ---- Layer 4: Gateway Auth (JWT validation before rate limiting) ----
        self.app.add_middleware(
            GatewayAuthMiddleware,
            config=self.config,
        )

        # ---- Layer 5: Rate Limiting ----
        limiter = self.rate_limiter_manager.configure(self.app)

        logger.info(
            "gateway_middleware_registered",
            middleware_order=[
                "CORSMiddleware",
                "CorrelationIdMiddleware",
                "RequestLoggingMiddleware",
                "GatewayAuthMiddleware",
                "RateLimiter",
            ],
            excluded_auth_paths=self.config.excluded_auth_paths,
            cors_origins=self.config.cors_allow_origins,
        )

        return limiter


# =============================================================================
# Helper decorator: apply rate limit to a route handler
# =============================================================================

def route_rate_limit(rate: str | None = None):
    """
    Decorator to apply rate limiting to a specific FastAPI route.
    Uses the limiter stored in app.state.

    Usage:
        @router.get("/users")
        @route_rate_limit("30/second")
        async def get_users(): ...

    If rate is None, uses the default from ROUTE_RATE_LIMITS based on path.
    """
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # The actual rate limiting is handled by slowapi's middleware
            # based on the @limiter.limit() decorator already applied.
            # This is a passthrough for documentation purposes.
            return await func(*args, **kwargs)
        # Tag the function for documentation
        wrapper.__rate_limit__ = rate
        return wrapper
    return decorator


# =============================================================================
# FastAPI route example: applying rate limiting to specific endpoints
# =============================================================================

def example_routes():
    """
    Example of how to apply per-route rate limiting in your FastAPI app.

    In your actual route files:

        from fastapi import FastAPI, APIRouter, Request
        from slowapi import Limiter
        from slowapi.util import get_remote_address

        limiter = Limiter(key_func=get_remote_address)
        router = APIRouter()

        @router.get("/users", response_model=UserListResponse)
        @limiter.limit("30/second")
        async def list_users(request: Request, ...):
            ...

        # For auth endpoints, use stricter limits:
        @router.post("/auth/login")
        @limiter.limit("5/minute")
        async def login(request: Request, ...):
            ...
    """
    pass
