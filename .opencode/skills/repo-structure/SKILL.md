---
name: repo-structure
description: 'Repository naming conventions, project type detection, and repository
  codification. Trigger: When creating a new repository or naming a project.'
version: 1.1
metadata:
  phase:
  - inception
  layer:
  - backend
  - frontend
  enforcement: recommended
  depends_on:
  consumed_by:
  - project-architecture
  - project-bootstrap
  - readme
  agent_roles:
  - orchestrator-agent
  - delivery-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Ask user to confirm repo name before creating | ALWAYS | Irreversible naming |
| Infer project type from user description | ALWAYS | Correct suffix |
| Use lowercase + hyphens for repo names | ALWAYS | URL-friendly |
| Prefix with project/system code | ALWAYS | Namespace isolation |
| Mix suffixes (e.g., both -api and -web in one repo) | NEVER | Single responsibility |

## Project Type Suffixes

| Type | Suffix | When to use |
|------|--------|-------------|
| Single project | *(none)* | One codebase for entire system |
| API / Backend | `-api` | REST API, GraphQL, gRPC services |
| Frontend / Web | `-web` | SPA, SSR web apps |
| Mobile | `-mobile` | iOS / Android / React Native |
| Gateway | `-gateway` | API Gateway, BFF |
| Worker / Consumer | `-worker` | Background jobs, message consumers |
| Library / Shared | `-libs` | Shared packages, SDKs |
| Infrastructure | `-infra` | Terraform |
| Tooling | `-tools` | Scripts, CLIs |
| Documentation | `-docs` | Documentation site |

## Naming Convention
```
{PROJECT-CODE}-{descriptor}-{suffix}
```

| Field | Convention | Example |
|-------|------------|---------|
| PROJECT-CODE | Uppercase, 2–5 chars | `ERP`, `CRM`, `BILLING` |
| descriptor | Optional, lowercase-hyphen | `orders`, `user-management` |
| suffix | From table above | `-api`, `-web` |

**Examples:**
- `erp-api` — ERP single API
- `crm-orders-api` — CRM Orders service
- `billing-web` — Billing frontend
- `platform-gateway` — Platform API Gateway
- `auth-libs` — Auth shared libraries

## Monorepo Naming
When multiple services live in one repo:
```
{PROJECT-CODE}/
├── services/
│   ├── orders-api/
│   └── billing-api/
├── apps/
│   └── admin-web/
└── packages/
    └── shared-libs/
```

## Confirmation Required
Before creating a repository structure, confirm with user:
```
Repository name: {proposed-name}
Project type: {inferred-type}
Is this correct? [yes/no]
```

## Multi-Repo vs Monorepo

| Criteria | Multi-Repo | Monorepo |
|----------|------------|----------|
| Team size | Larger, independent | Smaller, coordinated |
| Deployment | Independent | Coordinated |
| Tooling | Standard git | Requires monorepo tools (nx, turborepo) |
| Code sharing | Via package registry | Via direct imports |

## Estructura de repos por stack

Cada stack tecnológico tiene convenciones de estructura de directorios bien definidas. A continuación se presentan las estructuras canónicas.

### Python monorepo

```
{project-code}/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── lint.yml
│       └── security-scan.yml
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   └── {app}_api/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── core/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── config.py
│   │   │       │   ├── dependencies.py
│   │   │       │   ├── exceptions.py
│   │   │       │   └── logging.py
│   │   │       ├── api/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── v1/
│   │   │       │   │   ├── __init__.py
│   │   │       │   │   ├── orders.py
│   │   │       │   │   ├── products.py
│   │   │       │   │   └── health.py
│   │   │       │   └── deps.py
│   │   │       ├── models/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── order.py
│   │   │       │   ├── product.py
│   │   │       │   └── enums.py
│   │   │       ├── schemas/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── order.py
│   │   │       │   ├── product.py
│   │   │       │   └── common.py
│   │   │       ├── services/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── order_service.py
│   │   │       │   └── product_service.py
│   │   │       ├── repositories/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── order_repository.py
│   │   │       │   └── product_repository.py
│   │   │       └── middleware/
│   │   │           ├── __init__.py
│   │   │           ├── auth.py
│   │   │           └── request_id.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_orders.py
│   │   │   └── test_products.py
│   │   ├── alembic/
│   │   │   ├── alembic.ini
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   │       ├── 0001_initial_schema.py
│   │   │       └── 0002_add_order_status.py
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── README.md
│   ├── worker/
│   │   ├── src/
│   │   │   └── {app}_worker/
│   │   │       ├── __init__.py
│   │   │       ├── main.py
│   │   │       ├── tasks/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── order_tasks.py
│   │   │       │   └── notification_tasks.py
│   │   │       └── handlers/
│   │   │           ├── __init__.py
│   │   │           ├── order_handler.py
│   │   │           └── email_handler.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_tasks.py
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   └── admin/
│       ├── src/
│       │   └── {app}_admin/
│       │       ├── __init__.py
│       │       ├── main.py
│       │       ├── models.py
│       │       ├── views.py
│       │       └── templates/
│       ├── pyproject.toml
│       └── Dockerfile
├── libs/
│   ├── shared/
│   │   ├── src/
│   │   │   └── {app}_shared/
│   │   │       ├── __init__.py
│   │   │       ├── response.py
│   │   │       ├── pagination.py
│   │   │       ├── exceptions.py
│   │   │       ├── base_model.py
│   │   │       └── utils.py
│   │   ├── tests/
│   │   │   └── test_utils.py
│   │   └── pyproject.toml
│   ├── auth/
│   │   ├── src/
│   │   │   └── {app}_auth/
│   │   │       ├── __init__.py
│   │   │       ├── jwt.py
│   │   │       ├── permissions.py
│   │   │       └── dependencies.py
│   │   └── pyproject.toml
│   └── storage/
│       ├── src/
│       │   └── {app}_storage/
│       │       ├── __init__.py
│       │       ├── s3_client.py
│       │       └── local_storage.py
│       └── pyproject.toml
├── packages/
│   ├── sdk-client/
│   │   ├── src/
│   │   │   └── {app}_sdk/
│   │   │       ├── __init__.py
│   │   │       ├── client.py
│   │   │       ├── models.py
│   │   │       └── errors.py
│   │   └── pyproject.toml
│   └── cli-tools/
│       ├── src/
│       │   └── {app}_cli/
│       │       ├── __init__.py
│       │       └── main.py
│       └── pyproject.toml
├── docs/
│   ├── index.md
│   └── api/
│       └── openapi.json
├── scripts/
│   ├── run-dev.sh
│   └── migrate.sh
├── docker-compose.yml
├── docker-compose.dev.yml
├── .editorconfig
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── tox.ini
├── Makefile
├── README.md
└── CHANGELOG.md
```

