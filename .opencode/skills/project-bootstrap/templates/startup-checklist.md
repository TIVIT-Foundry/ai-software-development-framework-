# Startup & Onboarding Checklist — `{PROJECT_CODE}`

> **Project**: `{PROJECT_NAME}` — `{VERTICAL}`
> **Stack**: Python 3.12 / FastAPI · React 18+ · Bun (TypeScript) · PostgreSQL 16
> **Onboarded by**: `{MENTOR_NAME}` | **Date**: `{DATE}` | **New Member**: `{NAME}`

---

## Phase 1 — Access & Permissions

- [ ] **Git repository access** — Invited to `{REPO_URL}` with `Write` role
- [ ] **CI/CD access** — GitHub Actions / GitLab CI viewer permissions granted
- [ ] **Team communication** — Joined Slack/Teams channels:
  - [ ] `#{project}-dev` — Daily engineering
  - [ ] `#{project}-alerts` — Production alerts
  - [ ] `#general` — Company-wide announcements
- [ ] **Task board** — Invited to Jira / GitHub Projects / Linear:
  - [ ] Can view backlog
  - [ ] Can create and transition tickets
  - [ ] First ticket assigned
- [ ] **Documentation** — Access granted to:
  - [ ] Confluence / Notion project space
  - [ ] Architecture Decision Records (ADRs)
  - [ ] API Catalog
  - [ ] Runbooks
- [ ] **VPN / Network** — If required: VPN client installed and connected
- [ ] **Cloud access** — AWS/Azure/GCP console access (read-only for dev)
- [ ] **Container registry** — Docker Hub / ECR / ACR pull access
- [ ] **Secrets manager** — Read access to development secrets (Vault / AWS Secrets Manager)
- [ ] **SSH keys** — SSH key added to Git and any bastion hosts
- [ ] **Database** (if direct access needed):
  - [ ] PostgreSQL dev instance credentials shared
  - [ ] pgAdmin / DBeaver / DataGrip installed and connected

---

## Phase 2 — Local Environment Setup

### Prerequisites

- [ ] **Operating system**: Windows 10+ / macOS 13+ / Ubuntu 22.04+ (confirm version)
- [ ] **Git** 2.40+ installed: `git --version`
- [ ] **Docker Desktop** 25+ installed: `docker --version`
- [ ] **VS Code** installed with extensions (see below)
- [ ] **Terminal** configured: Windows Terminal / iTerm2 / kitty

### Python FastAPI Backend

- [ ] **Python 3.12** installed: `python --version`
- [ ] **uv** (or poetry) installed: `uv --version`
- [ ] **VS Code extensions**:
  - [ ] `ms-python.python`
  - [ ] `ms-python.vscode-pylance`
  - [ ] `charliermarsh.ruff`
  - [ ] `ms-python.mypy-type-checker`
  - [ ] `tamasfe.even-better-toml`
- [ ] **Repository cloned**: `git clone {REPO_URL}`
- [ ] **Dependencies installed**:
  ```bash
  cd backend
  uv sync
  ```
- [ ] **Environment configured**:
  ```bash
  cp .env.example .env
  # Edit .env with local values (JWT_SECRET_KEY, DATABASE_URL, etc.)
  ```
- [ ] **Local services started**:
  ```bash
  docker compose -f ../infrastructure/docker/docker-compose.yml up -d
  ```
- [ ] **Migrations applied**:
  ```bash
  alembic upgrade head
  ```
- [ ] **Server running**: `uvicorn src.main:app --reload --port 8000`
- [ ] **Health check passes**: `curl http://localhost:8000/health` → `200 OK`
- [ ] **Tests passing**: `pytest` (all green, 0 failures)
- [ ] **Lint passing**: `ruff check .` (0 errors)

### React Frontend

- [ ] **Node.js 20 LTS** installed: `node --version`
- [ ] **Bun 1.1+** installed: `bun --version`
- [ ] **Vite** available: `npm create vite@latest -- --version`
- [ ] **VS Code extensions**:
  - [ ] `dbaeumer.vscode-eslint`
  - [ ] `esbenp.prettier-vscode`
  - [ ] `burkeholland.simple-react-snippets`
  - [ ] `dsznajder.es7-react-js-snippets`
