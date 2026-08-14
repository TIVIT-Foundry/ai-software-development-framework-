---
name: angular
description: 'Angular component architecture: standalone components, signals, DI, routing, lifecycle hooks, template syntax, change detection, lazy loading, Angular CDK. Trigger: When creating Angular features, components, routing, or project structure.'
version: 1.0
metadata:
  phase:
    - construction
  layer:
    - frontend
  enforcement: recommended
  depends_on:
    - design-system
    - typescript
  consumed_by:
    - accesibilidad
    - agent-frontend
    - agent-fullstack
    - angular-doctor
    - angular-services
    - angular-upgrade
    - api-first-frontend
    - feature-flags
    - i18n
    - microfrontend
    - mobile-pwa
    - unit-testing
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define the architecture and conventions for Angular applications in the framework. Covers standalone components, signals, dependency injection, routing, lifecycle hooks, template syntax, change detection strategies, lazy loading, and Angular CDK integration. Angular is one of two accepted frontend frameworks (see ADR-005) — the project team picks React or Angular per project; `react` is the default when unspecified, `angular` is selected explicitly (e.g. `--frontend angular` in the scaffold generator, or when the target org standardizes on Angular).

## When to use this skill

Activate this skill when:

- The project has chosen Angular as its frontend framework (see `react` for the React equivalent)
- Creating new Angular components, services, or modules
- Designing Angular routing (lazy loading, guards, resolvers)
- Implementing Angular standalone components
- Setting up Angular project structure
- Working with Angular signals, RxJS, or DI
- Configuring change detection (OnPush, signals)
- Integrating Angular CDK (virtual scroll, drag-drop, overlays)
- Implementing Angular forms (reactive, template-driven)

**Do not** activate when:

- The project has chosen React as its frontend framework (use `react` instead)
- Creating backend APIs (use `backend-api` or `api-first-backend`)
- Working with Python/FastAPI (use `app-bootstrap`)
- Creating only TypeScript types without Angular (use `typescript`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `typescript` | Predecesora | TypeScript patterns are the foundation for Angular |
| `design-system` | Complementaria | Design tokens and theming applied to Angular components |
| `angular-services` | Complementaria | Angular services, RxJS, and data fetching patterns |
| `api-first-frontend` | Consumidora | Generates Angular components from OpenAPI spec |
| `accesibilidad` | Complementaria | ARIA patterns applied to Angular templates |
| `i18n` | Complementaria | Translation integration with @ngx-translate |
| `microfrontend` | Complementaria | Module Federation for Angular |

## Critical Rules

1. **Standalone components by default** — All components must be standalone (no NgModules). Angular 17+ convention.
2. **OnPush change detection** — All components use `ChangeDetectionStrategy.OnPush` for performance.
3. **Signals over RxJS for state** — Prefer Angular signals for local component state. Use RxJS for async streams and HTTP.
4. **Inject() over constructor injection** — Use `inject()` function instead of constructor-based DI.
5. **Lazy loading mandatory** — All routes must use `loadComponent` or `loadChildren` for lazy loading.
6. **No manual change detection** — Use signals or async pipe. No `ChangeDetectorRef.detectChanges()`.

## What the agent must do

1. **Create standalone components** — Every component uses `standalone: true`
2. **Use OnPush** — Every component uses `changeDetection: ChangeDetectionStrategy.OnPush`
3. **Apply signals** — Local state uses `signal()`, `computed()`, `effect()`
4. **Use inject()** — Dependencies via `inject(Service)` not constructor
5. **Lazy load routes** — All routes via `loadComponent: () => import(...)`
6. **Follow naming conventions** — `*.component.ts`, `*.service.ts`, `*.pipe.ts`, `*.directive.ts`
7. **Apply Angular CDK** — Virtual scroll, overlays, drag-drop where applicable

## Inputs expected

| Input | Source | Required | Description |
|-------|--------|----------|-------------|
| Feature requirements | user/hu-template | Yes | What the component must do |
| API spec | api-first-spec | No | OpenAPI spec for data models |
| Design tokens | design-system | No | Visual tokens for styling |
| TypeScript types | typescript | No | Type definitions |

## Outputs produced

| Artifact | Format | Description |
|----------|--------|-------------|
| Component file | `*.component.ts` | Standalone Angular component with OnPush |
| Template file | `*.component.html` | Angular template with signals, control flow |
| Styles file | `*.component.scss` | Component-scoped SCSS |
| Route config | `*.routes.ts` | Lazy-loaded route definitions |

## Code patterns

### Standalone Component

```typescript
import { Component, signal, computed, input, output, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-user-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './user-card.component.html',
  styleUrl: './user-card.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserCardComponent {
  user = input.required<User>();
  selected = output<User>();

  fullName = computed(() => `${this.user().firstName} ${this.user().lastName}`);

  onSelect(): void {
    this.selected.emit(this.user());
  }
}
```

### Template with Signals and Control Flow

```html
<div class="user-card" [class.selected]="isSelected()">
  <h3>{{ fullName() }}</h3>
  <p>{{ user().email }}</p>

  @if (user().avatar; as avatar) {
    <img [src]="avatar" [alt]="fullName()" />
  } @else {
    <div class="avatar-placeholder">{{ user().firstName[0] }}</div>
  }

  @for (role of user().roles; track role.id) {
    <span class="badge">{{ role.name }}</span>
  }

  <button (click)="onSelect()">Select</button>
</div>
```

### Signal State Management

```typescript
import { Component, signal, computed } from '@angular/core';

@Component({
  selector: 'app-user-list',
  standalone: true,
  templateUrl: './user-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserListComponent {
  private users = signal<User[]>([]);
  private filter = signal<string>('');

  filteredUsers = computed(() => {
    const term = this.filter().toLowerCase();
    return this.users().filter(u =>
      u.name.toLowerCase().includes(term)
    );
  });

  totalCount = computed(() => this.users().length);

  updateFilter(term: string): void {
    this.filter.set(term);
  }
}
```

### Lazy-Loaded Routes

```typescript
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/user-list/user-list.component').then(m => m.UserListComponent),
  },
  {
    path: ':id',
    loadComponent: () =>
      import('./pages/user-detail/user-detail.component').then(m => m.UserDetailComponent),
  },
  {
    path: ':id/edit',
    loadComponent: () =>
      import('./pages/user-edit/user-edit.component').then(m => m.UserEditComponent),
  },
];
```

### Angular Service with inject()

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private apiUrl = '/api/users';

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  getUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`);
  }

  createUser(data: CreateUserDto): Observable<User> {
    return this.http.post<User>(this.apiUrl, data);
  }
}
```

### Reactive Forms

```typescript
import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './user-form.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UserFormComponent {
  private fb = inject(FormBuilder);

  form = this.fb.group({
    firstName: ['', [Validators.required, Validators.maxLength(100)]],
    lastName: ['', [Validators.required, Validators.maxLength(100)]],
    email: ['', [Validators.required, Validators.email]],
  });

  onSubmit(): void {
    if (this.form.valid) {
      // emit or save
    }
  }
}
```

### HTTP Interceptor for JWT

```typescript
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.token();

  if (token) {
    const cloned = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
    return next(cloned);
  }

  return next(req);
};
```

### Route Guard

```typescript
import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/login']);
};
```

## File Structure

```
src/
├── app/
│   ├── app.component.ts
│   ├── app.config.ts
│   ├── app.routes.ts
│   ├── core/
│   │   ├── guards/
│   │   ├── interceptors/
│   │   ├── services/
│   │   └── models/
│   ├── features/
│   │   └── {feature}/
│   │       ├── {feature}.routes.ts
│   │       ├── pages/
│   │       │   └── {page}/
│   │       │       ├── {page}.component.ts
│   │       │       ├── {page}.component.html
│   │       │       └── {page}.component.scss
│   │       └── components/
│   └── shared/
│       ├── components/
│       ├── pipes/
│       └── directives/
├── environments/
├── assets/
└── styles/
    ├── _variables.scss
    ├── _mixins.scss
    └── styles.scss
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Need component state | `useState`, class properties | `signal()` or `computed()` |
| Need to fetch data | Manual HTTP in component | Service with `inject(HttpClient)` |
| Need route protection | Wrapper component | `CanActivateFn` guard |
| Need performance | Default change detection | `OnPush` + signals |
| Need dependency | Constructor injection | `inject(Service)` |
| Need lazy loading | Eager import | `loadComponent: () => import(...)` |

## Verification checklist

- [ ] Component is standalone (`standalone: true`)
- [ ] Uses `ChangeDetectionStrategy.OnPush`
- [ ] State managed with signals
- [ ] Dependencies via `inject()`
- [ ] Routes lazy-loaded
- [ ] No `any` types
- [ ] Template follows Angular control flow syntax (@if, @for, @switch)
- [ ] Styles scoped (ViewEncapsulation.Emulated default)
