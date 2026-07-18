---
name: api-first-testing
description: 'Generate E2E and API tests from OpenAPI spec using Playwright and API
  testing tools. Generates test cases, Page Objects, and assertions from endpoints.
  Trigger: When creating E2E tests from OpenAPI spec, generating test cases.'
version: 1.0
metadata:
  phase:
  - inception
  - quality
  - construction
  layer:
  - testing
  enforcement: mandatory
  depends_on:
  - api-first-spec
  - api-first-backend
  consumed_by:
  - playwright
  - integration-testing
  agent_roles:
  - control-agent
  validation_profile: skill-contract
  mcp_usage: governed
---

# api-first-testing

## Propósito

Esta skill define cómo generar tests de API y E2E a partir de una especificación OpenAPI, de modo que cada endpoint documentado tenga cobertura de testing derivada automáticamente del contrato.  
Su función es transformar la especificación OpenAPI (generada por `api-first-spec`) en escenarios de prueba, assertions, fixtures y Page Objects, asegurando que el contrato entre frontend y backend se valida antes de que los tests E2E en navegador se ejecuten (consumido por `playwright` y complementado por `integration-testing`).

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo derivar escenarios de prueba automáticamente desde una especificación OpenAPI?
2. ¿Qué categorías de tests se generan por cada tipo de endpoint (contract, schema validation, status codes, business rules)?
3. ¿Cómo usar Playwright APIRequestContext para testear endpoints de API sin levantar navegador?
4. ¿Cómo asegurar que los contracts entre frontend y backend se mantienen sincronizados?
5. ¿Cómo organizar fixtures, Page Objects y escenarios derivados del spec?

## Relación con otras skills

- `api-first-spec` provee la especificación OpenAPI de la cual se derivan todos los tests; es el insumo principal.
- `api-first-backend` provee los endpoints implementados que se testean; sus handlers y controllers son los sujetos de prueba.
- `api-first-testing` consume el spec y valida los endpoints, generando contract tests, schema validation y API tests.
- `playwright` consume los Page Objects y escenarios generados por esta skill para tests E2E en navegador.
- `integration-testing` complementa esta skill con tests que usan dependencias reales (BD, middleware) en vez de mocks.
- `framework-qa-validation` define la estrategia general de testing y valida que los artefactos de esta skill cumplen los criterios de calidad.

## Qué debe hacer el agente cuando esta skill está activa

1. Leer y parsear la especificación OpenAPI del módulo (`docs/api-first/{MODULE}.md` o archivo YAML/JSON).
2. Identificar todos los endpoints documentados y clasificarlos por tipo (List, Get, Create, Update, Delete, Operation, Remove, Reorder, Search).
3. Generar escenarios de prueba por cada endpoint: happy path, validation errors, business errors, not found, conflict, unauthorized.
4. Generar contract tests que validen que el schema de response cumple con lo definido en el spec.
5. Generar schema validation tests que verifiquen que los tipos de datos, campos requeridos y constraints se cumplen.
6. Generar status code coverage tests que verifiquen cada código de respuesta documentado en el spec.
7. Crear fixtures reutilizables con datos de prueba derivados de los ejemplos del spec.
8. Generar Page Objects que mapean los endpoints a funciones de API testing reutilizables.
9. Configurar Playwright APIRequestContext para tests de API sin navegador.
10. Asegurar que los `data-testid` de los componentes UI coincidan con los selectores usados en los tests.

## Entradas esperadas

Esta skill asume que ya existe:
- Especificación OpenAPI del módulo (`api-first-spec`);
- Endpoints de backend implementados y funcionales (`api-first-backend`);
- Esquemas de request/response documentados;
- Códigos de error y reglas de negocio documentados;
- Datos de seed para pruebas.

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- Contract tests derivados del spec OpenAPI;
- Schema validation de requests y responses;
- Status code coverage por endpoint;
- API tests con Playwright APIRequestContext;
- Fixtures y Page Objects derivados del spec;
- Test generation workflow automatizado;
- `data-testid` mapeados y documentados.

