---
name: api-gateway
description: 'API Gateway patterns for routing, authentication, rate limiting, and cross-cutting concerns. Uses FastAPI middleware + NGINX as reverse proxy. Trigger: When setting up an API Gateway, configuring request routing, or implementing cross-cutting middleware at the gateway level.'
when_to_use:
  - Setting up an API Gateway for microservices or modular monolith
  - Configuring request routing and path-based forwarding
  - Implementing authentication and authorization at the gateway level
  - Adding rate limiting, circuit breaking, and retry policies at the gateway
  - Managing API versioning and path prefixes at the gateway
  - Implementing header propagation and request/response transformation
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: recommended
  depends_on:
  - backend-api
  - authentication
  - authorization
  consumed_by:
  - api-resilience
  - real-time
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

## 1. Propósito

Definir los patrones, responsabilidades y decisiones de diseño para implementar un API Gateway como punto de entrada único al ecosistema de servicios, garantizando autenticación centralizada, enrutamiento consistente, observabilidad y políticas de resiliencia. Stack recomendado: **NGINX como reverse proxy + FastAPI middleware** para auth/transformación.

## 2. Objetivo

Responder estas 5 preguntas antes de producir artefactos:

1. **¿Qué rutas y servicios debe exponer el Gateway hacia el exterior?** — Definir el catálogo de upstream/downstream routes.
2. **¿Qué preocupaciones transversales (cross-cutting) se centralizan en el Gateway?** — Auth, rate limiting, CORS, logging, retries.
3. **¿Qué mecanismo de autenticación se valida en el Gateway y qué identidad se propaga a los servicios internos?** — JWT, API keys, OAuth2 introspection, header de identidad interna.
4. **¿Cómo se versionan las APIs en el nivel del Gateway?** — Path-based (`/v1/`, `/v2/`), header-based, o combinado.

## 3. Relación con otras skills

| Skill | Relación |
|-------|----------|
| `authentication` | Provee los mecanismos de JWT/OAuth2 que el Gateway valida |
| `authorization` | Define los roles/permisos que el Gateway puede verificar antes de enrutar |
| `backend-api` | Los downstream services que el Gateway enruta |
| `api-resilience` | Circuit breakers, retries y rate limiting que el Gateway aplica |
| `api-versioning` | Estrategia de versionado que el Gateway expone hacia los consumidores |
| `observabilidad` | Correlation IDs, distributed tracing, structured logging desde el Gateway |
| `security` | CORS, input validation, headers de seguridad que el Gateway aplica |
| `error-handling` | Mapeo de errores entre Gateway y downstream services |
| `real-time` | WebSocket proxying y connection upgrades a través del Gateway |

## 4. Qué debe hacer el agente

1. **Identificar servicios downstream** y mapear rutas públicas a servicios internos.
2. **Definir el esquema de autenticación** que el Gateway validará (JWT, API key, OAuth2).
3. **Diseñar la transformación de identidad** — qué headers se propagan a los servicios internos.
4. **Configurar rutas de enrutamiento** con path-based routing.
5. **Establecer políticas de rate limiting** por ruta, por tenant y por consumidor.
6. **Definir el orden de middleware** (crítico para consistencia).
7. **Configurar CORS y headers de seguridad** como preocupación centralizada.
8. **Definir rutas excluidas** de autenticación (health checks, Swagger, metrics).
9. **Configurar circuit breakers y retry policies** para proteger servicios downstream.
10. **Definir logging y correlation IDs** para trazabilidad distribuida.

## 5. Principios

1. **Single Entry Point**: Todo el tráfico externo pasa por el Gateway; ningún servicio interno se expone directamente.
2. **Auth at Gateway, Identity Downstream**: El Gateway valida credenciales y propaga identidad interna via headers; los servicios internos confían en el header de identidad.
3. **Separation of Concerns**: Preocupaciones transversales (auth, rate limiting, CORS, logging) se centralizan en el Gateway; lógica de negocio permanece en los servicios.
4. **Fail-Fast**: Validar autenticidad y autorización antes de resolver la ruta downstream; rechazar requests inválidos temprano.
5. **Observabilidad por Defecto**: Todo request que pasa por el Gateway genera correlation ID, structured log y trace span.
6. **Zero Trust Internally**: Los servicios internos validan el header de identidad propagated, pero no reimplementan la validación del token original.

## 6. Gateway Routing Patterns

| Pattern | Descripción | Cuándo usar |
|---------|-------------|-------------|
| **Path-based** | Rutas basadas en path prefix: `/users/api/v1/*` → UserService | Caso general, microservicios por dominio |
| **Host-based** | Rutas basadas en host header: `users.api.example.com` → UserService | Multi-tenant o servicios con dominios dedicados |
| **Header-based** | Rutas basadas en custom headers: `X-Service: users` → UserService | Canary deployments, A/B testing, feature flags |

