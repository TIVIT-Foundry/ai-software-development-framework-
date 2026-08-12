---
name: project-bootstrap
description: 'Entry point for onboarding to a new Python/FastAPI + React/Angular + Bun project. Trigger: When starting work on a new project, first-time setup, or project orientation.'
when_to_use:
  - Starting a new project from scratch
  - Onboarding to an existing project for the first time
  - Setting up development environment for a new team member
  - Defining the tech stack, team, and project context
  - Transitioning from framework scaffold to a concrete project
version: 1.1
metadata:
  phase:
  - inception
  layer:
  - process
  enforcement: mandatory
  depends_on:
  - framework-scaffold-implementation
  consumed_by:
  - project-architecture
  - readme
  - repo-structure
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: documentation
  mcp_usage: none
---

# project-bootstrap

## Propósito

Esta skill sirve para contextualizar y preparar un proyecto nuevo o existente antes de escribir cualquier línea de código de negocio. Su función es recoger, organizar y documentar el contexto completo del proyecto: stack tecnológico, equipo, cliente, entorno de desarrollo, herramientas, flujos de trabajo y estrategia de branching. Es el puente entre el scaffold genérico del framework y la configuración concreta de un proyecto real.

Sin esta skill, cada desarrollador interpreta convenciones de forma distinta, el CI/CD arranca sin baseline, y las herramientas de calidad no están sincronizadas. Project-bootstrap garantiza que cualquier persona que se una al proyecto pueda levantar el entorno y entender las reglas del juego en menos de una hora.

## Objetivo

Usa esta skill para responder estas cinco preguntas clave:

1. **¿Qué estamos construyendo y con qué?** — Tech stack, frameworks, versiones, runtimes, y restricciones técnicas.
2. **¿Quién lo construye y cómo se organizan?** — Roles, responsabilidades, canales de comunicación, ceremonias.
3. **¿Cómo se levanta el entorno de desarrollo?** — SDKs, dependencias, Docker, bases de datos locales, variables de entorno.
4. **¿Qué herramientas rigen la calidad del código?** — Linters, formatters, git hooks, CI/CD pipelines,覆盖率 mínima.
5. **¿Cuál es el contrato entre el scaffold del framework y este proyecto específico?** — Qué viene heredado, qué se personaliza, qué se extiende.

## Relación con otras skills

- `framework-scaffold-implementation` entrega la estructura base de repos, módulos y contratos del SDK. Project-bootstrap la consume y la adapta al proyecto concreto: versión de runtime, librerías específicas, equipo asignado, nombre del repositorio.
- `framework-discovery` identifica el vertical de negocio, actores y procesos. Project-bootstrap utiliza esa información para rellenar la ficha del proyecto con contexto de negocio real.
- `repo-structure` consume los datos de esta skill para determinar si el proyecto será monorepo o multi-repo, y cómo nombrar los repositorios según la convención. Se ejecuta inmediatamente después.
- `project-architecture` consume la ficha técnica y el entorno definido aquí para elegir el estilo arquitectónico (Vertical Slice, Modular Monolith, Microservicios) y la estructura de carpetas.
- `app-bootstrap` consume los datos de esta skill para registrar módulos y configurar middleware en el entry point de la aplicación.

Flujo típico:

```
framework-scaffold-implementation
  → framework-discovery
    → project-bootstrap  ← ESTA SKILL
      → repo-structure
        → project-architecture
          → app-bootstrap
```

## Qué debe hacer el agente cuando esta skill está activa

El agente debe:

1. **Recoger la ficha del proyecto**: nombre, código, vertical, cliente, stack primario y secundario, versiones, y restricciones.
2. **Definir el entorno de desarrollo por stack**: SDKs, runtimes, herramientas CLI, Docker, bases de datos locales, variables de entorno necesarias.
3. **Inicializar el repositorio Git**: estrategia de branching (.gitignore, hooks, convención de commits, protección de ramas).
4. **Configurar herramientas de calidad**: linter, formatter, pre-commit hooks, husky/lint-staged, configuración de CI/CD baseline.
5. **Documentar el contexto del equipo**: roles, responsabilidades, canales de comunicación, ceremonias ágiles.
6. **Documentar el contexto del cliente**: fuente de requisitos, flujo de aprobación, ambiente de despliegue, SLA.
7. **Verificar que el scaffold del framework está presente y actualizado**: leer la estructura existente, confirmar que los contratos base existen.
8. **Producir los artefactos de bootstrap**: ficha del proyecto, guía de setup, checklist de onboarding, archivos de configuración.
9. **Generar el archivo AGENTS.md del proyecto** con las reglas específicas de cómo trabajar en este repositorio.
10. **Crear el primer commit de baseline** con los archivos de configuración y documentación del proyecto.

## Entradas esperadas

Esta skill asume que ya existe:

- **Scaffold del framework** definido (viene de `framework-scaffold-implementation`).
- **Discovery del vertical** completado (viene de `framework-discovery`).
- **Decisiones de governance** documentadas (viene de `framework-governance`).

Si el scaffold no existe, esta skill debe pedir que se ejecute `framework-scaffold-implementation` primero. Si el discovery no se ha hecho, debe pedir contexto mínimo del vertical antes de continuar.

Entradas opcionales pero recomendadas:

- Repositorio ya inicializado con la estructura del scaffold.
- Acceso al sistema de control de versiones (GitHub, GitLab, Azure DevOps).
- Lista de miembros del equipo con sus roles.

## Alcance de la fase

La fase de project-bootstrap **sí incluye**:

- Ficha del proyecto con tech stack, versiones y restricciones.
- Entorno de desarrollo configurado (Python FastAPI, React o Angular, Bun).
- Inicialización del repositorio Git con estrategia de branching y protección.
- Checklist de onboarding para nuevos desarrolladores.
- Configuración de herramientas de calidad (linting, formatting, git hooks).
- CI/CD baseline (GitHub Actions starter workflow).
- Documento AGENTS.md específico del proyecto.
- Contexto del equipo y del cliente documentado.

La fase de project-bootstrap **no incluye**:

- Diseño de arquitectura detallada (va a `project-architecture`).
- Creación de endpoints o lógica de negocio (va a `backend-api`, `react-services`, etc.).
- Migraciones de base de datos (va a `database-migrations`).
- Diseño de APIs (va a `api-first-spec`).
- Configuración de infraestructura productiva (va a `infrastructure-as-code`).

## Principios que siempre debe respetar

1. **Reproducibilidad primero**: Cualquier desarrollador debe poder levantar el entorno con un solo comando después de clonar el repo.
2. **Documentar sobre asumir**: Si algo no está escrito, no existe. La ficha del proyecto debe ser explícita en versiones, dependencias y configuraciones.
3. **El scaffold es contrato, no sugerencia**: La estructura del framework no se altera sin justificación registrada. Se extiende, no se reescribe.
4. **Un proyecto, un AGENTS.md**: Cada repositorio tiene un archivo AGENTS.md con las reglas específicas de cómo trabajar en ese contexto.
5. **Calidad desde el commit cero**: Linter, formatter y hooks se instalan antes del primer commit de negocio. La cobertura mínima se define en esta fase.
6. **IoC del entorno**: Las variables de entorno y secretos nunca se hardcodean. Todo lo configurable vive en `.env.example` (gitignored).
7. **CI/CD mínimo viable**: El primer pipeline verifica build, lint y tests. No se necesita más para empezar a desarrollar.

## Qué decide y qué delega

Esta skill **sí decide**:

- Qué stack y versiones específicas usa el proyecto.
- Cómo se estructura el entorno de desarrollo local.
- Qué herramientas de calidad se instalan y con qué configuración.
- Cómo se inicializa el repositorio Git y qué estrategia de branching se adopta.
- Qué información entra en la ficha del proyecto y en el checklist de onboarding.

Esta skill **delega**:

- El nombre y convención del repositorio a `repo-structure`.
- El estilo arquitectónico y la estructura de carpetas a `project-architecture`.
- La configuración del entry point de la aplicación a `app-bootstrap`.
- Las decisiones de governance del framework a `framework-governance`.
- La estrategia de infraestructura productiva a `infrastructure-as-code`.

## Qué debe definir el diseño

### Bloque 1: Ficha del proyecto

La ficha del proyecto es el documento central que contextualiza todo el trabajo posterior. Debe contener:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Nombre del proyecto | Nombre comercial o interno | "ERP Corporativo v3" |
| Código del proyecto | Código corto único | `ERP` |
| Vertical | Dominio de negocio | "Financial Ops" |
| Cliente | Organización que recibe el producto | "Empresa ABC S.A.C." |
| Stack primario | Lenguaje/runtime principal | "Python 3.12 / FastAPI" |
| Stack secundario | Lenguaje/runtime adicional | "React 18+ / TypeScript 5" (o "Angular 17+ / TypeScript 5") |
| Motor de BD | Base de datos principal | "PostgreSQL 16" |
| Motor de BD secundario | Base de datos adicional | "Redis 7 (caché)" |
| Framework de agentes | Si aplica | "Framework Agéntico v1.0" |
| Repositorio | URL del repo | "github.com/org/erp-api" |
| Estado | Fase actual | "Bootstrap / Inception" |
| Fecha de inicio | Fecha de arranque | "2026-06-05" |

Plantilla multi-stack:

#### Python 3.12 / FastAPI

| Campo | Valor |
|-------|-------|
| Runtime | Python 3.12 |
| Framework | FastAPI 0.110+ |
| ORM | SQLAlchemy 2.0 + Alembic |
| Serialización | Pydantic v2 |
| Testing | pytest + httpx + TestContainers |
| Linter | Ruff (lint + format) + mypy |
| CI | GitHub Actions con `pytest` |

#### React 18+ Frontend

| Campo | Valor |
|-------|-------|
| Runtime | Node 20+ (LTS) |
| Framework | React 18+ (function components + hooks), Vite |
| UI Library | Radix UI / shadcn/ui |
| Estado | Zustand + @tanstack/react-query |
| HTTP | `fetch` envuelto en `apiFetch()` |
| Testing | Vitest + React Testing Library (unit) + Playwright (E2E) |
| Linter | ESLint (eslint-plugin-react, eslint-plugin-react-hooks) + Prettier |
| Build | `vite build` |
| CI | GitHub Actions con `npm run build` + `vitest run` |

#### Angular 17+ Frontend

| Campo | Valor |
|-------|-------|
| Runtime | Node 20+ (LTS) |
| Framework | Angular 17+ (standalone components, signals) |
| UI Library | Angular Material o PrimeNG |
| Estado | Signals + @ngneat/query (TanStack Query) |
| HTTP | HttpClient + interceptores |
| Testing | Vitest/Jest (unit) + Playwright (E2E) |
| Linter | ESLint (@angular-eslint) + Prettier |
| Build | `ng build` (esbuild/vite) |
| CI | GitHub Actions con `ng build` + `ng test` |

#### Bun (TypeScript) Backend

| Campo | Valor |
|-------|-------|
| Runtime | Bun 1.1+ |
| Lenguaje | TypeScript 5+ |
| Framework | Hono / Elysia (según preferencia) |
| ORM | Drizzle ORM o Bun SQL |
| Testing | `bun test` (bun:test nativo) |
| Linter | ESLint + Prettier |
| Bundler | Bun (nativo) |
| CI | GitHub Actions con `bun test` |

### Bloque 2: Entorno de desarrollo

Para el stack, definir los pasos concretos para levantar el entorno:

#### Python FastAPI

```
Prerrequisitos:
□ Python 3.12+
□ uv o poetry para gestión de dependencias
□ VS Code con extensión Python + Pylance
□ Docker Desktop 4.25+
□ Git 2.40+

Pasos:
1. git clone <repo-url>
2. uv sync  (o poetry install)
3. copiar .env.example → .env.local
4. docker compose up -d
5. alembic upgrade head
6. uvicorn app.main:app --reload --env-file .env.local
7. Verificar: GET http://localhost:8000/health → 200 OK

Extensiones VS Code recomendadas:
- ms-python.python
- ms-python.vscode-pylance
- charliermarsh.ruff
- ms-python.mypy-type-checker
```

