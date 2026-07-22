---
name: agent-fullstack
description: 'Meta-skill: activates all skills for full-stack feature implementation
  (DB → API → UI). Stack: Python/FastAPI + PostgreSQL + React. Trigger: When implementing a complete feature across all layers.'
version: 1.1
metadata:
  phase:
  - construction
  layer:
  - backend
  - frontend
  enforcement: recommended
  depends_on:
  - agent-backend
  - react
  - react-services
  - typescript
  consumed_by: []
  agent_roles:
  - design-agent
  - delivery-agent
  - orchestrator-agent
  validation_profile: skill-contract
  mcp_usage: governed
---

## Purpose
Master meta-skill for full-stack feature development. Orchestrates backend and frontend meta-skills.
Backend is always implemented first.

## Full-Stack Workflow

| Step | Skill | Layer | Artifacts |
|------|-------|-------|-----------|
| 1 | `api-first-spec` | Planning | Feature spec document |
| 2 | `database-modeling` | DB | Table design |
| 3 | `database-sp` | DB | Stored procedures |
| 4 | `database-audit` | DB | Audit columns |
| 5 | `data-access` | Backend | Handlers |
| 6 | `backend-api` | Backend | Endpoints |
| 7 | `api-integration` | Backend | Wiring |
| 8 | `error-handling` | Backend | Error flow |
| 9 | `openapi-docs` | Backend | OpenAPI docs |
| 10 | `typescript` | Frontend | Types |
| 11 | `react-services` | Frontend | Query/Mutation hooks |
| 12 | `react` | Frontend | Components + Pages |
| 13 | `export-excel` | Both | (if applicable) Export |
| 14 | `api-first-testing` | Testing | E2E tests |

## Sequence Diagram
```
[Spec] → [DB] → [Backend] → [OpenAPI] → [Frontend Types] →
[Services] → [Components] → [E2E Tests]
```

## Implementation Order (MANDATORY)
1. **Backend first** — never generate frontend code before backend is complete
2. **Spec driven** — always start with `api-first-spec` if building something new
3. **Types from spec** — generate TypeScript types from OpenAPI spec

## Cross-Layer Consistency Checks
| Check | When |
|-------|------|
| Error codes match DB ↔ Backend ↔ Frontend | After Step 8 |
| Request/Response types match OpenAPI | After Step 9 |
| TypeScript interfaces match OpenAPI schemas | After Step 10 |
| Services match endpoint URLs | After Step 11 |

## Conflict Resolution

| Conflict | Resolution |
|----------|------------|
| Spec change mid-implementation | Complete current layer first, then re-spec from `api-first-spec`, never switch layers mid-step |
| Backend contract breaks frontend | Document breaking change, complete backend migration, notify frontend via updated OpenAPI spec |
| Multiple features touch same table | Implement sequentially, not in parallel per table. Use separate SPs per feature. |
| Performance vs correctness | Default to correctness. Optimize only after profiling. Document each optimization decision. |

## Rollback Strategy

| Phase | Rollback point |
|-------|----------------|
| Planning (Step 1) | Discard spec, restart |
| DB (Steps 2-4) | Drop temp tables, restore from migration backup |
| Backend (Steps 5-9) | Revert endpoint files, keep DB changes |
| Frontend (Steps 10-13) | Revert feature folder, keep types |
| Testing (Step 14) | Discard test files, re-run after fix |

## Common Mistakes

- **Parallel implementation**: Never implement backend and frontend in parallel. Always backend first, then frontend.
- **Skipping spec**: Never skip `api-first-spec`. Without a spec, cross-layer consistency is unverifiable.
- **Stale OpenAPI**: After any backend change, regenerate OpenAPI before touching frontend types.
- **Missing E2E**: Never mark a feature complete without Playwright tests covering the happy path.

## Quality Gates

Los siguientes gates deben verificarse antes de considerar la meta-skill completada:

