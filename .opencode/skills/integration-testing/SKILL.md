---
name: integration-testing
description: "Integration testing patterns with real dependencies. Covers TestContainers for Python/PostgreSQL + pgvector, Angular TestBed + HttpClientTestingModule, Bun backend con Vitest + testcontainers, contract tests between services, test isolation by tenant, setup/teardown patterns, y parallel execution strategies. Trigger: When writing integration tests, setting up test databases, or testing service boundaries."
version: 1.0
metadata:
  phase:
  - quality
  layer:
  - testing
  enforcement: mandatory
  depends_on:
  - unit-testing
  - data-access
  - angular-services
  consumed_by:
  - framework-qa-validation
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: skill-contract
  mcp_usage: none
---

# integration-testing

## Propósito

Esta skill define cómo escribir y organizar tests de integración que verifican que múltiples unidades trabajan juntas correctamente, usando dependencias reales (base de datos, API, middleware) en vez de mocks.  
Su función es asegurar que los handlers, repositorios, middleware y endpoints se comunican correctamente entre sí, detectando errores que los tests unitarios no pueden encontrar.

Esta skill complementa `unit-testing` (tests aislados) y `playwright` (tests E2E). Mientras los unit tests validan cada unidad en aislamiento y los E2E tests validan el flujo completo, los integration tests validan las integraciones entre unidades.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo se levanta una base de datos de prueba para integration tests?
2. ¿Cómo se testea un endpoint completo con BD real?
3. ¿Cómo se testean contracts entre servicios?
4. ¿Cómo se aislan los tests por tenant?
5. ¿Cómo se maneja setup y teardown de datos de prueba?

## Relación con otras skills

- `unit-testing` testea unidades aisladas; esta skill testea integraciones.
- `data-access` define los handlers que esta skill testea con BD real.
- `database-seeding` provee los fixtures de datos para los tests.
- `database-migrations` crea el esquema de BD para los tests.
- `authentication` provee tokens de prueba para endpoints protegidos.
- `backend-api` define los endpoints que esta skill testea end-to-end.
- `angular-services` define los servicios Angular (RxJS/TanStack Query) que esta skill testea con `HttpClientTestingModule`.
- `angular` define los componentes standalone que esta skill testea con `TestBed`.
- `framework-qa-validation` define la estrategia de testing de la que esta skill forma la capa intermedia.
- Para operaciones vectoriales (similarity search, embeddings), esta skill testea la integración con la extensión `pgvector` sobre PostgreSQL 16.

## Qué debe hacer el agente cuando esta skill está activa

1. Configurar TestContainers para levantar una BD PostgreSQL (+ pgvector) de prueba por test suite.
2. Aplicar migraciones automáticamente antes de los tests.
3. Ejecutar seed de datos de prueba antes de cada test o suite.
4. Escribir integration tests que verifican el flujo completo (_request_ → handler → repository → BD → response).
5. Testear contracts entre servicios (request/response shapes).
6. Testear middleware (authentication, error handling, validation).
7. Aislar tests por tenant en multi-tenancy.
8. Configurar parallel execution strategy.
9. Para Angular: usar `TestBed` con `provideHttpClient()` + `provideHttpClientTesting()` y servicios reales (no mocks de lógica).
10. Para Bun backend: usar Vitest + `testcontainers` para levantar dependencias reales (PostgreSQL, Redis).
11. Para pgvector: testear similarity search y operaciones de embeddings contra BD real con vectores de prueba deterministas.

## Entradas esperadas