**Observaciones:**
- El `pyproject.toml` raíz solo contiene configuraciones de herramienta (flake8, mypy, pytest, coverage).
- Cada app, lib y package tiene su propio `pyproject.toml` con sus dependencias declaradas.
- Las apps dependen de libs mediante referencias de ruta: `{app}_shared = {path = "../libs/shared"}`.
- Los nombres de paquete Python usan `_` (snake_case) para consistencia con PEP 8.
- Se utiliza `src/` layout estándar para evitar conflictos de importación.
- `tox.ini` coordina la ejecución de tests en múltiples entornos.
- `alembic/` gestiona migraciones de base de datos con scripts por versión.

### React monorepo

```
{project-code}/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── lint.yml
│       └── security-scan.yml
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── core/
│   │   │   │   ├── auth/
│   │   │   │   │   ├── RequireAuth.tsx
│   │   │   │   │   ├── RequireRole.tsx
│   │   │   │   │   └── use-auth.ts
│   │   │   │   ├── http/
│   │   │   │   │   ├── api-client.ts
│   │   │   │   │   └── query-client.ts
│   │   │   │   └── types/
│   │   │   │       └── user.types.ts
│   │   │   ├── shared/
│   │   │   │   ├── components/
│   │   │   │   │   ├── Button/
│   │   │   │   │   │   ├── Button.tsx
│   │   │   │   │   │   └── Button.module.scss
│   │   │   │   │   └── Table/
│   │   │   │   │       ├── Table.tsx
│   │   │   │   │       └── Table.module.scss
│   │   │   │   ├── hooks/
│   │   │   │   │   └── use-permission.ts
│   │   │   │   └── utils/
│   │   │   │       └── format-currency.ts
│   │   │   ├── features/
│   │   │   │   ├── orders/
│   │   │   │   │   ├── pages/
│   │   │   │   │   │   ├── OrdersList.tsx
│   │   │   │   │   │   └── OrderDetail.tsx
│   │   │   │   │   ├── hooks/
│   │   │   │   │   │   └── use-orders.ts
│   │   │   │   │   ├── types/
│   │   │   │   │   │   └── order.types.ts
│   │   │   │   │   └── orders.routes.tsx
│   │   │   │   └── products/
│   │   │   │       ├── pages/
│   │   │   │       │   └── ProductsList.tsx
│   │   │   │       ├── hooks/
│   │   │   │       │   └── use-products.ts
│   │   │   │       └── products.routes.tsx
│   │   │   ├── App.tsx
│   │   │   ├── routes.tsx
│   │   │   ├── assets/
│   │   │   │   ├── i18n/
│   │   │   │   │   ├── en.json
│   │   │   │   │   └── es.json
│   │   │   │   └── images/
│   │   │   ├── styles/
│   │   │   │   ├── _variables.scss
│   │   │   │   ├── _mixins.scss
│   │   │   │   └── styles.scss
│   │   │   ├── index.html
│   │   │   └── main.tsx
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   ├── tsconfig.app.json
│   │   ├── tsconfig.node.json
│   │   ├── package.json
│   │   ├── vitest.config.ts
│   │   ├── .eslintrc.json
│   │   ├── Dockerfile
│   │   └── README.md
│   └── admin/
│       ├── src/
│       │   ├── features/
│       │   │   └── dashboard/
│       │   └── App.tsx
│       ├── vite.config.ts
│       └── package.json
├── libs/
│   ├── ui-components/
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   │   ├── Button/
│   │   │   │   ├── Table/
│   │   │   │   └── form-controls/
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsup.config.ts
│   ├── auth/
│   │   ├── src/
│   │   │   └── lib/
│   │   │       ├── use-auth.ts
│   │   │       ├── RequireAuth.tsx
│   │   │       └── api-client.ts
│   │   └── package.json
│   └── shared-utils/
│       ├── src/
│       │   └── lib/
│       │       ├── validators/
│       │       └── formatters/
│       └── package.json
├── docs/
│   └── architecture.md
├── docker-compose.yml
├── .editorconfig
├── .gitignore
├── nx.json
├── package.json
├── tsconfig.base.json
├── .eslintrc.json
├── README.md
└── CHANGELOG.md
```

