---
name: readme
description: 'README template for project modules (Python/FastAPI, Bun/TypeScript, React). Trigger: When creating module documentation, README files, or project docs.'
when_to_use:
  - Creating a new README for a module or project
  - Updating an existing README after significant changes
  - Onboarding new developers to a project
  - Standardizing README format across modules in a vertical
  - Documenting a library or shared package
version: 1.0
metadata:
  phase:
  - inception
  - closure
  layer:
  - process
  enforcement: recommended
  depends_on:
  - project-bootstrap
  - repo-structure
  consumed_by:
  - pull-request
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: documentation
  mcp_usage: none
---

## Propósito

Esta skill define la estructura, contenido y mantenimiento de archivos README para cada módulo del framework agéntico. Un README bien escrito es la **puerta de entrada** de cualquier desarrollador al proyecto: reduce el tiempo de onboarding, evita preguntas repetitivas y establece el contrato de uso del módulo.

La skill no busca producir documentación exhaustiva —busca producir documentación **accionable**: aquella que permite a un desarrollador pasar de clonar el repositorio a tener un servicio corriendo en el menor tiempo posible, con claridad sobre qué hace el módulo, cómo configurarlo y dónde encontrar más detalles.

## Objetivo

Todo README producido con esta skill debe responder **cinco preguntas clave** de forma directa y comprobable:

1. **¿Qué hace este módulo?** — Descripción funcional clara, sin jerga interna, orientada al desarrollador que llega por primera vez.
2. **¿Qué necesito antes de empezar?** — Prerrequisitos explícitos: versiones de runtime, servicios externos, variables de entorno, dependencias cross-repo.
3. **¿Cómo lo hago correr en mi máquina?** — Instrucciones de instalación y arranque local que funcionen de extremo a extremo sin supuestos.
4. **¿Cómo lo uso?** — Ejemplos de uso concretos: endpoints, comandos, imports, configuraciones mínimas.
5. **¿Dónde encuentro más detalle?** — Referencias a specs, OpenAPI, arquitectura, ADRs, sin duplicar contenido en el README.

## Relación con otras skills

| Skill | Relación | Descripción |
|-------|----------|-------------|
| `project-bootstrap` | **Predecesora** | `project-bootstrap` define el contexto del proyecto; `readme` lo materializa en documentación |
| `repo-structure` | **Predecesora** | `repo-structure` define nombre y tipo de repositorio; `readme` usa esa convención para estructurar secciones |
| `pull-request` | **Consumidora** | Un PR que modifica un módulo debe actualizar su README; `pull-request` valida que el README esté sincronizado |
| `api-first-spec` | **Referencia** | El README enlaza a la spec OpenAPI pero NO la duplica |
| `project-architecture` | **Referencia** | El diagrama de arquitectura puede mencionarse pero vive en docs separados |
| `openapi-docs` | **Complementaria** | `openapi-docs` genera la documentación de API; el README enlaza a ella |
| `docker-local` | **Referencia** | Si el módulo tiene Docker, el README referencia `docker compose` como opción de arranque |
| `changelog` | **Complementaria** | El CHANGELOG.md es referencia cruzada desde el README |

## Qué debe hacer el agente cuando esta skill está activa

1. **Leer el contexto del módulo**: Revisar `project-context.md`, `repo-structure` y los archivos de spec (`api-first-spec`) antes de escribir el README.
2. **Determinar el tipo de módulo**: Clasificar como API backend, frontend app, shared library, infra o pack del framework — cada tipo tiene secciones obligatorias distintas.
3. **Ejecutar el proyecto localmente**: Verificar que las instrucciones de quickstart funcionen realmente (instalación, configuración, arranque).
4. **Recopilar variables de entorno**: Extraer del código fuente todas las variables de entorno requeridas y opcionales con sus tipos y valores por defecto.
5. **Generar la tabla de endpoints/commands/routes**: Según el tipo de módulo, producir la tabla de referencia rápida (no la spec completa).
6. **Incluir badges relevantes**: Agregar badges de CI, cobertura, versión, licencia según corresponda al estado del proyecto.
7. **Escribir ejemplos de uso concretos**: Al menos un ejemplo funcional (curl, import, comando) que pueda copiarse y ejecutarse.
8. **Validar contra el checklist de calidad**: Revisar que todas las secciones obligatorias estén presentes y que no haya contenido duplicado con otros documentos.
9. **Enlazar en lugar de duplicar**: Referenciar OpenAPI specs, ADRs, diagramas de arquitectura y CHANGELOG en vez de copiar su contenido.
10. **Mantener actualizado**: Cada vez que se modifique el módulo, actualizar el README antes de cerrar el PR.

## Entradas esperadas

| Entrada | Origen | Obligatoria | Descripción |
|---------|--------|-------------|-------------|
| `project-context.md` | `project-bootstrap` | Sí | Contexto del proyecto: stack, convenciones, nombre |
| Tipo de módulo | `repo-structure` | Sí | Sufijo del repo (`-api`, `-web`, `-libs`, `-infra`, pack) |
| Spec OpenAPI | `api-first-spec` / `openapi-docs` | Condicional | Requerida si el módulo expone endpoints |
| `CHANGELOG.md` | `changelog` | Sí | Debe existir antes de cerrar el README |
| Diagrama de arquitectura | `project-architecture` | Recomendada | Referencia visual para la sección de arquitectura |
| Variables de entorno | Código fuente | Sí | `.env.example` o análisis del código |
| Scripts de arranque | `docker-local` / código fuente | Condicional | Si existe `docker-compose.yml` o scripts de setup |

