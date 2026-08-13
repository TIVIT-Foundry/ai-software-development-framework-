---
name: api-catalog
description: 'Generate complete API inventory/catalog documenting all endpoints end-to-end.
  Maps: DB object → API Endpoint → Service ID → Frontend Screen → Route. Trigger:
  When documenting APIs, creating service inventory, onboarding docs.'
version: 1.0
metadata:
  phase:
  - operations
  layer:
  - backend
  enforcement: recommended
  depends_on:
  - api-first-spec
  - openapi-docs
  consumed_by:
  - project-bootstrap
  agent_roles:
  - delivery-agent
  - design-agent
  validation_profile: documentation
mcp_usage: none
---

## Purpose
Map: Database (SP/Query) → Backend (Endpoint) → Service ID → Frontend (Screen + Route)

## Data Source Locations
| Source | Location |
|--------|----------|
| DB objects | `database/` or `src/migrations/` |
| Endpoints | `src/{module}/features/` or `src/controllers/` |
| Service IDs | Frontend constants or API config |
| Frontend Routes | `src/app/app.routes.ts` or routing module |

## Naming Convention Mapping
| Endpoint Name | DB Object | Method | Path |
|---------------|-----------|--------|------|
| `List{Entity}` | `List{Entity}` | GET | `/{entities}` |
| `Get{Entity}` | `Get{Entity}` | GET | `/{entities}/{id}` |
| `Create{Entity}` | `Create{Entity}` | POST | `/{entities}` |
| `Update{Entity}` | `Update{Entity}` | PUT | `/{entities}/{id}` |
| `Delete{Entity}` | `Delete{Entity}` | DELETE | `/{entities}/{id}` |

## Screen Name Convention
| Action | Screen Name |
|--------|-------------|
| List | `{Entity} List` |
| Get | `{Entity} Detail` |
| Create | `Create {Entity}` |
| Update | `Edit {Entity}` |
| Delete | — (no screen) |

## Output: `docs/API_CATALOG.md`
The catalog should contain a table with columns:
- Module / Feature
- DB Object name
- HTTP Method + Path
- Service ID (frontend)
- Frontend Screen
- Route

## When to Update
- New endpoint added
- Endpoint path/method changed
- New frontend screen added
- Service ID changed
- Module renamed

## Checklist
- [ ] All endpoints listed
- [ ] All DB objects mapped to endpoints
- [ ] All service IDs mapped to endpoints
- [ ] All frontend screens mapped to routes
- [ ] Index / README updated

## Ejemplo de catálogo

```markdown
# API Catalog — Módulo Users

| DB Object | API Endpoint | Service ID | Frontend Screen | Route |
|-----------|--------------|------------|-----------------|-------|
| `sp_users_list` | `GET /api/users` | `users-service` | UsersList | `/users` |
| `sp_users_get` | `GET /api/users/{id}` | `users-service` | UserDetail | `/users/:id` |
| `sp_users_create` | `POST /api/users` | `users-service` | UserForm | `/users/new` |
| `sp_users_update` | `PUT /api/users/{id}` | `users-service` | UserForm | `/users/:id/edit` |
| `sp_users_delete` | `DELETE /api/users/{id}` | `users-service` | UsersList | `/users` |
| `sp_users_search` | `GET /api/users/search` | `users-service` | UserSearch | `/users?q=` |
```

## Formato de archivo

El catálogo debe vivir en `docs/api-catalog.md` o `docs/modules/{module}/api-catalog.md` y seguir esta convención de columnas:

```yaml
# Frontmatter del archivo de catálogo
module: users
version: 1.0
generated_at: 2026-06-05
generated_by: api-catalog skill
endpoints_count: 6
```

## Proceso de generación del catálogo

### 1. Inputs requeridos

| Input | Origen típico | Ejemplo concreto |
|-------|---------------|------------------|
| `api-first-spec` outputs | `docs/api-specs/{module}.md` | `docs/api-specs/users.md` con ERD, endpoints, DTOs |
| Database schema | `database/schema.sql` o `src/migrations/` | `sp_users_list`, `sp_users_get`, `sp_users_create` |
| Frontend routes | `src/app/app.routes.ts`, `src/router/` o `pages/` | `{ path: 'users', loadComponent: () => import('./pages/users-list/users-list.component').then(m => m.UsersListComponent) }` |
| Service ID mapping | `src/services/{module}/service-id.ts` | `export const USERS_SERVICE_ID = 'users-service'` |

