---
name: playwright
description: 'E2E testing with Playwright: Page Object Model, selector strategy, file
  structure, tag categories. Trigger: When creating or updating end-to-end tests,
  or configuring Playwright.'
version: 1.1
metadata:
  phase:
  - quality
  layer:
  - testing
  enforcement: mandatory
  depends_on:
  - api-first-testing
  consumed_by:
  - a11y-testing
  - agent-qa
  - real-time
  agent_roles:
  - delivery-agent
  validation_profile: skill-contract
  mcp_usage: governed
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use Playwright MCP if available | ALWAYS | Browser interaction via MCP |
| Use Page Object Model | ALWAYS | Reusability and maintainability |
| Use `data-testid` as primary selector | ALWAYS | Stable under refactoring |
| Avoid CSS selectors that depend on order/position | NEVER | Brittle tests |
| Tag all tests (@smoke/@regression/@critical) | ALWAYS | Selective test runs |
| Test one scenario per test | ALWAYS | Isolated failures |

## Playwright MCP Workflow (MANDATORY when MCP available)
```
1. Start browser via MCP tool
2. Navigate to the page
3. Interact with elements
4. Capture selectors and behavior
5. Generate Page Object Model from real observation
6. Write test based on observed behavior
```

## File Structure
```
tests/
├── e2e/
│   ├── pages/
│   │   └── {Feature}Page.ts       # Page Object Models
│   ├── fixtures/
│   │   └── auth.fixture.ts        # Auth state
│   ├── specs/
│   │   └── {feature}/
│   │       ├── {feature}.create.spec.ts
│   │       ├── {feature}.list.spec.ts
│   │       └── {feature}.edit.spec.ts
│   └── utils/
│       └── test-helpers.ts
├── playwright.config.ts
└── .env.test
```

## Page Object Model Pattern
```typescript
import { Page, Locator } from '@playwright/test';

export class {Feature}Page {
  readonly page: Page;
  readonly createButton: Locator;
  readonly nameInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.createButton = page.getByTestId('btn-create');
    this.nameInput = page.getByTestId('input-name');
    this.submitButton = page.getByTestId('btn-submit');
  }

  async navigate() {
    await this.page.goto('/entities');
  }

  async create(data: { name: string }) {
    await this.createButton.click();
    await this.nameInput.fill(data.name);
    await this.submitButton.click();
  }
}
```

## Selector Priority
| Priority | Selector | Example |
|----------|----------|---------|
| 1st | `data-testid` | `getByTestId('btn-create')` |
| 2nd | ARIA role + name | `getByRole('button', { name: 'Create' })` |
| 3rd | Visible text | `getByText('Create Entity')` |
| 4th | Label | `getByLabel('Name')` |
| AVOID | CSS classes | `.btn-primary:nth-child(2)` |

## Test Tag Categories
| Tag | Purpose | Run frequency |
|-----|---------|---------------|
| `@smoke` | Critical happy path | On every commit |
| `@regression` | Full feature coverage | On every PR |
| `@critical` | Business-critical flows | On every deploy |
| `@slow` | Long-running tests | Nightly |
| `@manual` | Requires manual trigger | On demand |

## Test Structure
```typescript
import { test, expect } from '@playwright/test';
import { {Feature}Page } from '../pages/{Feature}Page';

test.describe('{Feature} @regression', () => {
  test('should create a new {entity} @smoke', async ({ page }) => {
    const featurePage = new {Feature}Page(page);
    await featurePage.navigate();

    await featurePage.create({ name: 'Test Entity' });

    await expect(page.getByText('Created successfully')).toBeVisible();
  });
});
```

## playwright.config.ts
```typescript
import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests/e2e/specs',
  testMatch: '**/*.spec.ts',
  timeout: 30000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [['html', { outputFolder: 'playwright-report' }]],
  use: {
    // React (Vite) app served alongside the Bun dev server
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
```

## Auth Fixture (JWT/OAuth2 — React fetch client)

Genera tokens de prueba directamente via API (sin UI login) para máxima velocidad y fiabilidad en CI.