## Alcance de la fase

**Incluido:**
- README.md raíz del módulo
- Secciones obligatorias según tipo de módulo
- Tablas de referencia rápida (endpoints, variables, comandos)
- Badges y status indicators
- Ejemplos de uso y quickstart
- Enlaces a documentación externa (OpenAPI, ADRs, arquitectura)

**Excluido:**
- Documentación de API detallada (responsabilidad de `openapi-docs`)
- Diagramas de arquitectura (responsabilidad de `project-architecture`)
- Guías de contribución detalladas (responsabilidad de templates de CONTRIBUTING.md)
- Changelog entries (responsabilidad de `changelog`)
- Decisiones de diseño (responsabilidad de ADRs separados)

## Principios que siempre debe respetar

1. **Accionable sobre descriptivo**: Priorizar instrucciones que se puedan copiar, ejecutar y verificar. Un `curl` funcional vale más que tres párrafos de descripción.
2. **Enlazar sobre duplicar**: No copiar la spec OpenAPI en el README; enlazar a ella. No copiar el CHANGELOG; enlazarlo. El README es índice, no enciclopedia.
3. **Verificable sobre teórico**: Cada instrucción de instalación y arranque debe haber sido validada en un entorno limpio. Si no se probó, marcarlo como "pendiente de verificación".
4. **Específico sobre genérico**: Evitar placeholders como `<TU-API-KEY>`. Usar valores de ejemplo realistas que ilustren el formato esperado (`sk-dev-abc123...` para development).
5. **Mínimo viable completo**: El README debe contener lo estrictamente necesario para que un desarrollador pueda clonar, configurar y ejecutar. Nada menos, nada más.
6. **Versionado explícito**: Documentar versiones exactas de runtime, SDK y herramientas. "Python 3.12" es preciso.
7. **Consistencia cross-módulo**: Todos los módulos del mismo vertical deben seguir la misma plantilla de README. Un desarrollador que conoce un módulo debe poder navegar cualquiera otro sin sorpresas.

## Qué decide esta skill y qué delega

| Decide esta skill | Delega a |
|-------------------|----------|
| Estructura y secciones del README | — |
| Qué badges incluir y su formato | — |
| Tabla de referencia rápida (endpoints, vars, comandos) | — |
| Ejemplos de uso y quickstart | — |
| Tipo de módulo y secciones obligatorias | `repo-structure` (provee el tipo) |
| Documentación detallada de API | `openapi-docs` / `api-first-spec` |
| Diagrama de arquitectura | `project-architecture` |
| Entradas de changelog | `changelog` |
| Contenido de CONTRIBUTING.md | Templates del repo |
| Decisiones de diseño (ADRs) | `project-architecture` |

## Qué debe definir el diseño

### Bloque 1 — README por tipo de módulo

Cada tipo de módulo tiene secciones obligatorias y opcionales distintas. El diseño debe definir la estructura para cada tipo:

#### API Backend (`-api`)

```
# {PROJECT-CODE}-{descriptor}-api

> Descripción funcional breve (1-2 líneas)

## Estado del proyecto
## Stack tecnológico
## Prerrequisitos
## Instalación y arranque local
## Variables de entorno
## Referencia de endpoints
## Estructura del proyecto
## Testing
## Arquitectura → link a docs
## Changelog → link a CHANGELOG.md
## Licencia
```

#### Frontend App (`-web`)

```
# {PROJECT-CODE}-{descriptor}-web

> Descripción funcional breve (1-2 líneas)

## Estado del proyecto
## Stack tecnológico
## Prerrequisitos
## Instalación y arranque local
## Variables de entorno
## Rutas y pantallas
## Estructura del proyecto
## Testing
## Arquitectura → link a docs
## Changelog → link a CHANGELOG.md
## Licencia
```

#### Shared Library (`-libs`)

```
# {PROJECT-CODE}-{descriptor}-libs

> Descripción funcional breve (1-2 líneas)

## Estado del proyecto
## Instalación como dependencia
## Uso
## API Reference
## Estructura del proyecto
## Testing
## Publicación (PyPI)
## Changelog → link a CHANGELOG.md
## Licencia
```

#### Infraestructura (`-infra`)

```
# {PROJECT-CODE}-{descriptor}-infra

> Descripción funcional breve (1-2 líneas)

## Estado del proyecto
## Stack de infraestructura
## Prerrequisitos
## Estructura del proyecto
## Comandos principales (plan, apply, destroy)
## Variables y tfvars
## Entornos (dev, staging, prod)
## Changelog → link a CHANGELOG.md
## Licencia
```

#### Framework Pack (pack agéntico)

```
# {pack-name}

> Descripción del pack: vertical, capacidades, agentes

## Estado del proyecto
## Capacidades del pack
## Agentes incluidos
## Herramientas MCP
## Configuración por tenant
## Instalación
## Uso
## Métricas y límites
## Changelog → link a CHANGELOG.md
## Licencia
```

### Bloque 2 — Secciones obligatorias y opcionales

