---
name: openapi-docs
description: 'OpenAPI/Swagger documentation generation and maintenance. Uses Python FastAPI built-in OpenAPI. Trigger: When creating API docs, updating Swagger, generating OpenAPI specs, or maintaining API documentation.'
when_to_use:
  - Creating API documentation for a new module
  - Updating OpenAPI specs after endpoint changes
  - Generating API docs from code annotations
  - Publishing interactive API documentation
  - Validating API spec completeness before consumer handoff
version: 1.1
metadata:
  phase:
  - construction
  - operations
  layer:
  - backend
  enforcement: mandatory
  depends_on:
  - backend-api
  consumed_by:
  - api-catalog
  - api-first-spec
  - api-first-testing
  - api-versioning
  - typescript
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: documentation
  mcp_usage: none
---

# openapi-docs

## Propósito

Esta skill define cómo generar, mantener y publicar documentación de APIs usando el estándar OpenAPI (3.1). Su función es asegurar que toda API exponga una especificación precisa, completa, validable y útil para consumidores internos y externos.

Esta skill complementa `backend-api` (estructura de endpoints) y `api-first-spec` (documento de especificación con 9 secciones). Mientras `api-first-spec` define QUÉ debe la API, esta skill define CÓMO se documenta y publica esa especificación como OpenAPI.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo generar y mantener documentación OpenAPI para mi API?
2. ¿Se usa enfoque Code-First o Design-First según el contexto?
3. ¿Cómo documentar esquemas de error, paginación y file upload consistentemente?
4. ¿Cómo validar completitud y consistencia de la especificación?
5. ¿Cómo publicar documentación interactiva (Swagger UI, ReDoc, Scalar)?

## Relación con otras skills

- `api-first-spec` es el insumo principal: el documento de especificación (9 secciones) se transforma en OpenAPI spec.
- `backend-api` define los endpoints que esta skill documenta.
- `api-catalog` consume el OpenAPI spec para generar el inventario de APIs (endpoint → serviceID → pantalla).
- `typescript` consume el OpenAPI spec para generar tipos TypeScript automáticamente.
- `api-first-frontend` usa el spec para generar hooks y componentes desde la definición de la API.
- `api-first-testing` usa el spec para generar tests E2E y contract tests.
- `api-versioning` versiona la documentación OpenAPI por versión de API.
- `api-integration` define los patrones de respuesta (`ApiResponse`) que esta skill debe documentar.
- `error-handling` define los códigos de error que esta skill debe reflejar en los schemas de error.

## Qué debe hacer el agente cuando esta skill está activa

1. Leer el documento de especificación `api-first-spec` para obtener endpoints, DTOs, reglas de negocio y códigos de error.
2. Seleccionar enfoque de documentación (Code-First o Design-First) según el stack y fase del proyecto.
3. Definir la estructura del archivo OpenAPI spec (paths, schemas, components, security).
4. Documentar todos los endpoints con operationId, summary, description, tags, parameters, requestBody y responses.
5. Incluir esquemas de error consistentes usando `ApiResponse` como wrapper estándar.
6. Documentar respuestas paginadas con los parámetros y metadata de paginación.
7. Documentar endpoints de file upload con `multipart/form-data` y restricciones de tipo/tamaño.
8. Configurar la UI de documentación interactiva (Swagger UI, ReDoc, Scalar o Redocly).
9. Ejecutar validación con Spectral u otro linter para verificar completitud y buenas prácticas.
10. Asegurar que el spec está accesible en `/swagger/v{N}/swagger.json` (o equivalente) para cada versión activa.
11. Generar tipos TypeScript desde el spec usando herramientas como `openapi-typescript` o `orval`.
12. Incluir ejemplos (`examples`) en request bodies y responses para facilitar la adopción de consumidores.

## Entradas esperadas

