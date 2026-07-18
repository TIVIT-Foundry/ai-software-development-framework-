# Project Scaffold Template — Multi-Stack

> Stack: **Python 3.12 / FastAPI** + **Angular 17+** + **Bun (TypeScript)**
> Database: PostgreSQL 16 + Redis 7 | Orchestration: LangChain/LangGraph
> IAAS: Terraform | CI/CD: GitHub Actions | Observability: Prometheus + Grafana + OpenTelemetry

---

## Directory Structure

```
{project-name}/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                       # CI pipeline: lint → test → build → security scan
│   │   ├── deploy-staging.yml           # Deploy to staging environment
│   │   ├── deploy-production.yml        # Deploy to production (with approval gate)
│   │   └── security-scan.yml            # Scheduled SAST + dependency scan
│   ├── dependabot.yml                   # Automated dependency updates
│   └── CODEOWNERS                       # PR review assignments
│
├── .vscode/
│   ├── settings.json                    # Shared IDE settings (formatters, linters)
│   ├── extensions.json                  # Recommended extensions for the team
│   └── launch.json                      # Debug configurations for all stacks
│
├── backend/                             # ── Python FastAPI ─────────────────────
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                      # Application entry point (FastAPI)
│   │   ├── config.py                    # Settings via pydantic-settings (.env)
│   │   ├── dependencies.py              # Shared FastAPI Depends (DB session, auth)
│   │   │
│   │   ├── modules/                     # Vertical slice modules
│   │   │   ├── __init__.py
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # SQLAlchemy models
│   │   │   │   ├── schemas.py           # Pydantic DTOs (request/response)
│   │   │   │   ├── repository.py        # Data access layer
│   │   │   │   ├── service.py           # Business logic
│   │   │   │   ├── router.py            # FastAPI APIRouter (endpoints)
│   │   │   │   └── tests/
│   │   │   │       ├── test_models.py
│   │   │   │       ├── test_service.py
│   │   │   │       └── test_router.py
│   │   │   ├── orders/
│   │   │   │   └── ...                  # Same structure per module
│   │   │   └── notifications/
│   │   │       └── ...
│   │   │
│   │   ├── core/                        # Cross-cutting concerns
│   │   │   ├── __init__.py
│   │   │   ├── database.py              # SQLAlchemy engine + session factory
│   │   │   ├── security.py              # JWT, password hashing, OAuth2
│   │   │   ├── exceptions.py            # Custom exception hierarchy
│   │   │   ├── error_handlers.py        # FastAPI exception handlers
│   │   │   ├── middleware.py            # Correlation ID, request logging, timing
│   │   │   ├── pagination.py            # Cursor + offset pagination utils
│   │   │   └── api_response.py          # ApiResponse envelope wrapper
│   │   │
│   │   ├── agents/                      # AI/ML agent orchestration (LangGraph)
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py          # Main agent orchestrator
│   │   │   ├── tools.py                 # MCP tool catalog & registration
│   │   │   ├── router.py                # Model-agnostic routing logic
│   │   │   ├── memory.py                # Agent memory (short-term / long-term)
│   │   │   └── guardrails.py            # Safety & validation guardrails
│   │   │
│   │   └── shared/                      # Shared utilities
│   │       ├── __init__.py
│   │       ├── constants.py
│   │       ├── logging_config.py        # structlog configuration
│   │       └── utils.py
│   │
│   ├── migrations/                      # Alembic migrations
│   │   ├── env.py
│   │   ├── alembic.ini
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   │
│   ├── tests/
│   │   ├── conftest.py                  # Shared pytest fixtures (test DB, client)
│   │   ├── integration/
│   │   │   ├── test_users_api.py
│   │   │   └── test_orders_api.py
│   │   └── e2e/
│   │       └── test_user_flow.py
│   │
│   ├── scripts/
│   │   ├── seed.py                      # Database seeding
│   │   ├── migrate.sh                   # Alembic migration helper
│   │   └── run-dev.sh                   # Dev server launcher
│   │
│   ├── pyproject.toml                   # Dependencies (uv/poetry) + tool config
│   ├── Dockerfile
│   ├── .env.example                     # Template for environment variables
│   └── README.md
│
├── frontend/                            # ── Angular 17+ ────────────────────────
│   ├── src/
│   │   ├── main.ts                      # Angular bootstrap
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.config.ts            # Standalone app config (providers, routes)
│   │   │   ├── app.routes.ts            # Top-level route definitions
│   │   │   │
│   │   │   ├── core/                    # Singleton services & guards
│   │   │   │   ├── auth/
│   │   │   │   │   ├── auth.service.ts
│   │   │   │   │   ├── auth.guard.ts
│   │   │   │   │   └── auth.interceptor.ts
│   │   │   │   ├── http/
│   │   │   │   │   ├── api-client.service.ts
│   │   │   │   │   └── error.interceptor.ts
│   │   │   │   ├── i18n/
│   │   │   │   │   ├── translate.loader.ts
│   │   │   │   │   └── locale/          # Translation files per language
│   │   │   │   │       ├── en.json
│   │   │   │   │       └── es.json
│   │   │   │   └── state/
│   │   │   │       └── app-state.service.ts
│   │   │   │
│   │   │   ├── shared/                  # Shared UI components & directives
│   │   │   │   ├── components/
│   │   │   │   │   ├── data-table/
│   │   │   │   │   ├── confirm-dialog/
│   │   │   │   │   ├── loading-spinner/
│   │   │   │   │   └── page-header/
│   │   │   │   ├── directives/
│   │   │   │   └── pipes/
│   │   │   │
│   │   │   └── features/                # Lazy-loaded feature modules
│   │   │       ├── users/
│   │   │       │   ├── users.routes.ts
│   │   │       │   ├── pages/
│   │   │       │   │   ├── user-list/
│   │   │       │   │   │   ├── user-list.component.ts
│   │   │       │   │   │   ├── user-list.component.html
│   │   │       │   │   │   └── user-list.component.scss
│   │   │       │   │   └── user-detail/
│   │   │       │   │       └── ...
│   │   │       │   ├── services/
│   │   │       │   │   └── user.service.ts
│   │   │       │   ├── models/
│   │   │       │   │   └── user.model.ts
│   │   │       │   └── store/
│   │   │       │       └── user.store.ts
│   │   │       ├── orders/
│   │   │       │   └── ...
│   │   │       └── dashboard/
│   │   │           └── ...
│   │   │
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   ├── icons/
│   │   │   └── styles/
│   │   │       ├── _variables.scss
│   │   │       ├── _typography.scss
│   │   │       ├── _mixins.scss
│   │   │       └── styles.scss          # Global styles entry point
│   │   │
│   │   └── environments/
│   │       ├── environment.ts           # Production
│   │       ├── environment.staging.ts
│   │       └── environment.local.ts     # Local dev (gitignored)
│   │
│   ├── e2e/                             # Playwright E2E tests
│   │   ├── page-objects/
│   │   │   ├── login.po.ts
│   │   │   └── users.po.ts
│   │   ├── specs/
│   │   │   ├── login.spec.ts
│   │   │   └── users.spec.ts
│   │   └── playwright.config.ts
│   │
│   ├── angular.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.spec.json
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── proxy.conf.json                  # Dev server proxy to backend
│   ├── Dockerfile
│   ├── nginx.conf                       # Production NGINX config for Angular SPA
│   └── README.md
│
├── bun-service/                         # ── Bun (TypeScript) Microservice ──────
│   ├── src/
│   │   ├── index.ts                     # Entry point (Hono / Elysia)
│   │   ├── config.ts                    # Environment config
│   │   │
│   │   ├── modules/
│   │   │   ├── health/
│   │   │   │   ├── health.router.ts
│   │   │   │   └── health.test.ts
│   │   │   └── {feature}/
│   │   │       ├── {feature}.router.ts
│   │   │       ├── {feature}.service.ts
│   │   │       ├── {feature}.repository.ts
│   │   │       ├── {feature}.schema.ts
│   │   │       └── {feature}.test.ts
│   │   │
│   │   ├── middleware/
│   │   │   ├── auth.ts
│   │   │   ├── correlation-id.ts
│   │   │   └── request-logger.ts
│   │   │
│   │   └── shared/
│   │       ├── errors.ts
│   │       ├── db.ts                    # Database connection (Drizzle / Bun SQL)
│   │       └── api-response.ts
│   │
│   ├── tests/
│   │   └── integration/
│   │
│   ├── bunfig.toml                      # Bun configuration
│   ├── tsconfig.json                    # TypeScript strict config
│   ├── package.json
│   ├── .env.example
│   ├── Dockerfile
│   └── README.md
│
├── shared-libs/                         # ── Shared Contracts & Types ──────────
│   ├── contracts/                       # Inter-service contracts
│   │   ├── user-events.json
│   │   └── order-events.json
│   ├── types/                           # Shared TypeScript types (Angular + Bun)
│   │   ├── api-response.ts
│   │   ├── pagination.ts
│   │   └── user.ts
│   └── errors/                          # Error code catalog
│       └── error-codes.md
│
├── infrastructure/                      # ── Infrastructure as Code ────────────
│   ├── terraform/
│   │   ├── environments/
│   │   │   ├── staging/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── terraform.tfvars
│   │   │   └── production/
│   │   │       └── ...
│   │   ├── modules/
│   │   │   ├── database/
│   │   │   ├── kubernetes/
│   │   │   ├── networking/
│   │   │   └── observability/
│   │   └── backend.tf                   # Remote state (S3 / Azure Blob)
│   │
│   ├── kubernetes/
│   │   ├── base/
│   │   │   ├── namespace.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── secrets.yaml             # SealedSecrets or references
│   │   └── overlays/
│   │       ├── staging/
│   │       │   └── kustomization.yaml
│   │       └── production/
│   │           └── kustomization.yaml
│   │
│   └── docker/
│       ├── docker-compose.yml           # Local dev environment
│       ├── docker-compose.ci.yml        # CI testing environment
│       └── docker-compose.prod.yml      # Production-like local testing
│
├── docs/                                # ── Project Documentation ────────────
│   ├── PROJECT.md                       # Ficha del proyecto (stack, team, cliente)
│   ├── ARCHITECTURE.md                  # Architecture Decision Records
│   ├── SETUP.md                         # Environment setup guide
│   ├── ONBOARDING.md                    # New developer onboarding checklist
│   ├── API-CATALOG.md                   # API inventory (if generated)
│   ├── RUNBOOK.md                       # Operational runbooks
│   ├── adr/                             # Architecture Decision Records
│   │   └── 001-use-fastapi.md
│   └── diagrams/                        # .png / .drawio / PlantUML
│       └── architecture-overview.png
│
├── scripts/                             # ── Automation Scripts ────────────────
│   ├── setup-env.sh                     # One-command environment setup
│   ├── migrate-all.sh                   # Run all DB migrations
│   ├── seed-all.sh                      # Seed all databases
│   ├── lint-all.sh                      # Lint all stacks
│   └── test-all.sh                      # Run all tests
│
├── .gitignore                           # Comprehensive ignore rules
├── .pre-commit-config.yaml              # Pre-commit hooks (ruff, eslint, prettier)
├── .editorconfig                        # Consistent editor settings
├── AGENTS.md                            # AI agent instructions for this repo
├── CHANGELOG.md                         # Conventional commits changelog
├── Makefile                             # Top-level convenience targets
├── README.md                            # Project overview
└── LICENSE
```