**Observaciones:**
- Se usan **function components + hooks** (sin clases) con `App.tsx` como raíz de providers (React Query, Router).
- Los feature modules se cargan con **code-splitting** vía `React.lazy()` + `Suspense` en `*.routes.tsx`.
- `core/` contiene hooks singleton y clientes (auth, `apiFetch`, query client); `shared/` contiene componentes/hooks/utils reutilizables.
- La configuración por ambiente se maneja vía `import.meta.env` (`.env`, `.env.development`, `.env.production`) leído por Vite.
- `libs/` aloja bibliotecas publicables (bundleadas con `tsup`) reutilizables entre apps.
- `nx.json` coordina caching, affected commands y task orchestration en monorepos React.
- `tsconfig.base.json` define path aliases compartidos (`@app/core`, `@app/shared`, `@libs/ui-components`).
- `assets/i18n/` contiene archivos de traducción consumidos por `react-i18next`.
- Los estilos globales viven en `src/styles/` con parciales SCSS (`_variables.scss`, `_mixins.scss`).

### Angular monorepo

```
{project-code}/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── lint.yml
│       └── security-scan.yml
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── core/
│   │   │   │   │   ├── guards/
│   │   │   │   │   │   ├── auth.guard.ts
│   │   │   │   │   │   └── role.guard.ts
│   │   │   │   │   ├── interceptors/
│   │   │   │   │   │   ├── auth.interceptor.ts
│   │   │   │   │   │   └── error.interceptor.ts
│   │   │   │   │   ├── services/
│   │   │   │   │   │   ├── auth.service.ts
│   │   │   │   │   │   └── http.service.ts
│   │   │   │   │   └── models/
│   │   │   │   │       └── user.model.ts
│   │   │   │   ├── shared/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── button/
│   │   │   │   │   │   │   ├── button.component.ts
│   │   │   │   │   │   │   ├── button.component.html
│   │   │   │   │   │   │   └── button.component.scss
│   │   │   │   │   │   └── table/
│   │   │   │   │   │       ├── table.component.ts
│   │   │   │   │   │       └── table.component.html
│   │   │   │   │   ├── directives/
│   │   │   │   │   │   └── permission.directive.ts
│   │   │   │   │   └── pipes/
│   │   │   │   │       └── format-currency.pipe.ts
│   │   │   │   ├── features/
│   │   │   │   │   ├── orders/
│   │   │   │   │   │   ├── pages/
│   │   │   │   │   │   │   ├── orders-list/
│   │   │   │   │   │   │   │   ├── orders-list.component.ts
│   │   │   │   │   │   │   │   └── orders-list.component.html
│   │   │   │   │   │   │   └── order-detail/
│   │   │   │   │   │   │       ├── order-detail.component.ts
│   │   │   │   │   │   │       └── order-detail.component.html
│   │   │   │   │   │   ├── services/
│   │   │   │   │   │   │   └── orders.service.ts
│   │   │   │   │   │   ├── models/
│   │   │   │   │   │   │   └── order.model.ts
│   │   │   │   │   │   ├── orders.routes.ts
│   │   │   │   │   │   └── orders.module.ts
│   │   │   │   │   └── products/
│   │   │   │   │       ├── pages/
│   │   │   │   │       │   └── products-list/
│   │   │   │   │       │       └── products-list.component.ts
│   │   │   │   │       ├── services/
│   │   │   │   │       │   └── products.service.ts
│   │   │   │   │       └── products.routes.ts
│   │   │   │   ├── app.component.ts
│   │   │   │   ├── app.component.html
│   │   │   │   ├── app.config.ts
│   │   │   │   └── app.routes.ts
│   │   │   ├── assets/
│   │   │   │   ├── i18n/
│   │   │   │   │   ├── en.json
│   │   │   │   │   └── es.json
│   │   │   │   └── images/
│   │   │   ├── environments/
│   │   │   │   ├── environment.ts
│   │   │   │   ├── environment.development.ts
│   │   │   │   └── environment.production.ts
│   │   │   ├── styles/
│   │   │   │   ├── _variables.scss
│   │   │   │   ├── _mixins.scss
│   │   │   │   └── styles.scss
│   │   │   ├── index.html
│   │   │   └── main.ts
│   │   ├── angular.json
│   │   ├── tsconfig.json
│   │   ├── tsconfig.app.json
│   │   ├── tsconfig.spec.json
│   │   ├── package.json
│   │   ├── karma.conf.js
│   │   ├── .eslintrc.json
│   │   ├── Dockerfile
│   │   └── README.md
│   └── admin/
│       ├── src/
│       │   └── app/
│       │       ├── features/
│       │       │   └── dashboard/
│       │       └── app.component.ts
│       ├── angular.json
│       └── package.json
├── libs/
│   ├── ui-components/
│   │   ├── src/
│   │   │   ├── lib/
│   │   │   │   ├── button/
│   │   │   │   ├── table/
│   │   │   │   └── form-controls/
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── ng-package.json
│   ├── auth/
│   │   ├── src/
│   │   │   └── lib/
│   │   │       ├── auth.service.ts
│   │   │       ├── auth.guard.ts
│   │   │       └── auth.interceptor.ts
│   │   └── package.json
│   └── shared-utils/
│       ├── src/
│       │   └── lib/
│       │       ├── validators/
│       │       └── formatters/
│       └── package.json
├── docs/
│   └── architecture.md
├── docker-compose.yml
├── .editorconfig
├── .gitignore
├── nx.json
├── package.json
├── tsconfig.base.json
├── .eslintrc.json
├── README.md
└── CHANGELOG.md
```

