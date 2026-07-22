---
name: authorization
description: 'Authorization patterns: permission models, role-based access control
  (RBAC), resource-level access, and frontend permission rendering. Uses FastAPI Depends for RBAC.
  Trigger: When implementing permissions, roles, or access control.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - backend
  - frontend
  enforcement: mandatory
  depends_on:
  - authentication
  - security
  consumed_by:
  - backend-api
  - react
  agent_roles:
  - design-agent
  - control-agent
  validation_profile: security-review
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Authorize server-side always | ALWAYS | Client-side is bypassable |
| Use centralized permission check | ALWAYS | No scattered `if (role == ...)` |
| Return 403 for insufficient permissions | ALWAYS | Consistent HTTP semantics |
| Never expose permission details in error messages | NEVER | Information disclosure |
| Frontend: hide UI elements based on permissions | ALWAYS | UX; not a security control |

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `authentication` | Predecesora | Authentication verifica la identidad. Authorization usa esa identidad para decidir permisos. |
| `security` | Complementaria | Authorization maneja RBAC y permisos. Security maneja protección general (CORS, CSP). |
| `framework-security` | Predecesora | Governance de seguridad. Authorization implementa el RBAC que framework-security define. |

## When to use this skill

Activate this skill when:
- Setting up RBAC (Role-Based Access Control) patterns
- Implementing permission-based access (resource:action naming)
- Configuring resource-level authorization (ownership checks)
- Setting up hierarchical access patterns in PostgreSQL
- Implementing frontend permission rendering (Can directives, route guards)
- Configuring multi-tenant data isolation in queries
- Setting up centralized permission checkers in FastAPI

Do not activate when:
- Implementing login/logout flows → use `authentication`
- Setting up CORS, CSP, or security headers → use `security`
- Designing governance-level security policies → use `framework-security`

## Authorization Models

| Model | Description | Best For |
|-------|-------------|----------|
| RBAC | Roles → Permissions | Simple role-based systems |
| ABAC | Attributes (context) → Decision | Complex, dynamic access rules |
| Permission-based | Fine-grained actions on resources | Flexible enterprise apps |
| Ownership-based | User owns the resource | User-generated content |
| Hierarchical | Org-level → Department → User | Org-chart access |

## RBAC Pattern (Python FastAPI)

```python
from fastapi import Depends, HTTPException, status

def require_permission(permission: str):
    def dependency(current_user: dict = Depends(get_current_user)):
        if permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "AUTH_001",
                    "message": "Insufficient permissions",
                    "required": permission
                }
            )
        return current_user
    return dependency

@router.post("/entities", dependencies=[Depends(require_permission("entities:write"))])
async def create_entity(request: CreateEntityRequest): ...

# For endpoints that require the user object:
@router.get("/entities")
async def list_entities(user: dict = Depends(require_permission("entities:read"))):
    return await service.list(tenant_id=user["tenant_id"])
```

## Resource-Level Authorization

```python
async def update_entity(entity_id: int, data: UpdateDto, current_user: dict):
    entity = await repo.find_by_id(entity_id)
    if entity.created_by != current_user["user_id"]:
        raise HTTPException(status_code=403, detail={
            "code": "AUTH_003",
            "message": "Insufficient permissions for resource"
        })
    if entity.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=403, detail={
            "code": "AUTH_003",
            "message": "Cross-tenant access denied"
        })
    return await repo.update(entity_id, data)
```

## Hierarchical Access Pattern (PostgreSQL)
```sql
-- 1. Self-access check
-- 2. Admin/elevated role check
-- 3. Same org-unit check
-- 4. Hierarchy descendant check (CTE)
CREATE OR REPLACE FUNCTION auth.check_hierarchical_access(
    p_user_id UUID,
    p_resource_tenant_id UUID,
    p_org_unit_id INT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_has_permission BOOLEAN := FALSE;
BEGIN
    -- Self-access
    IF p_user_id = current_setting('app.current_user_id')::UUID THEN
        RETURN TRUE;
    END IF;
    
    -- Admin role check
    IF EXISTS (
        SELECT 1 FROM user_roles ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = p_user_id AND r.name = 'Admin'
    ) THEN
        RETURN TRUE;
    END IF;
    
    -- Same org-unit check
    IF EXISTS (
        SELECT 1 FROM user_org_units
        WHERE user_id = p_user_id AND org_unit_id = p_org_unit_id
    ) THEN
        RETURN TRUE;
    END IF;
    
    -- Hierarchy descendant check (recursive CTE)
    WITH RECURSIVE org_tree AS (
        SELECT id, parent_id FROM org_units WHERE id = p_org_unit_id
        UNION ALL
        SELECT ou.id, ou.parent_id 
        FROM org_units ou
        INNER JOIN org_tree ot ON ou.parent_id = ot.id
    )
    SELECT EXISTS (
        SELECT 1 FROM user_org_units uou
        WHERE uou.user_id = p_user_id 
        AND uou.org_unit_id IN (SELECT id FROM org_tree)
    ) INTO v_has_permission;
    
    RETURN v_has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Permission Naming Convention
```
{resource}:{action}
Examples:
  entities:read
  entities:write
  entities:delete
  admin:users:manage