### 2. Algorithm de mapeo

El mapeo sigue **4 pasos encadenados** que convierten datos de base en una vista end-to-end:

```
[Step 1] Por cada SP/Query de la base
   └─> Buscar el handler que lo invoca
       └─> rg "sp_users_list" src/  →  users.py (handler)
           └─> Output: SP → Handler

[Step 2] Por cada Handler encontrado
   └─> Buscar el registro del endpoint (@router.get/@router.post)
       └─> rg "@router.get.*users" src/{module}/routes.py
           └─> Output: Handler → (Method, Path)

[Step3] Por cada Endpoint
   └─> Extraer el Service ID del path pattern (/api/{service}/...)
       └─> /api/users  →  service = "users"  →  Service ID = "users-service"
           └─> Output: Endpoint → Service ID

[Step 4] Por cada Endpoint
   └─> Buscar el hook/component que lo consume
       └─> rg "useGetUsers" src/hooks/  →  src/hooks/users/useGetUsers.ts
            └─> Buscar dónde se usa ese hook  →  users-list.component.ts
               └─> Buscar la ruta de esa página  →  <Route path="/users" />
                   └─> Output: Endpoint → Screen → Route
```

### 3. Output format

El catálogo siempre debe llevar la columna `Auth` para que el equipo de seguridad pueda auditar la exposición:

```markdown
# API Catalog — Módulo Users

| DB Object | API Endpoint | Service ID | Frontend Screen | Route | Auth |
|-----------|--------------|------------|-----------------|-------|------|
| `sp_users_list` | `GET /api/users` | `users-service` | UsersList | `/users` | JWT |
| `sp_users_get` | `GET /api/users/{id}` | `users-service` | UserDetail | `/users/:id` | JWT |
| `sp_users_create` | `POST /api/users` | `users-service` | UserForm | `/users/new` | JWT+Admin |
| `sp_users_update` | `PUT /api/users/{id}` | `users-service` | UserForm | `/users/:id/edit` | JWT+Admin |
| `sp_users_delete` | `DELETE /api/users/{id}` | `users-service` | UsersList | `/users` | JWT+Admin |
| `sp_users_search` | `GET /api/users/search` | `users-service` | UserSearch | `/users?q=` | JWT |
```

### 4. Multi-module catalog

Cuando el catálogo abarca varios módulos:

- Mantén **un índice maestro** en `docs/api-catalog.md` que liste los módulos y linkee al detalle.
- Genera **un archivo por módulo** en `docs/modules/{module}/api-catalog.md`.
- Usa la **misma convención de columnas** en todos los archivos.
- Ordena las filas siempre por `Module` → `Entity` → `Action` (List, Get, Create, Update, Delete, Search).
- Re-genera el índice maestro automáticamente desde los archivos por módulo (ver `Automation tips`).

### 5. Automation tips

#### a) Auto-generar desde la base de datos (PostgreSQL)

```sql
-- Listar todas las funciones del esquema 'app'
SELECT
    n.nspname  AS schema_name,
    p.proname  AS procedure_name,
    pg_get_function_arguments(p.oid) AS arguments
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname = 'app'
  AND p.prokind = 'f'
ORDER BY p.proname;
```

#### c) Parsear OpenAPI para extraer endpoints

```bash
# Extraer paths y métodos desde openapi.json con jq
jq -r '.paths | to_entries[] | .key as $path | .value | to_entries[] |
       "\(.key | ascii_upcase) \($path)"' docs/openapi.json
```