| Sección | API | Frontend | Library | Infra | Pack | Tipo |
|---------|-----|----------|---------|-------|------|------|
| Título + descripción | ✅ | ✅ | ✅ | ✅ | ✅ | Obligatoria |
| Estado del proyecto (badges) | ✅ | ✅ | ✅ | ✅ | ✅ | Obligatoria |
| Stack tecnológico | ✅ | ✅ | ✅ | ✅ | ✅ | Obligatoria |
| Prerrequisitos | ✅ | ✅ | — | ✅ | ✅ | Obligatoria |
| Instalación y arranque | ✅ | ✅ | ✅ | ✅ | ✅ | Obligatoria |
| Variables de entorno | ✅ | ✅ | — | ✅ | ✅ | Obligatoria |
| Referencia de endpoints/rutas | ✅ | ✅ | — | — | — | Obligatoria |
| Estructura del proyecto | ✅ | ✅ | ✅ | ✅ | ✅ | Obligatoria |
| Testing | ✅ | ✅ | ✅ | — | — | Obligatoria |
| Changelog (link) | ✅ | ✅ | ✅ | ✅ | ✅ | Obligatoria |
| Licencia | ✅ | ✅ | ✅ | ✅ | ✅ | Obligatoria |
| Arquitectura | 🔵 | 🔵 | — | 🔵 | 🔵 | Opcional |
| Docker / Compose | 🔵 | 🔵 | — | — | 🔵 | Opcional |
| Diagrama de flujo | 🔵 | 🔵 | — | — | 🔵 | Opcional |
| Troubleshooting | 🔵 | 🔵 | — | 🔵 | — | Opcional |
| Contributing | 🔵 | 🔵 | 🔵 | 🔵 | 🔵 | Opcional |

Leyenda: ✅ = Obligatoria, 🔵 = Opcional, — = No aplica

### Bloque 3 — Badges y status indicators

El diseño debe definir qué badges se incluyen por defecto y su formato:

```markdown
<!-- Badges estándar -->
[![CI Status](https://img.shields.io/github/actions/workflow/{owner}/{repo}/ci.yml?branch=main&label=CI)](https://github.com/{owner}/{repo}/actions)
[![Coverage](https://img.shields.io/codecov/c/github/{owner}/{repo})](https://codecov.io/gh/{owner}/{repo})
[![Version](https://img.shields.io/github/package-json/v/{owner}/{repo})](https://github.com/{owner}/{repo}/releases)
[![License](https://img.shields.io/github/license/{owner}/{repo})](https://github.com/{owner}/{repo}/blob/main/LICENSE)

<!-- Badges opcionales -->
[![Docker](https://img.shields.io/docker/v/{org}/{repo}?label=docker)](https://hub.docker.com/r/{org}/{repo})
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-green)](./docs/openapi.yaml)
```

Reglas para badges:
- **Máximo 6 badges** por README. Más badges generan ruido visual.
- Solo incluir badges que apunten a URLs reales y funcionales.
- Si el proyecto no tiene CI, no incluir el badge de CI.
- El badge de versión debe reflejar la **última release**, no el HEAD de main.

### Bloque 4 — Ejemplos de uso y quickstart

El diseño debe definir el formato del quickstart para cada tipo de módulo:

#### Quickstart para API Backend

```markdown
## Instalación y arranque local

```bash
# 1. Clonar
git clone https://github.com/{org}/{repo}.git
cd {repo}

# 2. Restaurar dependencias
pip install -r requirements.txt

# 3. Configurar entorno
cp .env.example .env
# Editar .env con tus valores locales

# 4. Arrancar dependencias (si aplica)
docker compose up -d    # Base de datos, caches, etc.

# 5. Ejecutar migraciones
alembic upgrade head

# 6. Arrancar el servicio
uvicorn app.main:app --reload
```

El servicio estará disponible en `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`
```

#### Quickstart para Shared Library

```markdown
## Instalación como dependencia

```bash
# PyPI
pip install {package-name}
```

## Uso

```python
# Ejemplo mínimo funcional
from {package} import ApiResponse

response = ApiResponse.success(data)
```
```

#### Quickstart para Frontend App

```markdown
## Instalación y arranque local

```bash
# 1. Clonar
git clone https://github.com/{org}/{repo}.git
cd {repo}

# 2. Instalar dependencias
npm install

# 3. Configurar entorno
cp .env.example .env
# Configurar VITE_API_URL y otras variables

# 4. Arrancar en modo desarrollo
npm run dev