Esta skill asume que ya existe:
- tests unitarios pasando (`unit-testing`);
- handlers y repositorios implementados (`data-access`);
- migraciones de BD (`database-migrations`);
- datos de seed (`database-seeding`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- TestContainers para BD de prueba (PostgreSQL + pgvector);
- Integration tests de servicios Angular con `HttpClientTestingModule` y `TestBed`;
- Integration tests de backend Bun con Vitest + testcontainers;
- Tests de operaciones pgvector (similarity search, embeddings, KNN);
- Contract tests entre servicios;
- Test isolation por tenant;
- Setup/teardown de datos;
- Parallel execution strategy;
- Tests de middleware;
- Tests de endpoints completos.

La fase no incluye todavía:
- tests unitarios en aislamiento (`unit-testing`);
- tests E2E en navegador (`playwright`);
- tests de carga o stress;
- tests de seguridad (penetration testing).

## Principios que siempre debe respetar

- Los integration tests DEBEN usar dependencias reales (BD, API), no mocks.
- Los integration tests DEBEN ser independientes: cada test debe poder ejecutarse solo.
- Los datos de prueba DEBEN ser sembrados antes de cada test o suite, no depender de datos existentes.
- Los tests DEBEN hacer cleanup de sus datos después de ejecutarse.
- Los tests POR TENANT no deben verse entre sí (aislamiento total).
- Los contract tests DEBEN verificar la forma del request/response, no la lógica interna.
- Los integration tests DEBEN ejecutarse en un entorno aislado (no producción, no staging compartido).
- Los integration tests PUEDEN ser más lentos que los unit tests (esperar < 1s por test).

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la estrategia de TestContainers;
- el setup/teardown de datos;
- la estrategia de isolation por tenant;
- la estrategia de parallel execution;
- los contracts a validar.

Esta skill delega:
- los tests unitarios a `unit-testing`;
- los tests E2E a `playwright`;
- la estrategia general de QA a `framework-qa-validation`;
- los datos de seed a `database-seeding`.

## Qué debe definir el diseño

### 1. TestContainers para BD de prueba (Python + PostgreSQL + pgvector)

```python
# tests/integration/conftest.py
import pytest
import asyncpg
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_container():
    # Imagen con pgvector habilitado (ankane/pgvector o pgvector/pgvector)
    postgres = PostgresContainer("pgvector/pgvector:pg16")
    postgres.start()
    yield postgres
    postgres.stop()

@pytest.fixture(scope="session")
async def db_pool(postgres_container):
    pool = await asyncpg.create_pool(
        host=postgres_container.get_container_host_ip(),
        port=postgres_container.get_exposed_port(5432),
        user=postgres_container.POSTGRES_USER,
        password=postgres_container.POSTGRES_PASSWORD,
        database=postgres_container.POSTGRES_DB,
    )
    # Apply migrations + habilitar extensión pgvector
    async with pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        await conn.execute("CREATE TABLE IF NOT EXISTS ...")
    yield pool
    await pool.close()

@pytest.fixture
async def clean_db(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM orders; DELETE FROM users;")
    yield
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM orders; DELETE FROM users;")
```

### 2. Integration test de endpoint (Python + httpx + pytest)

```python
# tests/integration/test_create_user.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_user_valid_request_returns_created(clean_db, client):
    # Arrange
    payload = {"name": "John Doe", "email": "john@test.com"}

    # Act
    response = await client.post("/api/v1/users", json=payload)

    # Assert
    assert response.status_code == 201
    result = response.json()
    assert result["name"] == "John Doe"
    assert result["email"] == "john@test.com"

@pytest.mark.asyncio
async def test_create_user_duplicate_email_returns_conflict(clean_db, client):
    # Arrange
    payload = {"name": "John Doe", "email": "john@test.com"}
    await client.post("/api/v1/users", json=payload)

    # Act
    response = await client.post("/api/v1/users", json=payload)

    # Assert
    assert response.status_code == 409
```

### 3. Integration test de servicio Angular (TestBed + HttpClientTestingModule)

```typescript
// src/app/features/users/services/users.service.integration.spec.ts
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { firstValueFrom } from 'rxjs';
import { UsersService } from './users.service';

describe('UsersService integration', () => {
  let service: UsersService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        UsersService,
        provideHttpClient(),
        provideHttpClientTesting(),
        // Providers reales (no mocks de lógica de negocio):
        // { provide: API_BASE_URL, useValue: '/api/v1' },
      ],
    });
    service = TestBed.inject(UsersService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // Verifica que no queden requests pendientes
    httpMock.verify();
  });

  it('list_WhenEndpointReturnsUsers_EmitsUsersFromAPI', async () => {
    // Arrange
    const expected = [
      { id: 1, name: 'John Doe', email: 'john@test.com' },
      { id: 2, name: 'Jane Doe', email: 'jane@test.com' },
    ];

    // Act
    const promise = firstValueFrom(service.list());
    const req = httpMock.expectOne('/api/v1/users');
    req.flush(expected);
    const result = await promise;

    // Assert
    expect(result).toHaveLength(2);
    expect(result[0].name).toBe('John Doe');
  });

  it('list_WhenEndpointReturnsError_PropagatesError', async () => {
    // Act
    const promise = firstValueFrom(service.list()).catch((e) => e);
    const req = httpMock.expectOne('/api/v1/users');
    req.flush({ message: 'Internal error' }, { status: 500, statusText: 'Server Error' });
    const error = await promise;

    // Assert
    expect(error.status).toBe(500);
  });
});
```

> **Patrón Angular con signals**: si el servicio usa `toSignal()` para exponer estado reactivo, testear el signal dentro de `TestBed.runInInjectionContext(() => { ... })` y leer su valor con `service.users()` después de resolver el mock HTTP.

### 4. Integration test de componente Angular con providers reales

```typescript
// src/app/features/users/components/user-list/user-list.component.integration.spec.ts
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { UserListComponent } from './user-list.component';
import { UsersService } from '../../services/users.service';

describe('UserListComponent integration', () => {
  let fixture: ComponentFixture<UserListComponent>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [
        UsersService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(UserListComponent);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('ngOnInit_FetchesUsers_DisplaysThemInTemplate', () => {
    // Arrange
    const users = [{ id: 1, name: 'John Doe', email: 'john@test.com' }];

    // Act
    fixture.detectChanges(); // dispara ngOnInit
    const req = httpMock.expectOne('/api/v1/users');
    req.flush(users);
    fixture.detectChanges(); // propaga el cambio

    // Assert
    const listItems = fixture.nativeElement.querySelectorAll('li');
    expect(listItems.length).toBe(1);
    expect(listItems[0].textContent).toContain('John Doe');
  });
});
```

### 5. Integration test de backend Bun (Vitest + testcontainers)

```typescript
// tests/integration/users.repository.integration.test.ts
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import { PostgreSqlContainer } from '@testcontainers/postgresql';
import { Pool } from 'pg';
import { UsersRepository } from '@/features/users/users.repository';

let container: StartedPostgreSqlContainer;
let pool: Pool;
let repo: UsersRepository;

beforeAll(async () => {
  // Imagen con pgvector para soporte de embeddings
  container = await new PostgreSqlContainer('pgvector/pgvector:pg16').start();
  pool = new Pool({
    host: container.getHost(),
    port: container.getPort(),
    user: container.getUsername(),
    password: container.getPassword(),
    database: container.getDatabase(),
  });
  // Apply migrations
  await pool.query('CREATE EXTENSION IF NOT EXISTS vector;');
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL
    );
  `);
  repo = new UsersRepository(pool);
});

