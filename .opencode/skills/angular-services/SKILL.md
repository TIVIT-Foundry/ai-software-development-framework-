---
name: angular-services
description: 'Angular services patterns: RxJS Observables, @ngneat/query (TanStack Query for Angular), signals interop, toSignal()/toObservable(), HTTP data fetching, caching, optimistic updates. Trigger: When implementing Angular services, data fetching, state management, or RxJS patterns.'
version: 1.0
metadata:
  phase:
    - construction
  layer:
    - frontend
  enforcement: recommended
  depends_on:
  - angular
  - typescript
    - angular
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

Define the patterns for Angular services, data fetching, state management, and RxJS integration. Covers HTTP services with HttpClient, reactive data streams with RxJS, signals-rxjs interop (`toSignal()`, `toObservable()`), and `@ngneat/query` for server state management. Use this skill when the project selected Angular as its frontend framework (see `react-services` for the React/TanStack Query equivalent).

## When to use this skill

Activate this skill when:

- Creating Angular services for data fetching
- Implementing HTTP data fetching with caching
- Working with RxJS Observables in Angular
- Converting between signals and RxJS streams
- Implementing optimistic updates
- Setting up query caching and invalidation
- Creating reusable data-access layers

**Do not** activate when:

- Creating UI components without data fetching (use `angular`)
- Working with Python/FastAPI (use `data-access`)
- Only defining TypeScript types (use `typescript`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `angular` | Predecesora | Component patterns that consume these services |
| `typescript` | Predecesora | TypeScript patterns for service contracts |
| `api-first-frontend` | Consumidora | Generates services from OpenAPI spec |
| `api-resilience` | Complementaria | Retry/circuit breaker patterns for HTTP |
| `real-time` | Complementaria | WebSocket/SSE services |
| `authentication` | Complementaria | Auth token management in interceptors |

## Critical Rules

1. **Services are providers** — All services use `@Injectable({ providedIn: 'root' })` for singleton scope
2. **HttpClient for all HTTP** — Never use `fetch()` directly. Always `inject(HttpClient)`
3. **Signals for local state** — Component state uses signals. Server state uses services
4. **toSignal() for subscriptions** — Convert Observable to signal in components with `toSignal()`
5. **Error handling mandatory** — All HTTP calls must handle errors with `catchError`
6. **Unsubscribe automatically** — Use `toSignal()` or `async` pipe. Manual `unsubscribe()` is forbidden

## What the agent must do

1. **Create services with inject()** — Use `inject(HttpClient)` not constructor
2. **Return Observables** — HTTP methods return `Observable<T>` not Promises
3. **Apply catchError** — Every HTTP call handles errors
4. **Use toSignal() in components** — Convert Observables to signals for template use
5. **Implement caching** — Use `shareReplay`, `@ngneat/query`, or `rxCache`
6. **Handle loading states** — Track loading, error, and success states
7. **Use type-safe responses** — All HTTP calls typed with interfaces

## Inputs expected

| Input | Source | Required | Description |
|-------|--------|----------|-------------|
| API spec | api-first-spec | Yes | Endpoints and DTOs to consume |
| TypeScript types | typescript | No | Type definitions for responses |
| Auth interceptor | authentication | No | JWT token management |

## Outputs produced

| Artifact | Format | Description |
|----------|--------|-------------|
| Data service | `*.service.ts` | Injectable service with HTTP methods |
| Query hooks | `*.queries.ts` | @ngneat/query hooks for server state |
| Signal state | `*.store.ts` | Signal-based state management |

## Code patterns

### Basic HTTP Service

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { User, CreateUserDto } from './user.types';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private apiUrl = '/api/users';

  getUsers(params?: { page?: number; limit?: number }): Observable<User[]> {
    let httpParams = new HttpParams();
    if (params?.page) httpParams = httpParams.set('page', params.page.toString());
    if (params?.limit) httpParams = httpParams.set('limit', params.limit.toString());

    return this.http.get<User[]>(this.apiUrl, { params: httpParams }).pipe(
      catchError(this.handleError)
    );
  }

  getUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`).pipe(
      catchError(this.handleError)
    );
  }

  createUser(data: CreateUserDto): Observable<User> {
    return this.http.post<User>(this.apiUrl, data).pipe(
      catchError(this.handleError)
    );
  }

  updateUser(id: string, data: Partial<CreateUserDto>): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${id}`, data).pipe(
      catchError(this.handleError)
    );
  }

  deleteUser(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: unknown): Observable<never> {
    console.error('API Error:', error);
    return throwError(() => error);
  }
}
```

### Signal-Based State Store

```typescript
import { Injectable, signal, computed } from '@angular/core';
import { User } from './user.types';

@Injectable({ providedIn: 'root' })
export class UserStore {
  private users = signal<User[]>([]);
  private selectedId = signal<string | null>(null);
  private loading = signal(false);
  private error = signal<string | null>(null);

  readonly userList = this.users.asReadonly();
  readonly selectedUser = computed(() => {
    const id = this.selectedId();
    return id ? this.users().find(u => u.id === id) ?? null : null;
  });
  readonly isLoading = this.loading.asReadonly();
  readonly errorMessage = this.error.asReadonly();

  setUsers(users: User[]): void {
    this.users.set(users);
  }