| Gate | Título | Descripción |
|------|--------|-------------|
| 1 | Gates de backend pasan | Todos los gates de agent-backend pasan |
| 2 | Gates de frontend pasan | Todos los gates de agent-frontend pasan |
| 3 | Integración E2E completa (CRUD) | La integración frontend→backend funciona E2E (CRUD completo) |
| 4 | Errores del backend visibles en UI | Los errores del backend se muestran correctamente en la UI |
| 5 | Roles muestran/ocultan funcionalidad | Los roles de usuario muestran/ocultan funcionalidad correctamente |
| 6 | Compatibilidad con navegadores | La app funciona en todos los navegadores soportados |

## Flujo de ejecución detallado

El pipeline completo de full-stack conecta 28 niveles desde la base de datos hasta las pruebas E2E. Cada nivel produce artefactos que el siguiente nivel consume. La ejecución es estrictamente secuencial dentro de cada fase.

### Fase E — Backend (Niveles 17–31)

| Nivel | Skill | Produce | Consumido Por |
|-------|-------|---------|---------------|
| 17 | `database-modeling` | Diseño de tablas, constraints, índices, relaciones ERD | N18 (database-sp), N19 (database-migrations), N20 (database-seeding) |
| 18 | `database-sp` | Stored procedures (List, Get, Create, Update, Delete, Search, Merge) | N22 (data-access) |
| 19 | `database-migrations` | Scripts de migración versionados, rollback scripts | N20 (database-seeding), pipeline CI/CD |
| 20 | `database-seeding` | Catálogos, fixtures, datos de prueba por ambiente | N22 (data-access), N38 (unit-testing), N39 (integration-testing) |
| 21 | `data-migration` (*recommended*) | Scripts ETL, verificación de integridad, rollback de datos | N22 (data-access), validación de datos |
| 22 | `data-access` | Handlers SQLAlchemy que llaman SPs | N23 (backend-api) |
| 23 | `backend-api` | Endpoints REST, controladores, requests, responses, routing | N24 (authentication), N25 (authorization), N27 (error-handling), N28 (api-integration) |
| 24 | `authentication` | Middleware JWT/OAuth2, propagación de identidad, login/logout | N25 (authorization), N26 (security), frontend N32–N37 |
| 25 | `authorization` | RBAC, políticas de permisos, claims, resource-level access | N26 (security), N31 (openapi-docs), frontend N34 (react) |
| 26 | `security` | CORS, validación OWASP Top 10, headers de seguridad, rate limiting | N27 (error-handling), N30 (api-resilience) |
| 27 | `error-handling` | Mapeo DB→Backend→Frontend, excepciones, códigos de error, middleware | N28 (api-integration), frontend N33 (react-services), N34 (react) |
| 28 | `api-integration` | Wiring DB→API, paginación, validación de entrada/salida, mapeo de errores | N29 (api-versioning), N30 (api-resilience), N31 (openapi-docs) |
| 29 | `api-versioning` | Estrategia de versionado (URI/header/media-type), sunset headers, deprecation | N30 (api-resilience), N31 (openapi-docs) |
| 30 | `api-resilience` (*recommended*) | Circuit breakers, retry policies, rate limiting, bulkheads, timeouts | N31 (openapi-docs), infraestructura |
| 31 | `openapi-docs` | Documentación OpenAPI 3.0, spec JSON/YAML, Swagger UI | **N32 (typescript) — handoff crítico**, frontend N33–N37, N44 (playwright) |

### Fase F — Frontend (Niveles 32–37)