**Observaciones:**
- Se usa **Angular standalone components** (sin NgModules en features nuevas) con `app.config.ts` standalone bootstrap.
- Los feature modules se cargan con **lazy loading** vía `loadChildren` en `*.routes.ts`.
- `core/` contiene servicios singleton (auth, interceptors, guards); `shared/` contiene componentes/pipes/directives reutilizables.
- `environments/` separa configuración por ambiente (development, production, staging).
- `libs/` aloja bibliotecas publicables (`ng-package.json`) reutilizables entre apps.
- `nx.json` coordina caching, affected commands y task orchestration en monorepos Angular.
- `tsconfig.base.json` define path aliases compartidos (`@app/core`, `@app/shared`, `@libs/ui-components`).
- `assets/i18n/` contiene archivos de traducción consumidos por `@ngx-translate/core`.
- Los estilos globales viven en `src/styles/` con parciales SCSS (`_variables.scss`, `_mixins.scss`).

### Bun (TypeScript) monorepo

```
{project-code}/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── lint.yml
│       └── security-scan.yml
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── server.ts
│   │   │   ├── core/
│   │   │   │   ├── config.ts
│   │   │   │   ├── dependencies.ts
│   │   │   │   ├── exceptions.ts
│   │   │   │   └── logger.ts
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── orders.controller.ts
│   │   │   │   │   ├── products.controller.ts
│   │   │   │   │   └── health.controller.ts
│   │   │   │   └── routes.ts
│   │   │   ├── models/
│   │   │   │   ├── order.model.ts
│   │   │   │   ├── product.model.ts
│   │   │   │   └── enums.ts
│   │   │   ├── schemas/
│   │   │   │   ├── order.schema.ts
│   │   │   │   ├── product.schema.ts
│   │   │   │   └── common.schema.ts
│   │   │   ├── services/
│   │   │   │   ├── order.service.ts
│   │   │   │   └── product.service.ts
│   │   │   ├── repositories/
│   │   │   │   ├── order.repository.ts
│   │   │   │   └── product.repository.ts
│   │   │   ├── middleware/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── error-handler.ts
│   │   │   │   └── request-id.ts
│   │   │   └── plugins/
│   │   │       ├── cors.ts
│   │   │       └── swagger.ts
│   │   ├── tests/
│   │   │   ├── setup.ts
│   │   │   ├── orders.test.ts
│   │   │   └── products.test.ts
│   │   ├── migrations/
│   │   │   ├── 0001_initial.ts
│   │   │   └── 0002_add_order_status.ts
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── bunfig.toml
│   │   ├── Dockerfile
│   │   └── README.md
│   ├── worker/
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── tasks/
│   │   │   │   ├── order.tasks.ts
│   │   │   │   └── notification.tasks.ts
│   │   │   └── handlers/
│   │   │       ├── order.handler.ts
│   │   │       └── email.handler.ts
│   │   ├── tests/
│   │   │   └── tasks.test.ts
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── bunfig.toml
│   └── cli/
│       ├── src/
│       │   ├── index.ts
│       │   └── commands/
│       │       └── migrate.ts
│       ├── package.json
│       └── tsconfig.json
├── libs/
│   ├── shared/
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── response.ts
│   │   │   ├── pagination.ts
│   │   │   ├── exceptions.ts
│   │   │   ├── types.ts
│   │   │   └── utils.ts
│   │   ├── tests/
│   │   │   └── utils.test.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── auth/
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── jwt.ts
│   │   │   ├── permissions.ts
│   │   │   └── dependencies.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── storage/
│       ├── src/
│       │   ├── index.ts
│       │   ├── s3.client.ts
│       │   └── local.storage.ts
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── sdk-client/
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── client.ts
│   │   │   ├── models.ts
│   │   │   └── errors.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── types/
│       ├── src/
│       │   ├── index.ts
│       │   └── contracts.ts
│       └── package.json
├── docs/
│   └── api/
│       └── openapi.json
├── scripts/
│   ├── run-dev.ts
│   └── migrate.ts
├── docker-compose.yml
├── docker-compose.dev.yml
├── .editorconfig
├── .gitignore
├── package.json
├── tsconfig.base.json
├── bunfig.toml
├── biome.json
├── Makefile
├── README.md
└── CHANGELOG.md
```

