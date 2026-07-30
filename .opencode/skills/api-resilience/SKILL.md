---
name: api-resilience
description: "API resilience patterns including rate limiting, circuit breakers, bulkheads, retry policies, timeouts, and API quotas. Covers patterns for multi-tenant APIs, backpressure handling, and fallback strategies. Uses Python/FastAPI with tenacity + slowapi. Trigger: When implementing rate limiting, circuit breakers, retry logic, or API resilience patterns."
version: 1.1
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: recommended
  depends_on:
  - backend-api
  - error-handling
  consumed_by:
  - backend-api
  - react-services
  - angular-services
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# api-resilience

## Propósito

Esta skill define cómo hacer que las APIs sean resilientes ante fallos, sobrecarga y dependencias inestables.  
Su función es asegurar que la API no se caiga cuando una dependencia falla, que los tenants no se afecten entre sí, y que los clientes reciban respuestas útiles en vez de timeouts silenciosos.

Esta skill complementa `error-handling` (estructura de errores) y `security` (validación de inputs). Mientras aquellos manejan errores conocidos y validación, esta skill maneja fallos inesperados, sobrecarga y degradación controlada.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué estrategia de rate limiting usar (fixed window, sliding window, token bucket)?
2. ¿Cómo implementar circuit breakers para dependencias externas?
3. ¿Cómo aislar fallos con bulkheads?
4. ¿Qué política de retry usar (exponential backoff, jitter)?
5. ¿Cuáles son los timeouts por defecto y cómo se configuran?

## Relación con otras skills

- `backend-api` define los endpoints que esta skill protege.
- `error-handling` define la estructura de errores; esta skill define cuándo devolverlos.
- `security` define la autenticación; esta skill define los límites por usuario/tenant.
- `authorization` define los permisos; esta skill define las cuotas por permiso.
- `shared-libs` puede incluir rate limiting como shared middleware.

## Qué debe hacer el agente cuando esta skill está activa

1. Definir la estrategia de rate limiting por endpoint y tenant.
2. Implementar circuit breakers para dependencias externas.
3. Configurar bulkheads para aislar recursos por tenant.
4. Definir políticas de retry con exponential backoff y jitter.
5. Configurar timeouts por defecto para todas las llamadas externas.
6. Implementar fallbacks para cuando los circuitos están abiertos.
7. Definir cuotas de API por tenant/plan.
8. Implementar backpressure para cuando el sistema está sobrecargado.

## Entradas esperadas