| Nivel | Skill | Produce | Consumido Por |
|-------|-------|---------|---------------|
| 32 | `typescript` | Tipos TypeScript generados desde OpenAPI, interfaces de DTOs, tipos de error | N33 (react-services) |
| 33 | `react-services` | Hooks de @tanstack/react-query (useQuery, useMutation), hooks de lógica de negocio | N34 (react) |
| 34 | `react` | Componentes de UI (function components), páginas, routing (react-router-dom), react-hook-form, tablas, layouts | N35 (i18n), N36 (feature-flags), N37 (file-upload) |
| 35 | `i18n` | Archivos de localización, react-i18next, formato fecha/moneda, RTL | N34 (react) — wrappers de componentes |
| 36 | `feature-flags` | Toggles de funcionalidad, A/B testing, kill switches, targeting por rol | N34 (react) — renderizado condicional |
| 37 | `file-upload` | Componentes de upload, progreso, thumbnails, servicios de blob storage | N34 (react), N44 (playwright) |

### Fase G — Calidad (Niveles 38–44)

| Nivel | Skill | Produce | Consumido Por |
|-------|-------|---------|---------------|
| 38 | `unit-testing` | Tests unitarios de handlers, servicios, componentes | N39 (integration-testing), pipeline CI |
| 39 | `integration-testing` | Tests de integración con TestContainers, BD real | N40 (load-testing), N41 (security-testing) |
| 40 | `load-testing` (*recommended*) | Scripts k6/Gatling, perfiles de carga, validación de SLOs, informes | Pipeline CI/CD, revisión de performance |
| 41 | `security-testing` (*recommended*) | Escaneo SAST/DAST, dependency scan, secret scan, reporte de vulnerabilidades | Pipeline CI/CD, gate de release |
| 42 | `accesibilidad` | Auditoría WCAG 2.2 AA, ARIA labels, navegación por teclado, axe-core | N44 (playwright) — tests de accesibilidad |
| 43 | `framework-qa-validation` | Estrategia de QA por capa, contract tests, validación de guardrails multi-tenant | N44 (playwright), compuerta go/no-go |
| 44 | `playwright` | Tests E2E (CRUD completo, flujos críticos, Page Objects), reportería | Pipeline CI/CD, release |

### Diagrama de handoff entre fases

```
FASE E (Backend)                    FASE F (Frontend)              FASE G (Calidad)
N17 ─► N18 ─► N19 ─► N20           N32 ─► N33 ─► N34             N38 ─► N39 ─► N40
       │                              │         │                    │
       ▼                              ▼         ▼                    ▼
N21 ─► N22 ─► N23 ─► N24 ─► N25    N35 ─► N34    N37 ─► N34      N41 ─► N42 ─► N43 ─► N44
              │         │         N36 ─► N34                           │
              ▼         ▼                                               ▼
       N26 ─► N27 ─► N28 ─► N29 ─► N30 ─► N31 ────────► N32      Pipeline CI/CD
                                                      (OpenAPI ─► Types)
```

### Puntos de sincronización obligatorios

| Punto | Niveles involucrados | Acción |
|-------|----------------------|--------|
| **Handoff DB→Backend** | N20 → N22 | Verificar que todas las SPs existen y devuelven los resultados esperados antes de escribir handlers |
| **Handoff Backend→Frontend** | N31 → N32 | Regenerar spec OpenAPI después de N28, verificar que todos los endpoints están documentados |
| **Handoff Backend→Testing** | N31 → N44 | Los tests E2E usan la spec OpenAPI como fuente de verdad para requests/responses |
| **Handoff Frontend→QA** | N34 → N38, N44 | Los tests unitarios de componentes se escriben después de que los componentes están estables |
| **Sincronización errores** | N27 → N33, N34 | Los códigos de error del backend deben coincidir con el manejo de errores en servicios y UI |

## Orquestación backend → frontend

### 1. Backend niveles 17–31 completados → OpenAPI spec generado

Cuando la Fase E finaliza en el nivel 31 (`openapi-docs`), el proyecto debe tener:

- Un archivo `openapi.json` o `openapi.yaml` que documenta **todos** los endpoints del módulo implementado.
- Cada endpoint con su método HTTP, ruta, parámetros de query/path, request body (schema), response body (schema) y códigos de error documentados.
- Los schemas de respuesta incluyen el wrapper estándar `ApiResponse<T>` con sus campos `data`, `message`, `errors`, `success`.
- Los schemas de error incluyen el formato estandarizado con `code`, `description`, `details`.

