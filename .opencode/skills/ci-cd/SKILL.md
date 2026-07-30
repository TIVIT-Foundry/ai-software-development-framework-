---
name: ci-cd
description: 'CI/CD pipeline design: GitHub Actions + GitLab CI, stages (lint → test
  → build → deploy), Bun/Python/React stacks, environment strategy, secrets management,
  artifact versioning, deployment gates, rollback. Trigger: When designing or configuring
  CI/CD pipelines.'
version: 1.2
metadata:
  phase:
  - operations
  layer:
  - infrastructure
  enforcement: recommended
  depends_on: []
  consumed_by:
  - agent-backend
  - agent-fullstack
  - agent-qa
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

## Propósito

Diseñar pipelines CI/CD repetibles, seguros y auditable: ejecución por etapas, promoción entre entornos, manejo de secretos, versionado de artefactos, deployment gates y rollback automático.

## Objetivo

1. ¿Cómo se estructura un pipeline CI/CD por etapas?
2. ¿Cómo se gestionan secretos sin exponerlos en logs o artefactos?
3. ¿Cómo se versionan artefactos para trazabilidad?
4. ¿Cómo se implementan deployment gates (manuales y automáticos)?
5. ¿Cómo se diseña una estrategia de rollback?
6. ¿Cómo se promueve un artefacto entre entornos (dev → qa → prod)?

## Relación con otras skills

- `framework-platform` define la infraestructura donde los pipelines despliegan.
- `framework-qa-validation` define los gates que los pipelines ejecutan (lint, tests, security scan).
- `security` define políticas de secretos, firma de artefactos y compliance.
- `docker-local` define cómo se construyen y versionan imágenes de contenedor.

## Qué debe hacer el agente

1. Diseñar pipeline con etapas secuenciales: lint → test → build → security scan → publish → deploy.
2. Usar GitHub Actions o GitLab CI según el repositorio del proyecto.
3. Configurar secretos desde el proveedor (GitHub Secrets / GitLab CI/CD Variables), nunca en código.
4. Versionar artefactos con hash + semver desde git tag o commit SHA.
5. Implementar gates: tests exitosos, code review, security scan pass.
6. Diseñar rollback automático (revertir tag de imagen o reiniciar versión anterior).
7. Promover el mismo artefacto entre entornos, no reconstruir.
8. Bloquear deploys a prod con aprobación manual (protected environment).
9. Registrar evidencia de cada deploy (commit, artefacto, resultado, responsable).

## Alcance

Incluye: pipeline YAML, secretos, artifact registry, environments, gates, rollback, approvals.
No incluye: infraestructura como tal (Terraform/Pulumi), monitoreo post-deploy, SLOs.

## Principios

- El mismo artifact binario que pasa tests en CI es el que se despliega en todos los entornos.
- Los secretos se inyectan en runtime, no se copian en imágenes ni se loguean.
- El pipeline debe fallar rápido (fail fast) en cada etapa.
- Un deploy a producción requiere al menos una aprobación manual.
- El rollback debe ser más rápido que el fix.
- Cada deploy deja un artefacto inmutable identificable por commit SHA.

## Technical Design

### GitHub Actions — Full pipeline

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff && ruff check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=src --cov-report=xml

  build:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4
      - id: version
        run: echo "version=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.version.outputs.version }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-dev:
    needs: build
    environment: dev
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }} to dev"

  deploy-prod:
    needs: deploy-dev
    if: github.ref == 'refs/heads/main'
    environment: prod
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }} to prod"
```

### Secrets management

```yaml
# GitHub Actions — secrets
steps:
  - name: Deploy
    uses: some-deploy-action@v1
    with:
      api-token: ${{ secrets.DEPLOY_API_TOKEN }}

# NEVER:
#   - echo ${{ secrets.SOMETHING }}  (leaks in log)
#   - storing secrets in artifact files
```

### Rollback strategy

```yaml
# Option A: Revert image tag
steps:
  - run: kubectl set image deployment/myapp app=${{ env.REGISTRY }}/myapp:${{ env.PREVIOUS_VERSION }}

# Option B: Blue-green swap
steps:
  - run: kubectl patch service myapp -p '{"spec":{"selector":{"version":"blue"}}}'