**Observaciones:**
- `bunfig.toml` raíz configura el runtime de Bun (test runner, macros, install resolution, lockfile).
- Cada app y lib tiene su propio `package.json` con dependencias declaradas y `tsconfig.json` extendiendo `tsconfig.base.json`.
- Las apps dependen de libs mediante workspace protocol: `"@{app}/shared": "workspace:*"` en `package.json`.
- Se usa **Biome** (`biome.json`) como formatter + linter unificado (reemplaza ESLint + Prettier) por velocidad nativa de Bun.
- `tests/` usa el test runner nativo de Bun (`bun test`) con archivos `*.test.ts` co-locados o en carpeta dedicada.
- `migrations/` contiene migraciones TypeScript ejecutadas con el runner de migraciones del proyecto (`bun run migrations`).
- Los nombres de paquete usan `@{project-code}/{name}` (scoped npm packages) para namespacing.
- `tsconfig.base.json` define `paths` aliases y `compilerOptions` compartidos (strict mode, `moduleResolution: bundler`).
- `src/` layout estándar; el entry point es `src/index.ts` que re-exports la API pública.

### Monorepo multi-stack (Bun backend + React frontend + Python AI/ML)

```
{project-code}/
├── .github/
│   └── workflows/
│       ├── ci-backend.yml
│       ├── ci-frontend.yml
│       ├── ci-ai.yml
│       └── security-scan.yml
├── apps/
│   ├── web/                          # React frontend
│   │   ├── src/
│   │   │   ├── core/
│   │   │   ├── shared/
│   │   │   ├── features/
│   │   │   │   ├── orders/
│   │   │   │   └── products/
│   │   │   ├── App.tsx
│   │   │   ├── routes.tsx
│   │   │   └── main.tsx
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   ├── package.json
│   │   └── Dockerfile
│   ├── api/                          # Bun backend (REST/BFF)
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── server.ts
│   │   │   ├── core/
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   ├── services/
│   │   │   └── middleware/
│   │   ├── tests/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── bunfig.toml
│   │   └── Dockerfile
│   └── ai-orchestrator/              # Python AI/ML core (FastAPI + LangChain)
│       ├── src/
│       │   └── {app}_ai/
│       │       ├── __init__.py
│       │       ├── main.py
│       │       ├── core/
│       │       │   ├── config.py
│       │       │   └── dependencies.py
│       │       ├── agents/
│       │       │   ├── router.py
│       │       │   ├── order_agent.py
│       │       │   └── product_agent.py
│       │       ├── chains/
│       │       │   └── order_chain.py
│       │       ├── tools/
│       │       │   ├── search_tool.py
│       │       │   └── calculator_tool.py
│       │       ├── memory/
│       │       │   └── conversation_memory.py
│       │       ├── prompts/
│       │       │   └── order_prompt.py
│       │       └── api/
│       │           └── v1/
│       │               └── agent_endpoints.py
│       ├── tests/
│       │   ├── conftest.py
│       │   └── test_agents.py
│       ├── pyproject.toml
│       ├── Dockerfile
│       └── README.md
├── libs/
│   ├── ui-components/                # React UI lib
│   │   ├── src/
│   │   │   └── lib/
│   │   ├── package.json
│   │   └── tsup.config.ts
│   ├── shared-ts/                    # Bun/TS shared contracts
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── types.ts
│   │   │   └── contracts.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── shared-py/                    # Python shared utilities
│       ├── src/
│       │   └── {app}_shared/
│       │       ├── response.py
│       │       └── exceptions.py
│       └── pyproject.toml
├── packages/
│   ├── sdk-client/                   # TS SDK para consumir API desde React
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   └── client.ts
│   │   └── package.json
│   └── openapi-spec/                 # OpenAPI spec compartida (source of truth)
│       ├── openapi.yaml
│       └── README.md
├── infra/
│   ├── terraform/
│   │   ├── modules/
│   │   └── environments/
│   │       ├── dev/
│   │       └── prod/
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── adr/                          # Architecture Decision Records
│   │   └── 0001-multi-stack-monorepo.md
│   └── api/
├── scripts/
│   ├── bootstrap.sh                  # Instala deps de los 3 stacks
│   └── generate-sdk.sh               # Genera SDK TS desde OpenAPI
├── .editorconfig
├── .gitignore
├── package.json                      # Workspace root (Bun)
├── tsconfig.base.json
├── bunfig.toml
├── pyproject.toml                    # Python tooling raíz
├── nx.json                           # Orquestación de tasks multi-stack
├── biome.json                        # Linter/formatter TS
├── Makefile                          # Targets: make dev, make test, make lint
├── README.md
└── CHANGELOG.md
```

**Observaciones:**
- **Tres stacks coexisten**: React (`apps/web`), Bun/TypeScript (`apps/api`), Python/FastAPI (`apps/ai-orchestrator`).
- **OpenAPI spec** en `packages/openapi-spec/` es el contrato compartido (source of truth); el SDK TypeScript consumido por React se genera desde ese contrato (generador del proyecto).
- **CI separado por stack**: workflows independientes (`ci-backend.yml`, `ci-frontend.yml`, `ci-ai.yml`) para paralelismo y caches diferenciados.
- **Makefile** orquesta comandos跨-stack: `make dev` levanta los 3 servicios, `make test` corre tests de los 3 stacks, `make lint` aplica Biome (TS) + ruff/mypy (Python).
- **nx.json** coordina affected builds y caching considerando dependencias entre apps y libs de distintos stacks.
- `libs/` se divide por lenguaje: `ui-components` (React), `shared-ts` (Bun), `shared-py` (Python).
- `infra/` centraliza Terraform con módulos reutilizables y environments separados.
- `docs/adr/` guarda Architecture Decision Records documentando decisiones como la adopción del multi-stack monorepo.
- El AI/ML core en Python expone endpoints consumidos por el Bun backend (BFF pattern), no directamente por React.