afterAll(async () => {
  await pool.end();
  await container.stop();
});

beforeEach(async () => {
  await pool.query('DELETE FROM users;');
});

describe('UsersRepository integration', () => {
  it('create_ValidUser_PersistsAndReturnsUser', async () => {
    // Act
    const user = await repo.create({ name: 'John Doe', email: 'john@test.com' });

    // Assert
    expect(user.id).toBeDefined();
    expect(user.name).toBe('John Doe');

    const found = await repo.findById(user.id);
    expect(found?.email).toBe('john@test.com');
  });

  it('create_DuplicateEmail_ThrowsUniqueViolation', async () => {
    // Arrange
    await repo.create({ name: 'John Doe', email: 'john@test.com' });

    // Act + Assert
    await expect(
      repo.create({ name: 'Other', email: 'john@test.com' })
    ).rejects.toThrow(/unique/i);
  });
});
```

> **Configuración Vitest**: usar `vitest.config.ts` con `pool: 'forks'` para aislar contenedores entre workers. Timeout extendido: `testTimeout: 30000`.

### 6. Tests de operaciones pgvector (similarity search, embeddings)

Los tests de operaciones vectoriales DEBEN ejecutarse contra una BD real con la extensión `vector` habilitada, ya que las operaciones de distancia (`<=>`, `<->`, `<#>`) y KNN no pueden mockearse de forma significativa.

