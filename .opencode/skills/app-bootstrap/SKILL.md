---
name: app-bootstrap
description: 'Application entry point and module registration patterns. Uses Python FastAPI.
  Trigger: When creating new API projects, adding modules, or configuring middleware.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - shared-libs
  - backend-api
  consumed_by:
  - agent-backend
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use shared library modules | ALWAYS | Standardized infrastructure |
| Register routers with app.include_router | ALWAYS | Consistent module pattern |
| Middleware order is critical | ALWAYS | Wrong order causes runtime bugs |
| Generate local config files | ALWAYS | Required for local development |
| Store secrets in environment variables, never in files | ALWAYS | Security requirement |

## Python FastAPI — main.py completo

```python
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.api.v1.router import api_v1_router
from app.core.database import engine, Base
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Eventos de ciclo de vida: startup y shutdown."""
    logger.info("Iniciando aplicación — %s", settings.APP_NAME)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Base de datos inicializada")
    yield
    logger.info("Apagando aplicación — %s", settings.APP_NAME)
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="API REST del módulo vertical con FastAPI",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/swagger" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# ── Middleware (orden CRÍTICO) ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# ── Routers ────────────────────────────────────────────────────────
app.include_router(api_v1_router, prefix="/api/v1")

# ── Health checks ──────────────────────────────────────────────────
@app.get("/health/live", tags=["health"])
async def health_live():
    return {"status": "alive"}

@app.get("/health/ready", tags=["health"])
async def health_ready():
    from app.core.database import get_session
    async with get_session() as session:
        await session.execute("SELECT 1")
    return {"status": "ready"}

# ── Exception handlers ─────────────────────────────────────────────
register_exception_handlers(app)
```

### Service Registration Order (FastAPI)
```python
# 1. Logging
logging.basicConfig(level=logging.INFO)

# 2. Database
engine = create_async_engine(DATABASE_URL)

# 3. Authentication context
from app.auth import configure_auth
configure_auth(app)

# 4. Validation
from app.core.exceptions import register_exception_handlers
register_exception_handlers(app)

# 5. Routers (Handlers + Services)
from app.modules.entity.router import router as entity_router
app.include_router(entity_router, prefix="/api/v1/{entities}")

# 6. OpenAPI / Swagger
app.docs_url = "/swagger"

# 7. Health Checks
@app.get("/health")
async def health(): return {"status": "ok"}
```

## Required Configuration Files
| File | Purpose |
|------|---------|
| `.env` | Base config (committed template) |
| `.env.local` | Local dev overrides (gitignored) |
| `config.py` or `settings.py` | Pydantic Settings class |

## Environment Variables (Never in source code)
| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Database connection |
| `JWT_SECRET_KEY` | Auth credentials |
| `EXTERNAL_SERVICES__{NAME}__BASE_URL` | External API URLs |

## Pipeline de middleware — orden crítico

El orden en que se registran los middleware determina el orden en que se ejecutan en cada request. Un orden incorrecto causa bugs silenciosos, bypass de seguridad o errores 500 difíciles de diagnosticar.

### Diagrama de flujo

```
Request entrante
       │
       ▼
┌──────────────────────┐
│  1. Logging          │  ← Registra método, ruta, duración
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  2. Correlation ID   │  ← Asigna/extrae X-Correlation-ID
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  3. Exception        │  ← Captura errores de todo lo que sigue
│     Handler          │     (debe ir antes que todo)
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  4. CORS             │  ← Responde OPTIONS antes de auth
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  5. Auth             │  ← Valida token antes de llegar a rutas
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  6. Rate Limiting    │  ← Limita requests antes de procesar
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  7. Endpoints        │  ← Lógica de negocio
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  8. 404 Handler      │  ← Atrapa rutas no coincidentes
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  9. Error Handler    │  ← Centraliza respuestas de error
└──────────────────────┘
           │
           ▼
       Response
```

### Explicación del orden

| Posición | Middleware | ¿Por qué va aquí? |
|----------|-----------|-------------------|
| 1 | **Logging** | Necesita capturar TODAS las requests, incluso las que fallen antes de auth. |
| 2 | **Correlation ID** | Debe asignar un ID único antes de cualquier procesamiento. |
| 3 | **Exception Handler** | Debe ser el primer middleware después de logging/ID. |
| 4 | **CORS** | Las preflight requests (OPTIONS) deben responderse antes de cualquier verificación de auth. |
| 5 | **Auth** | Valida el token JWT/sesión. Debe ir después de CORS (para OPTIONS) y antes de rate limiting. |
| 6 | **Rate Limiting** | Limita requests después de auth. |
| 7 | **Endpoints** | Lógica de negocio. Debe ir después de todas las validaciones. |
| 8 | **404 Handler** | Captura rutas no definidas. |
| 9 | **Error Handler** | Centraliza la respuesta de error. Debe ser el último middleware. |

### Regla nemotécnica

> **L**ogging → **C**orrelation → **E**xception → **C**ORS → **A**uth → **R**ate → **E**ndpoint → **4**04 → **E**rror

**LCE-CARE-4E** — el orden que salva tu debug.

### Anti-patrones comunes

| Anti-patrón | Consecuencia |
|-------------|-------------|
| Exception handler después de auth | Errores de autenticación se devuelven sin formato estándar |
| CORS después de auth | Preflight OPTIONS devuelve 401 en lugar de 204 |
| Logging después del exception handler | Errores 500 no se registran en logs |
| Rate limiting antes de auth | Atacantes no autenticados consumen cuota del rate limiter |
| 404 handler antes de endpoints | Todas las rutas devuelven 404 |
| Body parser después de auth | Auth no puede leer el body de la request |

## FastAPI Middleware Order in Code
```python
# CRITICAL: Add middleware in exact order shown
app.add_middleware(RequestLoggingMiddleware)      # 1 — Logging
app.add_middleware(CorrelationIdMiddleware)        # 2 — Correlation ID
# Exception handlers via add_exception_handler()   # 3 — Registered via app.add_exception_handler
app.add_middleware(CORSMiddleware, ...)            # 4 — CORS before auth
# Auth via dependencies in routers                 # 5 — Auth
# Rate limiting via middleware or slowapi          # 6 — Rate limiting
app.include_router(api_v1_router)                 # 7 — Endpoints
# 404 handler via custom middleware                # 8 — 404
# Error handler via add_exception_handler()        # 9 — Error handler
```

## Checklist
- [ ] applicationName set and unique per service
- [ ] Middleware registered in correct order
- [ ] Routers registered with app.include_router
- [ ] Health check endpoint exposed
- [ ] Swagger/OpenAPI accessible in non-production
- [ ] Local config files created (not committed)
- [ ] Secrets from environment variables only
- [ ] CORS configurado antes que autenticación
- [ ] Rate limiter configurado con ventana y límite definidos
- [ ] Correlation ID propagado a logs y respuestas
- [ ] Exception handler registrado como primer middleware de negocio