### Monorepo multi-stack (Bun backend + Angular frontend + Python AI/ML)

```
{project-code}/
├── .github/
│   └── workflows/
│       ├── ci-backend.yml
│       ├── ci-frontend.yml
│       ├── ci-ai.yml
│       └── security-scan.yml
├── apps/
│   ├── web/                          # Angular frontend
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── core/
│   │   │   │   ├── shared/
│   │   │   │   ├── features/
│   │   │   │   │   ├── orders/
│   │   │   │   │   └── products/
│   │   │   │   ├── app.component.ts
│   │   │   │   ├── app.config.ts
│   │   │   │   └── app.routes.ts
│   │   │   ├── environments/
│   │   │   │   ├── environment.ts
│   │   │   │   └── environment.production.ts
│   │   │   └── main.ts
│   │   ├── angular.json
│   │   ├── tsconfig.json
│   │   ├── package.json
│   │   └── Dockerfile
│   ├── api/                          # Bun backend (REST/BFF)
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── server.ts
│   │   │   ├── core/
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   ├── services/
│   │   │   └── middleware/
│   │   ├── tests/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── bunfig.toml
│   │   └── Dockerfile
│   └── ai-orchestrator/              # Python AI/ML core (FastAPI + LangChain)
│       ├── src/
│       │   └── {app}_ai/
│       │       ├── __init__.py
│       │       ├── main.py
│       │       ├── core/
│       │       │   ├── config.py
│       │       │   └── dependencies.py
│       │       ├── agents/
│       │       │   ├── router.py
│       │       │   ├── order_agent.py
│       │       │   └── product_agent.py
│       │       ├── chains/
│       │       │   └── order_chain.py
│       │       ├── tools/
│       │       │   ├── search_tool.py
│       │       │   └── calculator_tool.py
│       │       ├── memory/
│       │       │   └── conversation_memory.py
│       │       ├── prompts/
│       │       │   └── order_prompt.py
│       │       └── api/
│       │           └── v1/
│       │               └── agent_endpoints.py
│       ├── tests/
│       │   ├── conftest.py
│       │   └── test_agents.py
│       ├── pyproject.toml
│       ├── Dockerfile
│       └── README.md
├── libs/
│   ├── ui-components/                # Angular UI lib
│   │   ├── src/
│   │   │   └── lib/
│   │   ├── package.json
│   │   └── ng-package.json
│   ├── shared-ts/                    # Bun/TS shared contracts
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── types.ts
│   │   │   └── contracts.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── shared-py/                    # Python shared utilities
│       ├── src/
│       │   └── {app}_shared/
│       │       ├── response.py
│       │       └── exceptions.py
│       └── pyproject.toml
├── packages/
│   ├── sdk-client/                   # TS SDK para consumir API desde Angular
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   └── client.ts
│   │   └── package.json
│   └── openapi-spec/                 # OpenAPI spec compartida (source of truth)
│       ├── openapi.yaml
│       └── README.md
├── infra/
│   ├── terraform/
│   │   ├── modules/
│   │   └── environments/
│   │       ├── dev/
│   │       └── prod/
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── adr/                          # Architecture Decision Records
│   │   └── 0001-multi-stack-monorepo.md
│   └── api/
├── scripts/
│   ├── bootstrap.sh                  # Instala deps de los 3 stacks
│   └── generate-sdk.sh               # Genera SDK TS desde OpenAPI
├── .editorconfig
├── .gitignore
├── package.json                      # Workspace root (Bun)
├── tsconfig.base.json
├── bunfig.toml
├── pyproject.toml                    # Python tooling raíz
├── nx.json                           # Orquestación de tasks multi-stack
├── biome.json                        # Linter/formatter TS
├── Makefile                          # Targets: make dev, make test, make lint
├── README.md
└── CHANGELOG.md
```

**Observaciones:**
- **Tres stacks coexisten**: Angular (`apps/web`), Bun/TypeScript (`apps/api`), Python/FastAPI (`apps/ai-orchestrator`).
- **OpenAPI spec** en `packages/openapi-spec/` es el contrato compartido (source of truth); el SDK TypeScript consumido por Angular se genera desde ese contrato (generador del proyecto).
- **CI separado por stack**: workflows independientes (`ci-backend.yml`, `ci-frontend.yml`, `ci-ai.yml`) para paralelismo y caches diferenciados.
- **Makefile** orquesta comandos跨-stack: `make dev` levanta los 3 servicios, `make test` corre tests de los 3 stacks, `make lint` aplica Biome (TS) + ruff/mypy (Python).
- **nx.json** coordina affected builds y caching considerando dependencias entre apps y libs de distintos stacks.
- `libs/` se divide por lenguaje: `ui-components` (Angular), `shared-ts` (Bun), `shared-py` (Python).
- `infra/` centraliza Terraform con módulos reutilizables y environments separados.
- `docs/adr/` guarda Architecture Decision Records documentando decisiones como la adopción del multi-stack monorepo.
- El AI/ML core en Python expone endpoints consumidos por el Bun backend (BFF pattern), no directamente por Angular.