La fase no incluye todavía:
- tests unitarios en aislamiento (`unit-testing`);
- tests de integración con BD real (`integration-testing`);
- tests E2E completos en navegador (`playwright`);
- tests de carga o stress (`load-testing`);
- tests de seguridad (`security-testing`).

## Principios que siempre debe respetar

- Los tests DEBEN derivarse del spec OpenAPI, no de la implementación.
- Cada endpoint documentado DEBE tener al menos un contract test.
- Los contract tests DEBEN validar el schema completo del response, no solo campos sueltos.
- Los status code tests DEBEN cubrir todos los códigos documentados en el spec (200, 201, 400, 404, 409, 422, 500).
- Los fixtures DEBEN ser derivados de los ejemplos del spec (example objects).
- Los Page Objects de API DEBEN abstraer los detalles HTTP y exponer métodos de negocio.
- Los tests DEBEN ser independientes: cada test debe poder ejecutarse solo sin depender de otro.
- Los `data-testid` DEBEN coincidir entre componentes UI y Page Objects de testing.
- Los contract tests DEBEN romper el build si el backend cambia el schema sin actualizar el spec.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- las categorías de tests a generar desde el spec;
- los escenarios de prueba por tipo de endpoint;
- la estructura de fixtures y Page Objects de API;
- la configuración de Playwright APIRequestContext;
- los asserts y validaciones por endpoint.

Esta skill delega:
- los tests E2E en navegador a `playwright`;
- los tests de integración con BD real a `integration-testing`;
- la estrategia general de QA a `framework-qa-validation`;
- los datos de seed a `database-seeding`;
- los tests unitarios a `unit-testing`.

## Qué debe definir el diseño

### 1. Test categories from OpenAPI spec

Cada tipo de endpoint genera un conjunto fijo de categorías de tests:

| Endpoint Type | Contract Test | Schema Validation | Status Code Coverage | Business Rule Test |
|---------------|--------------|-------------------|----------------------|---------------------|
| GET /entities (list) | Response shape `{ data, pagination }` | Items array, pagination fields | 200, 400 (invalid filter), 401 | Filters work correctly |
| POST /entities | Response shape `{ data }` | Required fields present | 201, 400, 409, 422 | Duplicate, business rules |
| GET /entities/{id} | Response shape `{ data }` | Item fields match spec | 200, 404, 401 | — |
| PUT /entities/{id} | Response shape `{ data }` | Updated fields match | 200, 400, 404, 422 | Business rules on update |
| DELETE /entities/{id} | Response shape `{ data: { result } }` | Result fields present | 200, 400, 404 | Invalid state |
| POST /entities/{id}/{verb} | Response shape `{ data }` | Transition fields | 200, 400, 404, 422 | Wrong source state |
| POST /sub/{subId}/remove | Response shape `{ data: { result } }` | Justification required | 200, 400, 404 | Missing justification |
| PUT /sub/reorder | Response shape `{ data: items[] }` | Items reordered | 200, 400, 404, 422 | Invalid order |

Categorías de tests por endpoint:

```
Contract Test     → Valida que el response cumple el schema del spec.
Schema Validation → Valida tipos de datos, campos requeridos, constraints.
Status Code       → Valida que cada código documentado se produce correctamente.
Business Rule     → Valida reglas de negocio (duplicados, estados, justificaciones).
```

### 2. API testing tools

La herramienta primaria para API testing es **httpx + pytest** para tests de API directos, combinado con **Playwright APIRequestContext** para contract tests y validaciones cross-stack.

| Herramienta | Uso |
|-------------|-----|
| httpx + pytest | Async HTTP client para API tests en Python |
| Playwright APIRequestContext | API testing cross-stack con Playwright, contract tests |

### 3. Playwright API testing