Este spec se convierte en el **contrato único** entre backend y frontend. Cualquier cambio en el backend después de este punto **requiere regenerar el spec** antes de tocar código frontend.

### 2. Frontend niveles 32–37 consumen el OpenAPI spec

La Fase F arranca con el nivel 32 (`typescript`) que toma el `openapi.json` como entrada. El flujo es:

```
openapi.json ──► Generación de tipos ──► Interfaces TS ──► Servicios ──► Componentes
```

Cada nivel frontend depende del anterior:

- **N32 (typescript)**: Lee `openapi.json` y genera interfaces, tipos de request/response, tipos de error y constantes de endpoint.
- **N33 (react-services)**: Usa los tipos del N32 para crear hooks tipados con @tanstack/react-query.
- **N34 (react)**: Consume los hooks del N33 en componentes y páginas.
- **N35–N37**: Envuelven los componentes con i18n, feature flags y file upload según corresponda.

### 3. Cómo se generan los tipos desde OpenAPI

El proceso de generación de tipos sigue estos pasos:

1. **Extraer schemas del openapi.json**: Se recorren las secciones `components.schemas` y `paths` para identificar todos los DTOs de request y response.

2. **Mapear a interfaces TypeScript**:

   ```
   OpenAPI Schema          → TypeScript Interface
   ─────────────────────────────────────────────────
   type: object             → interface Nombre {}
   properties               → campos del interface
   required                 → campos obligatorios (sin ?)
   $ref                     → import de otro interface
   type: array, items: $ref → Array<Tipo>
   allOf/oneOf/anyOf        → uniones e intersecciones
   ```

3. **Generar tipos de endpoint**: Por cada ruta en `paths` se genera:

   ```typescript
   // Tipo para los parámetros del endpoint
   export type ListarUsuariosParams = {
     page?: number;
     limit?: number;
     search?: string;
   };

   // Tipo para la respuesta
   export type ListarUsuariosResponse = ApiResponse<Usuario[]>;

   // Constante con la ruta y método
   export const ENDPOINT_LISTAR_USUARIOS = '/api/v1/usuarios';
   ```

4. **Generar tipos de error**: Se extraen los códigos de error documentados en el spec y se genera un enum o tipo unión:

   ```typescript
   export type ErrorCode =
     | 'VALIDATION_ERROR'
     | 'NOT_FOUND'
     | 'UNAUTHORIZED'
     | 'FORBIDDEN'
     | 'INTERNAL_ERROR';
   ```

### 4. Cómo los hooks corresponden a los endpoints

Cada endpoint en el OpenAPI spec genera un hook específico siguiendo esta convención:

| Endpoint | Método | Hook generado |
|----------|--------|-------------------|
| `GET /api/v1/usuarios` | Listar | `useUsuariosListar(params)` → `useQuery` |
| `GET /api/v1/usuarios/{id}` | Obtener | `useUsuarioObtener(id)` → `useQuery` |
| `POST /api/v1/usuarios` | Crear | `useUsuarioCrear()` → `useMutation` |
| `PUT /api/v1/usuarios/{id}` | Actualizar | `useUsuarioActualizar()` → `useMutation` |
| `DELETE /api/v1/usuarios/{id}` | Eliminar | `useUsuarioEliminar()` → `useMutation` |

**Patrón de implementación del hook:**

```typescript
// Endpoint: GET /api/v1/usuarios
// Hook: useUsuariosListar

import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/core/http/api-client';
import type { ListarUsuariosParams, ListarUsuariosResponse } from '@/types';

export function useUsuariosListar(params: ListarUsuariosParams) {
  return useQuery({
    queryKey: ['usuarios', 'listar', params],
    queryFn: () =>
      apiFetch<ListarUsuariosResponse>('/api/v1/usuarios', {
        query: params,
      }),
  });
}
```