## Convenciones de nomenclatura

Todas las convenciones de nomenclatura en el framework siguen un conjunto uniforme de reglas que garantizan consistencia entre repositorios, proyectos, ramas, commits y etiquetas.

| Elemento | Patrón | Ejemplo |
|----------|--------|---------|
| **Nombre de repo** | `{prefijo}-{aplicación}-{tipo}` | `erp-orders-api`, `crm-admin-web`, `platform-libs` |
| **Prefijo** | Código de proyecto en minúsculas (2–5 chars) | `erp`, `crm`, `auth`, `billing`, `platform` |
| **Descriptor** | Opcional, kebab-case | `orders`, `user-management`, `invoice-processing` |
| **Tipo/sufijo** | Según tabla de sufijos | `-api`, `-web`, `-worker`, `-gateway`, `-libs` |
| **Carpeta de proyecto (monorepo)** | `{tipo}s/{app}/` | `apps/api/`, `apps/web/`, `packages/shared/`, `libs/auth/` |
| **Branch principal** | `main` o `master` | `main` |
| **Branch de desarrollo** | `develop` | `develop` |
| **Feature branch** | `feature/{id}-{descripcion-kebab}` | `feature/ERP-123-add-order-discount` |
| **Bugfix branch** | `fix/{id}-{descripcion-kebab}` | `fix/ERP-456-fix-null-reference` |
| **Hotfix branch** | `hotfix/{id}-{descripcion-kebab}` | `hotfix/ERP-789-security-patch` |
| **Release branch** | `release/{version}` | `release/v1.2.0` |
| **Commit message** | `{tipo}({alcance}): {descripción}` | `feat(orders): add discount calculation` |
| **Tipos de commit** | `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `build`, `revert` | Según conventional commits v1.0 |
| **Tag de versión** | `v{MAJOR}.{MINOR}.{PATCH}` | `v1.2.0`, `v2.0.0-beta.1` |
| **Tag de release candidate** | `v{MAJOR}.{MINOR}.{PATCH}-rc.{N}` | `v1.2.0-rc.1` |
| **Tag de pre-release** | `v{MAJOR}.{MINOR}.{PATCH}-{pre}.{N}` | `v1.2.0-alpha.1`, `v1.2.0-beta.2` |
| **Branch de soporte LTS** | `support/v{MAJOR}.{MINOR}` | `support/v1.2` |

### Reglas de branch naming

| Regla | Descripción |
|-------|-------------|
| **Máximo 72 caracteres** | El nombre completo del branch no debe exceder 72 caracteres |
| **ID de issue obligatorio** | Todo branch de feature, fix y hotfix debe incluir el ID del issue |
| **Separador de palabras** | Guiones (`-`) para separar palabras y entidades |
| **Sin mayúsculas** | Todo el branch name en minúsculas |
| **Sin caracteres especiales** | Solo letras, números y guiones |
| **Sin trailing slash** | No terminar con `/` |
| **Sin nombres genéricos** | Evitar `feature/update`, `fix/changes` |

### Reglas de commit message

| Elemento | Regla |
|----------|-------|
| **Longitud máxima del título** | 72 caracteres |
| **Longitud máxima del body** | 72 caracteres por línea |
| **Separación título/body** | Línea en blanco después del título |
| **Footer para breaking changes** | `BREAKING CHANGE:` seguido de descripción |
| **Footer para issues cerrados** | `Closes #123, #456` |
| **Referencia a issue** | Incluir ID del issue en el footer o alcance |
| **Idioma** | Inglés para el título, español o inglés para el body |

Ejemplos de commit message bien formados:

```
feat(orders): add discount calculation for bulk orders

Implement discount engine that applies tiered discounts
based on order quantity. Discounts are configurable per
product category.

Closes ERP-123
```

```
fix(api): handle null pointer in order validation

BREAKING CHANGE: The validateOrder function now requires
a non-null customer object. Existing callers must be updated.

Closes ERP-456
```

### Mapeo repositorio → proyecto interno

Cada repositorio debe declarar en su `README.md` o en un archivo `REPO.md` la siguiente metadata:

| Campo | Ejemplo |
|-------|---------|
| `project-code` | `ERP` |
| `repo-type` | `api` |
| `lifecycle` | `active` |
| `code` | `ACT-001` |
| `team` | `orders-team` |
| `slack-channel` | `#erp-orders` |

## Codificación de repos (código de repositorio)

Cada repositorio del framework recibe un **código único de repositorio** que permite identificarlo de forma inequívoca a través de todo el ciclo de vida del proyecto. Este código se utiliza en documentación, tableros, referencias cruzadas y reportes.

### Sistema de codificación

| Prefijo | Significado | Estado |
|---------|-------------|--------|
| `ACT-` | **Activo** — Repositorio en desarrollo activo con commits recientes | En producción, en desarrollo |
| `PLA-` | **Planificado** — Repositorio aprobado pero no iniciado | En backlog, priorizado |
| `IDL-` | **Inactivo** — Repositorio sin actividad, archivado o deprecado | Archivado, congelado, deprecado |
| `SUN-` | **Sunset** — Repositorio en proceso de desmantelamiento | En migración, reemplazado |
| `EXP-` | **Experimental** — Repositorio de prueba, PoC o prototipo | PoC, spike, sandbox |