```python
# Script Python para emitir filas del catálogo desde un OpenAPI
import yaml
import re
import sys

spec_path = sys.argv[1] if len(sys.argv) > 1 else "docs/openapi.yaml"
with open(spec_path) as f:
    spec = yaml.safe_load(f)

print("| DB Object | API Endpoint | Service ID | Frontend Screen | Route | Auth |")
print("|-----------|--------------|------------|-----------------|-------|------|")

for path, methods in spec.get("paths", {}).items():
    for method, op in methods.items():
        if method not in ("get", "post", "put", "delete", "patch"):
            continue

        match = re.match(r"^/api/(\w+)", path)
        service = f"{match.group(1)}-service" if match else "unknown"

        op_id = op.get("operationId", "")
        auth = "JWT" if op.get("security") else "Public"
        print(f"| `{op_id}` | `{method.upper()} {path}` | `{service}` | — | — | {auth} |")
```

#### d) Grep en el frontend para encontrar pantallas y rutas

```bash
# 1) Encontrar todos los hooks del módulo users
rg "use(Get|Create|Update|Delete|Search)Users" src/hooks/ -l

# 2) Encontrar qué componente consume cada hook
rg -l "useGetUsers" src/components/ src/pages/

# 3) Extraer la ruta del componente (asume react-router-dom)
rg "path.*users" src/router.tsx
```

```bash
# Ejemplo end-to-end: dado un Service ID, listar componentes que lo usan
SERVICE_ID="users-service"
rg -B 2 -A 2 "import.*$SERVICE_ID|from.*$SERVICE_ID" src/ \
   --type ts --type tsx -n
```

#### e) Orquestador: script bash que arma el catálogo completo

```bash
#!/usr/bin/env bash
# Ejemplo de orquestador: crear scripts/generate-api-catalog.sh en el proyecto
set -euo pipefail

OUT="docs/api-catalog.md"
echo "# API Catalog — Generado $(date +%Y-%m-%d)" > "$OUT"
echo "" >> "$OUT"

for module in users roles auth; do
    spec="docs/api-specs/${module}.md"
    [ -f "$spec" ] || continue

    echo "## Módulo: ${module^}" >> "$OUT"
    echo "" >> "$OUT"
    echo "| DB Object | API Endpoint | Service ID | Frontend Screen | Route | Auth |" >> "$OUT"
    echo "|-----------|--------------|------------|-----------------|-------|------|" >> "$OUT"

    # Parsear endpoints de la sección "## Endpoints" del api-first-spec
    awk '/^## Endpoints/{flag=1;next} /^## /{flag=0} flag && /^\|/{print}' \
        "$spec" >> "$OUT"
    echo "" >> "$OUT"
done

echo "Catálogo generado en $OUT"
```

## Ejemplo de catálogo multi-módulo

Catálogo realista que muestra cómo lucen tres módulos completos (Users, Roles, Auth) con la convención estándar:

```markdown
# API Catalog — Multi-Módulo (Users + Roles + Auth)

> Generado: 2026-06-05
> Total endpoints: 17
> Módulos: 3

## Módulo: Users

| DB Object | API Endpoint | Service ID | Frontend Screen | Route | Auth |
|-----------|--------------|------------|-----------------|-------|------|
| `sp_users_list` | `GET /api/users` | `users-service` | UsersList | `/users` | JWT |
| `sp_users_get` | `GET /api/users/{id}` | `users-service` | UserDetail | `/users/:id` | JWT |
| `sp_users_create` | `POST /api/users` | `users-service` | UserForm | `/users/new` | JWT+Admin |
| `sp_users_update` | `PUT /api/users/{id}` | `users-service` | UserForm | `/users/:id/edit` | JWT+Admin |
| `sp_users_delete` | `DELETE /api/users/{id}` | `users-service` | UsersList | `/users` | JWT+Admin |
| `sp_users_search` | `GET /api/users/search` | `users-service` | UserSearch | `/users?q=` | JWT |
| `sp_users_export` | `GET /api/users/export` | `users-service` | UsersList | `/users` | JWT+Admin |

## Módulo: Roles

| DB Object | API Endpoint | Service ID | Frontend Screen | Route | Auth |
|-----------|--------------|------------|-----------------|-------|------|
| `sp_roles_list` | `GET /api/roles` | `roles-service` | RolesList | `/roles` | JWT+Admin |
| `sp_roles_get` | `GET /api/roles/{id}` | `roles-service` | RoleDetail | `/roles/:id` | JWT+Admin |
| `sp_roles_create` | `POST /api/roles` | `roles-service` | RoleForm | `/roles/new` | JWT+Admin |
| `sp_roles_update` | `PUT /api/roles/{id}` | `roles-service` | RoleForm | `/roles/:id/edit` | JWT+Admin |
| `sp_roles_delete` | `DELETE /api/roles/{id}` | `roles-service` | RolesList | `/roles` | JWT+Admin |
| `sp_roles_assign_permissions` | `POST /api/roles/{id}/permissions` | `roles-service` | RolePermissions | `/roles/:id/permissions` | JWT+Admin |

## Módulo: Auth

| DB Object | API Endpoint | Service ID | Frontend Screen | Route | Auth |
|-----------|--------------|------------|-----------------|-------|------|
| `sp_auth_login` | `POST /api/auth/login` | `auth-service` | LoginPage | `/login` | Public |
| `sp_auth_logout` | `POST /api/auth/logout` | `auth-service` | — | — | JWT |
| `sp_auth_refresh` | `POST /api/auth/refresh` | `auth-service` | — | — | JWT+Refresh |
| `sp_auth_me` | `GET /api/auth/me` | `auth-service` | UserMenu | `/` | JWT |
```

