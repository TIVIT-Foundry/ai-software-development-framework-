---
name: react
description: 'React component architecture: function components, hooks, context, routing (react-router-dom), code-splitting, Vite/Next.js project structure. Trigger: When creating React features, components, routing, or project structure.'
version: 2.0
metadata:
  phase:
    - construction
  layer:
    - frontend
  enforcement: mandatory
  depends_on:
    - design-system
    - typescript
  consumed_by:
    - accesibilidad
    - agent-frontend
    - agent-fullstack
    - api-first-frontend
    - feature-flags
    - i18n
    - microfrontend
    - mobile-pwa
    - react-doctor
    - react-services
    - react-upgrade
    - unit-testing
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define the architecture and conventions for React applications in the framework. Covers function components, hooks (`useState`, `useMemo`, `useCallback`, `useEffect`), context, routing, code-splitting, and project structure. This skill replaces the former `angular` skill to align with the company's React stack (see ADR-004).

## Variant selection

"React" in this framework means React with one of two accepted variants — pick per project, not per component:

| Variant | When to use | Routing | Build |
|---------|-------------|---------|-------|
| **React + Vite (default)** | Internal CRUD/admin apps, dashboards — same profile Angular covered before | `react-router-dom` | Vite |
| **Next.js (App Router)** | Public-facing pages needing SSR/SSG, SEO, or ISR | File-based routing | Next.js |

The scaffold generator (`.opencode/scaffold/`) emits Vite + React by default. Next.js is a documented alternative, not auto-scaffolded — pick it explicitly when the project needs server rendering.

## When to use this skill

Activate this skill when:

- Creating new React components, hooks, or project structure
- Designing routing (lazy-loaded routes, guards, loaders)
- Implementing function components with hooks
- Setting up a Vite or Next.js project structure
- Working with Context, `useReducer`, or Zustand for state
- Configuring code-splitting (`React.lazy` + `Suspense`)
- Implementing forms (`react-hook-form`)

**Do not** activate when:

- Creating backend APIs (use `backend-api` or `api-first-backend`)
- Working with Python/FastAPI (use `app-bootstrap`)
- Creating only TypeScript types without React (use `typescript`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|--------------|
| `typescript` | Predecesora | TypeScript patterns are the foundation for React |
| `design-system` | Complementaria | Design tokens (CSS custom properties) applied to React components |
| `react-services` | Complementaria | Data fetching, TanStack Query, Zustand stores |
| `api-first-frontend` | Consumidora | Generates React components from OpenAPI spec |
| `accesibilidad` | Complementaria | ARIA patterns applied to JSX |
| `i18n` | Complementaria | Translation integration with react-i18next |
| `microfrontend` | Complementaria | Module Federation for React |

## Critical Rules

1. **Function components only** — No class components. Every component is a typed function.
2. **Hooks for state and lifecycle** — `useState`/`useReducer` for local state, `useEffect` for side effects, never lifecycle classes.
3. **TanStack Query for server state, not `useEffect` fetch** — Server data goes through `react-services` hooks, never raw `fetch()` inside a component body.
4. **`useMemo`/`useCallback` deliberately** — Only to stabilize referentially-expensive values/handlers passed to memoized children or effect deps, not by default on everything.
5. **Code-splitting mandatory for routes** — Every route component is loaded via `React.lazy()` (Vite) or is a route segment (Next.js `app/`), never eagerly bundled.
6. **Props are explicitly typed** — No `any`; use `interface Props` or inline typed destructuring.

## What the agent must do

1. **Create typed function components** — `function UserCard({ user, onSelect }: UserCardProps)`
2. **Split local vs server state** — `useState` for UI-only state, `react-services` hooks for anything from the API
3. **Memoize deliberately** — `useMemo`/`useCallback` only where profiling or a memoized child justifies it
4. **Lazy-load routes** — `React.lazy(() => import(...))` wrapped in `<Suspense>`
5. **Follow naming conventions** — `PascalCase.tsx` for components, `use{Thing}.ts` for hooks, `{thing}.types.ts` for types
6. **Use Radix UI primitives** — For overlays, dialogs, dropdowns, virtualized lists where applicable instead of hand-rolling accessibility

## Inputs expected

| Input | Source | Required | Description |
|-------|--------|----------|--------------|
| Feature requirements | user/hu-template | Yes | What the component must do |
| API spec | api-first-spec | No | OpenAPI spec for data models |
| Design tokens | design-system | No | Visual tokens for styling |
| TypeScript types | typescript | No | Type definitions |

## Outputs produced

| Artifact | Format | Description |
|----------|--------|--------------|
| Component file | `*.tsx` | Function component, typed props |
| Route module | `*.routes.tsx` (Vite) or `app/**/page.tsx` (Next.js) | Lazy-loaded route definitions |
| Styles | `*.module.css` or CSS custom properties | Component-scoped styling |

## Code patterns

### Function Component

```tsx
import { useMemo } from 'react';

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  avatar?: string;
  roles: { id: string; name: string }[];
}

interface UserCardProps {
  user: User;
  selected?: boolean;
  onSelect: (user: User) => void;
}

export function UserCard({ user, selected = false, onSelect }: UserCardProps) {
  const fullName = useMemo(() => `${user.firstName} ${user.lastName}`, [user.firstName, user.lastName]);

  return (
    <div className={`user-card${selected ? ' selected' : ''}`}>
      <h3>{fullName}</h3>
      <p>{user.email}</p>

      {user.avatar ? (
        <img src={user.avatar} alt={fullName} />
      ) : (
        <div className="avatar-placeholder">{user.firstName[0]}</div>
      )}

      {user.roles.map((role) => (
        <span className="badge" key={role.id}>{role.name}</span>
      ))}

      <button onClick={() => onSelect(user)}>Select</button>
    </div>
  );
}
```

### Local State with Hooks

```tsx
import { useMemo, useState } from 'react';

interface UserListProps {
  users: User[];
}

export function UserList({ users }: UserListProps) {
  const [filter, setFilter] = useState('');

  const filteredUsers = useMemo(() => {
    const term = filter.toLowerCase();
    return users.filter((u) => `${u.firstName} ${u.lastName}`.toLowerCase().includes(term));
  }, [users, filter]);

  return (
    <div>
      <input value={filter} onChange={(e) => setFilter(e.target.value)} placeholder="Filter users" />
      <p>{filteredUsers.length} of {users.length}</p>
      {filteredUsers.map((u) => (
        <UserCard key={u.id} user={u} onSelect={() => {}} />
      ))}
    </div>
  );
}
```

### Lazy-Loaded Routes (Vite + react-router-dom)

```tsx
import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const UserListPage = lazy(() => import('./pages/UserListPage'));
const UserDetailPage = lazy(() => import('./pages/UserDetailPage'));
const UserEditPage = lazy(() => import('./pages/UserEditPage'));

const withSuspense = (element: JSX.Element) => <Suspense fallback={<div>Loading...</div>}>{element}</Suspense>;

const router = createBrowserRouter([
  { path: '/users', element: withSuspense(<UserListPage />) },
  { path: '/users/:id', element: withSuspense(<UserDetailPage />) },
  { path: '/users/:id/edit', element: withSuspense(<UserEditPage />) },
]);

export function App() {
  return <RouterProvider router={router} />;
}
```

### Route Segment (Next.js App Router alternative)

```tsx
// app/users/[id]/page.tsx
export default async function UserDetailPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id); // server component: direct data access, no client fetch
  return <UserDetail user={user} />;
}
```

### Reactive Forms (react-hook-form + zod)

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const userFormSchema = z.object({
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
  email: z.string().email(),
});

type UserFormValues = z.infer<typeof userFormSchema>;

export function UserForm({ onSubmit }: { onSubmit: (values: UserFormValues) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<UserFormValues>({
    resolver: zodResolver(userFormSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('firstName')} />
      {errors.firstName && <span>{errors.firstName.message}</span>}
      <input {...register('lastName')} />
      {errors.lastName && <span>{errors.lastName.message}</span>}
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      <button type="submit">Save</button>
    </form>
  );
}
```

### Fetch Wrapper with Auth Header

```ts
import { useAuthStore } from './auth.store';

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = useAuthStore.getState().token;

  const res = await fetch(`/api${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });

  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}
```

### Route Guard (Vite)

```tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from './auth.store';

export function RequireAuth() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
```

## File Structure

### Vite (default)

```
src/
├── App.tsx
├── main.tsx
├── router.tsx
├── core/
│   ├── auth/
│   ├── api/
│   └── store/
├── features/
│   └── {feature}/
│       ├── {feature}.routes.tsx
│       ├── pages/
│       │   └── {Page}.tsx
│       └── components/
│           └── {Component}.tsx
└── shared/
    ├── components/
    ├── hooks/
    └── styles/
```

### Next.js (App Router alternative)

```
app/
├── layout.tsx
├── page.tsx
└── {feature}/
    ├── page.tsx
    ├── [id]/
    │   └── page.tsx
    └── components/
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|---------------------|
| Need component state | Class component with `this.state` | `useState()` or `useReducer()` |
| Need to fetch data | `fetch()` inside `useEffect` | `react-services` hook (TanStack Query) |
| Need route protection | Manual redirect in every page | `RequireAuth` wrapper route / middleware (Next.js) |
| Need performance | Wrapping every value in `useMemo` | Memoize only expensive/referentially-sensitive values |
| Need shared state across features | Prop drilling through 4+ levels | Zustand store or Context |
| Need lazy loading | Eager top-level import | `React.lazy()` + `Suspense`, or Next.js route segment |

## Verification checklist

- [ ] Component is a typed function component (no classes)
- [ ] Props interface has no `any`
- [ ] Server data fetched via `react-services` hooks, not raw `fetch` in the component
- [ ] Routes are code-split (`React.lazy` or Next.js segment)
- [ ] Forms use `react-hook-form` + `zod` schema
- [ ] No unnecessary `useMemo`/`useCallback` without a concrete reason
- [ ] Accessible primitives (Radix) used for overlays/dialogs