---

## Key Conventions

### Naming

| Layer | Convention | Example |
|-------|-----------|---------|
| Python modules | `snake_case` | `user_service.py`, `test_users_api.py` |
| Python classes | `PascalCase` | `UserService`, `CreateUserRequest` |
| Python constants | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE` |
| TypeScript files | `kebab-case` | `user-list.component.ts`, `auth.service.ts` |
| TypeScript classes | `PascalCase` | `UserService`, `AuthGuard` |
| TypeScript interfaces | `PascalCase` | `UserResponse`, `PaginationMeta` |
| Database tables | `snake_case`, plural | `users`, `order_items` |
| Database schemas | `snake_case` | `users`, `orders`, `audit` |
| API endpoints | `kebab-case`, plural | `/users/api/v1/order-items` |
| Git branches | `kebab-case` | `feature/user-export`, `fix/login-timeout` |

### API Response Envelope

Every API response (Python + Bun) follows this shape:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "correlation_id": "uuid"
  }
}
```

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(users): add user export to Excel
fix(orders): correct tax calculation for multi-currency
chore(deps): bump fastapi to 0.112.0
docs(api): update OpenAPI spec for v2
test(users): add integration tests for password reset
refactor(core): extract pagination to shared module
```

### Branch Strategy

```
main          ── Production (protected, requires PR + review + CI)
  └── develop ── Integration branch
       └── feature/{name}  ── Feature branches
       └── fix/{name}      ── Bug fix branches
       └── chore/{name}    ── Maintenance / dependency branches