```typescript
// auth.fixture.ts — store auth state once, reuse across tests
import { test as base, APIRequestContext } from '@playwright/test';

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

async function authenticateViaAPI(request: APIRequestContext): Promise<AuthTokens> {
  // Authenticate via Bun backend OAuth2/JWT endpoint
  const response = await request.post(
    `${process.env.API_URL || 'http://localhost:8000'}/api/auth/login`,
    {
      data: {
        email: process.env.TEST_USER_EMAIL!,
        password: process.env.TEST_USER_PASSWORD!,
      },
    }
  );

  if (!response.ok()) {
    throw new Error(`Auth failed: ${response.status()} ${await response.text()}`);
  }

  return response.json() as Promise<AuthTokens>;
}

export const test = base.extend<{
  authedApi: APIRequestContext;
  authTokens: AuthTokens;
}>({
  authTokens: async ({ playwright }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_URL || 'http://localhost:8000',
    });
    const tokens = await authenticateViaAPI(apiContext);
    await apiContext.dispose();
    await use(tokens);
  },
  authedApi: async ({ playwright, authTokens }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_URL || 'http://localhost:8000',
      extraHTTPHeaders: {
        Authorization: `Bearer ${authTokens.accessToken}`,
        'Content-Type': 'application/json',
      },
    });
    await use(apiContext);
    await apiContext.dispose();
  },
});

export { expect } from '@playwright/test';
```

**Uso en tests E2E** — inyecta cookies/token en el contexto del navegador para que el fetch client de React lo consuma automáticamente:

```typescript
// tests/e2e/fixtures/react-auth.fixture.ts
import { test as base } from '@playwright/test';
import { authenticateViaAPI } from './auth.fixture';

export const test = base.extend({
  page: async ({ playwright, browser }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_URL || 'http://localhost:8000',
    });
    const tokens = await authenticateViaAPI(apiContext);
    await apiContext.dispose();

    // Create browser context with auth cookies/storage
    const context = await browser.newContext({
      storageState: undefined,
    });

    // Inject JWT token into localStorage (the Zustand auth store reads it)
    const page = await context.newPage();
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('access_token', token);
      localStorage.setItem('refresh_token', token);
    }, tokens.accessToken);

    await use(page);
    await context.close();
  },
});
```

## Auth Fixture (JWT/OAuth2 — Angular HttpClient)

Genera tokens de prueba directamente via API usando Angular `HttpClient` patterns (sin UI login) para máxima velocidad y fiabilidad en CI.

```typescript
// auth.fixture.ts — store auth state once, reuse across tests
import { test as base, APIRequestContext } from '@playwright/test';

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

async function authenticateViaAPI(request: APIRequestContext): Promise<AuthTokens> {
  // Authenticate via Bun backend OAuth2/JWT endpoint
  const response = await request.post(
    `${process.env.API_URL || 'http://localhost:8000'}/api/auth/login`,
    {
      data: {
        email: process.env.TEST_USER_EMAIL!,
        password: process.env.TEST_USER_PASSWORD!,
      },
    }
  );

  if (!response.ok()) {
    throw new Error(`Auth failed: ${response.status()} ${await response.text()}`);
  }

  return response.json() as Promise<AuthTokens>;
}

export const test = base.extend<{
  authedApi: APIRequestContext;
  authTokens: AuthTokens;
}>({
  authTokens: async ({ playwright }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_URL || 'http://localhost:8000',
    });
    const tokens = await authenticateViaAPI(apiContext);
    await apiContext.dispose();
    await use(tokens);
  },
  authedApi: async ({ playwright, authTokens }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_URL || 'http://localhost:8000',
      extraHTTPHeaders: {
        Authorization: `Bearer ${authTokens.accessToken}`,
        'Content-Type': 'application/json',
      },
    });
    await use(apiContext);
    await apiContext.dispose();
  },
});

export { expect } from '@playwright/test';
```

**Uso en tests E2E** — inyecta cookies/token en el contexto del navegador para que Angular HttpClient lo consuma automáticamente:

```typescript
// tests/e2e/fixtures/angular-auth.fixture.ts
import { test as base } from '@playwright/test';
import { authenticateViaAPI } from './auth.fixture';

export const test = base.extend({
  page: async ({ playwright, browser }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: process.env.API_URL || 'http://localhost:8000',
    });
    const tokens = await authenticateViaAPI(apiContext);
    await apiContext.dispose();

    // Create browser context with auth cookies/storage
    const context = await browser.newContext({
      storageState: undefined,
    });

    // Inject JWT token into localStorage (Angular AuthService reads it)
    const page = await context.newPage();
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('access_token', token);
      localStorage.setItem('refresh_token', token);
    }, tokens.accessToken);

    await use(page);
    await context.close();
  },
});
```

## Patrones avanzados de Playwright

### 1. API Testing con APIRequestContext

Playwright permite probar APIs directamente con `APIRequestContext`, ideal para validar endpoints del Bun backend antes de las pruebas E2E y compartir estado de autenticación entre tests.

```typescript
// tests/e2e/fixtures/api.fixture.ts
import { test as base, APIRequestContext } from '@playwright/test';

// Bun backend runs on port 8000 by default
const API_BASE_URL = process.env.API_URL || 'http://localhost:8000';

export const test = base.extend<{
  api: APIRequestContext;
  authedApi: APIRequestContext;
}>({
  api: async ({ playwright }, use) => {
    const apiContext = await playwright.request.newContext({
      baseURL: API_BASE_URL,
    });
    await use(apiContext);
    await apiContext.dispose();
  },
  authedApi: async ({ playwright }, use) => {
    // Acquire JWT token via login endpoint (Bun backend)
    const loginResponse = await playwright.request.newContext({
      baseURL: API_BASE_URL,
    }).then(ctx =>
      ctx.post('/api/auth/login', {
        data: {
          email: process.env.TEST_USER_EMAIL!,
          password: process.env.TEST_USER_PASSWORD!,
        },
      })
    );

    const { accessToken } = await loginResponse.json();

    const authedContext = await playwright.request.newContext({
      baseURL: API_BASE_URL,
      extraHTTPHeaders: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });
    await use(authedContext);
    await authedContext.dispose();
  },
});
```

```typescript
// tests/e2e/specs/orders/orders.api.spec.ts
import { test, expect } from '../fixtures/api.fixture';

test.describe('Orders API @regression', () => {
  test('debe crear un pedido y devolver 201', async ({ authedApi }) => {
    const response = await authedApi.post('/api/orders', {
      data: { productId: 1, quantity: 3 },
    });

    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.productId).toBe(1);
    expect(body.quantity).toBe(3);
  });

  test('debe listar pedidos con paginación', async ({ authedApi }) => {
    const response = await authedApi.get('/api/orders?page=1&size=10');

    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.items).toHaveLength(10);
    expect(body.total).toBeGreaterThan(0);
  });

  test('debe rechazar acceso sin autenticación', async ({ api }) => {
    const response = await api.get('/api/orders');

    expect(response.status()).toBe(401);
  });
});
```

**Estado de autenticación compartido** — crear `storageState` via API directamente (sin UI) para reutilizar en E2E:

```typescript
// tests/e2e/setup/auth-setup.ts
import { test as setup } from '@playwright/test';

setup('autenticar via API y guardar estado', async ({ playwright }) => {
  const apiContext = await playwright.request.newContext({
    baseURL: process.env.API_URL || 'http://localhost:8000',
  });

  const response = await apiContext.post('/api/auth/login', {
    data: {
      email: process.env.TEST_USER_EMAIL!,
      password: process.env.TEST_USER_PASSWORD!,
    },
  });

  if (!response.ok()) {
    throw new Error(`Auth setup failed: ${response.status()}`);
  }

  const { accessToken, refreshToken } = await response.json();

  // Save tokens for reuse in E2E tests
  const fs = require('fs');
  const path = require('path');
  const authDir = path.resolve(__dirname, '../.auth');
  fs.mkdirSync(authDir, { recursive: true });
  fs.writeFileSync(
    path.join(authDir, 'user.json'),
    JSON.stringify({ accessToken, refreshToken })
  );

  await apiContext.dispose();
});
```