- [ ] **Dependencies installed**:
  ```bash
  cd frontend
  bun install
  ```
- [ ] **Local configuration**:
  ```bash
  cp .env.example .env.local
  # Edit API URL if needed
  ```
- [ ] **Dev server running**: `npm run dev -- --port 5173`
- [ ] **App loads at** `http://localhost:5173` without console errors
- [ ] **Tests passing**: `vitest run` (all green)
- [ ] **Lint passing**: `eslint .` (0 errors)
- [ ] **Build passing**: `vite build` (no errors)

### Bun TypeScript Backend

- [ ] **Bun 1.1+** installed: `bun --version`
- [ ] **VS Code extensions**:
  - [ ] `ms-vscode.vscode-typescript-next`
  - [ ] `dbaeumer.vscode-eslint`
  - [ ] `esbenp.prettier-vscode`
  - [ ] `oven.bun-vscode`
- [ ] **Dependencies installed**:
  ```bash
  cd bun-service
  bun install
  ```
- [ ] **Environment configured**:
  ```bash
  cp .env.example .env
  # Edit .env with local values
  ```
- [ ] **Server running**: `bun run src/index.ts`
- [ ] **Health check passes**: `curl http://localhost:3000/health` → `200 OK`
- [ ] **Tests passing**: `bun test` (all green)
- [ ] **Lint passing**: `bunx eslint .` (0 errors)
- [ ] **Type check passing**: `bunx tsc --noEmit` (0 errors)

---

## Phase 3 — Code Quality & Workflow

### Git Configuration

- [ ] **Git user configured**:
  ```bash
  git config user.name "{YOUR_NAME}"
  git config user.email "{YOUR_EMAIL}"
  ```
- [ ] **Pre-commit hooks installed**: `pre-commit install`
- [ ] **Pre-commit hooks passing**: `pre-commit run --all-files` (all hooks green)
- [ ] **Conventional commits understood** — Review [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] **Branch strategy understood**: `main` ← `develop` ← `feature/*` / `fix/*`
- [ ] **First branch created**: `git checkout -b feature/my-first-task`

### IDE Configuration

- [ ] **Auto-format on save** enabled (Prettier for TS, Ruff for Python)
- [ ] **Auto-organize imports** on save enabled
- [ ] **EditorConfig** working (indentation, line endings consistent)
- [ ] **Inlay hints** enabled (TypeScript parameter names, Python type hints)

### Quality Gates (must pass before every commit)

- [ ] **Python**: `ruff check .` + `ruff format --check .` + `mypy src/`
- [ ] **React**: `eslint .` + `vitest run` (optional for speed)
- [ ] **Bun**: `bunx eslint .` + `bun test`
- [ ] **All**: `pre-commit run` (triggered automatically on `git commit`)

---

## Phase 4 — Project Knowledge

### Core Documentation (read in order)

- [ ] `README.md` — Project overview, stack, quickstart
- [ ] `docs/PROJECT.md` — Ficha del proyecto (team, client, constraints)
- [ ] `docs/ARCHITECTURE.md` — Architecture overview and ADRs
- [ ] `docs/SETUP.md` — Detailed environment setup
- [ ] `AGENTS.md` — AI agent instructions for this repository
- [ ] `CHANGELOG.md` — Recent changes and release history

### API & Domain

- [ ] **API Catalog reviewed** (`docs/API-CATALOG.md` or Swagger at `/docs`)
- [ ] **Key domain concepts understood**:
  - [ ] Users, roles, permissions (RBAC model)
  - [ ] Core entities for the vertical
  - [ ] Event-driven flows (if applicable)
- [ ] **Agent architecture** (if AI agents):
  - [ ] Orchestrator flow
  - [ ] MCP tool catalog
  - [ ] Guardrails and HITL (human-in-the-loop) points

