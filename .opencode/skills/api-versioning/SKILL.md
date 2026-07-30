---
name: api-versioning
description: "API versioning strategies and deprecation policies. Covers URI versioning (v1/v2), header versioning, media-type versioning, backward compatibility rules, OpenAPI spec versioning, sunset headers, and consumer migration. Uses Python/FastAPI. Trigger: When designing, implementing, or maintaining versioned REST APIs."
version: 1.1
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - backend-api
  - openapi-docs
  consumed_by:
  - api-first-frontend
  - react-services
  - angular-services
  - api-first-testing
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# api-versioning

## Propósito

Esta skill define cómo versionar APIs REST de forma predecible, trazable y amigable para los consumidores.  
Su función es asegurar que las APIs evolucionen sin romper clientes existentes, con reglas claras de cuándo crear una nueva versión, cuándo deprecar y cómo migrar consumidores.

Esta skill complementa `backend-api` (estructura de endpoints) y `openapi-docs` (documentación OpenAPI). Mientras esos definen QUÉ endpoints existen, esta skill define CÓMO evolucionan sin romper contratos.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cuándo se debe crear una nueva versión de API vs extender la existente?
2. ¿Qué estrategia de versionado usar (URI, header, media-type)?
3. ¿Cómo se depreca una versión sin romper consumidores?
4. ¿Cómo se documentan las versiones en OpenAPI spec?
5. ¿Cómo se migra consumidores de una versión antigua a una nueva?

## Relación con otras skills

- `backend-api` define la estructura de endpoints que esta skill versiona.
- `openapi-docs` documenta las versiones en OpenAPI spec.
- `api-first-frontend` consume la versión correcta de la API desde el frontend.
- `react-services` / `angular-services` implementa los services con la versión de API seleccionada.
- `error-handling` define cómo se reportan errores de versión incompatible.

## Qué debe hacer el agente cuando esta skill está activa

1. Definir la estrategia de versionado para la API (URI por defecto).
2. Establecer reglas claras de backward compatibility (qué cambios son breaking vs non-breaking).
3. Definir el formato de URL versionada (`/api/v{N}/{resource}`).
4. Crear mecanismos de deprecation con Sunset headers y documentación.
5. Definir la política de soporte de versiones (cuántas versiones activas, duración de soporte).
6. Asegurar que cada versión tiene su OpenAPI spec correspondiente.
7. Definir cómo los consumidores descubren la versión disponible.
8. Documentar el proceso de migración para consumidores.

## Entradas esperadas