```python
# tests/integration/test_pgvector_similarity.py
import pytest
import numpy as np

@pytest.fixture
async def seed_documents(db_pool):
    """Inserta documentos con embeddings deterministas para tests reproducibles."""
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM documents;")
        # Vectores ortogonales y colineales para casos predecibles
        await conn.execute(
            """
            INSERT INTO documents (id, content, embedding) VALUES
              (1, 'gato',      '[1, 0, 0]'),
              (2, 'felino',    '[0.99, 0.1, 0]'),  -- cercano a 'gato'
              (3, 'perro',     '[0, 1, 0]'),
              (4, 'automovil', '[0, 0, 1]');
            """
        )
    yield

@pytest.mark.asyncio
async def test_similarity_search_returns_nearest_neighbors(db_pool, seed_documents):
    # Arrange - query vector cercano a 'gato'
    query_embedding = "[1, 0, 0]"
    k = 2

    # Act - cosine distance (<=>)
    async with db_pool.acquire() as conn:
        results = await conn.fetch(
            """
            SELECT id, content, embedding <=> $1::vector AS distance
            FROM documents
            ORDER BY distance
            LIMIT $2;
            """,
            query_embedding, k
        )

    # Assert - 'gato' (distance 0) es el más cercano, 'felino' el segundo
    assert len(results) == 2
    assert results[0]["content"] == "gato"
    assert results[0]["distance"] == pytest.approx(0.0, abs=1e-6)
    assert results[1]["content"] == "felino"
    assert results[1]["distance"] < 0.2  # cercano pero no idéntico

@pytest.mark.asyncio
async def test_knn_search_respects_k_limit(db_pool, seed_documents):
    # Act
    async with db_pool.acquire() as conn:
        results = await conn.fetch(
            """
            SELECT id FROM documents
            ORDER BY embedding <=> '[1, 0, 0]'::vector
            LIMIT 3;
            """
        )

    # Assert
    assert len(results) == 3

@pytest.mark.asyncio
async def test_embedding_dimension_mismatch_raises(db_pool):
    # Act + Assert - insertar vector de dimensión incorrecta debe fallar
    async with db_pool.acquire() as conn:
        with pytest.raises(Exception, match="dimension"):
            await conn.execute(
                "INSERT INTO documents (content, embedding) VALUES ('x', '[1, 0]');"
            )
```

```typescript
// tests/integration/vector-search.integration.test.ts (Bun + Vitest)
import { describe, it, expect, beforeAll } from 'vitest';

describe('pgvector similarity search integration', () => {
  it('search_NearQueryVector_ReturnsRankedResults', async () => {
    // Act - cosine distance
    const results = await pool.query(
      `SELECT id, content, embedding <=> $1::vector AS distance
       FROM documents ORDER BY distance LIMIT 2;`,
      ['[1, 0, 0]']
    );

    // Assert
    expect(results.rows).toHaveLength(2);
    expect(results.rows[0].content).toBe('gato');
    expect(parseFloat(results.rows[0].distance)).toBeCloseTo(0, 6);
  });

  it('search_UsesHnswIndex_CompletesUnderLatencyBudget', async () => {
    // Act
    const start = performance.now();
    await pool.query(
      `SELECT id FROM documents ORDER BY embedding <=> '[1,0,0]'::vector LIMIT 10;`
    );
    const elapsed = performance.now() - start;

    // Assert - HNSW index debe mantener latencia baja
    expect(elapsed).toBeLessThan(50); // ms
  });
});
```

> **Notas clave para pgvector**:
> - Usar **vectores deterministas** (ortogonales y colineales) para que los resultados sean predecibles y reproducibles.
> - Testear los tres operadores de distancia: coseno (`<=>`), L2 (`<->`), inner product (`<#>`).
> - Verificar que el **HNSW/IVFFlat index** está siendo usado (vía `EXPLAIN`) para garantizar latencia.
> - Validar que embeddings de **dimensión incorrecta** son rechazados por la constraint de BD.
> - El cleanup debe incluir `DELETE` de documentos de test para no contaminar el índice.

