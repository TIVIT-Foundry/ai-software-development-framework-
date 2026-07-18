---
name: shared-libs
description: 'Shared library patterns: common contracts, exceptions, response wrappers,
  middleware, and utilities. Uses Python/FastAPI. Trigger: When configuring shared libraries, using common
  patterns, or setting up middleware.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  enforcement: mandatory
  depends_on: []
  consumed_by:
  - backend-api
  - data-access
  - api-integration
  - app-bootstrap
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use typed exceptions for business errors | ALWAYS | Automatic HTTP mapping |
| Use UTC for all logging timestamps | ALWAYS | Distributed tracing consistency |
| Use typed response wrappers, never raw objects | ALWAYS | Consistent API contract |
| Middleware order is critical | ALWAYS | Wrong order causes runtime bugs |

## Core Libraries Overview
| Library | Purpose | Python Package Example |
|---------|---------|---------------------|
| `common` | Base contracts: `ApiResponse`, exceptions, error codes | `shared.common` |
| `common-api` | API contracts: identity context, pagination, Swagger helpers | `shared.common_api` |
| `common-data` | DB infrastructure: connection, resilience, logging stores | `shared.common_data` |
| `common-logging` | Structured logging + correlation ID middleware | `shared.common_logging` |
| `common-inspection` | Exception middleware + HTTP audit middleware | `shared.common_inspection` |
| `common-validation` | Validation registration + input validation | `shared.common_validation` |
| `auth` | Auth HTTP client + identity propagation | `shared.auth` |
| `storage` | Cloud storage (S3, Azure Blob) presigned URLs | `shared.storage` |

## ApiResponse — Standard Contract
```python
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str | None = None
    errors: list[dict] | None = None

    @classmethod
    def ok(cls, data: T, message: str = "Success") -> "ApiResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def ok_list(cls, items: list, pagination: dict = None) -> "ApiResponse":
        return cls(success=True, data={"items": items}, metadata=pagination)

    @classmethod
    def fail(cls, message: str, errors: list[dict] = None) -> "ApiResponse":
        return cls(success=False, message=message, errors=errors)
```

## Exception Hierarchy
| Exception | HTTP | Usage |
|-----------|------|-------|
| `ValidationException` | 400 | Input and business validation failures |
| `ForbiddenException` | 403 | Authorization failures |
| `NotFoundException` | 404 | Resource not found |
| `ConflictException` | 409 | Duplicate or state conflict |
| `BusinessRuleException` | 422 | Business rule violation |
| `BadGatewayException` | 502 | Downstream service failure |

## Error Code → Exception Mapping (SP errors)
| Error pattern | Exception type |
|--------------|----------------|
| `VAL_*` | `ValidationException` |
| `AUTH_*` | `ForbiddenException` |
| `SYS_*` | `InternalException` |
| `*_001` | `NotFoundException` |
| `*_002` | `ConflictException` |
| `*_003+` | `BusinessRuleException` |

## Common Error Codes
- **VAL_**: VAL_001 (required) through VAL_008 (length exceeded)
- **AUTH_**: AUTH_001 (unauthorized), AUTH_002 (token expired), AUTH_003 (insufficient permissions)
- **SYS_**: SYS_001 (internal error)

## Cross-cutting Models
- `PaginationResult`: Page, PageSize, TotalRecords, TotalPages, HasNext, HasPrevious
- `ApiError`: Code, Field, Message
- `IdentityContext`: UserId, Email, Roles, Claims

## Identity Context Pattern
```python
from fastapi import Request
from dataclasses import dataclass

@dataclass
class IdentityContext:
    user_id: str
    email: str | None = None
    roles: list[str] = None
    claims: dict = None
    
    def __post_init__(self):
        self.roles = self.roles or []
        self.claims = self.claims or {}

async def get_identity_context(request: Request) -> IdentityContext:
    """Extract identity from headers (propagated by gateway)."""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Identity not found")
    return IdentityContext(
        user_id=user_id,
        email=request.headers.get("X-User-Email"),
        roles=request.headers.get("X-Roles", "").split(",") if request.headers.get("X-Roles") else [],
    )
```

## Rate Limiting Levels
| Level | Effective limit |
|-------|-----------------|
| Disabled | No limiter |
| Low | 50/min per IP |
| Standard | 100/min per IP |
| High | 200/min per IP |
| Critical | 30/min per IP |