Notas:
- `—` indica que el endpoint no tiene pantalla propia (ej. logout es una acción, no una pantalla).
- `Public` y `JWT+Admin` son los valores de la columna `Auth` según el `authentication`/`authorization` skill.
- El `Service ID` se reutiliza en el frontend como constante de Axios/fetch.

## Integración con docs/

### Ubicación del archivo

| Escenario | Ubicación | Convención de nombre |
|-----------|-----------|----------------------|
| Catálogo único del proyecto (1-2 módulos) | `docs/api-catalog.md` | Un solo archivo raíz |
| Catálogo por módulo (3+ módulos) | `docs/modules/{module}/api-catalog.md` | Un archivo por módulo |
| Índice maestro + detalle (recomendado) | `docs/api-catalog.md` (índice) + `docs/modules/{module}/api-catalog.md` (detalle) | Índice + archivos por módulo |

### Link desde el README raíz

En el `README.md` raíz, agregar una entrada a la sección "Documentación":

```markdown
## Documentación

- [API Catalog](docs/api-catalog.md) — Inventario completo de endpoints DB → Frontend
- [Módulos](docs/modules/)
  - [Users](docs/modules/users/api-catalog.md) — 7 endpoints
  - [Roles](docs/modules/roles/api-catalog.md) — 6 endpoints
  - [Auth](docs/modules/auth/api-catalog.md) — 4 endpoints
```

### Workflow de actualización al agregar un nuevo endpoint

1. **Crear el endpoint** siguiendo `api-first-spec` y `backend-api`.
2. **Agregar la fila** al catálogo en `docs/modules/{module}/api-catalog.md` con todas las columnas.
3. **Regenerar el índice maestro** con el orquestador de ejemplo (bloque e) si aplica.
4. **Validar en CI** que la fila exista (ver bloque siguiente y `framework-qa-validation`).
5. **Commitear ambos cambios** en el mismo PR (endpoint + catálogo).

### Validación en CI

```bash
#!/bin/bash
# Ejemplo de validación CI: crear scripts/validate-api-catalog.sh en el proyecto
set -euo pipefail

ENDPOINTS=$(rg -t py "@router\.(get|post|put|delete|patch)\b" src/ -c 2>/dev/null \
            | awk -F: '{s+=$2} END {print s}')
CATALOG_ROWS=$(rg "^\| \`sp_" docs/api-catalog.md docs/modules/*/api-catalog.md 2>/dev/null \
               | wc -l)

if [ "$ENDPOINTS" -ne "$CATALOG_ROWS" ]; then
  echo "ERROR: $ENDPOINTS endpoints en código vs $CATALOG_ROWS filas en el catálogo"
  echo "Actualiza docs/api-catalog.md antes de hacer merge."
  exit 1
fi

echo "OK: $ENDPOINTS endpoints correctamente documentados en el catálogo."
```

Esta validación se integra en el stage `test` de `ci-cd` y bloquea el merge si hay drift entre código y documentación.