```

---

## Environment Variables

### Required per stack

**Python FastAPI** (`.env`):
```bash
APP_ENV=local
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:4200,http://localhost:3000
LOG_LEVEL=DEBUG
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

**Angular Frontend** (`environment.local.ts`):
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000/ws',
  auth: {
    issuer: 'http://localhost:8080/auth/realms/app',
    clientId: 'angular-app',
  },
};
```

**Bun Backend** (`.env`):
```bash
APP_ENV=local
PORT=3000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=change-me-in-production
LOG_LEVEL=debug
```

---

## Quality Gates

| Gate | Python | Angular | Bun |
|------|--------|---------|-----|
| **Lint** | `ruff check` | `ng lint` (eslint) | `bunx eslint` |
| **Format** | `ruff format` | `prettier --check` | `prettier --check` |
| **Type check** | `mypy` | `ng build` (strict) | `tsc --noEmit` |
| **Unit tests** | `pytest` | `ng test --watch=false` | `bun test` |
| **Coverage min** | 70% | 70% | 70% |
| **Integration** | `pytest -m integration` | — | `bun test --integration` |
| **E2E** | — | Playwright | — |
| **Security** | `pip-audit` + `bandit` | `npm audit` | `bun audit` |

### CI stages (in order)

```
lint → type-check → unit-tests → build → integration-tests → security-scan
```

All must pass before merge to `main`.

---

## Local Dev Quickstart

```bash
# 1. Clone and install
git clone <repo-url>
cd <project-name>

