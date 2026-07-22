# Scaffolding Generator

Genera scaffolding de proyectos para el stack del **TIVIT Foundry Framework** a partir de un documento `api-first-spec` en markdown.

Stack soportado:

- **Backend:** Python/FastAPI + SQLAlchemy 2.0 async (default) o Bun/TypeScript + Elysia + postgres.js
- **Frontend:** React + Vite (function components, hooks, TypeScript). Next.js es una variante aceptada para proyectos que necesitan SSR/SSG — ver la skill `react` — pero el generador no la scaffoldea automáticamente.
- **Database:** PostgreSQL (CREATE TABLE + funciones PL/pgSQL)
- **Tests:** Playwright E2E

## Uso

```powershell
# Backend Python (default)
python .opencode\scaffold\generate.py spec.md --output .\output

# Backend Bun
python .opencode\scaffold\generate.py spec.md --output .\output --backend bun

# Con namespace y schema personalizados
python .opencode\scaffold\generate.py spec.md --output .\my-module --backend python --namespace "app.mymodule" --schema "app"
```

## Estructura generada

```
output/
├── backend/                    # FastAPI o Bun según --backend
│   ├── python:
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy async engine/session
│   │   ├── {entity}_router.py  # FastAPI CRUD endpoints
│   │   ├── {entity}_service.py # Lógica de negocio
│   │   └── {entity}_schemas.py # Pydantic v2 + SQLAlchemy model
│   └── bun:
│       ├── {entity}.route.ts   # Elysia routes + Zod validation
│       ├── {entity}.service.ts # Lógica de negocio con postgres.js
│       ├── {entity}.dto.ts     # Zod schemas + tipos
│       └── {entity}.db.ts      # Cliente postgres
├── frontend/                   # React (Vite)
│   ├── {entity}.model.ts       # Interfaces TypeScript
│   ├── {entity}.api.ts         # Cliente HTTP tipado (fetch)
│   ├── {entity}-list.tsx       # Componente de lista (toolbar + tabla)
│   ├── {entity}-table.tsx      # Tabla con orden y paginación
│   ├── {entity}-form.tsx       # Formulario controlado
│   ├── {entity}-page.tsx       # Página que orquesta list/form + estado
│   └── index.ts                # Barrel exports
├── database/
│   ├── 001_create_{entity}.sql  # CREATE TABLE
│   └── 002_fn_{entity}_crud.sql # CRUD stored functions
└── tests/
    └── {module}.spec.ts        # Playwright E2E tests
```

## Formato del documento spec

El generador espera un documento markdown con:

- Un título `# Module: Name` (o `# Name`)
- Una sección `## Entity / ERD` con definiciones de entidades en tablas
- Una sección `## Endpoints` con tabla method/path/description
- Una sección opcional `## DTOs / Types` con definiciones request/response

Ver `example-spec.md` para un ejemplo completo.

## Placeholders

Las plantillas usan formato Python `string.Template`:

| Placeholder | Descripción |
|-------------|-------------|
| `$MODULE` | Nombre del módulo en PascalCase |
| `$MODULE_CAMEL` | Nombre del módulo en camelCase |
| `$ENTITY` | Nombre de la entidad en PascalCase |
| `$ENTITIES` | Nombre plural de la entidad en PascalCase |
| `$entity` | Nombre de la entidad en camelCase |
| `$entities` | Nombre plural de la entidad en camelCase |
| `$SCHEMA` | Nombre del schema de base de datos |
| `$TABLE` | Nombre de la tabla (plural snake_case) |

## Plantillas

Las plantillas están en `templates/`:

### Backend Python
- `router.py.j2` - FastAPI endpoints
- `service.py.j2` - Lógica de negocio
- `schemas.py.j2` - Pydantic v2 + SQLAlchemy model
- `database.py.j2` - SQLAlchemy async session

### Backend Bun
- `route.ts.j2` - Elysia routes
- `bun_service.ts.j2` - Lógica de negocio con postgres.js
- `dto.ts.j2` - Zod schemas
- `db.ts.j2` - Cliente postgres

### Frontend React
- `model.ts.j2` - Interfaces TypeScript
- `api.ts.j2` - Cliente HTTP tipado (fetch wrapper), sin dependencias externas
- `component.tsx.j2` - Componente de lista (`{Entity}List`)
- `table.component.tsx.j2` - Componente de tabla con orden/paginación (`{Entity}Table`)
- `form.component.tsx.j2` - Formulario controlado (`{Entity}Form`)
- `page.component.tsx.j2` - Página que orquesta list/form y estado (`{Entity}Page`)
- `index.ts.j2` - Barrel exports

### Database + Tests
- `sql_create.sql.j2` - CREATE TABLE
- `sql_fn.sql.j2` - Funciones PL/pgSQL CRUD
- `sql_sp.sql.j2` - Plantilla de stored procedures (referencia)
- `test.spec.ts.j2` - Playwright E2E test

## Nota sobre React vs Next.js

El generador scaffoldea siempre React + Vite (componentes de función, `fetch` nativo). Si el proyecto necesita SSR/SSG (páginas públicas, SEO), la skill `react` documenta el patrón equivalente con Next.js App Router — la migración de un módulo generado a un route segment de Next.js es manual, no automatizada por este generador.

Para proyectos reales, se recomienda envolver `{entity}.api.ts` con hooks de `@tanstack/react-query` (ver la skill `react-services`) en vez de llamar la API directamente desde los componentes de página — el scaffold genera la versión mínima con `fetch` + `useState` para no forzar una dependencia externa en el output inicial.