### 2. Trace Viewer y Debugging

El **Trace Viewer** permite inspeccionar la ejecución completa de un test: acciones, DOM, red y consola.

**Configuración en `playwright.config.ts`:**

```typescript
export default defineConfig({
  use: {
    trace: 'on-first-retry',     // Captura trace solo al reintentar
    // trace: 'on',               // Captura siempre (más lento, útil en debug)
    // trace: 'retain-on-failure', // Conserva trace solo si falla
  },
});
```

**Abrir un trace localmente:**

```bash
npx playwright show-trace trace.zip
```

**Abrir traces en CI** — guardar como artifact:

```yaml
# .github/workflows/e2e.yml
- name: Upload Playwright traces
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-traces
    path: test-results/**/trace.zip
    retention-days: 7
```

**Debug interactivo** con `--debug`:

```bash
npx playwright test --debug                    # Abre Playwright Inspector
npx playwright test -g "should login" --debug  # Solo un test específico
```

**Pause en medio del test:**

```typescript
test('flujo complejo', async ({ page }) => {
  await page.goto('/orders');
  await page.pause(); // Pausa el test, abre Inspector
  await page.getByTestId('btn-create').click();
});
```

**Capturar screenshots al fallar con traza:**

```typescript
test('debe mostrar detalles del pedido', async ({ page }) => {
  await page.goto('/orders/1');

  // Si falla, el trace contendrá el snapshot del DOM completo
  await expect(page.getByTestId('order-status')).toHaveText('Entregado');
});
```

### 3. Ejecución en Paralelo y Sharding

**Workers en `playwright.config.ts`:**

```typescript
export default defineConfig({
  workers: process.env.CI ? 4 : '50%', // En CI: 4 workers, local: 50% de CPUs
});
```

**Sharding para dividir la suite en múltiples máquinas de CI:**

```bash
# Máquina 1: ejecuta el fragmento 1 de 4
npx playwright test --shard=1/4

# Máquina 2: ejecuta el fragmento 2 de 4
npx playwright test --shard=2/4

# Máquina 3: ejecuta el fragmento 3 de 4
npx playwright test --shard=3/4

# Máquina 4: ejecuta el fragmento 4 de 4
npx playwright test --shard=4/4
```

**CI workflow con sharding y merge de reportes:**

```yaml
# .github/workflows/e2e.yml
jobs:
  e2e:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-playwright
      - name: Run E2E shard ${{ matrix.shard }}/4
        run: npx playwright test --shard=${{ matrix.shard }}/4
      - name: Upload blob report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report
          retention-days: 1

  merge-reports:
    needs: e2e
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-report-*
      - name: Merge reports
        run: npx playwright merge-reports --reporter=html all-blob-reports
      - name: Upload HTML report
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report
```

**Selección de tests por tags para paralelismo controlado:**

```bash
npx playwright test --grep @smoke      # Solo smoke tests
npx playwright test --grep @regression # Solo regression tests
```

### 4. Visual Regression Testing (Comparación de Screenshots)

Playwright incluye comparación de screenshots nativa con `toHaveScreenshot()` y `toMatchSnapshot()`.

**Configuración base en `playwright.config.ts`:**

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,    // Tolera 1% de diferencia en píxeles
      threshold: 0.2,              // Sensibilidad de comparación
    },
  },
});
```

**Captura y comparación de pantallas completas:**

```typescript
// tests/e2e/specs/dashboard/dashboard.visual.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard — Visual Regression @regression', () => {
  test('vista de dashboard principal', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page).toHaveScreenshot('dashboard-main.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01,
    });
  });

  test('vista de dashboard con filtros aplicados', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByTestId('btn-filters').click();
    await page.getByTestId('select-status').selectOption('active');

    await expect(page).toHaveScreenshot('dashboard-filtered.png', {
      fullPage: true,
    });
  });
});
```

**Comparación de componentes individuales:**

```typescript
test('badge de estado debería verse correcto', async ({ page }) => {
  await page.goto('/orders/1');
  const badge = page.getByTestId('order-status-badge');

  await expect(badge).toHaveScreenshot('status-badge.png');
});
```

**Flujo de trabajo para actualizar snapshots:**

```bash
# Primera ejecución: genera los snapshots base
npx playwright test --update-snapshots