Esta skill asume que ya existe:
- estructura de endpoints (`backend-api`);
- manejo de errores definido (`error-handling`);
- autenticación (`authentication`) y autorización (`authorization`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- rate limiting (fixed window, sliding window, token bucket);
- circuit breakers para dependencias externas;
- bulkheads por tenant;
- retry con exponential backoff y jitter;
- timeouts configurables;
- fallbacks y degradación controlada;
- cuotas de API por tenant/plan;
- backpressure;

La fase no incluye todavía:
- estructura de errores (cubierta por `error-handling`);
- autenticación y autorización (`authentication`, `authorization`);
- caching (cubierta parcialmente por `performance`);
- load testing (cubierta por `load-testing`).

## Principios que siempre debe respetar

- Rate limiting DEBE ser por tenant en APIs multi-tenant.
- Circuit breakers DEBEN tener estados (closed, open, half-open) con timeouts configurables.
- Retries NUNCA deben ser sin backoff (retry instantáneo = murdering the service).
- Timeouts DEBEN estar configurados para TODAS las llamadas externas (nunca infinito).
- Bulkheads DEBEN aislar recursos por tenant (un tenant no puede agotar el pool de otro).
- Fallbacks DEBEN degradar controladamente (cached response, default value, error amigable).
- Los rate limits DEBEN incluir headers de respuesta (X-RateLimit-Remaining, X-RateLimit-Reset).

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la estrategia de rate limiting y las cuotas;
- los circuit breakers y sus configuraciones;
- las políticas de retry y timeouts;
- los bulkheads y su aislamiento;

Esta skill delega:
- la estructura de errores a `error-handling`;
- la autenticación a `authentication`;
- la autorización de permisos a `authorization`;
- la optimización de rendimiento a `performance`.

## Qué debe definir el diseño

### 1. Rate Limiting

| Algoritmo | Pros | Contras | Uso recomendado |
|-----------|------|---------|-----------------|
| **Fixed Window** | Simple, rápido | Burst al reset del window | APIs con límites generosos |
| **Sliding Window** | Preciso, sin burst | Más complejo | **Por defecto** para APIs multi-tenant |
| **Token Bucket** | Permite burst controlado | Más memoria | APIs con límites estrictos por segundo |
| **Leaky Bucket** | Smooth output | Sin burst | APIs donde la tasa constante importa |

**Decisión por defecto**: Sliding Window para APIs multi-tenant.

### 2. Rate limiting con slowapi (FastAPI)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Rate limit por tenant
@limiter.limit("100/minute")
@router.get("/entities")
async def list_entities(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    return await service.list(tenant_id=current_user["tenant_id"])
```

### 3. Rate limit headers

```python
from fastapi import Response

@router.get("/entities")
async def list_entities(response: Response):
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "99"
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
    return await service.list()
```

### 4. Circuit Breaker con tenacity

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    CircuitBreaker, retry_if_result
)
import httpx
import logging

logger = logging.getLogger(__name__)

# Circuit breaker para dependencias externas
circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,  # seconds
    expected_exception=httpx.HTTPStatusError,
)

class ExternalServiceHandler:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_result(lambda r: r.status_code in [502, 503]),
        before_sleep=lambda retry_state: logger.warning(
            "Retry %d after %.1fs", retry_state.attempt_number, retry_state.idle_for
        ),
    )
    async def call_external_service(self, url: str) -> dict:
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                circuit_breaker.record_failure()
                logger.warning("Circuit breaker failure recorded")
            raise
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error("External service error: %s", e)
            raise
```

### 5. Retry con exponential backoff y jitter

```python
from tenacity import retry, stop_after_attempt, wait_exponential

# Retry policy con exponential backoff + jitter
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def call_with_retry(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code in [502, 503, 504]:
            raise httpx.HTTPStatusError(
                "Service unavailable", request=response.request, response=response
            )
        return response.json()
```

### 6. Timeouts configurables

```python
import httpx
from contextlib import asynccontextmanager

# Timeout policy via httpx
timeout = httpx.Timeout(30.0, connect=5.0)

async def call_external(url: str) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        return response.json()

# Configurable timeouts per endpoint
class TimeoutConfig:
    default_timeout: float = 30.0
    connect_timeout: float = 5.0
    per_endpoint: dict[str, float] = {
        "orders": 10.0,
        "reports": 60.0,
    }
```

### 7. Bulkheads por tenant

```python
import asyncio
from collections import defaultdict

class TenantBulkheadFactory:
    def __init__(self, max_concurrency_per_tenant: int = 10):
        self._bulkheads: dict[str, asyncio.Semaphore] = defaultdict(
            lambda: asyncio.Semaphore(max_concurrency_per_tenant)
        )

    async def execute(self, tenant_id: str, action):
        bulkhead = self._bulkheads[tenant_id]
        async with bulkhead:
            return await action()
```

### 8. Cuotas de API por plan

```python
from dataclasses import dataclass

@dataclass
class RateLimitPlan:
    requests_per_minute: int
    requests_per_day: int
    burst_limit: int

RATE_LIMIT_PLANS: dict[str, RateLimitPlan] = {
    "free": RateLimitPlan(requests_per_minute=10, requests_per_day=1000, burst_limit=5),
    "pro": RateLimitPlan(requests_per_minute=100, requests_per_day=10000, burst_limit=50),
    "enterprise": RateLimitPlan(requests_per_minute=1000, requests_per_day=100000, burst_limit=200),
}
```

### 9. Fallback y degradación controlada

| Escenario | Fallback | Ejemplo |
|-----------|----------|---------|
| Servicio externo caído | Cache local | Última respuesta cacheada por 5 min |
| BD no disponible | Read-only mode | Solo GETs, POSTs devuelven 503 |
| Rate limit excedido | 429 + Retry-After | Header con segundos hasta reset |
| Timeout de dependencia | Respuesta default | Valor por defecto o 202 Accepted |
| Circuit breaker abierto | Fallback cache | Última respuesta exitosa cacheada |

### 10. Backpressure

```python
import asyncio
from fastapi import HTTPException, status

class BackpressureMiddleware:
    def __init__(self, max_concurrent_requests: int = 100):
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def __call__(self, request, call_next):
        try:
            acquired = await asyncio.wait_for(
                self._semaphore.acquire(), timeout=5.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=503,
                detail="Server is busy. Please retry later."
            )
        try:
            response = await call_next(request)
            return response
        finally:
            self._semaphore.release()
```

## Preguntas guía

### 1. Sobre rate limiting
- ¿Cuál es el límite de requests por minuto/por tenant?
- ¿Se usa rate limiting por IP, por usuario o por tenant?
- ¿Qué respuesta se devuelve cuando se excede el límite?

### 2. Sobre circuit breakers
- ¿Qué dependencias externas necesitan circuit breaker?
- ¿Cuántos fallos antes de abrir el circuito?
- ¿Cuánto tiempo hasta half-open?
- ¿Qué fallback se devuelve cuando el circuito está abierto?

### 3. Sobre retry
- ¿Cuántos retries máximo?
- ¿Qué códigos de estado generan retry?
- ¿Se usa exponential backoff con jitter?

### 4. Sobre timeouts
- ¿Cuál es el timeout por defecto para llamadas externas?
- ¿Se puede configurar por endpoint?
- ¿Qué se devuelve cuando se excede el timeout?

### 5. Sobre bulkheads
- ¿Se aísla por tenant o por servicio?
- ¿Cuál es la concurrencia máxima por tenant?
- ¿Qué se devuelve cuando el bulkhead está lleno?

## Salidas esperadas de esta skill

### A. Rate limiting configurado
- Middleware de rate limiting con cuotas por tenant/plan.
- Headers de rate limit en respuestas 429.

### B. Circuit breakers implementados
- Circuit breaker por dependencia externa.
- Fallbacks para cada circuit breaker.

### C. Retry con backoff
- Política de retry con exponential backoff + jitter.
- Configuración de retries por endpoint.

### D. Timeouts configurables
- Timeout por defecto para todas las llamadas externas.
- Timeout configurables por endpoint.

### E. Bulkheads por tenant
- Bulkhead factory con concurrencia máxima por tenant.

### F. Consumidores de esta skill
- `backend-api` consume los middlewares de rate limiting, circuit breaker y bulkhead;
- `react-services` / `angular-services` implementa retry del lado del cliente cuando recibe 429;
- `error-handling` define la estructura de errores 429 y 503;
- `load-testing` valida que los rate limits funcionan bajo carga.

## Criterios de calidad

- Rate limiting está configurado por tenant.
- Circuit breakers están configurados para dependencias externas.
- Retry usa exponential backoff con jitter.
- Timeouts están configurados para todas las llamadas externas.
- Bulkheads aíslan recursos por tenant.
- Fallbacks existen para cada circuit breaker.
- Rate limit headers están en respuestas 429.
- Backpressure protege contra sobrecarga.
- Las cuotas de API están definidas por plan.

## Comportamiento esperado del agente

Cuando el usuario implemente retry sin backoff, el agente debe proponer exponential backoff con jitter y explicar por qué retry instantáneo es peligroso.  
Cuando el usuario no configure timeout para llamadas externas, el agente debe proponer un timeout por defecto (30 segundos) y uno configurable por endpoint.  
Cuando el usuario no tenga rate limiting, el agente debe advertir que un solo tenant puede saturar la API y proponer rate limiting por tenant.  
Cuando el usuario no tenga circuit breaker, el agente debe explicar que una dependencia lenta puede arrastrar toda la aplicación.

## Checklist final de la skill

- ¿Rate limiting está configurado por tenant/plan?
- ¿Circuit breakers están configurados para dependencias externas?
- ¿Retry usa exponential backoff con jitter?
- ¿Timeouts están configurados para llamadas externas?
- ¿Bulkheads aíslan recursos por tenant?
- ¿Fallbacks existen para cada circuit breaker?
- ¿Rate limit headers están en respuestas 429?
- ¿Backpressure protege contra sobrecarga?
- ¿Las cuotas de API están documentadas por plan?
- ¿Se probó que el rate limiting funciona bajo carga?