## Store Selection by API Type
| API Type | Stores to enable |
|----------|-----------------|
| Internal API | LogHttp |
| Gateway | LogHttp + AuditHttp + AuditEndpoint |
| Worker | LogHttp + LogJob |

## Patrones avanzados de librerías compartidas

### Estrategia Monorepo vs paquete PyPI

| Criterio | Monorepo (workspace) | Paquete PyPI privado |
|----------|---------------------|---------------------|
| Velocidad de iteración | Alta — cambios reflejados inmediatamente | Baja — requiere publish + update |
| Versionado | Unificado con la app | Independiente (semver) |
| Governance | Centralizado | Descentralizado, requiere proceso de release |
| Complejidad CI/CD | Menor (un pipeline) | Mayor (pipeline por paquete) |
| Reuso entre organizaciones | No nativo | Sí — consumo via registry |

**Cuándo usar Monorepo:**
- Equipo pequeño a mediano (< 10 servicios).
- Todas las apps comparten el mismo ciclo de release.
- Se necesita consistencia estricta entre contratos y consumidores.

**Cuándo usar paquetes PyPI privados:**
- Múltiples equipos con ciclos de release independientes.
- Las librerías se consumen desde fuera de la organización.
- Se requiere versionado independiente y retrocompatibilidad estricta.

**Recomendación híbrida:** Usar monorepo para desarrollo, y publicar solo los paquetes estables a un registry interno (Artifactory, GitHub Packages) para que otros equipos los consuman sin depender del código fuente.

### Versionado de paquetes compartidos (semver)

El versionado de librerías compartidas sigue **Semantic Versioning (semver)** estricto.

**Reglas de semver para librerías compartidas:**
- **PATCH (x.y.Z):** Bug fixes, cambios internos sin afectar la API pública.
- **MINOR (x.Y.z):** Nuevos exports, nuevos campos opcionales, nuevos endpoints o tipos. Retrocompatible.
- **MAJOR (X.y.z):** Breaking changes: renombrar un export, cambiar tipo de retorno, eliminar un campo obligatorio.

### Tree-shaking para paquetes compartidos (TypeScript)

El tree-shaking permite eliminar código no utilizado en el bundle final de producción. Para que funcione correctamente con librerías compartidas:

**Reglas para maximizar el tree-shaking:**
- Usar `export` nombrados en lugar de `export default`. Los exports nombrados permiten al bundler rastrear qué símbolos se usan.
- Evitar efectos secundarios (side effects) en el nivel de módulo. Si un módulo ejecuta lógica al importarse, el bundler no puede eliminarlo.
- Declarar `"sideEffects": false` en `package.json` (o listar los archivos con efectos secundarios).
- Mantener los módulos pequeños y cohesionados: un concepto por archivo.

```json
// package.json — Declaración de sideEffects
{
  "name": "@shared/common",
  "sideEffects": false,
  "exports": {
    "./api-response": "./src/api-response/index.ts",
    "./exceptions": "./src/exceptions/index.ts",
    "./pagination": "./src/pagination/index.ts"
  }
}
```

```typescript
// BIEN — export nombrado, sin side effects
export class ValidationException extends AppException { ... }
export class NotFoundException extends AppException { ... }

// MAL — export default con side effects
export default { /* obliga a incluir todo el objeto */ };
```

### Generación de archivos de declaración TypeScript (.d.ts)

Los archivos `.d.ts` garantizan que los consumidores TypeScript de las librerías compartidas reciban autocompletado y verificación de tipos sin necesidad de acceder al código fuente.

**Configuración en `tsconfig.json` de la librería:**
```json
{
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "declarationDir": "./dist/types",
    "emitDeclarationOnly": false,
    "outDir": "./dist",
    "sourceMap": true
  }
}
```

**En `package.json` de la librería:**
```json
{
  "types": "./dist/types/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/types/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    },
    "./exceptions": {
      "types": "./dist/types/exceptions/index.d.ts",
      "import": "./dist/exceptions/index.mjs",
      "require": "./dist/exceptions/index.cjs"
    }
  }
}
```

**Reglas para .d.ts:**
- Usar `declarationMap: true` para que los consumidores puedan hacer "Go to Definition" al código fuente.
- Exportar tipos con `export type` cuando sea posible para favorecer tree-shaking.
- Los tipos de API response y request se declaran en `types.d.ts`, separados de la implementación.
- Los tipos compartidos entre frontend y backend se ubican en `@shared/common` y se referencian via `exports` condicionales según el entorno.
- Validar con `tsc --noEmit` que los tipos compilan correctamente antes de publicar.