```

## Preguntas guía

- ¿El mismo artefacto se despliega en todos los entornos?
- ¿Los secretos se inyectan en runtime o están en el repositorio?
- ¿Cada entorno tiene sus propias variables de entorno?
- ¿Hay un gate antes de producción (aprobación manual)?
- ¿El rollback se puede ejecutar en menos de 5 minutos?
- ¿Hay evidencia de cada deploy (quién, qué, cuándo)?

## Salidas esperadas

- Pipeline YAML (GitHub Actions o GitLab CI según el repositorio).
- Definición de entornos (dev, qa, prod) con variables y secretos.
- Estrategia de versionado de artefactos (semver + commit SHA).
- Deployment gates (automáticos + manuales).
- Procedimiento de rollback documentado.

## Criterios de calidad

- El pipeline pasa lint + test + security scan antes de build.
- No hay secretos en ningún archivo del repositorio.
- Cada deploy produce un artefacto inmutable trazable a un commit.
- El rollback está definido y es ejecutable por un solo comando.
- Producción requiere aprobación manual explicita.

## Comportamiento esperado del agente

Cuando un pipeline mezcle lint/test/build/deploy en un solo job, debe separarlos en stages paralelizables.
Cuando no haya environment separation, debe definir dev → qa → prod con sus gates.
Cuando los secretos aparezcan en YAML o scripts, debe moverlos a GitHub Secrets.
Cuando no haya rollback definido, debe proponer al menos una estrategia de revert image tag.

## Plantilla de respuesta

```
1. Pipeline provider (GitHub Actions).
2. Stage breakdown (lint → test → build → security → deploy).
3. Environment definitions (dev, qa, prod).
4. Secrets map (env vars per environment).
5. Artifact versioning scheme.
6. Rollback procedure.
```

## Ejemplos

### Ejemplo 1 — Rollback por revert de tag

```bash
# Current: myapp:abc123, Previous: myapp:def456
kubectl set image deployment/myapp app=myapp:def456
```

### Ejemplo 2 — Deployment gate con GitHub Actions

```yaml
# Pre-deployment conditions in Azure portal
- Gates:
  - Evaluate artifact: check test results pass
  - Evaluate artifact: check security scan pass
  - Manual approval: required
```

## Checklist

- [ ] Pipeline organizado en stages secuenciales (fail fast).
- [ ] Mismo artefacto promovido entre entornos (no rebuild).
- [ ] Secretos inyectados desde provider, no en código.
- [ ] Entorno de producción protegido con approval gate.
- [ ] Rollback documentado (revert tag / blue-green).
- [ ] Artifact versionado con commit SHA o build ID.
- [ ] Logs de cada deploy preservados para auditoría.
- [ ] Pruebas, lint y security scan ejecutados en CI.

## Pipelines multi-stack

Patrones de CI/CD balanceados para múltiples stacks tecnológicos, usando workflows reutilizables de GitHub Actions como base compartida y pipelines especializados por lenguaje/framework.

### 1. GitHub Actions — Workflows reutilizables (workflow_call)

Los workflows reutilizables evitan duplicación y estandarizan etapas comunes (lint, test, security scan, publish) entre proyectos de distinto stack.

```yaml
# .github/workflows/ci-shared.yml
name: Shared CI Steps

on:
  workflow_call:
    inputs:
      stack:
        required: true
        type: string
      version:
        required: true
        type: string
    outputs:
      artifact-name:
        value: ${{ jobs.build.outputs.artifact-name }}
    secrets:
      REGISTRY_TOKEN:
        required: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint (${{ inputs.stack }})
        run: echo "Ejecutando lint para ${{ inputs.stack }}"

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test (${{ inputs.stack }})
        run: echo "Ejecutando tests para ${{ inputs.stack }}"

  security-scan:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Security scan (${{ inputs.stack }})
        run: echo "Ejecutando security scan para ${{ inputs.stack }}"

  build:
    needs: security-scan
    runs-on: ubuntu-latest
    outputs:
      artifact-name: ${{ inputs.stack }}-app-${{ inputs.version }}
    steps:
      - uses: actions/checkout@v4
      - name: Build artifact
        run: echo "Build ${{ inputs.stack }} v${{ inputs.version }}"
      - uses: actions/upload-artifact@v4
        with:
          name: ${{ inputs.stack }}-app-${{ inputs.version }}
          path: ./dist
```

Uso desde un pipeline consumidor:

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI

on:
  push:
    branches: [main]

jobs:
  ci:
    uses: ./.github/workflows/ci-shared.yml
    with:
      stack: frontend
      version: ${{ github.sha }}
    secrets:
      REGISTRY_TOKEN: ${{ secrets.REGISTRY_TOKEN }}
```

### 2. Frontend — React Build (Vite + pnpm)