**Reglas de generación:**

- `GET` → `useQuery` con `queryKey` que incluye el nombre del recurso y los parámetros.
- `POST`, `PUT`, `DELETE`, `PATCH` → `useMutation` con `onSuccess` que invalida las queries relacionadas.
- El `queryKey` sigue el patrón `[recurso, acción, ...identificadores]`.
- Los hooks exponen el resultado completo de @tanstack/react-query (`data`, `isLoading`, `isError`, `error`, `refetch`).

### 5. Cómo los componentes usan los hooks

Los componentes consumen los hooks directamente en función components:

**Patrón de componente con lista:**

```tsx
// pages/usuarios/UsuariosList.tsx
import { useState } from 'react';
import { useUsuariosListar } from '@/features/usuarios/hooks/use-usuarios';
import { SkeletonTable } from '@/shared/components/SkeletonTable';
import { ErrorBanner } from '@/shared/components/ErrorBanner';
import { UsuarioRow } from './UsuarioRow';
import { Pagination } from '@/shared/components/Pagination';

export function UsuariosList() {
  const [page, setPage] = useState(1);
  const query = useUsuariosListar({ page, limit: 10 });

  if (query.isLoading) return <SkeletonTable />;
  if (query.isError) return <ErrorBanner message={query.error?.message ?? ''} />;

  return (
    <table>
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Email</th>
          <th>Rol</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {(query.data?.data ?? []).map((usuario) => (
          <UsuarioRow key={usuario.id} usuario={usuario} />
        ))}
      </tbody>
      <tfoot>
        <Pagination page={page} total={query.data?.total ?? 0} onPageChange={setPage} />
      </tfoot>
    </table>
  );
}
```

**Patrón de componente con mutación:**

```tsx
// components/usuarios/CrearUsuarioForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useUsuarioCrear } from '@/features/usuarios/hooks/use-usuarios';
import { crearUsuarioSchema } from '@/features/usuarios/usuarios.schema';
import type { CrearUsuarioRequest } from '@/types';
import { ErrorAlert } from '@/shared/components/ErrorAlert';

export function CrearUsuarioForm() {
  const mutation = useUsuarioCrear();
  const { register, handleSubmit } = useForm<CrearUsuarioRequest>({
    resolver: zodResolver(crearUsuarioSchema),
  });

  const onSubmit = (data: CrearUsuarioRequest) => {
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* campos del formulario con register(...) */}
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Guardando...' : 'Crear Usuario'}
      </button>
      {mutation.isError && <ErrorAlert message={mutation.error?.message ?? ''} />}
    </form>
  );
}
```

**Manejo de errores consistente:**

El flujo de errores desde la base de datos hasta la UI sigue esta cadena:

```
DB (código SQL) → SP → Handler → API (código HTTP + error code) → 
Hook (captura en isError) → Componente (renderiza ErrorBanner/ErrorAlert)
```

## Prompt templates por fase

### Prompt para orquestación completa full-stack

Template para invocar al agente orquestador cuando se implementa un módulo completo:

```
Eres el orquestador full-stack del Framework Agéntico. 
Tu tarea es implementar el módulo [NOMBRE_MODULO] de principio a fin.

## Contexto del módulo
- Módulo: [NOMBRE_MODULO]
- Vertical: [NOMBRE_VERTICAL]
- Features: [LISTA_DE_FEATURES]
- Tabla principal: [NOMBRE_TABLA]
- Roles que acceden: [ROLES]
- Requiere exportación Excel: [SI/NO]
- Requiere file upload: [SI/NO]
- Navegador soporte: [MODERNOS/LEGACY]

## Flujo de ejecución
Ejecuta las siguientes fases EN ORDEN, esperando a que cada una termine antes de empezar la siguiente:

### Fase 1: Backend (agente agent-backend)
Activa agent-backend con los siguientes parámetros:
- Módulo: [NOMBRE_MODULO]
- Incluir niveles desde N17 hasta N31
- Features a implementar: [LISTA]
- Database: [PostgreSQL]

Espera a que agent-backend confirme que todos los niveles han completado y los gates han pasado.

### Fase 2: Regenerar OpenAPI spec
Verificar que el archivo openapi.json existe y contiene todos los endpoints del módulo.
Si falta algún endpoint, detener y reportar.

### Fase 3: Frontend (agente agent-frontend)
Activa agent-frontend con los siguientes parámetros:
- Módulo: [NOMBRE_MODULO]
- Ruta del openapi.json: [RUTA]
- Incluir niveles desde N32 hasta N37
- UI Framework: [React]
- Librería de componentes: [Radix UI / shadcn/ui]

Espera a que agent-frontend confirme que todos los niveles han completado y los gates han pasado.

### Fase 4: Verificación de integración
1. Verificar que los tipos TypeScript existen para todos los DTOs del módulo.
2. Verificar que los servicios existen para todos los endpoints del módulo.
3. Verificar que los componentes consumen los servicios correctamente.
4. Verificar que los códigos de error del backend se muestran en la UI.
5. Verificar que las rutas del frontend están registradas en el router.

### Fase 5: Calidad (niveles N38–N44)
Activar en orden:
1. N38 unit-testing: Tests unitarios de handlers, servicios y componentes.
2. N39 integration-testing: Tests de integración con base de datos real.
3. N44 playwright: Tests E2E del flujo CRUD completo.

### Fase 6: Validación final
Ejecutar los 6 quality gates:
1. Los gates de backend pasan.
2. Los gates de frontend pasan.
3. Integración E2E completa con CRUD funcional.
4. Errores del backend visibles en la UI.
5. Roles muestran/ocultan funcionalidad correctamente.
6. Compatibilidad con navegadores verificada.

## Restricciones
- NO ejecutar backend y frontend en paralelo.
- NO saltarse la especificación (api-first-spec).
- NO modificar el openapi.json sin regenerarlo desde el backend.
- NO marcar como completo sin E2E tests.

## Output esperado
Al finalizar, reportar:
1. Resumen de lo implementado (backend + frontend + tests).
2. Archivos creados/modificados.
3. Quality gates y su estado (passed/failed).
4. Cualquier desviación del plan original.
```

### Prompt para delegar a agent-backend

```
Activa agent-backend para implementar el backend del módulo [NOMBRE_MODULO].

## Parámetros
- Módulo: [NOMBRE_MODULO]
- Feature: [DESCRIPCIÓN]
- Database: [TIPO]
- Stack: [Python]
- Incluir export-excel: [SI/NO]
- Incluir api-resilience: [SI/NO]

## Niveles a ejecutar
Desde N17 (database-modeling) hasta N31 (openapi-docs).
```

### Prompt para delegar a agent-frontend

```
Activa agent-frontend para implementar el frontend del módulo [NOMBRE_MODULO].

## Parámetros
- Módulo: [NOMBRE_MODULO]
- Ruta openapi: [RUTA_OPENAPI_JSON]
- Stack frontend: [React]
- Librería UI: [Radix UI / shadcn/ui]
- Requiere i18n: [SI/NO]
- Requiere feature flags: [SI/NO]
- Requiere file upload: [SI/NO]
- Ruta base frontend: [RUTA_BASE]

## Niveles a ejecutar
Desde N32 (typescript) hasta N37 (file-upload) si aplica.

## Reglas
- Generar tipos desde openapi.json.
- Hooks con @tanstack/react-query (o alternativa del stack).
- Componentes con manejo de loading, empty, error states.
- El estado vacío debe mostrar un mensaje amigable.
- El estado de error debe mostrar el mensaje del backend.
- Paginación en todas las tablas LIST.

## Output esperado
- Archivos de tipos TypeScript.
- Servicios de query y mutation.
- Componentes y páginas.
- Archivos de i18n (si aplica).
- Componentes de file upload (si aplica).
```