### Operations

- [ ] **Runbook reviewed** (`docs/RUNBOOK.md`)
  - [ ] Alert severity levels (P1–P4)
  - [ ] Escalation path
  - [ ] Rollback procedure
- [ ] **Monitoring dashboards**:
  - [ ] Grafana: Application dashboard
  - [ ] Grafana: Infrastructure dashboard
  - [ ] Langfuse: LLM observability (if agents)
- [ ] **Logging access**: ELK / Loki / CloudWatch logs searchable

---

## Phase 5 — Verification & Sign-off

### Self-Verification

- [ ] **All health checks pass** (backend + frontend + bun)
- [ ] **All tests pass in all stacks** (`scripts/test-all.sh`)
- [ ] **All linters pass in all stacks** (`scripts/lint-all.sh`)
- [ ] **Able to make a small code change and see it work end-to-end**
- [ ] **Able to run the full CI pipeline locally** (or know where CI runs)

### Mentor Verification

- [ ] **Pair programming session** — Mentor and new member pair on a real task
- [ ] **Code review** — New member submits a PR and gets their first review
- [ ] **First deploy** — New member observes or performs a staging deploy
- [ ] **Architecture walkthrough** — Mentor explains the system architecture with diagrams
- [ ] **Q&A** — New member asks 5+ questions about the system (questions documented)

### Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **New Member** | `{NAME}` | ________ | `{DATE}` |
| **Mentor** | `{MENTOR}` | ________ | `{DATE}` |
| **Tech Lead** | `{TECH_LEAD}` | ________ | `{DATE}` |

---

## Troubleshooting Common Issues

### Docker fails to start

```bash
# Check Docker is running
docker info

# Restart Docker Desktop
# Windows: Restart Docker Desktop app
# macOS: killall Docker && open /Applications/Docker.app

# Clear Docker state (last resort)
docker system prune -a --volumes
```

### Python import errors after install

```bash
# Ensure virtual environment is active
# With uv: uv sync creates .venv automatically
# With poetry: poetry shell

# Verify Python path
python -c "import fastapi; print(fastapi.__version__)"  # Should print version

# Reinstall if needed
uv sync --reinstall
```

### Vite build fails with memory error

```bash
# Increase Node memory limit
export NODE_OPTIONS="--max-old-space-size=4096"

# Clear Vite cache
rm -rf node_modules/.vite
```

### PostgreSQL connection refused

```bash
# Verify PostgreSQL container is running
docker ps | grep postgres

# Check logs
docker logs {postgres-container-name}

# Reset database (WARNING: deletes all local data)
docker compose -f infrastructure/docker/docker-compose.yml down -v
docker compose -f infrastructure/docker/docker-compose.yml up -d
alembic upgrade head
```

### Environment variables not loading

```bash
# Python: ensure .env is in the backend/ directory
# Bun: ensure .env is in the bun-service/ directory
# React: ensure .env.local exists

# Verify which file is being loaded:
# Python: print(os.getenv("DATABASE_URL"))
# Bun: console.log(process.env.DATABASE_URL)
```

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Start all infrastructure | `docker compose -f infrastructure/docker/docker-compose.yml up -d` |
| Start Python backend | `cd backend && uvicorn src.main:app --reload --port 8000` |
| Start Bun service | `cd bun-service && bun run src/index.ts` |
| Start React dev | `cd frontend && npm run dev` |
| Run all tests | `scripts/test-all.sh` |
| Run all linters | `scripts/lint-all.sh` |
| Run DB migrations | `cd backend && alembic upgrade head` |
| Seed database | `cd backend && python scripts/seed.py` |
| Build production | `cd frontend && vite build` |
| Docker build all | `docker compose -f infrastructure/docker/docker-compose.prod.yml build` |

---

> **Estimated time to complete**: 4–6 hours for experienced developers, 1–2 days for juniors with mentor guidance.
>
> If any step takes longer than expected or fails, escalate immediately to `{MENTOR_NAME}` in `#{project}-dev`.