# 5. (Opcional) Arrancar API backend en otro terminal
cd ../{api-repo} && uvicorn app.main:app --reload
```

La aplicación estará disponible en `http://localhost:5173`.
```

## Preguntas guía

### Área 1 — Contenido esencial
1. ¿Un desarrollador nuevo puede clonar el repo, seguir el README y tener el servicio corriendo en menos de 15 minutos?
2. ¿Todas las variables de entorno requeridas están documentadas con tipo, valor por defecto y ejemplo?
3. ¿Los comandos de instalación y arranque incluyen las versiones exactas de runtime y herramientas?

### Área 2 — Estructura y navegación
1. ¿Las secciones siguen el orden estándar definido por tipo de módulo sin secciones inventadas?
2. ¿Cada sección enlaza a documentación detallada en lugar de duplicar contenido?
3. ¿La tabla de endpoints/rutas/comandos es suficiente para usar el módulo sin leer toda la spec?

### Área 3 — Mantenimiento y consistencia
1. ¿El README se actualiza en cada PR significativo o solo cuando alguien se acuerda?
2. ¿Los badges apuntan a URLs reales y funcional, o son placeholders rotos?
3. ¿Los ejemplos de uso han sido verificados recientemente contra la versión actual del módulo?

## Salidas esperadas

| Artefacto | Formato | Descripción |
|-----------|---------|-------------|
| `README.md` | Markdown | Archivo README completo del módulo, siguiendo la plantilla del tipo correspondiente |
| `/.env.example` | Shell vars | Archivo con todas las variables de entorno documentadas y valores de ejemplo |
| **Tabla de endpoints/rutas** (dentro de README) | Markdown table | Referencia rápida de la superficie del módulo |
| **Badges validados** (dentro de README) | Markdown + shields.io | Badges que apuntan a URLs reales del proyecto |

## Criterios de calidad

1. **Quickstart funcional**: Un desarrollador nuevo puede seguir las instrucciones de instalación y arranque de extremo a extremo sin errores, sin pasos faltantes y sin supuestos sobre su entorno.
2. **Sin duplicación**: Ningún contenido del README existe idénticamente en otro documento del proyecto. Si algo se describe en OpenAPI, CHANGELOG o ADRs, el README enlaza en lugar de copiar.
3. **Cobertura de variables**: Todas las variables de entorno requeridas y opcionales están documentadas con nombre, tipo, valor por defecto, descripción y ejemplo. Cero variables ocultas o "solo las sabe el equipo".
4. **Consistencia cross-módulo**: Todos los módulos del mismo vertical usan la misma plantilla, el mismo orden de secciones y el mismo estilo de tabla. Un desarrollador que conoce un módulo no tiene sorpresas en otro.
5. **Verificabilidad**: Cada badge apunta a una URL real y funcional. Cada comando de ejemplo ha sido ejecutado en un entorno limpio dentro de los últimos 30 días.
6. **Concisidad**: El README no excede las 300 líneas para módulos estándar. Si el contenido crece más allá, se extraen secciones a documentos separados y se enlazan.
7. **Búsqueda-friendly**: Los títulos de sección usan términos estándar (Installation, Configuration, Usage) que un desarrollador buscaría con `Ctrl+F`.

## Comportamiento esperado del agente

| Situación | Respuesta incorrecta | Respuesta esperada |
|-----------|---------------------|-------------------|
| El usuario dice "escribe un README rápido" | Escribir 3 líneas sin estructura | Aplicar la plantilla completa según tipo de módulo, explicando que la estructura estándar beneficia a todo el equipo |
| El README existente tiene 600+ líneas | Dejarlo como está | Identificar secciones que deben extraerse a docs separados, reescribir con enlaces y reducir a ≤300 líneas |
| No existe `.env.example` | Documentar variables solo en el README | Crear `.env.example` con las variables documentadas Y referenciarlo desde el README |
| El proyecto tiene stack Python + React | Escribir README solo para backend | Documentar ambos stacks con secciones dedicadas, indicando prerrequisitos por stack y el flujo de desarrollo integrado |
| Los ejemplos de curl usan datos inventados | Dejar `{"id": 1}` genérico | Usar datos de ejemplo que coincidan con los seed data del proyecto (`/api/v1/orders/ord-0001`) |
| Hay secciones vacías con "TODO" | Dejar los TODOs como placeholders | Eliminar secciones vacías; solo incluir secciones con contenido real. Agregar las pendientes al backlog, no al README |

## Plantilla de respuesta recomendada

La plantilla completa del README sigue esta estructura de 8 secciones estándar (se adaptan por tipo de módulo):

### Sección 1 — Encabezado y descripción

```markdown
# {PROJECT-CODE}-{descriptor}-{suffix}

> Descripción funcional del módulo en 1-2 líneas.
> Qué problema resuelve, para quién, en qué contexto.

[![CI Status](...)](...) [![Coverage](...)](...) [![Version](...)](...) [![License](...)](...)
```

### Sección 2 — Stack tecnológico

```markdown
## Stack tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Runtime | Python 3.12 / Bun 1.1+ / Node 20+ | LTS |
| Framework (AI/ML) | FastAPI | 0.110+ |
| Framework (Backend general) | Bun + TypeScript (Hono/Elysia) | 1.1+ |
| Frontend | React (Vite) | 18+ |
| UI libs | Radix UI / shadcn/ui | — |
| Base de datos | PostgreSQL 16 | 16.x |
| Cache / Colas | Redis 7 / Kafka | 7.x |
| ORM / Query | SQLAlchemy 2.0 (Py) / Drizzle (TS) | 2.0.x |
| Auth | Keycloak / OAuth2 / JWT | — |
| Test runner | pytest / Vitest | 8.x |
```

### Sección 3 — Prerrequisitos e instalación

```markdown
## Prerrequisitos