#### React Frontend

```
Prerrequisitos:
□ Node.js 20+ (LTS)
□ Bun 1.1+ (gestor de paquetes y runtime)
□ Vite (via `npm create vite@latest`)
□ VS Code con extensiones ESLint + React
□ Navegador con React DevTools

Pasos:
1. cd frontend
2. npm create vite@latest <app-name> -- --template react-ts
3. cd <app-name>
4. bun install  (o npm install)
5. bun add @tanstack/react-query zustand react-router-dom react-hook-form zod @hookform/resolvers
6. copiar .env.example → .env.local
7. npm run dev
8. Verificar: http://localhost:5173 → carga sin errores

Archivos clave:
- vite.config.ts (config de build, dev server, plugins)
- tsconfig.json + tsconfig.app.json + tsconfig.node.json
- .eslintrc.json (eslint-plugin-react-hooks)
- .prettierrc

Extensiones VS Code recomendadas:
- dbaeumer.vscode-eslint
- esbenp.prettier-vscode
- burkeholland.simple-react-snippets
- dsznajder.es7-react-js-snippets
```

#### Angular Frontend

```
Prerrequisitos:
□ Node.js 20+ (LTS)
□ Bun 1.1+ (gestor de paquetes y runtime)
□ Angular CLI 17+ (npx @angular/cli)
□ VS Code con extensiones Angular + ESLint
□ Navegador con Angular DevTools

Pasos:
1. cd frontend
2. npx @angular/cli new <app-name> --style=scss --routing --ssr=false
3. cd <app-name>
4. bun install  (o npm install)
5. ng add @angular/material   (o: ng add primeng)
6. copiar src/environments/environment.example.ts → environment.local.ts
7. ng serve --configuration=local
8. Verificar: http://localhost:4200 → carga sin errores

Archivos clave:
- angular.json (config de build, serve, test, lint)
- tsconfig.json + tsconfig.app.json + tsconfig.spec.json
- .eslintrc.json (@angular-eslint)
- .prettierrc

Extensiones VS Code recomendadas:
- angular.ng-template
- esbenp.prettier-vscode
- dbaeumer.vscode-eslint
- ryanivey.vscode-angular2-switcher
- natewallace.angular2-vscode-html-syntax
```

#### Bun (TypeScript) Backend

```
Prerrequisitos:
□ Bun 1.1+ instalado (https://bun.sh)
□ VS Code con extensión TypeScript + ESLint
□ Docker Desktop 4.25+ (para servicios dependientes)

Pasos:
1. cd backend
2. bun init
3. bun install
4. copiar .env.example → .env.local
5. bun run src/index.ts  (o: bun --watch src/index.ts)
6. Verificar: GET http://localhost:3000/health → 200 OK

Archivos clave:
- tsconfig.json (strict mode)
- bunfig.toml (config de Bun: test, install, macros)
- package.json (scripts: dev, test, lint, build)
- .eslintrc.json
- .prettierrc

Extensiones VS Code recomendadas:
- ms-vscode.vscode-typescript-next
- dbaeumer.vscode-eslint
- esbenp.prettier-vscode
- oven.bun-vscode
```

### Bloque 3: Checklist de onboarding

Checklist que todo nuevo miembro del equipo debe completar:

```markdown
## Onboarding Checklist — [CÓDIGO DEL PROYECTO]

### Acceso y permisos
□ Cuenta de Git creada y acceso al repositorio confirmado
□ Cuenta de CI/CD (GitHub Actions / Azure DevOps) configurada
□ Acceso al canal del equipo (Slack / Teams / Discord)
□ Acceso a la documentación del proyecto (Confluence / Notion / Wiki)
□ Acceso al board de tareas (Jira / GitHub Projects / Linear)

### Entorno local
□ SDK/Runtime correcto instalado (ver ficha del proyecto)
□ IDE configurado con extensiones recomendadas
□ Docker Desktop instalado y corriendo
□ Repositorio clonado y dependencias restauradas
□ Variables de entorno configuradas (.env)
□ Servicios locales levantados (docker compose up -d)
□ Migraciones aplicadas
□ Health check responde 200 OK
□ Tests unitarios pasando (pytest / bun test / vitest run)
□ Frontend levanta correctamente (npm run dev → http://localhost:5173)

### Calidad de código
□ Pre-commit hooks instalados (husky / lint-staged)
□ Linter pasando sin errores
□ Formatter configurado en el IDE (save on format)
□ Tests locales pasando antes de primer commit

### Conocimiento del proyecto
□ Ficha del proyecto leída
□ AGENTS.md del repositorio leído
□ Arquitectura del proyecto comprendida (ARCHITECTURE.md)
□ API catalog revisado (si existe)
□ Board de tareas revisado
□ Primer ticket asignado
```

### Bloque 4: Configuración de herramientas

#### Linting y formatting

**Python:**
```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"
select = ["E", "W", "F", "I", "N", "UP", "B", "A", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
```

**TypeScript (React + Bun):**
```json
// .eslintrc.json (compartido React + Bun)
{
  "root": true,
  "ignorePatterns": ["dist/**", "node_modules/**"],
  "overrides": [
    {
      "files": ["*.ts", "*.tsx"],
      "extends": [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "plugin:react/recommended",
        "plugin:react-hooks/recommended"
      ],
      "rules": {
        "@typescript-eslint/no-unused-vars": "error",
        "@typescript-eslint/explicit-function-return-type": "warn",
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn"
      }
    }
  ]
}
```

```json
// .prettierrc
{
  "singleQuote": true,
  "semi": true,
  "printWidth": 120,
  "tabWidth": 2,
  "trailingComma": "all"
}
```

#### Git hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # --- Python ---
      - id: ruff-check
        name: ruff check
        entry: ruff check --fix
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: ruff format
        language: system
        types: [python]
      # --- TypeScript (React + Bun) ---
      - id: eslint
        name: eslint
        entry: bunx eslint --fix
        language: system
        files: \.(ts|tsx)$
        pass_filenames: true
      - id: prettier
        name: prettier
        entry: bunx prettier --write
        language: system
        files: \.(ts|tsx|js|jsx|json|html|scss|css|md)$
        pass_filenames: true
```

#### CI/CD baseline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # --- Python FastAPI ---
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Setup
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Lint
        run: ruff check .
      - name: Test
        run: pytest --cov=src

  # --- Bun (TypeScript) Backend ---
  bun:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      - name: Install
        run: bun install
        working-directory: backend
      - name: Lint
        run: bunx eslint .
        working-directory: backend
      - name: Test
        run: bun test
        working-directory: backend

  # --- React Frontend ---
  react:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest
      - name: Install
        run: bun install
        working-directory: frontend
      - name: Lint
        run: bunx eslint .
        working-directory: frontend
      - name: Build
        run: bunx vite build
        working-directory: frontend
      - name: Test
        run: bunx vitest run
        working-directory: frontend
```

## Preguntas guía

### 1. Sobre el proyecto y el stack
- ¿Cuál es el stack primario y por qué se eligió?
- ¿Qué versiones de runtime, framework y librerías principales se usan?
- ¿Hay servicios externos obligatorios (APIs de terceros, SaaS, bases de datos gestionadas)?
- ¿Qué bases de datos se necesitan en desarrollo local y en producción?
- ¿Existen restricciones de licenciamiento, compliance o regionales que afecten las herramientas?

### 2. Sobre el equipo y el cliente
- ¿Cuántos desarrolladores hay y qué roles cubren (backend, frontend, fullstack, QA, DevOps)?
- ¿Cómo se comunican (Slack, Teams, Discord)? ¿Cuáles son los canales principales?
- ¿Quién aprueba requisitos, diseños y despliegues del lado del cliente?
- ¿Hay dentro del equipo alguien con contexto profundo del dominio?
- ¿Cuál es el SLA o acuerdo de disponibilidad esperado por el cliente?