### Prompt para verificación de integración

```
Verifica la integración backend ↔ frontend del módulo [NOMBRE_MODULO].

## Checklist de verificación

### Tipos TypeScript vs OpenAPI
- [ ] Cada schema en openapi.json tiene su interface en types/
- [ ] Los nombres de los tipos siguen la convención PascalCase
- [ ] Los tipos opcionales están marcados con ?
- [ ] Los arrays están tipados como Array<T> o T[]

### Servicios vs Endpoints
- [ ] Cada endpoint GET tiene un hook useQuery
- [ ] Cada endpoint POST/PUT/DELETE tiene un hook useMutation
- [ ] Los queryKeys incluyen recurso + acción + identificadores
- [ ] Las mutations invalidan las queries relacionadas en onSuccess

### Componentes vs Servicios
- [ ] Cada pantalla de lista usa su hook useQuery correspondiente
- [ ] Cada formulario de creación/edición usa su hook useMutation
- [ ] Los componentes manejan isLoading (skeleton/spinner)
- [ ] Los componentes manejan isError (banner/alert)
- [ ] Los componentes manejan datos vacíos (empty state)

### Errores
- [ ] Los códigos de error del backend se muestran en la UI
- [ ] Errores de validación (400) muestran los detalles del campo
- [ ] Errores de autenticación (401) redirigen al login
- [ ] Errores de permiso (403) muestran mensaje de acceso denegado
- [ ] Errores de servidor (500) muestran mensaje genérico

### Routing
- [ ] Las rutas del frontend están registradas en el router
- [ ] Las rutas siguen la convención /modulo/recurso/accion
- [ ] La navegación entre lista y detalle funciona
- [ ] Los parámetros de ruta (id) se pasan correctamente
```

### Prompt para quality gates post-integration

```
Ejecuta los quality gates del módulo [NOMBRE_MODULO].

## Gate 1: Backend gates
Verificar que todos los gates definidos en agent-backend pasan:
- [ ] Tests unitarios de handlers pasan
- [ ] Tests de integración de API pasan
- [ ] Cobertura de código mínima alcanzada
- [ ] OpenAPI spec completo y válido

## Gate 2: Frontend gates
Verificar que todos los gates definidos en agent-frontend pasan:
- [ ] Tests unitarios de servicios pasan
- [ ] Tests unitarios de componentes pasan
- [ ] Typescript compila sin errores
- [ ] Linter pasa sin warnings

## Gate 3: Integración E2E (CRUD completo)
Ejecutar prueba manual o automatizada:
- [ ] Listar registros: GET funciona y muestra datos
- [ ] Crear registro: POST funciona y redirige a lista
- [ ] Ver detalle: GET por id funciona
- [ ] Actualizar registro: PUT funciona y refleja cambios
- [ ] Eliminar registro: DELETE funciona con confirmación

## Gate 4: Errores visibles en UI
- [ ] Enviar formulario vacío → mostrar errores de validación
- [ ] Crear registro duplicado → mostrar error de conflicto
- [ ] Acceder sin token → redirigir a login
- [ ] Acceder sin permiso → mostrar acceso denegado

## Gate 5: Roles
- [ ] Usuario admin ve todas las funcionalidades
- [ ] Usuario editor ve formularios de edición
- [ ] Usuario viewer solo ve lectura (sin botones de acción)
- [ ] Los elementos no permitidos están ocultos (no solo deshabilitados)

## Gate 6: Compatibilidad
- [ ] Chrome (última versión)
- [ ] Firefox (última versión)
- [ ] Edge (última versión)
- [ ] Safari (última versión) — si aplica
- [ ] Responsive: funciona en mobile (viewport < 768px)

## Resultado
- Gates passed: [X/6]
- Gates failed: [LISTA]
- Acciones correctivas: [DESCRIPCIÓN]
```