  addUser(user: User): void {
    this.users.update(current => [...current, user]);
  }

  updateUser(updated: User): void {
    this.users.update(current =>
      current.map(u => (u.id === updated.id ? updated : u))
    );
  }

  removeUser(id: string): void {
    this.users.update(current => current.filter(u => u.id !== id));
  }

  selectUser(id: string): void {
    this.selectedId.set(id);
  }

  setLoading(loading: boolean): void {
    this.loading.set(loading);
  }

  setError(error: string | null): void {
    this.error.set(error);
  }
}
```

### Service with Signal Store Integration

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { UserStore } from './user.store';
import { User, CreateUserDto } from './user.types';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private store = inject(UserStore);
  private apiUrl = '/api/users';

  loadUsers(): Observable<User[]> {
    this.store.setLoading(true);
    return this.http.get<User[]>(this.apiUrl).pipe(
      tap(users => {
        this.store.setUsers(users);
        this.store.setLoading(false);
      }),
      catchError(err => {
        this.store.setError(err.message);
        this.store.setLoading(false);
        return throwError(() => err);
      })
    );
  }

  createUser(data: CreateUserDto): Observable<User> {
    return this.http.post<User>(this.apiUrl, data).pipe(
      tap(user => this.store.addUser(user)),
      catchError(this.handleError)
    );
  }

  private handleError(error: unknown): Observable<never> {
    return throwError(() => error);
  }
}
```

### @ngneat/query Pattern (TanStack Query for Angular)

```typescript
import { Injectable, inject } from '@angular/core';
import { QueryRef, QueryClientService } from '@ngneat/query';
import { HttpClient } from '@angular/common/http';
import { injectQuery, injectMutation, injectQueryClient } from '@ngneat/query';
import { User, CreateUserDto } from './user.types';

@Injectable({ providedIn: 'root' })
export class UserQueries {
  private http = inject(HttpClient);
  private queryClient = inject(QueryClientService);

  users = injectQuery(() => ({
    queryKey: ['users'],
    queryFn: () => this.http.get<User[]>('/api/users').toPromise(),
  }));

  user = (id: string) => injectQuery(() => ({
    queryKey: ['user', id],
    queryFn: () => this.http.get<User>(`/api/users/${id}`).toPromise(),
  }));

  createUser = injectMutation(() => ({
    mutationFn: (data: CreateUserDto) =>
      this.http.post<User>('/api/users', data).toPromise(),
    onSuccess: () => {
      this.queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  }));

  updateUser = injectMutation(() => ({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateUserDto> }) =>
      this.http.put<User>(`/api/users/${id}`, data).toPromise(),
    onSuccess: () => {
      this.queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  }));

  deleteUser = injectMutation(() => ({
    mutationFn: (id: string) =>
      this.http.delete<void>(`/api/users/${id}`).toPromise(),
    onSuccess: () => {
      this.queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  }));
}
```

### Component Using Services

```typescript
import { Component, inject, OnInit } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { UserQueries } from './user.queries';
import { UserStore } from './user.store';

@Component({
  selector: 'app-user-list',
  standalone: true,
  templateUrl: './user-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserListComponent implements OnInit {
  private queries = inject(UserQueries);
  private store = inject(UserStore);

  users = this.queries.users;
  isLoading = this.store.isLoading;
  error = this.store.errorMessage;

  ngOnInit(): void {
    // Data is automatically fetched by @ngneat/query
  }

  onCreate(data: CreateUserDto): void {
    this.queries.createUser.mutate(data);
  }

  onDelete(id: string): void {
    this.queries.deleteUser.mutate(id);
  }
}
```

### Template with Query State

```html
@if (users(); as result) {
  @if (result.isLoading) {
    <div class="spinner">Loading...</div>
  } @else if (result.error) {
    <div class="error">{{ result.error.message }}</div>
  } @else if (result.data?.length === 0) {
    <div class="empty">No users found</div>
  } @else {
    @for (user of result.data; track user.id) {
      <app-user-card [user]="user" (selected)="onSelect($event)" />
    }
  }
}
```

### Caching with shareReplay

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay, catchError, throwError } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private http = inject(HttpClient);
  private config$: Observable<Config> | null = null;

  getConfig(): Observable<Config> {
    if (!this.config$) {
      this.config$ = this.http.get<Config>('/api/config').pipe(
        shareReplay(1),
        catchError(this.handleError)
      );
    }
    return this.config$;
  }

  private handleError(error: unknown): Observable<never> {
    return throwError(() => error);
  }
}
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Fetch data in component | HTTP call in ngOnInit | Service method, consume with toSignal() |
| Manage server state | Component signals only | @ngneat/query or service with store |
| Cache API responses | No caching | shareReplay(1) or @ngneat/query |
| Handle loading state | Boolean flag in component | Service/store loading signal |
| Subscribe in component | Manual subscribe + unsubscribe | toSignal() or async pipe |
| Error handling | Ignored errors | catchError + error state |

## Verification checklist

- [ ] Service uses `@Injectable({ providedIn: 'root' })`
- [ ] HTTP via `inject(HttpClient)`
- [ ] All HTTP calls typed
- [ ] Error handling with `catchError`
- [ ] No manual subscriptions (use `toSignal()` or async pipe)
- [ ] Server state managed with @ngneat/query or store
- [ ] Local state uses signals