```yaml
name: React Frontend CI

on:
  push:
    paths: ['frontend/**']

jobs:
  lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile
      - run: pnpm eslint . --max-warnings=0

  test:
    needs: lint
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile
      - run: pnpm vitest run --coverage

  build:
    needs: test
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile
      - run: pnpm vite build --mode production
      - uses: actions/upload-artifact@v4
        with:
          name: react-dist-${{ github.sha }}
          path: frontend/dist/
```

### 3. Frontend — Angular Build (pnpm)

```yaml
name: Angular Frontend CI

on:
  push:
    paths: ['frontend/**']

jobs:
  lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile
      - run: pnpm ng lint

  test:
    needs: lint
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile
      - run: pnpm ng test --code-coverage --watch=false

  build:
    needs: test
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml
      - run: pnpm install --frozen-lockfile
      - run: pnpm ng build --configuration=production
      - uses: actions/upload-artifact@v4
        with:
          name: angular-dist-${{ github.sha }}
          path: frontend/dist/
```

### 4. Docker — Multi-stage build + push

```dockerfile
# Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```yaml
name: Docker Build & Push

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE: ${{ github.repository }}

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 5. Security scanning — Trivy, npm audit/Snyk, SonarQube

```yaml
name: Security Scan

on:
  pull_request:
    branches: [main]

jobs:
  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/myorg/myapp:latest
          format: table
          exit-code: 1
          severity: CRITICAL,HIGH

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
      # Alternativa con Snyk:
      # - uses: snyk/actions/node@master
      #   env:
      #     SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: SonarSource/sonarqube-scan-action@v4
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

### 6. SBOM generation — syft + grype

```yaml
name: SBOM & Vulnerability Report

on:
  push:
    branches: [main]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate SBOM with syft
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/myorg/myapp:latest
          format: spdx-json
          output-file: sbom.spdx.json
      - name: Scan SBOM with grype
        uses: anchore/scan-action@v5
        with:
          image: ghcr.io/myorg/myapp:latest
          fail-build: true
          severity-cutoff: high
      - uses: actions/upload-artifact@v4
        with:
          name: sbom-report
          path: sbom.spdx.json
```

### 7. Python FastAPI pipeline

```yaml
name: FastAPI CI

on:
  push:
    paths: ['backend/**']

defaults:
  run:
    working-directory: backend

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install black isort flake8
      - run: black --check .
      - run: isort --check-only .
      - run: flake8 src/

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4

  docker:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: backend
          push: true
          tags: |
            ghcr.io/myorg/api:${{ github.sha }}
```

### 8. Bun (TypeScript backend) pipeline

```yaml
name: Bun Backend CI

on:
  push:
    paths: ['backend/**']

defaults:
  run:
    working-directory: backend

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      - run: bun install --frozen-lockfile
      - run: bunx eslint src/ --max-warnings=0
      - run: bunx tsc --noEmit
      # Alternativa con biome (más rápido, sin config):
      # - run: bunx biome check ./src

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      - run: bun install --frozen-lockfile
      - run: bunx vitest run --coverage
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/testdb
      - uses: codecov/codecov-action@v4

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      - run: bun install --frozen-lockfile
      - run: bun build ./src/index.ts --outdir ./dist --target bun
      - uses: actions/upload-artifact@v4
        with:
          name: bun-backend-${{ github.sha }}
          path: backend/dist/

  docker:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: backend
          push: true
          tags: |
            ghcr.io/myorg/bun-api:${{ github.sha }}
            ghcr.io/myorg/bun-api:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Dockerfile multi-stage para Bun:

```dockerfile
FROM oven/bun:alpine AS build
WORKDIR /app
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun build ./src/index.ts --outdir ./dist --target bun

FROM oven/bun:alpine AS runtime
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./
EXPOSE 3000
USER bun
CMD ["bun", "run", "dist/index.js"]
```

### 9. GitLab CI — Pipeline completo

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - security
  - build
  - deploy

variables:
  REGISTRY: ${CI_REGISTRY}
  IMAGE_TAG: ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}