```typescript
// tests/api/fixtures/api.fixture.ts
import { test as base, APIRequestContext } from '@playwright/test';

type ApiFixtures = {
  api: APIRequestContext;
  authenticatedApi: APIRequestContext;
};

export const test = base.extend<ApiFixtures>({
  api: async ({ playwright }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_BASE_URL || 'http://localhost:5000',
    });
    await use(apiContext);
    await apiContext.dispose();
  },
  authenticatedApi: async ({ playwright }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_BASE_URL || 'http://localhost:5000',
      extraHTTPHeaders: {
        Authorization: `Bearer ${process.env.TEST_TOKEN || 'test-token'}`,
      },
    });
    await use(apiContext);
    await apiContext.dispose();
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/api/pages/EntityApiPage.ts
import { APIRequestContext } from '@playwright/test';

export class EntityApiPage {
  constructor(private api: APIRequestContext) {}

  async list(params?: { page?: number; pageSize?: number; filter?: string }) {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', params.page.toString());
    if (params?.pageSize) query.set('pageSize', params.pageSize.toString());
    if (params?.filter) query.set('filter', params.filter);
    const response = await this.api.get(`/api/v1/entities?${query.toString()}`);
    return { status: response.status(), body: await response.json() };
  }

  async create(data: Record<string, unknown>) {
    const response = await this.api.post('/api/v1/entities', { data });
    return { status: response.status(), body: await response.json() };
  }

  async getById(id: string) {
    const response = await this.api.get(`/api/v1/entities/${id}`);
    return { status: response.status(), body: await response.json() };
  }

  async update(id: string, data: Record<string, unknown>) {
    const response = await this.api.put(`/api/v1/entities/${id}`, { data });
    return { status: response.status(), body: await response.json() };
  }

  async delete(id: string) {
    const response = await this.api.delete(`/api/v1/entities/${id}`);
    return { status: response.status(), body: await response.json() };
  }

  async executeOperation(id: string, verb: string, data?: Record<string, unknown>) {
    const response = await this.api.post(`/api/v1/entities/${id}/${verb}`, { data });
    return { status: response.status(), body: await response.json() };
  }
}
```

### 4. Test generation workflow

```
OpenAPI Spec
    │
    ▼
Parse endpoints & schemas
    │
    ▼
Classify by type (List, Get, Create, Update, Delete, Operation, Remove, Reorder, Search)
    │
    ▼
Generate test scenarios per endpoint
    │
    ├── Contract tests (schema validation)
    ├── Status code coverage (each documented code)
    ├── Business rule tests (duplicates, states, validations)
    └── Error path tests (validation, not found, conflict, unauthorized)
    │
    ▼
Generate fixtures from spec examples
    │
    ▼
Generate API Page Objects
    │
    ▼
Configure Playwright APIRequestContext
    │
    ▼
Output: tests/api/{feature}.api.spec.ts
```

## Test Scenarios by Endpoint Type (detalle)

| Endpoint Type | Test Case | Type | Expected Status |
|---------------|-----------|------|-----------------|
| GET /entities (list) | List all entities | Happy path | 200 |
| GET /entities (list) | List with filter | Happy path | 200 |
| GET /entities (list) | List with search | Happy path | 200 |
| GET /entities (list) | List with pagination | Happy path | 200 |
| GET /entities (list) | Invalid filter parameter | Validation | 400 |
| POST /entities | Create with valid data | Happy path | 201 |
| POST /entities | Missing required fields | Validation | 400 |
| POST /entities | Duplicate unique field | Business error | 409 |
| POST /entities | Invalid data type | Validation | 400 |
| GET /entities/{id} | Valid ID | Happy path | 200 |
| GET /entities/{id} | Non-existent ID | Not found | 404 |
| PUT /entities/{id} | Valid update | Happy path | 200 |
| PUT /entities/{id} | Invalid data | Validation | 400 |
| PUT /entities/{id} | Non-existent ID | Not found | 404 |
| DELETE /entities/{id} | Valid ID in DRAFT | Happy path | 200 |
| DELETE /entities/{id} | Invalid state | Business error | 400 |
| DELETE /entities/{id} | Non-existent ID | Not found | 404 |
| POST /entities/{id}/{verb} | Valid state transition | Happy path | 200 |
| POST /entities/{id}/{verb} | Wrong source state | Business error | 422 |
| POST /entities/{id}/{verb} | Missing preconditions | Business error | 400 |
| POST /sub/{subId}/remove | Remove with justification | Happy path | 200 |
| POST /sub/{subId}/remove | Missing justification | Validation | 400 |
| PUT /sub/reorder | Valid reorder | Happy path | 200 |
| GET /entities (search) | Search with limit | Happy path | 200 |