Esta skill asume que ya existe:
- documento de especificación API (`api-first-spec`);
- estructura de endpoints definida (`backend-api`);
- manejo de errores definido (`error-handling`);
- patrones de respuesta definidos (`api-integration`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- generación y mantenimiento de OpenAPI spec (3.1);
- configuración de Code-First o Design-First según stack;
- documentación de esquemas de error, paginación y file upload;
- configuración de UI interactiva (Swagger UI, ReDoc, Scalar, Redocly);
- validación de specs con Spectral;
- integración con generación de tipos TypeScript;
- versionado de documentación OpenAPI;
- ejemplos y descripciones para adopción de consumidores.

La fase no incluye todavía:
- diseño de endpoints (cubierta por `backend-api`);
- documento de especificación de 9 secciones (cubierta por `api-first-spec`);
- tests de API (cubierta por `api-first-testing`);
- deployment de múltiples versiones (cubierta por `framework-platform`).

## Principios que siempre debe respetar

- El OpenAPI spec es la **fuente de verdad** para contratos de API, no el código.
- Todos los endpoints DEBEN tener `operationId` único, `summary`, `description` y `tags`.
- Toda respuesta DEBE documentar el esquema de error estándar (`ApiResponse` con `errors[]`).
- Toda respuesta paginada DEBE documentar los campos `pagination` (page, pageSize, totalRecords, totalPages).
- Los esquemas DEBEN usar `$ref` para reutilizar componentes, nunca duplicar definiciones.
- Los endpoints que requieren autenticación DEBEN declarar `security` explícitamente.
- El spec DEBE pasar validación Spectral sin errores de nivel `error`.
- Los ejemplos (`examples`) DEBEN incluirse en requests y responses para facilitar adopción.
- Las versiones deprecadas DEBEN incluir `deprecated: true` y descripción con fecha de remoción.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- el enfoque de documentación (Code-First vs Design-First);
- la estructura y organización del OpenAPI spec;
- los esquemas de error, paginación y file upload en el spec;
- la herramienta de UI interactiva (Swagger UI, ReDoc, Scalar, Redocly);
- las reglas de validación Spectral y su configuración;
- la estrategia de ejemplos y descripciones.

Esta skill delega:
- el diseño de endpoints a `backend-api`;
- el documento de especificación de 9 secciones a `api-first-spec`;
- los tests de API a `api-first-testing`;
- el versionado de APIs a `api-versioning`;
- el manejo de errores a `error-handling`;
- el deployment a `framework-platform`.

## Qué debe definir el diseño

### 1. Estructura del OpenAPI Spec

```yaml
openapi: 3.1.0
info:
  title: "{ModuleName} API"
  description: |
    Descripción detallada del módulo.
    Incluye propósito, audiencia y enlace al documento api-first-spec.
  version: "1.0.0"
  contact:
    name: "{TeamName}"
    email: "{team@company.com}"
  license:
    name: "Proprietary"
    url: "https://company.com/license"

servers:
  - url: "https://api.{tenant}.company.com/{apiVersion}"
    description: "Production"
    variables:
      tenant:
        default: "default"
        description: "Tenant identifier"
      apiVersion:
        default: "v1"
        description: "API version"
  - url: "https://localhost:8000/{apiVersion}"
    description: "Local development"
    variables:
      apiVersion:
        default: "v1"

tags:
  - name: "{Entity}"
    description: "Operations for {Entity}"
  - name: "{Entity} Reports"
    description: "Export and reporting for {Entity}"

paths:
  /api/v1/{entityPlural}:
    # ... (ver secciones siguientes)

components:
  schemas:
    # ... (ver secciones siguientes)
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - BearerAuth: []
```

Reglas de estructura:
- `info.title` sigue el formato `{ModuleName} API`.
- `info.version` sigue semver (mayor.menor.patch).
- `servers` usa variables para tenant y versión.
- `tags` agrupa endpoints por entidad funcional, no por método HTTP.
- `components.schemas` centraliza DTOs, nunca duplica definiciones.
- `security` se declara a nivel global y se puede sobreescribir por endpoint.

### 2. Enfoque Code-First vs Design-First

#### Code-First: Se genera el spec desde el código

**Usar cuando**: la API ya existe o se está construyendo iterativamente. El código es la fuente de verdad inicial y el spec se genera automáticamente.

| Stack | Herramienta | Configuración clave |
|-------|-------------|---------------------|
| **Python (FastAPI)** | FastAPI built-in | `openapi_url`, `get_openapi()`, `Field(description=...)` en Pydantic |

**Python FastAPI — Built-in OpenAPI**:

```python
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="Orders API",
    version="1.0.0",
    description="API para gestión de órdenes de compra",
    docs_url="/swagger",
    redoc_url="/api-docs",
    openapi_url="/swagger/v1/openapi.json",
)

class OrderResponse(BaseModel):
    id: str = Field(..., description="Order unique identifier", examples=["550e8400-e29b-41d4"])
    customer_name: str = Field(..., min_length=2, max_length=100, description="Customer name")
    total: float = Field(..., description="Order total amount")
    status: str = Field(..., description="Order status", examples=["Pending", "Completed"])

class PaginationMetadata(BaseModel):
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_records: int = Field(..., description="Total number of records")
    total_pages: int = Field(..., description="Total number of pages")

class PagedOrderResponse(BaseModel):
    success: bool = True
    data: dict
    pagination: PaginationMetadata

@app.get(
    "/api/v1/orders",
    response_model=PagedOrderResponse,
    summary="List orders with pagination",
    description="Returns a paginated list of orders filtered by the given criteria.",
    tags=["Orders"],
    responses={
        400: {"description": "Bad Request - Validation errors"},
        401: {"description": "Unauthorized - Missing or invalid auth"},
        500: {"description": "Internal Server Error"},
    },
)
async def get_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("DESC", description="Sort direction"),
):
    ...

@app.post(
    "/api/v1/files/upload",
    summary="Upload a file",
    tags=["Files"],
    responses={
        200: {"description": "File uploaded successfully"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported media type"},
    },
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    category: str = Query(..., description="Category: image, document, spreadsheet"),
):
    ...
```

#### Design-First: Se escribe el spec primero y se genera código desde él

**Usar cuando**: se requiere contrato formal antes de implementar, hay múltiples equipos consumiendo la API, o se necesita validación temprana del diseño.

| Stack | Herramienta | Flujo |
|-------|-------------|-------|
| **General** | Stoplight Studio, Redocly CLI | Editar YAML/JSON visualmente, validar, generar código |
| **Python** | datamodel-code-generator | Spec → Pydantic models |
| **TypeScript Frontend** | openapi-typescript, orval | Spec → TypeScript types |

**Decisión por defecto**:
- Proyectos nuevos con `api-first-spec`: **Design-First** (spec primero, código después).
- Proyectos existentes con endpoints ya implementados: **Code-First** (código primero, spec generado).
- APIs públicas o compartidas entre equipos: **Design-First** obligatorio.

### 3. Documentación Interactiva (Swagger UI, ReDoc, Scalar, Redocly)

| Herramienta | Fortaleza | Uso recomendado |
|-------------|-----------|-----------------|
| **Swagger UI** | Try-it-out interactivo, amplio soporte | **Por defecto** para desarrollo |
| **ReDoc** | Diseño limpio, three-panel, buena referencia | Documentación pública, partner-facing |
| **Scalar** | UI moderna, dark mode, diseño premium | APIs internas con UX moderna |
| **Redocly** | Generación de sitios estáticos, customización | Portales de API empresariales |

**Configuración Python FastAPI**:

```python
app = FastAPI(
    title="Orders API",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/api-docs",
    openapi_url="/swagger/v1/openapi.json",
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
```

Reglas de configuración de UI:
- Swagger UI en `/swagger` para desarrollo interactivo.
- ReDoc o Scalar en `/api-docs` para documentación de referencia.
- Deshabilitar Swagger UI en producción si no se requiere acceso público.
- Incluir `try-it-out` habilitado para endpoints sin destructivos (GET, OPTIONS).
- Incluir autenticación Bearer JWT configurada en la UI.

### 4. Ciclo de vida de la documentación API

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  api-first-  │────►│  OpenAPI Spec     │────►│  Validación con   │
│  spec (9     │     │  (YAML/JSON)      │     │  Spectral         │
│  secciones)  │     │                   │     │                    │
└──────────────┘     └────────┬─────────┘     └────────┬──────────┘
                              │                          │
                    ┌─────────▼──────────┐      ┌───────▼──────────┐
                    │  UI Interactiva     │      │  Fix errors y     │
                    │  (Swagger/ReDoc/    │      │  warnings          │
                    │   Scalar)           │      │                    │
                    └────────────────────┘      └───────┬──────────┘
                                                          │
                              ┌───────────────────────────▼──────────┐
                              │  Generación de artefactos:           │
                              │  - Tipos TypeScript (api-first-       │
                              │    frontend, typescript)              │
                              │  - Contract tests (api-first-testing) │
                              │  - API Catalog (api-catalog)          │
                              │  - Client SDKs (opcional)             │
                              └──────────────────────────────────────┘
```

Reglas del ciclo de vida:
- El spec se valida con Spectral en CI antes de merge.
- Los cambios breaking en el spec requieren nueva versión (`api-versioning`).
- El spec se versiona junto con la API: `/swagger/v1/swagger.json`, `/swagger/v2/swagger.json`.
- Los tipos TypeScript se regeneran automáticamente cuando el spec cambia.
- El `api-catalog` se actualiza cuando se publica una nueva versión del spec.

#### Validación con Spectral

```yaml
# .spectral.yaml
extends: ["spectral:oas"]
rules:
  operation-operationId: error
  operation-summary: error
  operation-description: warn
  operation-tag-defined: error
  operation-success-response: error
  oas3-valid-schema: error
  no-eq-in-json-name: warn
  info-contact: error
  info-description: error

  # Reglas custom del framework
  response-contains-apiresponse-wrapper:
    description: "All responses must use ApiResponse wrapper"
    severity: error
    given: "$.paths[*][*].responses[*].content[*].schema"
    then:
      field: "properties.success"
      assert:
        defined: true

  operation-has-error-responses:
    description: "All operations must document 400, 401, 500 responses"
    severity: error
    given: "$.paths[*][*]"
    then:
      function: "oasOpSuccessResponse"
```

```bash
# Ejecutar validación con Spectral (consume directamente .spectral.yaml)
npx @stoplight/spectral-cli lint openapi.yaml --ruleset .spectral.yaml

# Alternativa: Redocly CLI, pero usa SU PROPIO formato de config (redocly.yaml),
# no es compatible con reglas de Spectral (.spectral.yaml)
npx @redocly/cli lint openapi.yaml --config redocly.yaml
```

### 5. Documentación de errores

```yaml
# En components/schemas del OpenAPI spec
components:
  schemas:
    ApiErrorResponse:
      type: object
      required: [success, errors]
      properties:
        success:
          type: boolean
          example: false
        errors:
          type: array
          items:
            $ref: '#/components/schemas/ErrorDetail'
          minItems: 1
        message:
          type: string
          example: "Validation failed"
        traceId:
          type: string
          format: uuid
          description: "Correlation ID for tracing"
    
    ErrorDetail:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          description: "Error code from the catalog (VAL_001, VAL_002, etc.)"
          example: "VAL_001"
        message:
          type: string
          description: "Human-readable error message"
          example: "Contact phone is required"
        field:
          type: string
          description: "Field that caused the error (for validation errors)"
          example: "contactPhone"
        severity:
          type: string
          enum: [error, warning]
          default: error

    # Errores por status code
    ErrorResponse400:
      allOf:
        - $ref: '#/components/schemas/ApiErrorResponse'
        - description: "Bad Request - Validation errors or malformed request"

    ErrorResponse401:
      allOf:
        - $ref: '#/components/schemas/ApiErrorResponse'
        - description: "Unauthorized - Missing or invalid authentication"

    ErrorResponse403:
      allOf:
        - $ref: '#/components/schemas/ApiErrorResponse'
        - description: "Forbidden - Insufficient permissions"

    ErrorResponse404:
      allOf:
        - $ref: '#/components/schemas/ApiErrorResponse'
        - description: "Not Found - Resource does not exist"

    ErrorResponse500:
      allOf:
        - $ref: '#/components/schemas/ApiErrorResponse'
        - description: "Internal Server Error - Unexpected error"
```

Regla: Todo endpoint DEBE documentar al menos las respuestas 200/201, 400, 401, 500 (y 404 si aplica GET por ID).

### 6. Documentación de respuestas paginadas

```yaml
# Schema de request paginado
components:
  schemas:
    PagedRequest:
      type: object
      properties:
        page:
          type: integer
          minimum: 1
          default: 1
          description: "Page number (1-based)"
        pageSize:
          type: integer
          minimum: 1
          maximum: 100
          default: 10
          description: "Items per page (max 100)"
        search:
          type: string
          description: "Search term"
        sortBy:
          type: string
          description: "Field to sort by"
        sortOrder:
          type: string
          enum: [ASC, DESC]
          default: DESC

    PaginationMetadata:
      type: object
      required: [page, pageSize, totalRecords, totalPages]
      properties:
        page:
          type: integer
          example: 1
        pageSize:
          type: integer
          example: 10
        totalRecords:
          type: integer
          example: 157
        totalPages:
          type: integer
          example: 16
```

### 7. Esquemas de autenticación y seguridad

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: "JWT token obtained from /api/v1/auth/login"
    
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: "API key for service-to-service communication"
    
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: "https://auth.company.com/oauth/authorize"
          tokenUrl: "https://auth.company.com/oauth/token"
          refreshUrl: "https://auth.company.com/oauth/refresh"
          scopes:
            read: "Read access"
            write: "Write access"
            admin: "Administrative access"

security:
  - BearerAuth: []
```

Reglas de seguridad en el spec:
- Declarar `securitySchemes` a nivel global en `components`.
- Documentar todos los flujos de autenticación relevantes (JWT, API Key, OAuth2).
- Marcar endpoints públicos con `security: []` (array vacío sobreescribe global).
- Incluir `401` y `403` en las respuestas de endpoints protegidos.

### 8. Server variables y ambientes

```yaml
servers:
  - url: "https://api.{tenant}.company.com/{apiVersion}"
    description: "Production environment"
    variables:
      tenant:
        default: "default"
        description: "Tenant identifier for multi-tenant deployments"
        enum: ["default", "tenant-a", "tenant-b"]
      apiVersion:
        default: "v1"
        description: "API version"
        enum: ["v1"]
  - url: "https://staging-api.company.com/{apiVersion}"
    description: "Staging environment"
    variables:
      apiVersion:
        default: "v1"
  - url: "https://localhost:8000/{apiVersion}"
    description: "Local development"
    variables:
      apiVersion:
        default: "v1"
```

### 9. Generación de tipos TypeScript

```bash
# Con openapi-typescript
npx openapi-typescript openapi.yaml --output src/types/api.d.ts

# Con orval (genera tipos + hooks)
npx orval --config orval.config.ts
```

```typescript
// orval.config.ts
import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: "https://localhost:8000/swagger/v1/openapi.json",
    output: {
      target: "src/api/endpoints.ts",
      schemas: "src/api/models",
      client: "axios",
      override: {
        mutator: {
          path: "src/api/axios-instance.ts",
          name: "customInstance",
        },
      },
    },
  },
});
```

## Preguntas guía

### 1. Sobre enfoque de documentación
- ¿Se usa Code-First (generar spec desde código) o Design-First (escribir spec primero)?
- ¿La API es pública, interna o entre equipos? ¿El enfoque cambia?
- ¿Los consumidores necesitan el spec antes de que la API esté implementada?

### 2. Sobre completitud y calidad
- ¿Todos los endpoints tienen operationId, summary, description y tags?
- ¿Todas las respuestas documentan el esquema de error estándar?
- ¿Se incluyen ejemplos en requests y responses?

### 3. Sobre publicación y adopción
- ¿Qué UI interactiva se expone (Swagger UI, ReDoc, Scalar)?
- ¿Cómo se asegura que el spec está siempre actualizado?
- ¿Se valida el spec con Spectral en CI?

## Salidas esperadas de esta skill

### A. Archivo OpenAPI Spec
- `openapi.yaml` o `openapi.json` con la especificación completa de la API.
- Todos los endpoints documentados con operationId, summary, description, tags.
- Esquemas de error, paginación y file upload incluidos en `components/schemas`.
- Server variables configuradas para tenant y versión.

### B. Configuración de UI interactiva
- Swagger UI configurado en `/swagger` para desarrollo.
- ReDoc o Scalar configurado en `/api-docs` para referencia.
- Autenticación JWT configurada en la UI (Bearer token).

### C. Configuración de validación Spectral
- `.spectral.yaml` con reglas del framework (ApiResponse wrapper, error responses, operationId).
- CI step que ejecuta `spectral lint` o `redocly lint` antes de merge.

### D. Generación de tipos (opcional)
- Tipos TypeScript generados desde el spec (`openapi-typescript` o `orval`).
- Hooks de TanStack Query generados (si se usa `orval`).

## Criterios de calidad

- Todo endpoint tiene `operationId` único, `summary`, `description` y al menos un `tag`.
- Toda respuesta de error usa el esquema `ApiErrorResponse` con `errors[]`.
- Toda respuesta paginada incluye `pagination` con `page`, `pageSize`, `totalRecords`, `totalPages`.
- Todo endpoint de file upload usa `multipart/form-data` con restricciones documentadas.
- El spec pasa validación Spectral sin errores de nivel `error`.
- Los ejemplos (`examples`) están presentes en al menos los endpoints principales.
- Las versiones deprecadas incluyen `deprecated: true` y descripción con fecha de remoción.
- La UI interactiva permite probar los endpoints con autenticación JWT.

## Comportamiento esperado del agente

Cuando el usuario documente endpoints sin `operationId`, el agente debe generarlos siguiendo el patrón `{verb}{Entity}` (`getUsers`, `createUser`, `updateUser`, `deleteUser`).
Cuando el usuario no documente respuestas de error, el agente debe agregar automáticamente `400`, `401` y `500` con el esquema `ApiErrorResponse`.
Cuando el usuario use OpenAPI 3.0, el agente debe sugerir migración a 3.1 para soportar `examples` (no `example`) y JSON Schema draft 2020-12.
Cuando el usuario duplique definiciones de schemas, el agente debe refactorizar a `$ref` en `components/schemas`.

## Checklist final de la skill

- [ ] ¿Se seleccionó el enfoque (Code-First o Design-First) según el contexto?
- [ ] ¿Todos los endpoints tienen `operationId`, `summary`, `description` y `tags`?
- [ ] ¿Todas las respuestas de error usan el esquema `ApiErrorResponse`?
- [ ] ¿Las respuestas paginadas incluyen `pagination` con metadata completa?
- [ ] ¿Los endpoints de file upload usan `multipart/form-data` con restricciones?
- [ ] ¿Se configuró la UI interactiva (Swagger UI + ReDoc/Scalar)?
- [ ] ¿Se configuró validación Spectral en CI?
- [ ] ¿Se generaron tipos TypeScript desde el spec?
- [ ] ¿Las versiones deprecadas tienen `deprecated: true`?
- [ ] ¿Se usan `$ref` en `components/schemas` sin duplicar definiciones?
- [ ] ¿Se incluyen ejemplos (`examples`) en los endpoints principales?
- [ ] ¿Se documentaron los esquemas de seguridad (JWT, API Key)?
- [ ] ¿Los server variables están configurados (tenant, versión)?