### Formato del código

```
{PREFIJO}-{NNNN}-{slug}
```

| Componente | Regla | Ejemplo |
|------------|-------|---------|
| Prefijo | 3 letras mayúsculas con guión | `ACT-`, `PLA-`, `IDL-` |
| Número secuencial | 4 dígitos, zero-padded | `0001`, `0042`, `1023` |
| Slug | Opcional, kebab-case descriptivo | `erp-orders-api` |

### Ejemplos

| Código | Repositorio | Estado | Descripción |
|--------|-------------|--------|-------------|
| `ACT-0001` | `erp-orders-api` | Activo | API de órdenes del ERP |
| `ACT-0002` | `erp-orders-web` | Activo | Frontend de órdenes |
| `ACT-0003` | `crm-admin-web` | Activo | Panel de administración CRM |
| `PLA-0001` | `billing-api` | Planificado | API de facturación (Q3 2026) |
| `PLA-0002` | `billing-web` | Planificado | Frontend de facturación |
| `IDL-0001` | `legacy-reporting-api` | Inactivo | API legacy de reportes (reemplazada por ACT-0010) |
| `IDL-0002` | `monolith-v3` | Inactivo | Monolito versión 3 (archivado) |
| `SUN-0001` | `erp-gateway-v1` | Sunset | Gateway v1, migrando a ACT-0015 |
| `EXP-0001` | `sandbox-llm-agents` | Experimental | PoC de agentes con LLM |

### Gestión del ciclo de vida

```
PLA- → ACT- → SUN- → IDL-
  │                │
  └──→ EXP-→ IDL--┘
```

| Transición | Cuándo ocurre | Acción requerida |
|------------|---------------|------------------|
| **PLA → ACT** | El equipo comienza a desarrollar el repositorio | Crear repositorio, asignar código ACT, migrar documentación |
| **PLA → EXP** | Se decide prototipar antes de implementar | Renombrar a EXP, crear branch de PoC |
| **EXP → ACT** | El PoC se valida y pasa a producción | Renombrar a ACT, mergear a main, crear documentación |
| **EXP → IDL** | El PoC se descarta o no se continúa | Archivar repositorio, marcar como IDL |
| **ACT → SUN** | El repositorio tiene reemplazo o deprecación anunciada | Marcar como SUN, notificar consumidores, establecer sunset date |
| **SUN → IDL** | Fecha de sunset alcanzada | Archivar repositorio, actualizar dependencias, eliminar acceso de escritura |
| **ACT → IDL** | El proyecto se abandona sin reemplazo directo | Archivar, documentar decisión, código IDL |

### Registro maestro de repositorios

Cada proyecto debe mantener un archivo `REPO-REGISTRY.md` en la raíz del repositorio principal o en un repositorio de gobierno centralizado. El formato sugerido es una tabla markdown:

```markdown
# Registro de repositorios — ERP

| Código | Repositorio | Tipo | Estado | Team | Slack | URL |
|--------|-------------|------|--------|------|-------|-----|
| ACT-0001 | erp-orders-api | api | active | orders-team | #erp-orders | github.com/org/erp-orders-api |
| ACT-0002 | erp-orders-web | web | active | orders-team | #erp-orders | github.com/org/erp-orders-web |
| PLA-0001 | billing-api | api | planned | billing-team | #billing | — |
| IDL-0001 | legacy-reporting-api | api | inactive | — | — | github.com/org/legacy-reporting-api |
```

### Integración con git tags

Cada release debe incluir el código de repositorio en el mensaje del tag anotado:

```bash
git tag -a v1.2.0 -m "ACT-0001: v1.2.0 - Add discount calculation"
git tag -a v1.2.0-rc.1 -m "ACT-0001: v1.2.0-rc.1 - Release candidate 1"
```

### Referencias cruzadas

El código de repositorio se utiliza para referencias en:

- **Issues y PRs**: `Relacionado con: ACT-0001`
- **Documentación técnica**: `Ver repositorio ACT-0001 para detalles de implementación`
- **Tableros de proyecto**: Columna `Código repo` en tableros Jira/Linear/GitHub Projects
- **Reportes de estado**: `ACT-0001 (erp-orders-api): En desarrollo, 80% completo`
- **Alertas y monitoreo**: `[ACT-0001] Error rate above threshold in erp-orders-api`
- **CHANGELOG**: `### ACT-0001 - v1.2.0 (2026-06-01)`
- **Arquitectura**: `El componente X se despliega en ACT-0001`

### Herramienta de asignación de códigos

Para proyectos grandes, se recomienda mantener un script de CLI que automatice la asignación de códigos:

```bash
# Asignar nuevo código activo
repo-code assign --name erp-orders-api --type api --team orders-team
# Output: ACT-0042

# Buscar repositorio por código
repo-code search ACT-0042
# Output: erp-orders-api (active)

# Listar repositorios por estado
repo-code list --status active
# Output: ACT-0001, ACT-0002, ACT-0003, ...
```

Este sistema de codificación garantiza trazabilidad total entre la documentación, el código fuente, las decisiones arquitectónicas y las operaciones de mantenimiento, incluso cuando los repositorios cambian de nombre o se transfieren entre organizaciones.