### 7. Contract tests entre servicios

```typescript
// tests/contracts/userApi.contract.test.ts (Bun + Vitest + msw + zod)
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { z } from 'zod';
import { userResponseSchema } from '@/features/users/types';

const server = setupServer();

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('User API contract', () => {
  it('GET /api/v1/users_ReturnsArrayOfWorkingUserSchema', async () => {
    // Arrange
    server.use(
      http.get('/api/v1/users', () =>
        HttpResponse.json({
          data: [{ id: 1, name: 'Test', email: 'test@test.com' }],
          totalCount: 1,
        })
      )
    );

    // Act
    const response = await fetch('/api/v1/users');
    const json = await response.json();

    // Assert
    const result = userResponseSchema.safeParse(json);
    expect(result.success).toBe(true);
  });

  it('POST /api/v1/users_ValidatesRequiredFields_ReturnsValidationError', async () => {
    // Arrange
    server.use(
      http.post('/api/v1/users', () =>
        HttpResponse.json(
          { errors: [{ field: 'name', message: 'Name is required' }] },
          { status: 400 }
        )
      )
    );

    // Act
    const response = await fetch('/api/v1/users', {
      method: 'POST',
      body: JSON.stringify({ email: 'test@test.com' }), // missing name
    });

    // Assert
    expect(response.status).toBe(400);
    const json = await response.json();
    expect(json.errors).toBeDefined();
    expect(json.errors[0].field).toBe('name');
  });
});
```

> **Contract tests Angular**: en el frontend Angular, los contract tests validan que los tipos generados desde el OpenAPI spec (`api-first-frontend`) coinciden con las respuestas reales del backend. Usar `HttpTestingController` para interceptar y validar el schema con `zod` dentro del `TestBed`.

### 8. Test isolation por tenant

```python
# tests/integration/test_tenant_isolation.py
@pytest.mark.asyncio
async def test_create_user_in_tenant_a_not_visible_in_tenant_b(client):
    # Arrange - Tenant A
    headers_a = {"X-Tenant-Id": "tenant-a", "Authorization": "Bearer token-a"}
    payload = {"name": "User A", "email": "a@test.com"}
    await client.post("/api/v1/users", json=payload, headers=headers_a)

    # Act - Tenant B queries
    headers_b = {"X-Tenant-Id": "tenant-b", "Authorization": "Bearer token-b"}
    response = await client.get("/api/v1/users", headers=headers_b)

    # Assert - Tenant B doesn't see Tenant A's data
    users = response.json()["items"]
    assert not any(u["email"] == "a@test.com" for u in users)
```

### 9. Parallel execution strategy

```ini
# pytest.ini (Python)
[pytest]
addopts = -n auto --dist loadscope
timeout = 30
```

```typescript
// vitest.config.ts (Bun)
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    pool: 'forks',
    poolOptions: {
      forks: { singleFork: false, maxForks: 4 },
    },
    testTimeout: 30000,
    include: ['tests/integration/**/*.integration.test.ts'],
  },
});
```

## Preguntas guía

### 1. Sobre infraestructura de tests
- ¿Se usa TestContainers para BD o una BD compartida de test?
- ¿Las migraciones se aplican automáticamente antes de los tests?
- ¿Los datos de seed se limpian después de cada test suite?
- ¿La imagen de PostgreSQL incluye la extensión `pgvector` cuando se testean operaciones vectoriales?

### 2. Sobre contracts
- ¿Se validan los schemas de request/response con Zod/o schemas similares?
- ¿Los contract tests corren en el pipeline de CI?
- ¿Se valida que el backend y frontend usan el mismo contrato?
- ¿Los tipos Angular generados desde OpenAPI coinciden con las respuestas reales del backend?

### 3. Sobre isolation
- ¿Los tests por tenant son completamente aislados?
- ¿Se usa una BD por test suite o una BD por test?
- ¿Los tests paralelos pueden interferir entre sí?