```

## Error Codes
| Code | HTTP | Meaning |
|------|------|---------|
| `AUTH_001` | 403 | Unauthorized (no permission) |
| `AUTH_002` | 401 | Token expired |
| `AUTH_003` | 403 | Insufficient permissions for resource |

## Patrones de autorización

### Python FastAPI

```python
# 1. Dependencia reutilizable para verificación de permisos
from fastapi import Depends, HTTPException, status
from typing import List

class PermissionChecker:
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    async def __call__(self, current_user: dict = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        for perm in self.required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "AUTH_001",
                        "message": "Permiso insuficiente",
                        "required": perm
                    }
                )
        return current_user

# Uso en rutas
@router.get("/entities", dependencies=[Depends(PermissionChecker(["entities:read"]))])
async def list_entities(page: int = 1, user: dict = Depends(get_current_user)):
    return await service.list_entities(tenant_id=user["tenant_id"], page=page)

@router.post("/entities", dependencies=[Depends(PermissionChecker(["entities:write"]))])
async def create_entity(data: CreateEntityRequest, user: dict = Depends(get_current_user)):
    return await service.create(data, created_by=user["user_id"])

# 2. Clases de permisos personalizadas — enfoque OOP
class BasePermission:
    async def has_permission(self, user: dict, action: str, resource: dict = None) -> bool:
        raise NotImplementedError

class IsOwner(BasePermission):
    async def has_permission(self, user: dict, action: str, resource: dict = None) -> bool:
        if resource is None:
            return False
        return resource.get("created_by") == user["user_id"]

class IsTenantMember(BasePermission):
    async def has_permission(self, user: dict, action: str, resource: dict = None) -> bool:
        if resource is None:
            return False
        return resource.get("tenant_id") == user["tenant_id"]

# 3. Decorador de verificación de roles
from functools import wraps

def require_roles(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            if current_user.get("role") not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"code": "AUTH_001", "message": "Role not authorized"}
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@router.get("/admin/users")
@require_roles(["admin", "super_admin"])
async def admin_list_users(current_user: dict = Depends(get_current_user)):
    return await service.list_all_users()
```

## Autorización a nivel de recurso

La autorización a nivel de recurso (resource-level authorization) va más allá del RBAC tradicional. Mientras que RBAC responde "¿puede este rol hacer X?", la autorización por recurso responde "¿puede **este usuario específico** hacer X sobre **este recurso concreto**?"

Esto es esencial cuando:
- Un usuario solo puede editar sus propios registros (ownership)
- Un gerente solo puede ver empleados de su departamento
- Un tenant solo puede acceder a datos de su propio tenant (multi-tenancy)
- Existen jerarquías organizacionales que determinan acceso

### Ejemplo Python

```python
# Python — Verificación explícita en service layer
async def update_entity(entity_id: int, data: UpdateDto, current_user: dict):
    entity = await repo.find_by_id(entity_id)
    if entity.created_by != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "AUTH_003", "message": "Not the owner of this resource"}
        )
    if entity.tenant_id != current_user["tenant_id"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "AUTH_003", "message": "Cross-tenant access denied"}
        )
    return await repo.update(entity_id, data)
```

### Filtrado multi-tenant con tenant_id en claims

El tenant_id debe estar presente en el token JWT y propagarse a todos los queries:

```python
# Python — Filtro automático por tenant via middleware
@router.get("/entities")
async def list_entities(
    current_user: dict = Depends(get_current_user),
    repo: EntityRepository = Depends()
):
    # El tenant_id se extrae del token y se pasa automáticamente
    entities = await repo.find_by_tenant(current_user["tenant_id"])
    return entities