## data-testid Convention

| Component | data-testid |
|-----------|-------------|
| List table | `{entity}-table` |
| Create button | `create-{entity}-btn` |
| Edit button | `edit-{entity}-btn` |
| Delete button | `delete-{entity}-btn` |
| Form inputs | `{field}-input` |
| Submit button | `submit-btn` |
| Operation button | `{verb}-{entity}-btn` |
| Justification input | `justification-input` |
| Confirm dialog | `confirm-dialog` |
| Confirm button | `confirm-btn` |
| Pagination next | `next-page-btn` |
| Pagination prev | `prev-page-btn` |
| Filter input | `{field}-filter` |
| Search input | `{entity}-search` |
| Error alert | `error-alert` |

## Preguntas guía

### 1. Sobre derivación desde el spec
- ¿Todos los endpoints del spec tienen tests generados?
- ¿Cada endpoint tiene al menos un contract test y un status code test?
- ¿Los ejemplos del spec se usan como fixtures?

### 2. Sobre contract tests
- ¿Los contract tests validan el schema completo del response?
- ¿Se validan los tipos de datos (integer, string, date, boolean)?
- ¿Se validan los campos requeridos vs opcionales?
- ¿Se validan los enums y constraints?

### 3. Sobre API testing con Playwright
- ¿Se usa APIRequestContext para tests de API sin navegador?
- ¿Los Page Objects de API abstraen los detalles HTTP?
- ¿Los fixtures de Playwright incluyen autenticación?

### 4. Sobre coverage
- ¿Todos los códigos de estado documentados en el spec están cubiertos?
- ¿Los errores de negocio (409, 422) tienen tests?
- ¿Los errores de autenticación (401, 403) tienen tests?

### 5. Sobre mantenimiento
- ¿Los tests se regeneran cuando el spec cambia?
- ¿Los contract tests rompen el build si el backend cambia sin actualizar el spec?
- ¿Los fixtures son derivados de los ejemplos del spec?

## Salidas esperadas de esta skill

### A. Contract tests por módulo
- `tests/api/{feature}.api.spec.ts` — contract tests que validan schema y status codes.
- Al menos 1 contract test por endpoint documentado.
- Al menos 1 test por status code documentado.

### B. API Page Objects
- `tests/api/pages/{Entity}ApiPage.ts` — Page Object de API por entidad.
- Métodos para cada operación (list, create, get, update, delete, operation).
- Configuración de APIRequestContext con autenticación.

### C. Fixtures derivados del spec
- `tests/api/fixtures/{feature}.fixtures.ts` — fixtures con datos de prueba derivados de los ejemplos del spec.
- Datos mínimos para happy path y error paths.

### D. Reporte de coverage
- Mapeo de endpoints → tests generados.
- Mapeo de status codes → tests que los cubren.
- Mapeo de business rules → tests que las validan.
- Gaps de coverage identificados.

## Criterios de calidad

- Todos los endpoints del spec tienen al menos un contract test.
- Todos los status codes documentados en el spec tienen un test que los produce.
- Los contract tests validan el schema completo del response (tipos, campos, constraints).
- Los fixtures se derivan de los ejemplos del spec, no son datos hardcodeados.
- Los Page Objects de API abstraen los detalles HTTP y exponen métodos de negocio.
- Los tests son independientes y pueden ejecutarse en cualquier orden.
- Los contract tests rompen el build si el backend cambia el schema.
- Los `data-testid` están mapeados y documentados entre componentes UI y Page Objects.
- Se usa Playwright APIRequestContext para tests de API sin navegador.
- El reporte de coverage muestra gaps identificados.

## Comportamiento esperado del agente