**Reglas de enrutamiento:**

1. Toda ruta upstream sigue el patrón `/{Service}/api/v{Version}/{everything}`.
2. El path downstream se reescribe eliminando el prefix del servicio: `/api/v{Version}/{everything}`.
3. Los paths de health, metrics y Swagger se excluyen del auth middleware.
4. Los WebSocket upgrades se detectan y se proxy con connection upgrade.

## 7. Authentication and Authorization at Gateway

```
Client → [Auth Token] → Gateway → Token Validation → Extract Identity →
  Gateway adds: X-Internal-User-Id, X-Internal-Roles, X-Correlation-Id →
    NGINX → Downstream Service → Reads identity from headers
```

| Mecanismo | Flujo en Gateway | Header propagado |
|-----------|------------------|-------------------|
| **JWT Validation** | Verificar signature, expiry, claims localmente | `X-User-Id`, `X-Roles` |
| **API Key** | Lookup en store/key-vault, validar vigencia y scope | `X-Api-Key-Id`, `X-Api-Key-Scope` |
| **OAuth2 Introspection** | Token introspection al IdP (o JWT local con JWKS) | `X-User-Id`, `X-Roles`, `X-Tenant-Id` |
| **mTLS** | Validar client certificate contra CA | `X-Client-Cn`, `X-Client-Fingerprint` |

**Reglas:**

- La validación de token SIEMPRE ocurre antes del enrutamiento downstream.
- Los downstream services NO reimplementan la validación del token original; confían en el header de identidad.
- Las rutas excluidas (health, swagger, metrics) se listan explícitamente.
- El Gateway NO tiene acceso a la base de datos de usuarios; solo valida tokens y extrae claims.

## 8. Cross-cutting Concerns

| Concern | Configuración | Notas |
|---------|--------------|-------|
| **Rate Limiting** | Por route, por tenant, por API key | Sliding window o fixed window |
| **Circuit Breaking** | Por downstream service | Falling threshold, reset timeout |
| **Retries** | Por route, con jitter exponencial | Max 3 retries, idempotent methods only |
| **CORS** | Orígenes permitidos, methods, headers | Centralizado en el Gateway |
| **Logging** | Structured JSON, correlation ID | Nivel Gateway: audit log de request |
| **Correlation ID** | Generar si no existe `X-Correlation-Id` | Propagar a todos los downstream |
| **Request Timeout** | Default por route, override por servicio | Evitar cascading timeouts |
| **Response Caching** | Por route, con TTL configurable | Solo para GET idempotentes |
| **Request/Response Transform** | Header add/remove, body rewrite | Mínimo, solo para adaptación |

## 9. NGINX como API Gateway

### NGINX (como API Gateway)

- **Tipo**: Reverse proxy con capacidades de gateway
- **IDEAL para**: Alta performance, routing simple, configuración declarativa
- **Configuración**: `nginx.conf` con upstream blocks y location rules
- **Auth**: Validación con `auth_request` o JWT via Lua/NJS

### `nginx.conf` — Routing simple con auth_request:

```nginx
upstream user_service {
    server user-service:8080;
}

upstream order_service {
    server order-service:8081;
}

server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    add_header X-Correlation-Id $correlation_id always;

    set $correlation_id $http_x_correlation_id;
    if ($correlation_id = "") {
        set $correlation_id $request_id;
    }

    location /users/api/v1/ {
        auth_request /auth/validate;
        auth_request_set $user_id $upstream_http_x_user_id;
        auth_request_set $roles $upstream_http_x_roles;

        proxy_set_header X-User-Id $user_id;
        proxy_set_header X-Roles $roles;
        proxy_set_header X-Correlation-Id $correlation_id;
        proxy_set_header Host $host;

        rewrite ^/users(/api/v1/.*)$ $1 break;
        proxy_pass http://user_service;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /orders/api/v1/ {
        auth_request /auth/validate;
        auth_request_set $user_id $upstream_http_x_user_id;
        auth_request_set $roles $upstream_http_x_roles;

        proxy_set_header X-User-Id $user_id;
        proxy_set_header X-Roles $roles;
        proxy_set_header X-Correlation-Id $correlation_id;
        proxy_set_header Host $host;

        rewrite ^/orders(/api/v1/.*)$ $1 break;
        proxy_pass http://order_service;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /auth/validate {
        internal;
        proxy_pass http://auth-service:8082/validate;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI $request_uri;
    }

    location /health {
        auth_request off;
        proxy_pass http://user_service/health;
    }

    location /swagger {
        auth_request off;
        proxy_pass http://user_service/swagger;
    }
}
```