- Python 3.12 (3.12+) — [descargar](https://python.org/downloads)
- Docker & Docker Compose — para servicios dependientes
- PostgreSQL 16 — o usar `docker compose up db`

## Instalación y arranque local

```bash
git clone https://github.com/{org}/{repo}.git
cd {repo}
# ... (ver Bloque 4 para plantillas por tipo)
```

El servicio estará disponible en `http://localhost:{PORT}`.
Documentación interactiva: `http://localhost:{PORT}/swagger`.
```

### Sección 4 — Variables de entorno

```markdown
## Variables de entorno

Crear `.env` a partir de `.env.example`:

| Variable | Requerida | Tipo | Default | Descripción |
|----------|-----------|------|---------|-------------|
| `DATABASE_URL` | Sí | `string` | — | Connection string de PostgreSQL |
| `REDIS_URL` | No | `string` | `redis://localhost:6379` | URL de Redis |
| `JWT_SECRET` | Sí | `string` | — | Clave de firma de tokens JWT |
| `LOG_LEVEL` | No | `enum` | `info` | Nivel de logging (`debug`, `info`, `warn`, `error`) |
| `PORT` | No | `int` | `8000` | Puerto de escucha del servidor |

### Keycloak / OAuth2 (cuando aplica)

| Variable | Requerida | Tipo | Default | Descripción |
|----------|-----------|------|---------|-------------|
| `KEYCLOAK_URL` | Sí | `string` | — | URL base del realm Keycloak (ej. `https://kc.acme.io/realms/erp`) |
| `KEYCLOAK_CLIENT_ID` | Sí | `string` | — | `client_id` registrado en Keycloak |
| `KEYCLOAK_CLIENT_SECRET` | Sí* | `string` | — | Secret del client (confidential clients). Omitir para public clients |
| `KEYCLOAK_REALM` | Sí | `string` | — | Nombre del realm |
| `KEYCLOAK_PUBLIC_KEY` | No | `string` | — | Clave pública para validar JWT sin llamada al IdP (RS256) |
| `OAUTH2_ISSUER` | No | `string` | = `KEYCLOAK_URL` | Emisor del token (`iss` claim) |
| `OAUTH2_AUDIENCE` | No | `string` | `KEYCLOAK_CLIENT_ID` | Audience esperada (`aud` claim) |
| `OAUTH2_SCOPES` | No | `string` | `openid profile email` | Scopes solicitados en flujo authorization code |
| `TOKEN_TTL_MINUTES` | No | `int` | `15` | TTL del access token para rotación |
| `REFRESH_TOKEN_TTL_DAYS` | No | `int` | `7` | TTL del refresh token |

> \* `KEYCLOAK_CLIENT_SECRET` es requerida solo para **confidential clients** (backend-to-backend o service accounts). Para SPAs React (public clients) se usa PKCE y no se expone el secret.
> Frontend React consume estas vars vía `import.meta.env` (prefijo `VITE_`) inyectadas en build time (nunca secretos en el bundle).
```

### Sección 5 — Referencia rápida (endpoints/rutas/comandos)

```markdown
## Referencia de endpoints

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/orders` | Listar órdenes (paginado) | Sí |
| `POST` | `/api/v1/orders` | Crear orden | Sí |
| `GET` | `/api/v1/orders/{id}` | Obtener orden por ID | Sí |
| `PATCH` | `/api/v1/orders/{id}/status` | Actualizar estado | Sí |

> Documentación completa: [OpenAPI Spec](./docs/openapi.yaml) · [Swagger UI](http://localhost:8000/docs)
```

### Sección 6 — Estructura del proyecto

```markdown
## Estructura del proyecto

```
{repo}/
├── src/                    # Código fuente
│   ├── app/                # FastAPI application
│   │   ├── main.py         # Entry point
│   │   ├── modules/        # Feature modules
│   │   └── common/         # Shared utilities
├── tests/                  # Tests
│   ├── test_api.py
│   └── conftest.py
├── docs/                   # Documentación adicional
│   └── openapi.yaml
├── .env.example            # Variables de entorno template
├── CHANGELOG.md            # Historial de cambios
└── README.md               # Este archivo
```
```

### Sección 7 — Testing

```markdown
## Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=src --cov-report=html

# Ejecutar un test específico
pytest tests/test_order_service.py
```
```

### Sección 8 — Enlaces y licencia

```markdown
## Enlaces

- [OpenAPI Spec](./docs/openapi.yaml)
- [CHANGELOG.md](./CHANGELOG.md)
- [Arquitectura](./docs/architecture.md)
- [ADRs](./docs/adr/)
- [Repo de infra](https://github.com/{org}/{repo}-infra)

## Licencia

MIT — ver [LICENSE](./LICENSE) para detalles.
```

## Ejemplos de uso

### Ejemplo 1 — API Backend (Python FastAPI)

Para un módulo `erp-orders-api`, el README resultante:

```markdown
# ERP-orders-api

> Microservicio de gestión de órdenes para el vertical ERP.
> Permite crear, consultar y actualizar órdenes de compra con control de estado y auditoría.

[![CI Status](https://img.shields.io/github/actions/workflow/acme/erp-orders-api/ci.yml?branch=main&label=CI)](https://github.com/acme/erp-orders-api/actions) [![Coverage](https://img.shields.io/codecov/c/github/acme/erp-orders-api)](https://codecov.io/gh/acme/erp-orders-api) [![Version](https://img.shields.io/github/v/tag/acme/erp-orders-api?label=version)](https://github.com/acme/erp-orders-api/releases) [![License: MIT](https://img.shields.io/github/license/acme/erp-orders-api)](./LICENSE)

## Stack tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Runtime | Python 3.12 | 3.12+ |
| Framework | FastAPI | 0.110+ |
| Base de datos | PostgreSQL 16 | 16.x |
| ORM | SQLAlchemy | 2.0 |
| Test runner | pytest | 8.x |

## Prerrequisitos

- Python 3.12+
- PostgreSQL 16 o Docker para levantar la BD
- Redis 7 (opcional, para caching)

## Instalación y arranque local

```bash
git clone https://github.com/acme/erp-orders-api.git
cd erp-orders-api
pip install -r requirements.txt
cp .env.example .env
docker compose up -d          # Levanta PostgreSQL + Redis
alembic upgrade head           # Ejecuta migraciones
uvicorn app.main:app --reload  # Arranca en http://localhost:8000
```

Swagger UI: `http://localhost:8000/docs`

## Variables de entorno

| Variable | Requerida | Tipo | Default | Descripción |
|----------|-----------|------|---------|-------------|
| `DATABASE_URL` | Sí | `string` | — | Connection string PostgreSQL |
| `REDIS_URL` | No | `string` | `redis://localhost:6379` | URL de Redis |
| `JWT_SECRET` | Sí | `string` | — | Clave de firma JWT |
| `JWT_ISSUER` | No | `string` | `erp-orders-api` | Emisor del token |
| `LOG_LEVEL` | No | `enum` | `info` | Nivel de logging |
| `PORT` | No | `int` | `8000` | Puerto de escucha |

## Referencia de endpoints

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/orders` | Listar órdenes (paginado) | Sí |
| `POST` | `/api/v1/orders` | Crear orden | Sí |
| `GET` | `/api/v1/orders/{id}` | Obtener orden por ID | Sí |
| `PATCH` | `/api/v1/orders/{id}/status` | Actualizar estado de orden | Sí |
| `DELETE` | `/api/v1/orders/{id}` | Eliminar orden (soft delete) | Admin |

> Spec completa: [OpenAPI](./docs/openapi.yaml) · [Swagger UI](http://localhost:8000/docs)

## Estructura del proyecto

```
erp-orders-api/
├── src/
│   └── app/
│       ├── main.py              # FastAPI application
│       ├── modules/
│       │   └── orders/          # Order module
│       │       ├── router.py    # API endpoints
│       │       ├── schemas.py   # Pydantic models
│       │       └── service.py   # Business logic
│       └── common/              # Shared utilities
├── tests/
│   ├── test_orders.py
│   └── conftest.py
├── alembic/
├── .env.example
├── CHANGELOG.md
└── README.md
```

## Testing

```bash
pytest                                    # Todos los tests
pytest -m integration                     # Solo integración
pytest --cov=src --cov-report=html        # Con cobertura
```

## Enlaces

- [OpenAPI Spec](./docs/openapi.yaml)
- [CHANGELOG](./CHANGELOG.md)
- [Arquitectura](./docs/architecture.md)

## Licencia

MIT — ver [LICENSE](./LICENSE).
```

### Ejemplo 2 — Shared Library (Python/PyPI)

Para un módulo `erp-shared-libs`, el README resultante:

```markdown
# ERP-shared-libs

> Librería compartida con contratos, respuesta API estandarizada y utilidades comunes para el ecosistema ERP.

[![CI Status](https://img.shields.io/github/actions/workflow/acme/erp-shared-libs/ci.yml?branch=main)](https://github.com/acme/erp-shared-libs/actions) [![PyPI version](https://img.shields.io/pypi/v/erp-shared)](https://pypi.org/project/erp-shared/) [![Coverage](https://img.shields.io/codecov/c/github/acme/erp-shared-libs)](https://codecov.io/gh/acme/erp-shared-libs) [![License: MIT](https://img.shields.io/github/license/acme/erp-shared-libs)](./LICENSE)

## Stack tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Runtime | Python | 3.12+ |
| Lenguaje | Python | 3.12+ |
| Empaquetado | setuptools / poetry | 2.0+ |
| Test runner | pytest | 8.x |

## Instalación como dependencia

```bash
pip install erp-shared
```

## Uso

### ApiResponse estandarizada

```python
from erp_shared import ApiResponse, PaginatedResponse

# Respuesta exitosa
ok = ApiResponse.success({"id": "ord-0001", "total": 1500})

# Respuesta paginada
page = PaginatedResponse.of(items, page=1, size=20, total=150)

# Respuesta de error
err = ApiResponse.error("NOT_FOUND", "Orden no encontrada", 404)
```

### Contratos y tipos

```python
from erp_shared import OrderDto, OrderStatus

order = OrderDto(
    id="ord-0001",
    status=OrderStatus.CONFIRMED,
    total=1500,
    created_at="2026-05-30T10:00:00Z",
)
```

## API Reference

> Documentación completa de tipos: [Sphinx docs](https://acme.github.io/erp-shared-libs/)

| Export | Tipo | Descripción |
|--------|------|-------------|
| `ApiResponse` | Class | Wrapper estandarizado de respuestas |
| `PaginatedResponse` | Class | Respuesta paginada con metadata |
| `OrderDto` | Class | DTO de orden |
| `OrderStatus` | Enum | Estados de orden |
| `ErrorCode` | Enum | Catálogo de errores ERP |

## Estructura del proyecto

```
erp-shared-libs/
├── src/
│   └── erp_shared/
│       ├── api_response.py      # ApiResponse y PaginatedResponse
│       ├── contracts/            # DTOs y enums compartidos
│       ├── errors/               # ErrorCode y error handling
│       └── __init__.py           # Barrel export
├── tests/
│   ├── test_api_response.py
│   └── test_contracts.py
├── pyproject.toml
├── CHANGELOG.md
└── README.md
```

## Testing

```bash
pytest                                    # Todos los tests
pytest --cov=src --cov-report=html        # Con cobertura
```

## Publicación

```bash
python -m build                           # Build del paquete
pip install -e .                          # Instalación local
poetry publish                            # Publica en PyPI
```

> La publicación se realiza automáticamente vía CI en merge a `main`.

## Enlaces

- [CHANGELOG](./CHANGELOG.md)
- [Sphinx docs](https://acme.github.io/erp-shared-libs/)
- [PyPI package](https://pypi.org/project/erp-shared/)

## Licencia

MIT — ver [LICENSE](./LICENSE).
```

### Ejemplo 3 — API Backend (Bun/TypeScript)

Para un módulo `erp-inventory-api` con stack Bun, el README resultante:

```markdown
# ERP-inventory-api

> Microservicio de inventario para el vertical ERP.
> Gestiona stock, movimientos y reservas con eventos a Kafka. Implementado en Bun/TypeScript.

[![CI Status](https://img.shields.io/github/actions/workflow/acme/erp-inventory-api/ci.yml?branch=main&label=CI)](https://github.com/acme/erp-inventory-api/actions) [![Coverage](https://img.shields.io/codecov/c/github/acme/erp-inventory-api)](https://codecov.io/gh/acme/erp-inventory-api) [![Version](https://img.shields.io/github/v/tag/acme/erp-inventory-api?label=version)](https://github.com/acme/erp-inventory-api/releases) [![License: MIT](https://img.shields.io/github/license/acme/erp-inventory-api)](./LICENSE)

## Stack tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Runtime | Bun | 1.1+ |
| Lenguaje | TypeScript | 5.4+ |
| Framework | Hono (o Elysia) | 4.x |
| Base de datos | PostgreSQL 16 | 16.x |
| ORM / Query | Drizzle ORM | 0.30+ |
| Colas / Eventos | Kafka (kafkajs) | 3.x |
| Auth | Keycloak / OAuth2 / JWT | — |
| Test runner | Vitest | 1.x |

## Prerrequisitos

- Bun 1.1+ — [descargar](https://bun.sh)
- PostgreSQL 16 o Docker para levantar la BD
- Kafka 3.x (opcional, para eventos de inventario)

## Instalación y arranque local

```bash
git clone https://github.com/acme/erp-inventory-api.git
cd erp-inventory-api
bun install                # Instala dependencias
cp .env.example .env       # Configurar variables locales
docker compose up -d       # Levanta PostgreSQL + Kafka
bun run db:migrate         # Ejecuta migraciones (Drizzle Kit)
bun run dev                # Arranca en http://localhost:3001
```

Documentación interactiva: `http://localhost:3001/swagger` (Scalar/Hono Swagger).

### `tsconfig.json` (referencia)

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "types": ["bun-types"],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src"]
}
```

## Variables de entorno

| Variable | Requerida | Tipo | Default | Descripción |
|----------|-----------|------|---------|-------------|
| `DATABASE_URL` | Sí | `string` | — | Connection string PostgreSQL |
| `KAFKA_BROKERS` | No | `string` | `localhost:9092` | Brokers Kafka (CSV) |
| `PORT` | No | `int` | `3001` | Puerto de escucha |
| `LOG_LEVEL` | No | `enum` | `info` | Nivel de logging |
| `KEYCLOAK_URL` | Sí | `string` | — | URL del realm Keycloak |
| `KEYCLOAK_CLIENT_ID` | Sí | `string` | — | Client ID |
| `KEYCLOAK_CLIENT_SECRET` | Sí | `string` | — | Secret (confidential client) |
| `OAUTH2_AUDIENCE` | No | `string` | `erp-inventory-api` | Audience esperada del JWT |

## Referencia de endpoints

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/api/v1/inventory` | Listar items (paginado) | Sí |
| `POST` | `/api/v1/inventory/:id/movement` | Registrar movimiento | Sí |
| `GET` | `/api/v1/inventory/:id/stock` | Stock actual | Sí |

> Spec completa: [OpenAPI](./docs/openapi.yaml)

## Estructura del proyecto

```
erp-inventory-api/
├── src/
│   ├── index.ts                # Entry point (Hono app)
│   ├── routes/                 # API routes
│   ├── services/               # Business logic
│   ├── db/                     # Drizzle schema + client
│   └── events/                 # Kafka producers/consumers
├── tests/
├── drizzle/                    # Migraciones
├── tsconfig.json
├── package.json
├── .env.example
├── CHANGELOG.md
└── README.md
```

## Testing

```bash
bun test                       # Todos los tests
bun test --coverage            # Con cobertura
bun run test:e2e               # E2E
```

## Enlaces

- [OpenAPI Spec](./docs/openapi.yaml)
- [CHANGELOG](./CHANGELOG.md)
- [Arquitectura](./docs/architecture.md)

## Licencia

MIT — ver [LICENSE](./LICENSE).
```

### Ejemplo 4 — Frontend (React)

Para un módulo `erp-portal-web` con React, el README resultante:

```markdown
# ERP-portal-web

> SPA del portal ERP: órdenes, inventario y administración.
> React 18 (function components + hooks) + Vite, code-splitting por feature (`React.lazy`), auth vía Keycloak/OAuth2.

[![CI Status](https://img.shields.io/github/actions/workflow/acme/erp-portal-web/ci.yml?branch=main&label=CI)](https://github.com/acme/erp-portal-web/actions) [![Coverage](https://img.shields.io/codecov/c/github/acme/erp-portal-web)](https://codecov.io/gh/acme/erp-portal-web) [![Version](https://img.shields.io/github/v/tag/acme/erp-portal-web?label=version)](https://github.com/acme/erp-portal-web/releases) [![License: MIT](https://img.shields.io/github/license/acme/erp-portal-web)](./LICENSE)

## Stack tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Framework | React | 18+ |
| UI | Radix UI / shadcn/ui | — |
| Lenguaje | TypeScript | 5.4+ |
| Build | Vite | 5+ |
| Estado | Zustand | — |
| Data fetching | @tanstack/react-query | — |
| i18n | react-i18next | 15+ |
| Auth | Keycloak / OAuth2 (keycloak-js + PKCE) | — |
| Test runner | Vitest + React Testing Library | — |
| E2E | Playwright | 1.x |

## Prerrequisitos

- Node.js 20+ y npm (o Bun 1.1+ como package manager)
- Vite 5+ — `npm create vite@latest`
- Backend API corriendo (ver `erp-orders-api` / `erp-inventory-api`)

## Instalación y arranque local

```bash
git clone https://github.com/acme/erp-portal-web.git
cd erp-portal-web
npm install                 # o: bun install
cp .env.example .env.local  # Configurar API URL y Keycloak
npm run dev                 # Arranca en http://localhost:5173
```

> Alternativa con Bun: `bunx vite`.

### `vite.config.ts` (snippet relevante)

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
```

> Para theming con shadcn/ui: configurar `tailwind.config.ts` y registrar los tokens de diseño en `src/styles/globals.css`.

## Variables de entorno

Configuradas en `.env.local` (dev) y `.env.production` (prod), leídas vía `import.meta.env` e inyectadas en build time:

| Variable | Requerida | Tipo | Default | Descripción |
|----------|-----------|------|---------|-------------|
| `VITE_API_URL` | Sí | `string` | `http://localhost:8000` | URL base del backend API |
| `VITE_KEYCLOAK_URL` | Sí | `string` | — | URL del realm Keycloak |
| `VITE_KEYCLOAK_REALM` | Sí | `string` | `erp` | Realm |
| `VITE_KEYCLOAK_CLIENT_ID` | Sí | `string` | `erp-portal-web` | Client ID (public, PKCE) |
| `VITE_KEYCLOAK_SCOPES` | No | `string` | `openid profile email` | Scopes |
| `VITE_PRODUCTION` | Sí | `boolean` | `false` | Flag de build de producción |

> El client del SPA es **public** (PKCE). Nunca incluir `clientSecret` en el bundle React.

## Rutas y pantallas

| Ruta | Pantalla | Code-split | Guard |
|------|----------|------|-------|
| `/login` | Login (Keycloak redirect) | Sí | `<PublicRoute>` |
| `/orders` | Listado de órdenes | Sí | `<RequireAuth>` + `<RequireRole role="orders:read">` |
| `/orders/:id` | Detalle de orden | Sí | `<RequireAuth>` |
| `/inventory` | Inventario | Sí | `<RequireAuth>` + `<RequireRole role="inventory:read">` |
| `/admin` | Administración | Sí | `<RequireAuth>` + `<RequireRole role="admin">` |

## Estructura del proyecto

```
erp-portal-web/
├── src/
│   ├── core/                   # Auth, apiFetch, guards, layout
│   ├── features/
│   │   ├── orders/              # Components + routes + hooks
│   │   └── inventory/
│   ├── shared/                 # UI components, hooks, utils
│   ├── App.tsx                  # Providers (QueryClient, Router)
│   ├── routes.tsx               # React.lazy + Suspense routes
│   └── main.tsx
├── .env.example
├── .env.local
├── vite.config.ts
├── tsconfig.json
├── package.json
├── CHANGELOG.md
└── README.md
```

## Testing

```bash
vitest run                    # Unit tests (Vitest + React Testing Library)
npx playwright test           # E2E (Playwright)
vite build                    # Build de producción
```

## Enlaces

- [CHANGELOG](./CHANGELOG.md)
- [Arquitectura](./docs/architecture.md)
- [Design System](./docs/design-system.md)

## Licencia

MIT — ver [LICENSE](./LICENSE).
```

## Checklist final de la skill

Antes de cerrar la activación de esta skill, verificar:

- [ ] **Tipo de módulo identificado**: El README corresponde al tipo correcto (API, frontend, library, infra, pack) con las secciones obligatorias correspondientes.
- [ ] **Quickstart verificado**: Las instrucciones de instalación y arranque se han ejecutado en un entorno limpio y funcionan sin errores.
- [ ] **Variables de entorno completas**: Todas las variables requeridas y opcionales están documentadas con tipo, default y ejemplo. Existe `.env.example` sincronizado.
- [ ] **Sin duplicación**: Ningún contenido del README existe idéntico en otro archivo. Todo contenido detallado está enlazado, no copiado.
- [ ] **Badges funcionales**: Todos los badges apuntan a URLs reales. No hay placeholders rotos ni badges de servicios no configurados.
- [ ] **Consistencia cross-módulo**: Los otros módulos del mismo vertical siguen la misma plantilla y orden de secciones.
- [ ] **Ejemplos accionables**: Los ejemplos de uso (curl, import, comandos) usan datos realistas del proyecto y son copiables sin modificación.
- [ ] **Longitud adecuada**: El README no supera las 300 líneas. Contenido adicional se extrae a `docs/` y se enlaza.