### 3. Sobre el entorno y la calidad
- ¿Todos los desarrolladores pueden levantar el proyecto localmente con un solo comando?
- ¿Hay dependencias que no se puedan dockerizar (licencias, binarios privados)?
- ¿Qué cobertura mínima de tests se exige como gate de merge?
- ¿Cómo se gestionan los secretos en desarrollo local y en CI?
- ¿Qué rama es la base para feature branches y qué protección tiene?

## Salidas esperadas

Cuando esta skill responda, debe producir estos cuatro artefactos:

### A. Ficha del proyecto (PROJECT.md)
- nombre, código, vertical, cliente;
- stack primario y secundario con versiones exactas;
- repositorio y estado actual;
- restricciones técnicas y de compliance;
- decisiones de stack con justificación.

### B. Guía de setup del entorno (SETUP.md)
- prerrequisitos por stack;
- pasos de instalación y verificación;
- comando de health check;
- troubleshooting de problemas comunes;
- extensiones de IDE recomendadas.

### C. Checklist de onboarding (ONBOARDING.md)
- acceso y permisos;
- entorno local;
- calidad de código;
- conocimiento del proyecto;
- firma de completado para el nuevo miembro.

### D. Configuración de herramientas y CI (archivos de configuración)
- `pyproject.toml` con tool.ruff y tool.mypy;
- `.eslintrc.json` y `.prettierrc` para TypeScript (React + Bun);
- `vite.config.ts`, `tsconfig.json` (frontend);
- `bunfig.toml`, `tsconfig.json` (backend Bun);
- `.pre-commit-config.yaml`;
- `.github/workflows/ci.yml` starter;
- `.gitignore` completo;
- `AGENTS.md` específico del proyecto.

## Criterios de calidad

La skill debe evaluar el bootstrap usando estos criterios:

1. **Reproducibilidad**: Un desarrollador nuevo puede clonar, instalar y correr el proyecto en menos de 60 minutos.
2. **Completitud de la ficha**: Todos los campos obligatorios de la ficha del proyecto están rellenos sin ambigüedad.
3. **Verificabilidad**: Existe un health check o comando de verificación que confirma que el entorno está correctamente configurado.
4. **Cobertura de stack**: La guía de setup cubre el stack primario y el secundario con la misma profundidad.
5. **Calidad desde cero**: Linter, formatter y pre-commit hooks están configurados y pasan antes del primer commit de negocio.
6. **Alineación con el scaffold**: La configuración del proyecto extiende el scaffold del framework, no lo contradice.
7. **Documentación viva**: Los archivos de configuración están versionados y AGENTS.md refleja las reglas reales del proyecto.
8. **Sin secretos expuestos**: Ningún secreto, contraseña o token aparece en texto plano en ningún archivo versionado.

## Comportamiento esperado del agente

Cuando el stack no esté claro, el agente debe preguntar explícitamente en lugar de asumir.  
Cuando el scaffold del framework no exista, el agente debe recomendar ejecutar `framework-scaffold-implementation` antes de continuar.  
Cuando el entorno local no se levante en un solo comando, el agente debe proponer scripts de automatización.  
Cuando el equipo no tenga definidos roles o canales de comunicación, el agente debe proponer una estructura mínima en lugar de dejar vacíos.  
Cuando las herramientas de calidad no estén configuradas, el agente debe incluirlas como parte del bootstrap, no como deuda técnica posterior.

Antipatrones a evitar:

1. **Asumir el stack sin confirmar**: No presumir que porque el framework sugiere Bun, el proyecto usa Bun. Preguntar siempre.
2. **Dejar el CI/CD para después**: El pipeline baseline no es opcional. Si no existe, crearlo como parte del primer commit.
3. **Documentar sin verificar**: Si el agente dice "ejecuta `pip install -r requirements.txt`", debe verificar que el comando funciona en el contexto del repo.
4. **Ignorar el contexto del cliente**: La ficha del proyecto sin la sección del cliente está incompleta. El flujo de aprobación y el ambiente de despliegue son datos críticos.