## 10. FastAPI Gateway Middleware

Para escenarios donde se usa FastAPI como BFF/light gateway:

```python
from fastapi import FastAPI, Request, HTTPException
from jose import jwt, JWTError
import os

app = FastAPI()

EXCLUDED_PATHS = ["/swagger", "/health", "/metrics"]
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

@app.middleware("http")
async def gateway_auth_middleware(request: Request, call_next):
    # Skip auth for excluded paths
    if any(request.url.path.startswith(p) for p in EXCLUDED_PATHS):
        return await call_next(request)

    # Extract and validate JWT
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": {"code": "AUTH_001", "message": "Unauthorized"}}
        )

    try:
        token = auth_header.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # Propagate identity to downstream
        request.headers.__dict__["_list"].extend([
            (b"x-user-id", payload["sub"].encode()),
            (b"x-roles", ",".join(payload.get("roles", [])).encode()),
            (b"x-tenant-id", payload.get("tenant_id", "").encode()),
        ])
    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": {"code": "AUTH_002", "message": "Invalid token"}}
        )

    return await call_next(request)
```

## 11. Preguntas guía

1. ¿Cuántos servicios downstream tendrá el Gateway y cuál es el plan de crecimiento?
2. ¿Qué mecanismo de autenticación usan los consumidores (JWT, API key, OAuth2)?
3. ¿Se requiere rate limiting diferenciado por plan de suscripción o tenant?
4. ¿Qué rutas deben excluirse de autenticación y por qué?
5. ¿Qué información de identidad se propaga a los servicios internos y en qué formato?
6. ¿Se necesita WebSocket proxying para funcionalidades real-time?
7. ¿Cuál es la estrategia de deployment del Gateway (container, cloud-managed)?
8. ¿Qué SLOs de latencia y disponibilidad se esperan para el Gateway?

## 12. Salidas esperadas

| Artefacto | Descripción |
|-----------|-------------|
| `gateway-routes.md` | Catálogo de rutas upstream/downstream con patterns, rewrite rules y excluded paths |
| `gateway-middleware-order.md` | Orden de middleware con justificación |
| `gateway-auth-flow.md` | Flujo de autenticación y headers propagados |
| `nginx.conf` | Configuración del NGINX reverse proxy |
| `gateway-cross-cutting.md` | Políticas de rate limiting, circuit breaking, retries y CORS |

## 13. Criterios de calidad

- [ ] Toda ruta downstream está mapeada a una ruta upstream con versionado
- [ ] El orden de middleware está documentado y justificado
- [ ] Las rutas excluidas de auth están explícitamente listadas
- [ ] Los headers de identidad propagated están definidos y documentados
- [ ] Rate limiting está configurado por ruta y por tenant
- [ ] Circuit breaking está definido para cada downstream service
- [ ] Correlation IDs se generan y propagan en toda la cadena
- [ ] CORS está centralizado en el Gateway
- [ ] La configuración es declarativa y versionable en Git

## 14. Comportamiento esperado del agente

1. **Siempre** validar que auth middleware se ejecuta ANTES del routing downstream.
2. **Siempre** definir el orden de middleware.
3. **Siempre** documentar los headers de identidad que se propagan.
4. **Siempre** listar explícitamente las rutas excluidas de autenticación.
5. **Nunca** implementar lógica de negocio en el Gateway.
6. **Nunca** permitir que un downstream service valide el token original si el Gateway ya lo hizo.
7. **Siempre** generar correlation IDs si no existen en el request.

## 15. Checklist final

- [ ] Rutas upstream/downstream mapeadas con path rewrite rules
- [ ] Autenticación validada ANTES del routing downstream
- [ ] Headers de identidad propagados documentados (`X-User-Id`, `X-Roles`, `X-Tenant-Id`, `X-Correlation-Id`)
- [ ] Rutas excluidas de autenticación explícitamente listadas (`/health`, `/swagger`, `/metrics`)
- [ ] Rate limiting configurado por ruta y por tenant/consumidor
- [ ] Circuit breaking configurado para cada downstream service
- [ ] Retry policies con jitter exponencial definidos (solo métodos idempotentes)
- [ ] CORS centralizado en el Gateway
- [ ] Correlation IDs generados y propagados end-to-end
- [ ] Audit logging configurado en el Gateway
- [ ] Error logging en ambos niveles (Gateway + servicios internos)
- [ ] Configuración declarativa y versionada en Git
- [ ] WebSocket proxying configurado si hay requisitos real-time
- [ ] Timeout por ruta configurado para evitar cascading timeouts