# 2. Start infrastructure (PostgreSQL + Redis + Kafka)
docker compose -f infrastructure/docker/docker-compose.yml up -d

# 3. Python backend
cd backend
cp .env.example .env
uv sync
alembic upgrade head
uvicorn src.main:app --reload --port 8000

# 4. Bun service
cd bun-service
cp .env.example .env
bun install
bun run src/index.ts

# 5. Angular frontend
cd frontend
bun install
ng serve --configuration=local --port 4200

# 6. Verify
curl http://localhost:8000/health    # → 200 OK
curl http://localhost:3000/health    # → 200 OK
open http://localhost:4200           # → Angular app loads
```

---

## Technology Versions (Pinned)

| Technology | Version | Notes |
|-----------|---------|-------|
| Python | 3.12.x | Runtime for FastAPI + AI/ML agents |
| FastAPI | 0.110.x | REST API framework |
| SQLAlchemy | 2.0.x | Async ORM with Alembic |
| Pydantic | 2.x | Data validation & serialization |
| PostgreSQL | 16 | Primary database |
| pgvector | 0.7.x | Vector similarity search |
| Redis | 7.x | Cache + message broker |
| Node.js | 20 LTS | Angular build runtime |
| Angular | 17.x | Frontend framework (standalone) |
| Angular Material | 17.x | UI component library |
| Bun | 1.1.x | TypeScript backend runtime |
| Hono | 4.x | Bun HTTP framework |
| Drizzle ORM | 0.30.x | TypeScript ORM for Bun |
| Docker | 25.x | Container runtime |
| Terraform | 1.8.x | Infrastructure as Code |
| Prometheus | 2.50.x | Metrics collection |
| Grafana | 10.x | Dashboards |
| OpenTelemetry | 1.24.x | Distributed tracing |
| Langfuse | 2.x | LLM observability |
| Keycloak | 24.x | Identity Provider (if used) |