### 4. Sobre setup/teardown
- ¿Los datos de prueba se seedean antes de cada test o antes de cada suite?
- ¿El cleanup es exacto (DELETE de lo insertado) o truncado completo?
- ¿Los tests son idempotentes (pueden ejecutarse más de una vez)?

### 5. Sobre pgvector
- ¿Los tests de similarity search usan vectores deterministas (ortogonales/colineales)?
- ¿Se verifican los tres operadores de distancia (`<=>`, `<->`, `<#>`)?
- ¿Se valida que el índice HNSW/IVFFlat está siendo usado (vía `EXPLAIN`)?
- ¿Se valida el rechazo de embeddings con dimensión incorrecta?

## Salidas esperadas de esta skill

### A. Infraestructura de tests
- `conftest.py` configurado con TestContainers PostgreSQL + pgvector.
- `vitest.config.ts` configurado con pool forks y timeouts extendidos (Bun).
- Scripts de seed para integration tests.

### B. Integration tests por feature
- Al menos 1 test por endpoint (happy path + error path).
- Al menos 1 contract test por API.
- Al menos 1 test de isolation por tenant (si aplica).
- Al menos 1 test de servicio Angular con `HttpClientTestingModule` por feature.
- Al menos 1 test de repository Bun con BD real por feature.
- Al menos 1 test de operaciones pgvector (similarity search) si la feature usa embeddings.

### C. Parallel execution strategy
- Configuración de pytest-xdist para parallel execution (Python).
- Configuración de Vitest con `pool: 'forks'` (Bun).
- Límite de workers.

### D. Consumidores de esta skill
- `unit-testing` provee la base de tests rápidos;
- `framework-qa-validation` define qué integration tests son obligatorios;
- `playwright` complementa con E2E tests;
- `database-seeding` provee los fixtures de datos.

## Criterios de calidad

- Los integration tests usan dependencias reales (BD, API), no mocks.
- Los tests son independientes y pueden ejecutarse en cualquier orden.
- Los datos de prueba se seedean antes de cada test o suite.
- El cleanup se ejecuta después de cada test o suite.
- Los tests por tenant están completamente aislados.
- Los contract tests validan el schema del request/response.
- Los tests corren en CI con timeouts extendidos.
- La BD de prueba se levanta con TestContainers o equivalente.
- Los tests son idempotentes (pueden ejecutarse más de una vez).
- Los tests de servicios Angular usan `HttpClientTestingModule` con `HttpTestingController` y verifican requests pendientes (`httpMock.verify()`).
- Los tests de backend Bun usan Vitest + testcontainers con BD real (no mocks de repositorio).
- Los tests de pgvector usan vectores deterministas y validan los operadores de distancia contra BD real.

## Comportamiento esperado del agente

Cuando el usuario escriba un integration test que use mocks, el agente debe explicar que los integration tests deben usar dependencias reales y proponer TestContainers.  
Cuando el usuario tenga tests que dependan de datos existentes en la BD, el agente debe proponer seed antes del test y cleanup después.  
Cuando el usuario tenga tests flaky por race conditions, el agente debe sugerir isolation por tenant o serialización.  
Cuando el usuario no valide el contract de la API, el agente debe proponer contract tests con schema validation.

## Checklist final de la skill

- ¿Se configuró TestContainers o equivalente para BD de prueba?
- ¿Se configuró httpx + pytest para API tests (Python)?
- ¿Se configuró Vitest + testcontainers para integration tests (Bun)?
- ¿Se configuró `TestBed` + `provideHttpClientTesting()` para servicios Angular?
- ¿Las migraciones se aplican automáticamente antes de los tests?
- ¿Los datos de seed se ejecutan antes de cada test o suite?
- ¿El cleanup se ejecuta después de cada test o suite?
- ¿Los contract tests validan request/response schemas?
- ¿Los tests por tenant están completamente aislados?
- ¿Se configuró parallel execution con límites?
- ¿Los timeouts están extendidos para integration tests?
- ¿Los tests son idempotentes?
- ¿Los tests de pgvector usan vectores deterministas y validan los operadores de distancia?
- ¿Se valida que el índice HNSW/IVFFlat está siendo usado en queries de similarity search?