Cuando el usuario escriba tests de API que validen solo el status code sin validar el response body, el agente debe sugerir agregar contract tests con schema validation.  
Cuando el usuario hardcodee datos de prueba en lugar de usar fixtures derivados del spec, el agente debe proponer fixtures basados en los ejemplos del spec.  
Cuando el usuario testee solo el happy path sin cubrir error paths (400, 404, 409, 422), el agente debe generar los escenarios de error faltantes.  
Cuando el usuario use `fetch` directo en vez de Page Objects de API, el agente debe sugerir crear un `{Entity}ApiPage` que abstraiga los detalles HTTP.

### Antipatrones a evitar

- **Antipatrón 1**: Hardcodear datos de prueba en lugar de usar fixtures del spec. Los fixtures DEBEN derivarse de los ejemplos del OpenAPI spec.
- **Antipatrón 2**: Solo testear happy paths (200, 201) sin cubrir error paths. Cada endpoint DEBE tener tests para todos los status codes documentados.
- **Antipatrón 3**: Validar solo campos sueltos del response en lugar del schema completo. Los contract tests DEBEN validar el schema completo.
- **Antipatrón 4**: Usar `fetch` directo en tests en lugar de Page Objects de API. Los tests DEBEN usar Page Objects que abstraigan los detalles HTTP.
- **Antipatrón 5**: Crear dependencias entre tests (ej: test B depende del resultado de test A). Los tests DEBEN ser independientes.

## Plantilla de referencia

```
docs/api-first/{MODULE}.md          ← Especificación OpenAPI (input)
tests/api/
├── {feature}.api.spec.ts           ← Contract tests + status code coverage
├── pages/
│   ├── {Entity}ApiPage.ts          ← Page Object de API
│   └── BaseApiPage.ts              ← Base page con configuración común
├── fixtures/
│   ├── {feature}.fixtures.ts       ← Fixtures derivados del spec
│   └── api.fixture.ts              ← Playwright APIRequestContext fixture
└── reports/
    └── {feature}-coverage.md       ← Reporte de coverage por endpoint
```

## Ejemplos de uso

### Ejemplo 1: Contract test derivado del spec

```typescript
// tests/api/users.api.spec.ts
import { test, expect } from './fixtures/api.fixture';
import { UsersApiPage } from './pages/UsersApiPage';

test.describe('Users API - Contract Tests', () => {
  let usersApi: UsersApiPage;

  test.beforeEach(async ({ authenticatedApi }) => {
    usersApi = new UsersApiPage(authenticatedApi);
  });

  test('GET /api/v1/users - List response matches spec schema', async () => {
    const { status, body } = await usersApi.list();

    expect(status).toBe(200);
    expect(body).toMatchObject({
      data: {
        items: expect.arrayContaining([
          expect.objectContaining({
            id: expect.any(String),
            name: expect.any(String),
            email: expect.any(String),
            status: expect.stringMatching(/^(active|inactive|suspended)$/),
            createdAt: expect.any(String),
          }),
        ]),
        pagination: expect.objectContaining({
          page: expect.any(Number),
          pageSize: expect.any(Number),
          totalCount: expect.any(Number),
          totalPages: expect.any(Number),
        }),
      },
    });
  });

  test('POST /api/v1/users - Create returns 201 with created user', async () => {
    const { status, body } = await usersApi.create({
      name: 'Test User',
      email: 'test@example.com',
    });

    expect(status).toBe(201);
    expect(body.data).toMatchObject({
      id: expect.any(String),
      name: 'Test User',
      email: 'test@example.com',
      status: 'active',
    });
  });

  test('POST /api/v1/users - Missing required fields returns 400', async () => {
    const { status, body } = await usersApi.create({ email: '' });

    expect(status).toBe(400);
    expect(body).toMatchObject({
      errors: expect.arrayContaining([
        expect.objectContaining({
          field: expect.any(String),
          message: expect.any(String),
        }),
      ]),
    });
  });

  test('POST /api/v1/users - Duplicate email returns 409', async () => {
    await usersApi.create({ name: 'User A', email: 'dup@example.com' });
    const { status } = await usersApi.create({ name: 'User B', email: 'dup@example.com' });

    expect(status).toBe(409);
  });

  test('GET /api/v1/users/{id} - Non-existent ID returns 404', async () => {
    const { status } = await usersApi.getById('non-existent-id');

    expect(status).toBe(404);
  });
});
```