Esta skill asume que ya existe:
- estructura de endpoints definida (`backend-api`);
- documentación OpenAPI (`openapi-docs`);
- manejo de errores definido (`error-handling`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- selección de estrategia de versionado;
- reglas de backward compatibility;
- naming y routing de versiones;
- deprecation policy con timelines;
- OpenAPI spec versionado;
- headers de respuesta (Sunset, Deprecation, Link);
- guía de migración para consumidores.

La fase no incluye todavía:
- implementación específica de endpoints (cubierta por `backend-api`);
- testing de versiones (cubierta por `api-first-testing`);
- deployment de múltiples versiones (cubierta por `framework-platform`).

## Principios que siempre debe respetar

- Una versión de API NUNCA debe romper clientes existentes sin un periodo de deprecation.
- Los cambios non-breaking (nuevos campos opcionales, nuevos endpoints) NO requieren nueva versión.
- Los cambios breaking (eliminar campo, cambiar tipo, renombrar endpoint) SÍ requieren nueva versión.
- Las versiones deprecadas DEBEN incluir header Sunset con fecha de remoción.
- Las versiones deprecadas DEBEN seguir funcionando durante el periodo de gracia.
- OpenAPI spec DEBE existir para cada versión activa.
- Los consumidores DEBEN poder descubrir versiones disponibles sin documentación externa.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la estrategia de versionado (URI, header, media-type);
- las reglas de backward compatibility;
- la política de deprecation y timelines;
- el formato de URL y headers de versión.

Esta skill delega:
- la implementación de endpoints a `backend-api`;
- la documentación OpenAPI a `openapi-docs`;
- el manejo de errores de versión incompatible a `error-handling`;
- el deployment de múltiples versiones a `framework-platform`.

## Qué debe definir el diseño

### 1. Estrategia de versionado

| Estrategia | URL/Header | Pros | Contras | Uso recomendado |
|------------|-----------|------|---------|-----------------|
| URI versioning | `/api/v1/resource` | Explícita, cacheable, simple | URLs más largas | **Por defecto** |
| Header versioning | `X-API-Version: 1` | URLs limpias, versionado invisible | No cacheable, menos visible | APIs internas |
| Media-type | `Accept: application/vnd.api.v1+json` | RESTful, flexible | Complejo, poco intuitivo | APIs públicas avanzadas |

**Decisión por defecto**: URI versioning (`/api/v{N}/{resource}`) a menos que el contexto requiera otra estrategia.

### 2. Reglas de backward compatibility

**Cambios NON-breaking (no requieren nueva versión)**:
- Agregar campo opcional en response
- Agregar nuevo endpoint
- Agregar nuevo valor en enum (si el cliente lo ignora)
- Agregar query parameter opcional
- Relajar constraint (requerido → opcional)

**Cambios BREAKING (requieren nueva versión)**:
- Eliminar campo de response
- Cambiar tipo de campo
- Renombrar endpoint o campo
- Agregar constraint (opcional → requerido)
- Eliminar endpoint
- Cambiar semántica de campo existente
- Eliminar valor de enum

### 3. Formato de URL versionada

```
/api/v{N}/{resource}

Ejemplos:
/api/v1/users
/api/v1/users/{id}
/api/v2/users          ← versión 2 con cambios en response
/api/v2/users/{id}
```

Reglas:
- `v{N}` siempre en minúscula.
- N es un entero secuencial (v1, v2, v3).
- No usar versiones menores (v1.1, v1.2); si hay cambio breaking, es v2.
- Versiones se activan a nivel de router, no a nivel de método.

### 4. Headers de deprecation

```http
HTTP/1.1 200 OK
Sunset: Sat, 01 Mar 2026 00:00:00 GMT
Deprecation: true
Link: </api/v2/users>; rel="successor-version"
Content-Type: application/json
```

Reglas:
- `Sunset`: fecha exacta de remoción (mínimo 6 meses desde deprecation).
- `Deprecation: true`: marca la versión como deprecada.
- `Link`: URL de la versión sucesora para facilitar migración.

### 5. OpenAPI spec versionado

```
/swagger/v1/swagger.json    ← OpenAPI spec para v1
/swagger/v2/swagger.json    ← OpenAPI spec para v2
/swagger/latest/swagger.json ← Redirect a la versión más reciente
```

Reglas:
- Cada versión activa tiene su propio OpenAPI spec.
- La spec deprecada incluye `deprecated: true` en campos y endpoints.
- La spec más reciente está disponible en `/swagger/latest/`.

### 6. Política de soporte de versiones

| Regla | Valor |
|-------|-------|
| Versiones activas simultáneas | Máximo 2 (actual + anterior) |
| Periodo de deprecation | Mínimo 6 meses |
| Notificación de deprecation | Header Sunset + email a consumidores registrados |
| Versión deprecada | Sigue funcionando, no recibe nuevas features |
| Versión removida | Retorna HTTP 410 Gone |
| Nueva versión | Se publica junto a la anterior (ambas funcionan) |

### 7. Versiones con FastAPI

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# v1 router
v1_router = APIRouter(prefix="/api/v1")

@v1_router.get("/users")
async def list_users_v1():
    return {"version": "v1", "users": [...]}

# v2 router
v2_router = APIRouter(prefix="/api/v2")

@v2_router.get("/users")
async def list_users_v2():
    return {"version": "v2", "users": [...], "metadata": {...}}

app.include_router(v1_router)
app.include_router(v2_router)
```

### 8. Middleware de deprecation headers (FastAPI)

```python
from fastapi import Request
from datetime import datetime

DEPRECATED_VERSIONS = {
    "v1": datetime(2026, 3, 1),  # Sunset date
}

@app.middleware("http")
async def deprecation_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Check if the request path contains a deprecated version
    for version, sunset_date in DEPRECATED_VERSIONS.items():
        if f"/api/{version}/" in request.url.path:
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = sunset_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
            response.headers["Link"] = f'</api/v2{request.url.path.replace(f"/api/{version}", "")}>; rel="successor-version"'
            break
    
    return response
```

### 9. Guía de migración template

```markdown
# Migration Guide: v1 → v2

## Breaking Changes
1. `User.email` renamed to `User.emailAddress`
2. `User.active` removed, use `User.status` instead
3. `POST /users` now requires `lastName` field

## Field Mapping
| v1 Field | v2 Field | Notes |
|----------|----------|-------|
| email | emailAddress | Renamed |
| active | status | Replaced by enum: Active/Inactive |
| - | lastName | Now required |

## Timeline
- **Now**: v2 available, v1 deprecated
- **March 2026**: v1 returns 410 Gone
- **Support**: v1 receives critical fixes only
```

### 10. Consumidores de esta skill
- `api-first-frontend` usa la versión correcta para generar tipos TypeScript;
- `react-services` / `angular-services` implementa services con la versión de API seleccionada;
- `api-first-testing` genera tests para cada versión activa;
- `openapi-docs` documenta cada versión en OpenAPI spec;
- `error-handling` define respuestas de error para versiones inexistentes o deprecadas.

## Criterios de calidad

- La estrategia de versionado está definida y documentada.
- Las reglas de backward compatibility están claras (breaking vs non-breaking).
- Las versiones deprecadas incluyen headers Sunset, Deprecation y Link.
- Cada versión activa tiene su propio OpenAPI spec.
- La guía de migración existe para cada versión nueva.
- Se soportan máximo 2 versiones activas simultáneamente.
- El periodo de deprecation es de al menos 6 meses.
- Los consumers pueden descubrir versiones disponibles sin documentación externa.

## Comportamiento esperado del agente

Cuando el usuario quiera eliminar un campo de una response, el agente debe proponer una nueva versión v2 con el campo eliminado y mantener v1 deprecada con el campo existente.  
Cuando el usuario quiera crear una versión v2 por un cambio non-breaking, el agente debe explicar que no es necesaria una nueva versión y sugerir agregar el campo como opcional.  
Cuando el usuario tenga v1 y v2 compartiendo lógica, el agente debe proponer un patrón de shared service con mappers por versión.  
Cuando el usuario depreque una versión sin fecha límite, el agente debe exigir una fecha Sunset de al menos 6 meses.

## Checklist final de la skill

- ¿Se definió la estrategia de versionado (URI por defecto)?
- ¿Se documentaron las reglas de backward compatibility?
- ¿Se definió el formato de URL versionada?
- ¿Las versiones deprecadas incluyen headers Sunset y Deprecation?
- ¿Cada versión activa tiene su OpenAPI spec?
- ¿Se definió la política de soporte (máx 2 versiones, 6 meses deprecation)?
- ¿Existe guía de migración para consumidores?
- ¿Se configuró el middleware de deprecation headers?
- ¿Los routers versionados están mapeados correctamente?
- ¿Se probó que v1 sigue funcionando después de publicar v2?