```

### Validación en base de datos

Para evitar incluso la consulta cuando no hay permiso, las funciones PL/pgSQL pueden incluir el tenant_id como filtro:

```sql
CREATE OR REPLACE FUNCTION core.list_entities(
    p_tenant_id UUID,
    p_user_id UUID,
    p_page_number INT DEFAULT 1,
    p_page_size INT DEFAULT 20
)
RETURNS TABLE (
    id INT,
    name VARCHAR(255),
    created_by UUID,
    created_at TIMESTAMPTZ,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.name,
        e.created_by,
        e.created_at,
        COUNT(*) OVER() AS total_count
    FROM core.entities e
    WHERE e.tenant_id = p_tenant_id
      AND (e.created_by = p_user_id OR EXISTS (
          SELECT 1 FROM user_roles ur
          JOIN roles r ON ur.role_id = r.id
          WHERE ur.user_id = p_user_id AND r.name = 'Admin'
      ))
    ORDER BY e.created_at DESC
    LIMIT p_page_size
    OFFSET (p_page_number - 1) * p_page_size;
END;
$$ LANGUAGE plpgsql STABLE;
```

**Alternativa: SQLAlchemy con paginación segura**

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

async def list_entities(
    db: AsyncSession,
    tenant_id: str,
    user_id: str,
    page: int = 1,
    page_size: int = 20
):
    # Subquery para verificar permisos (admin o owner)
    permission_subquery = (
        select(1)
        .join(UserRole, UserRole.user_id == user_id)
        .join(Role, Role.id == UserRole.role_id)
        .where(Role.name == 'Admin')
    ).exists()
    
    query = (
        select(Entity)
        .where(
            Entity.tenant_id == tenant_id,
            (Entity.created_by == user_id) | permission_subquery
        )
        .order_by(Entity.created_at.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    
    result = await db.execute(query)
    return result.scalars().all()
```

## Frontend Permission Rendering

La autorización en frontend **no es un control de seguridad** (es evitable desde el cliente). Su propósito es mejorar la experiencia de usuario ocultando acciones que el backend rechazaría.

### Store de autenticación y permisos (Zustand)

```typescript
// core/auth/auth.store.ts
import { create } from 'zustand';

export interface AuthUser {
  user_id: string;
  tenant_id: string;
  role: string;
  permissions: string[];
}

export type Action = 'create' | 'read' | 'update' | 'delete' | 'manage';
export type Resource = 'Entity' | 'User' | 'Report' | 'all';

interface AuthState {
  user: AuthUser | null;
  isLoggedIn: boolean;
  login: (user: AuthUser) => void;
  logout: () => void;
  can: (action: Action, resource: Resource) => boolean;
  hasPermission: (permission: string) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoggedIn: false,

  login: (user) => set({ user, isLoggedIn: true }),
  logout: () => set({ user: null, isLoggedIn: false }),

  can: (action, resource) => {
    const { user } = get();
    if (!user) return false;
    if (user.role === 'admin') return true; // Admin tiene todos los permisos

    const permission = `${resource.toLowerCase()}:${action === 'manage' ? 'manage' : action}`;
    return user.permissions?.includes(permission) ?? false;
  },

  hasPermission: (permission) => get().user?.permissions?.includes(permission) ?? false,
}));
```

### Componente `Can`

```tsx
// shared/components/Can.tsx
import type { ReactNode } from 'react';
import { useAuthStore } from '../../core/auth/auth.store';
import type { Action, Resource } from '../../core/auth/auth.store';

interface CanProps {
  action: Action;
  resource: Resource;
  children: ReactNode;
  fallback?: ReactNode;
}

export function Can({ action, resource, children, fallback = null }: CanProps) {
  const can = useAuthStore((s) => s.can(action, resource));
  return can ? <>{children}</> : <>{fallback}</>;
}
```

**Uso:**

```tsx
<Can action="update" resource="Entity">
  <button onClick={() => edit(entity)}>Editar</button>
</Can>

<Can action="delete" resource="Entity">
  <button onClick={() => remove(entity)}>Eliminar</button>
</Can>
```

### Renderizado condicional con hook

```typescript
// core/auth/use-has-permission.ts
import { useAuthStore } from './auth.store';

export function useHasPermission(permission: string): boolean {
  return useAuthStore((s) => s.hasPermission(permission));
}
```

**Uso:**

```tsx
const canEdit = useHasPermission('entities:write');
const canDelete = useHasPermission('entities:delete') || isOwner;

return (
  <>
    {canEdit && <button onClick={edit}>Editar</button>}
    {canDelete && <button onClick={remove}>Eliminar</button>}
  </>
);
```

### Route Guards (react-router-dom)

```tsx
// core/auth/RequirePermission.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from './auth.store';
import type { Action, Resource } from './auth.store';

export function RequirePermission({ action, resource }: { action: Action; resource: Resource }) {
  const can = useAuthStore((s) => s.can(action, resource));
  return can ? <Outlet /> : <Navigate to="/unauthorized" replace />;
}

// Uso en rutas (router.tsx)
const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      {
        element: <RequirePermission action="read" resource="Entity" />,
        children: [{ path: 'entities', element: <EntityList /> }],
      },
      {
        element: <RequirePermission action="update" resource="Entity" />,
        children: [{ path: 'entities/:id/edit', element: <EntityEdit /> }],
      },
      {
        element: <RequirePermission action="manage" resource="all" />,
        children: [{ path: 'admin', element: <AdminPanel /> }],
      },
    ],
  },
]);
```

### Tabla resumen: responsabilidades frontend vs backend

| Aspecto | Frontend | Backend |
|---------|----------|---------|
| Ocultar botones/acciones | Sí (UX) | No aplica |
| Validar permiso en cada request | No (redundante) | Sí (obligatorio) |
| Redirigir a login/403 | Sí (routing) | No aplica |
| Decidir si ejecutar acción | No | Sí (autoridad final) |
| Cachear permisos del usuario | Sí (store Zustand) | Sí (token/DB) |
| Retornar 403 | No | Sí |
