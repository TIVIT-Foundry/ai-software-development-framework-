---
name: react-services
description: 'React data layer patterns: @tanstack/react-query for server state, Zustand for shared client state, typed fetch wrappers, caching, optimistic updates. Trigger: When implementing React data fetching, hooks, state management, or query/mutation patterns.'
version: 2.0
metadata:
  phase:
    - construction
  layer:
    - frontend
  enforcement: mandatory
  depends_on:
  - react
  - typescript
    - react
    - typescript
  consumed_by:
  - agent-frontend
  - agent-fullstack
  - api-first-frontend
  - export-excel
  - integration-testing
    - api-first-frontend
    - agent-frontend
    - agent-fullstack
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define the patterns for React data fetching, state management, and server/client state separation. Covers `@tanstack/react-query` for server state (queries, mutations, cache invalidation, optimistic updates), Zustand for shared client state, and typed `fetch` wrappers. This skill replaces the former `angular-services` skill to align with the company's React stack (see ADR-004).

## When to use this skill

Activate this skill when:

- Creating data-fetching hooks for a feature
- Implementing HTTP calls with caching and invalidation
- Converting a signal-based Angular store to a Zustand store
- Implementing optimistic updates
- Setting up query caching and invalidation
- Creating reusable data-access layers

**Do not** activate when:

- Creating UI components without data fetching (use `react`)
- Working with Python/FastAPI (use `data-access`)
- Only defining TypeScript types (use `typescript`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|--------------|
| `react` | Predecesora | Component patterns that consume these hooks |
| `typescript` | Predecesora | TypeScript patterns for hook/store contracts |
| `api-first-frontend` | Consumidora | Generates hooks from OpenAPI spec |
| `api-resilience` | Complementaria | Retry/circuit breaker patterns for HTTP |
| `real-time` | Complementaria | WebSocket/SSE hooks |
| `authentication` | Complementaria | Auth token management in the fetch wrapper |

## Critical Rules

1. **Server state via TanStack Query, never `useEffect` + `useState`** — All API reads/writes go through `useQuery`/`useMutation`.
2. **`fetch()` centralized in one client** — Never call `fetch()` directly from a component; always through `apiFetch()`/typed API modules.
3. **Client-only state in Zustand or Context** — Local UI state (`useState`) is fine per-component; state shared across features goes in a Zustand store, not prop drilling.
4. **Error handling mandatory** — Every query/mutation defines `onError` or is unwrapped through an error boundary.
5. **No manual cache bookkeeping** — Use `queryClient.invalidateQueries()`; never mutate cached data by hand outside optimistic-update `onMutate`/`onSettled`.
6. **Type-safe responses** — All hooks typed with the response interface, no `any`.

## What the agent must do

1. **Create query hooks with `useQuery`** — One hook per resource/query-key shape
2. **Create mutation hooks with `useMutation`** — Invalidate related query keys `onSuccess`
3. **Centralize HTTP in `apiFetch()`** — Auth header, error normalization, base URL in one place
4. **Use Zustand for shared state** — `create<Store>()` with selectors, not a giant global object
5. **Implement optimistic updates** — `onMutate`/`onError` rollback/`onSettled` refetch for delete/update flows
6. **Handle loading/error/empty states** — Every list hook exposes `isLoading`, `isError`, `data`

## Inputs expected

| Input | Source | Required | Description |
|-------|--------|----------|--------------|
| API spec | api-first-spec | Yes | Endpoints and DTOs to consume |
| TypeScript types | typescript | No | Type definitions for responses |
| Auth wrapper | authentication | No | JWT token management in `apiFetch` |

## Outputs produced

| Artifact | Format | Description |
|----------|--------|--------------|
| Query hook | `use{Entities}.ts` | `useQuery`-based hook for reads |
| Mutation hook | `use{Verb}{Entity}.ts` | `useMutation`-based hook for writes |
| Zustand store | `{entity}.store.ts` | Shared client state |

## Code patterns

### Typed Fetch Client

```ts
export interface ApiError {
  status: number;
  code: string;
  message: string;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init.headers },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const error: ApiError = { status: res.status, code: body.code ?? 'UNKNOWN', message: body.message ?? res.statusText };
    throw error;
  }

  return res.json() as Promise<T>;
}
```

### Query Hook

```ts
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../../core/api/fetch-client';
import type { User } from './user.types';

export function useUsers(params?: { page?: number; limit?: number }) {
  return useQuery({
    queryKey: ['users', 'list', params],
    queryFn: () => apiFetch<User[]>(`/users?${new URLSearchParams(params as Record<string, string>)}`),
    staleTime: 30_000,
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: ['users', 'detail', id],
    queryFn: () => apiFetch<User>(`/users/${id}`),
    enabled: !!id,
  });
}
```

### Mutation Hook with Cache Invalidation

```ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiFetch } from '../../core/api/fetch-client';
import type { CreateUserDto, User } from './user.types';

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserDto) => apiFetch<User>('/users', { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
    },
  });
}
```

### Zustand Store (equivalent to a signal-based store)

```ts
import { create } from 'zustand';
import type { User } from './user.types';

interface UserStoreState {
  selectedId: string | null;
  select: (id: string | null) => void;
}

export const useUserStore = create<UserStoreState>((set) => ({
  selectedId: null,
  select: (id) => set({ selectedId: id }),
}));

// Selector usage in a component:
// const selectedId = useUserStore((s) => s.selectedId);
```

### Optimistic Delete

```ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiFetch } from '../../core/api/fetch-client';
import type { User } from './user.types';

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiFetch<void>(`/users/${id}`, { method: 'DELETE' }),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['users', 'list'] });
      const previous = queryClient.getQueryData<User[]>(['users', 'list']);
      queryClient.setQueryData<User[]>(['users', 'list'], (old) => old?.filter((u) => u.id !== id));
      return { previous };
    },
    onError: (_err, _id, context) => {
      if (context?.previous) queryClient.setQueryData(['users', 'list'], context.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
    },
  });
}
```

### Component Consuming Hooks

```tsx
import { useUsers } from './hooks/useUsers';
import { useDeleteUser } from './hooks/useDeleteUser';

export function UserListPage() {
  const { data: users, isLoading, isError } = useUsers({ page: 1, limit: 20 });
  const deleteUser = useDeleteUser();

  if (isLoading) return <div className="spinner">Loading...</div>;
  if (isError) return <div className="error">Failed to load users</div>;
  if (!users?.length) return <div className="empty">No users found</div>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>
          {user.firstName} {user.lastName}
          <button disabled={deleteUser.isPending} onClick={() => deleteUser.mutate(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|---------------------|
| Fetch data in component | `fetch()` inside `useEffect` | `useQuery` hook |
| Manage server state | `useState` synced from an effect | `@tanstack/react-query` |
| Cache API responses | No caching | `staleTime`/`gcTime` on the query |
| Handle loading state | Boolean flag set manually | `isLoading` from `useQuery` |
| Share state across features | Prop drilling | Zustand store |
| Error handling | Ignored errors | `onError` + `isError` in UI |

## Verification checklist

- [ ] All server reads use `useQuery`, all writes use `useMutation`
- [ ] HTTP calls go through a single typed `apiFetch()` client
- [ ] Mutations invalidate the correct query keys `onSuccess`/`onSettled`
- [ ] Shared client state lives in a Zustand store, not prop drilling
- [ ] Optimistic updates roll back on error
- [ ] No `any` in hook return types