## Plantilla de respuesta recomendada

Usa esta estructura cuando respondas con el resultado de esta skill:

```
1. Ficha del proyecto
   - Nombre, código, vertical, cliente
   - Stack primario y secundario con versiones
   - Restricciones técnicas y de compliance
   - Repositorio y estado actual

2. Entorno de desarrollo
   - Prerrequisitos (SDKs, runtimes, Docker)
   - Pasos de instalación y verificación
   - Comandos de health check
   - Extensiones de IDE recomendadas

3. Inicialización del repositorio Git
   - Estrategia de branching
   - Protección de ramas
   - Convención de commits
   - .gitignore por stack

4. Herramientas de calidad
   - Linter y configuración
   - Formatter y configuración
   - Pre-commit hooks
   - Cobertura mínima de tests

5. CI/CD baseline
   - Pipeline de integración continua
   - Gates de calidad
   - Ambientes iniciales

6. Contexto del equipo
   - Roles y responsabilidades
   - Canales de comunicación
   - Ceremonias ágiles

7. Contexto del cliente
   - Fuente de requisitos
   - Flujo de aprobación
   - Ambiente de despliegue destino
   - SLA esperado

8. Checklist de onboarding
   - Accesos
   - Entorno local
   - Calidad
   - Conocimiento del proyecto
```

## Ejemplos de uso

### Ejemplo 1: Proyecto Python FastAPI + React + Bun para ERP Corporativo

**Consulta**: "Estamos arrancando el ERP Corporativo v3 con Python FastAPI, React 18 y Bun. Equipo de 6 devs, cliente es Empresa ABC. Necesitamos configurar todo para empezar a desarrollar."

**Respuesta esperada**:
- Ficha del proyecto: código `ERP`, stack `Python 3.12 / FastAPI / React 18+ / Bun`, BD `PostgreSQL 16`, cliente `Empresa ABC S.A.C.`
- Entorno de desarrollo: Python 3.12, Node 20, Bun 1.1, VS Code con extensiones Python + React + ESLint, Docker Desktop, `docker compose up -d` levanta PostgreSQL + Redis, health check en `/health`
- Git: branching `develop` + feature branches, protección en `main`, conventional commits, `.gitignore` para Python + Node + React
- Herramientas: Ruff (lint + format) + mypy para Python; ESLint (eslint-plugin-react-hooks) + Prettier para TypeScript; `pyproject.toml`, `.eslintrc.json`, `.prettierrc`, pre-commit con `ruff`, `eslint`, `prettier`
- CI/CD: GitHub Actions con 3 jobs (Python: `pytest` + `ruff check`; Bun: `bun test` + `eslint`; React: `vite build` + `vitest run`), cobertura mínima 70%
- Equipo: 4 backend, 2 frontend, canal `#erp-dev`, dailies a las 9:30
- Cliente: requisitos en Jira, aprobación por PM del cliente, deploys a AWS ECS, SLA 99.5%
- Checklist de onboarding: 16 pasos verificados

## Checklist final de la skill

Antes de cerrar una respuesta, verificar:

- [ ] ¿Se completó la ficha del proyecto con todos los campos obligatorios?
- [ ] ¿Se definió el entorno de desarrollo por stack con pasos verificables?
- [ ] ¿Se configuró la inicialización del repositorio Git con estrategia de branching?
- [ ] ¿Se instalaron y configuaron herramientas de calidad (linter, formatter, hooks)?
- [ ] ¿Se creó el pipeline de CI/CD baseline?
- [ ] ¿Se documentó el contexto del equipo y del cliente?
- [ ] ¿Se elaboró el checklist de onboarding?
- [ ] ¿Se verificó la alineación con el scaffold del framework?
- [ ] ¿Se creó o actualizó el archivo AGENTS.md del proyecto?
- [ ] ¿Se confirmó que ningún secreto está expuesto en archivos versionados?