# Cuando cambia el diseño intencionalmente, regenera los snapshots
npx playwright test --update-snapshots dashboard.visual.spec.ts

# Revisa los cambios con git diff
git diff --stat tests/e2e/specs/dashboard/
```

**Estructura de snapshots:**

```
tests/e2e/specs/dashboard/
├── dashboard.visual.spec.ts
└── dashboard.visual.spec.ts-snapshots/
    ├── dashboard-main.png
    ├── dashboard-filtered.png
    └── status-badge.png
```

### 5. Integración Docker para E2E

Usa la skill **docker-local** para levantar servicios dependientes (API Bun, base de datos) antes de ejecutar los tests E2E.

**`docker-compose.e2e.yml`** — stack Bun + PostgreSQL para tests:

```yaml
services:
  api:
    build:
      context: ../../
      dockerfile: Dockerfile
      target: development
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/e2e_test
      - JWT_SECRET=test-secret-key-do-not-use-in-production
      - NODE_ENV=test
      - PORT=8000
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 5s
      timeout: 5s
      retries: 5

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: e2e_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  frontend:
    build:
      context: ../../client
      dockerfile: Dockerfile
      target: development
    environment:
      - API_URL=http://api:8000
    ports:
      - "4200:4200"
    depends_on:
      api:
        condition: service_healthy
```

**Script de inicio para E2E:**

```typescript
// tests/e2e/utils/e2e-setup.ts
import { execSync } from 'child_process';

// Bun backend runs on port 8000, React (Vite) on 5173
const API_URL = process.env.API_URL || 'http://localhost:8000';

export async function startE2EStack(): Promise<void> {
  console.log('Levantando stack Docker para E2E (Bun + PostgreSQL)...');
  execSync('docker compose -f docker-compose.e2e.yml up -d --wait', {
    stdio: 'inherit',
  });

  // Esperar a que la API Bun esté lista
  const maxRetries = 30;
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (response.ok) {
        console.log('Stack E2E listo (Bun + PostgreSQL)');
        return;
      }
    } catch {
      await new Promise((r) => setTimeout(r, 1000));
    }
  }
  throw new Error('Stack E2E no respondió en 30 segundos');
}

export async function stopE2EStack(): Promise<void> {
  console.log('Deteniendo stack Docker...');
  execSync('docker compose -f docker-compose.e2e.yml down -v', {
    stdio: 'inherit',
  });
}
```

**Configuración global en `playwright.config.ts`:**

```typescript
import { defineConfig } from '@playwright/test';
import { startE2EStack, stopE2EStack } from './tests/e2e/utils/e2e-setup';

export default defineConfig({
  use: {
    // React (Vite) app served alongside the Bun dev server on port 5173
    baseURL: 'http://localhost:5173',
  },
});
```

**Setup/teardown con proyecto global:**

```typescript
// tests/e2e/setup/global-setup.ts
import { startE2EStack } from '../utils/e2e-setup';

export default async () => {
  await startE2EStack();
};
```

```typescript
// tests/e2e/setup/global-teardown.ts
import { stopE2EStack } from '../utils/e2e-setup';

export default async () => {
  await stopE2EStack();
};
```

```typescript
// En playwright.config.ts, agregar el proyecto de setup:
import { defineConfig } from '@playwright/test';

export default defineConfig({
  globalSetup: './tests/e2e/setup/global-setup.ts',
  globalTeardown: './tests/e2e/setup/global-teardown.ts',
  projects: [
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
  ],
});
```

**Ejecutar E2E con Docker:**

```bash
# Levantar stack, ejecutar tests y detener
docker compose -f docker-compose.e2e.yml up -d --wait
npx playwright test
docker compose -f docker-compose.e2e.yml down -v

# O usar el script npm
npm run test:e2e:docker
```