### Ejemplo 2: Playwright API test con Page Object y fixtures derivados del spec

```typescript
// tests/api/orders.api.spec.ts
import { test, expect } from './fixtures/api.fixture';
import { OrdersApiPage } from './pages/OrdersApiPage';
import { orderFixtures } from './fixtures/orders.fixtures';

test.describe('Orders API - Business Rule Tests', () => {
  let ordersApi: OrdersApiPage;

  test.beforeEach(async ({ authenticatedApi }) => {
    ordersApi = new OrdersApiPage(authenticatedApi);
  });

  test('POST /api/v1/orders/{id}/submit - Valid DRAFT order can be submitted', async () => {
    const { body: created } = await ordersApi.create(orderFixtures.draftOrder);
    const orderId = created.data.id;

    const { status, body } = await ordersApi.executeOperation(orderId, 'submit');

    expect(status).toBe(200);
    expect(body.data.status).toBe('SUBMITTED');
  });

  test('POST /api/v1/orders/{id}/submit - Cannot submit already SUBMITTED order', async () => {
    const { body: created } = await ordersApi.create(orderFixtures.submittedOrder);
    const orderId = created.data.id;

    const { status, body } = await ordersApi.executeOperation(orderId, 'submit');

    expect(status).toBe(422);
    expect(body.errorCode).toMatch(/^ORD_\d{3}$/);
  });

  test('POST /api/v1/orders/{id}/cancel - Cancel with valid reason', async () => {
    const { body: created } = await ordersApi.create(orderFixtures.draftOrder);
    const orderId = created.data.id;

    const { status, body } = await ordersApi.executeOperation(orderId, 'cancel', {
      reason: 'Customer requested cancellation',
    });

    expect(status).toBe(200);
    expect(body.data.status).toBe('CANCELLED');
  });

  test('POST /api/v1/orders/{id}/cancel - Cancel without reason returns 400', async () => {
    const { body: created } = await ordersApi.create(orderFixtures.draftOrder);
    const orderId = created.data.id;

    const { status, body } = await ordersApi.executeOperation(orderId, 'cancel');

    expect(status).toBe(400);
    expect(body.errors[0].field).toBe('reason');
  });

  test('DELETE /api/v1/orders/{id} - Delete in DRAFT state succeeds', async () => {
    const { body: created } = await ordersApi.create(orderFixtures.draftOrder);
    const orderId = created.data.id;

    const { status } = await ordersApi.delete(orderId);

    expect(status).toBe(200);
  });

  test('DELETE /api/v1/orders/{id} - Delete in SUBMITTED state returns 400', async () => {
    const { body: created } = await ordersApi.create(orderFixtures.submittedOrder);
    const orderId = created.data.id;

    const { status } = await ordersApi.delete(orderId);

    expect(status).toBe(400);
  });
});
```

## Checklist final de la skill

- [ ] ¿Se parseó el spec OpenAPI y se identificaron todos los endpoints?
- [ ] ¿Cada endpoint tiene al menos un contract test que valida el schema del response?
- [ ] ¿Cada status code documentado tiene un test que lo produce?
- [ ] ¿Los business rule tests cubren duplicados, estados y validaciones?
- [ ] ¿Los fixtures se derivan de los ejemplos del spec?
- [ ] ¿Los Page Objects de API abstraen los detalles HTTP?
- [ ] ¿Se configuró Playwright APIRequestContext con autenticación?
- [ ] ¿Los tests son independientes (pueden ejecutarse en cualquier orden)?
- [ ] ¿Los contract tests rompen el build si el backend cambia el schema?
- [ ] ¿Los `data-testid` están documentados y mapeados a Page Objects?
- [ ] ¿El reporte de coverage muestra endpoints sin tests?
- [ ] ¿Operation tests cubren transiciones de estado válidas e inválidas?
- [ ] ¿Remove tests cubren con y sin justificación?
- [ ] ¿Reorder tests cubren el caso de reordenamiento válido?