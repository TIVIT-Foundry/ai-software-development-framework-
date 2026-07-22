# Project Scaffold Template — Multi-Stack

> Stack: **Python 3.12 / FastAPI** + **React 18+** + **Bun (TypeScript)**
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
├── frontend/                            # ── React 18+ (Vite) ────────────────────
│   ├── src/
│   │   ├── main.tsx                     # React bootstrap (ReactDOM.createRoot)
│   │   ├── App.tsx                      # Root component (providers, router)
│   │   ├── routes.tsx                   # Top-level route definitions (react-router-dom)
│   │   │
│   │   ├── core/                        # Singleton hooks, clients & guards
│   │   │   ├── auth/
│   │   │   │   ├── use-auth.ts
│   │   │   │   ├── RequireAuth.tsx      # Guard wrapper route (<Outlet />)
│   │   │   │   └── auth.store.ts        # Zustand store
│   │   │   ├── http/
│   │   │   │   ├── api-client.ts        # apiFetch() wrapper
│   │   │   │   └── query-client.ts      # @tanstack/react-query client
│   │   │   ├── i18n/
│   │   │   │   ├── i18n.ts              # react-i18next config
│   │   │   │   └── locale/              # Translation files per language
│   │   │   │       ├── en.json
│   │   │   │       └── es.json
│   │   │   └── state/
│   │   │       └── app.store.ts         # Zustand store
│   │   │
│   │   ├── shared/                      # Shared UI components & hooks
│   │   │   ├── components/
│   │   │   │   ├── data-table/
│   │   │   │   ├── confirm-dialog/
│   │   │   │   ├── loading-spinner/
│   │   │   │   └── page-header/
│   │   │   ├── hooks/
│   │   │   └── utils/
│   │   │
│   │   └── features/                    # Code-split feature modules (React.lazy)
│   │       ├── users/
│   │       │   ├── users.routes.tsx
│   │       │   ├── pages/
│   │       │   │   ├── UserList.tsx
│   │       │   │   └── UserDetail/
│   │       │   │       └── ...
│   │       │   ├── hooks/
│   │       │   │   └── use-users.ts     # react-query queries/mutations
│   │       │   ├── types/
│   │       │   │   └── user.types.ts
│   │       │   └── store/
│   │       │       └── user.store.ts    # Zustand store
│   │       ├── orders/
│   │       │   └── ...
│   │       └── dashboard/
│   │           └── ...
│   │
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   ├── icons/
│   │   │   └── styles/
│   │   │       ├── _variables.scss
│   │   │       ├── _typography.scss
│   │   │       ├── _mixins.scss
│   │   │       └── styles.scss          # Global styles entry point
│   │   │
│   │   └── config/
│   │       ├── env.ts                   # Reads import.meta.env (production)
│   │       └── env.local.ts             # Local dev (gitignored)
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
│   ├── vite.config.ts                   # Build, dev server, proxy to backend (server.proxy)
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── Dockerfile
│   ├── nginx.conf                       # Production NGINX config for React SPA
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
│   ├── types/                           # Shared TypeScript types (React + Bun)
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
| TypeScript components | `PascalCase.tsx` | `UserList.tsx`, `RequireAuth.tsx` |
| TypeScript hooks | `use-{name}.ts` | `use-auth.ts`, `use-users.ts` |
| TypeScript stores | `{name}.store.ts` | `auth.store.ts`, `user.store.ts` |
| TypeScript types | `{name}.types.ts` | `user.types.ts` |
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
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=DEBUG
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

**React Frontend** (`.env.local`):
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_AUTH_ISSUER=http://localhost:8080/auth/realms/app
VITE_AUTH_CLIENT_ID=react-app
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

| Gate | Python | React | Bun |
|------|--------|---------|-----|
| **Lint** | `ruff check` | `eslint .` | `bunx eslint` |
| **Format** | `ruff format` | `prettier --check` | `prettier --check` |
| **Type check** | `mypy` | `tsc --noEmit` | `tsc --noEmit` |
| **Unit tests** | `pytest` | `vitest run` | `bun test` |
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

# 5. React frontend
cd frontend
bun install
npm run dev -- --port 5173

# 6. Verify
curl http://localhost:8000/health    # → 200 OK
curl http://localhost:3000/health    # → 200 OK
open http://localhost:5173           # → React app loads
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
| Node.js | 20 LTS | React build runtime |
| React | 18.x | Frontend framework (function components + hooks) |
| Vite | 5.x | Build tool & dev server |
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