# ─── Backend: Python FastAPI ──────────────────────────────────
backend-lint:
  stage: lint
  image: python:3.12
  rules:
    - changes: [backend/**]
  script:
    - cd backend
    - pip install ruff black isort
    - ruff check .
    - black --check .
    - isort --check-only .

backend-test:
  stage: test
  image: python:3.12
  services:
    - postgres:16
  variables:
    POSTGRES_PASSWORD: test
    POSTGRES_DB: testdb
    DATABASE_URL: postgres://postgres:test@postgres:5432/testdb
  rules:
    - changes: [backend/**]
  script:
    - cd backend
    - pip install -r requirements.txt -r requirements-dev.txt
    - pytest --cov=src --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml

# ─── Backend: Bun (TypeScript) ─────────────────────────────────
bun-lint:
  stage: lint
  image: oven/bun:latest
  rules:
    - changes: [services/**]
  before_script:
    - cd services
    - bun install --frozen-lockfile
  script:
    - bunx eslint src/ --max-warnings=0
    - bunx tsc --noEmit

bun-test:
  stage: test
  image: oven/bun:latest
  services:
    - postgres:16
  variables:
    POSTGRES_PASSWORD: test
    POSTGRES_DB: testdb
    DATABASE_URL: postgres://postgres:test@postgres:5432/testdb
  rules:
    - changes: [services/**]
  before_script:
    - cd services
    - bun install --frozen-lockfile
  script:
    - bunx vitest run --coverage
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: services/coverage/

# ─── Frontend: React ────────────────────────────────────────
frontend-lint:
  stage: lint
  image: node:20
  rules:
    - changes: [frontend/**]
  before_script:
    - corepack enable
    - cd frontend
    - pnpm install --frozen-lockfile
  script:
    - pnpm eslint . --max-warnings=0

frontend-test:
  stage: test
  image: node:20
  rules:
    - changes: [frontend/**]
  before_script:
    - corepack enable
    - cd frontend
    - pnpm install --frozen-lockfile
  script:
    - pnpm vitest run --coverage

# ─── Security scanning ───────────────────────────────────────
trivy-scan:
  stage: security
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - trivy image --exit-code 1 --severity CRITICAL,HIGH ${IMAGE_TAG} || true
    - trivy fs --exit-code 1 --severity CRITICAL,HIGH .

sast:
  stage: security
  image: node:20
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - npm audit --audit-level=high || true

# ─── Build & Push ────────────────────────────────────────────
build-backend:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  rules:
    - changes: [backend/**]
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t ${CI_REGISTRY_IMAGE}/api:${CI_COMMIT_SHORT_SHA} -f backend/Dockerfile backend/
    - docker push ${CI_REGISTRY_IMAGE}/api:${CI_COMMIT_SHORT_SHA}

build-frontend:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  rules:
    - changes: [frontend/**]
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t ${CI_REGISTRY_IMAGE}/web:${CI_COMMIT_SHORT_SHA} -f frontend/Dockerfile frontend/
    - docker push ${CI_REGISTRY_IMAGE}/web:${CI_COMMIT_SHORT_SHA}

build-bun:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  rules:
    - changes: [services/**]
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t ${CI_REGISTRY_IMAGE}/bun-api:${CI_COMMIT_SHORT_SHA} -f services/Dockerfile services/
    - docker push ${CI_REGISTRY_IMAGE}/bun-api:${CI_COMMIT_SHORT_SHA}

# ─── Deploy ──────────────────────────────────────────────────
deploy-dev:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: dev
    url: https://dev.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
  script:
    - kubectl set image deployment/api api=${CI_REGISTRY_IMAGE}/api:${CI_COMMIT_SHORT_SHA} -n dev
    - kubectl set image deployment/bun-api bun-api=${CI_REGISTRY_IMAGE}/bun-api:${CI_COMMIT_SHORT_SHA} -n dev
    - kubectl set image deployment/web web=${CI_REGISTRY_IMAGE}/web:${CI_COMMIT_SHORT_SHA} -n dev

deploy-prod:
  stage: deploy
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
  script:
    - kubectl set image deployment/api api=${CI_REGISTRY_IMAGE}/api:${CI_COMMIT_SHORT_SHA} -n prod
    - kubectl set image deployment/bun-api bun-api=${CI_REGISTRY_IMAGE}/bun-api:${CI_COMMIT_SHORT_SHA} -n prod
    - kubectl set image deployment/web web=${CI_REGISTRY_IMAGE}/web:${CI_COMMIT_SHORT_SHA} -n prod
```

### Patrones comunes entre stacks

| Patrón | Implementación |
|---|---|
| Versionado de artefactos | `git sha` o `semver` desde git tag |
| Mismo artefacto en todos los entornos | Docker image tag inmutable, promovido por tag |
| Secrets en runtime | GitHub Secrets, nunca en YAML |
| Security scan obligatorio | Trivy (container), Snyk/npm-audit (deps), SonarQube (SAST) |
| SBOM obligatorio para prod | syft genera SPDX, grype valida vulnerabilidades |
| Rollback rápido | `kubectl set image` al tag anterior o blue-green swap |
| Fail fast | Stages secuenciales con `needs`, fail inmediato en error |
