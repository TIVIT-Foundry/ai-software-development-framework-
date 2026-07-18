---
name: unit-testing
description: "Unit testing patterns and best practices. Covers pytest (Python), Angular TestBed (Angular), Vitest/Jest (Bun/TypeScript), AAA pattern, mocks vs fakes vs stubs, test naming, coverage by layer, TDD workflow, and test isolation. Trigger: When writing unit tests, setting up test projects, or establishing testing conventions."
version: 2.0
metadata:
  phase:
  - quality
  layer:
  - testing
  enforcement: mandatory
  depends_on:
  - backend-api
  - file-upload
  - angular
  consumed_by:
  - integration-testing
  - framework-qa-validation
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: skill-contract
  mcp_usage: none
---

# unit-testing

## Propósito

Esta skill define cómo escribir y organizar tests unitarios de forma consistente, aislada y mantenible.  
Su función es asegurar que cada unidad de código (handler, service, util, component, hook) tenga tests rápidos, deterministas y enfocados en comportamiento, no en implementación.

Esta skill complementa `integration-testing` (tests con dependencias reales) y `framework-qa-validation` (estrategia general de QA). Mientras aquellos validan integración y estrategia, esta skill valida cada unidad en aislamiento.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué framework de testing usar y cómo se configura?
2. ¿Cómo se estructuran los tests unitarios (AAA pattern)?
3. ¿Cuándo usar mocks, fakes o stubs?
4. ¿Cómo se nombra un test unitario?
5. ¿Qué cobertura por capa se espera?

## Relación con otras skills

- `backend-api` define los handlers/endpoints que esta skill testea unitariamente.
- `angular` define los componentes, servicios, pipes y directivas que esta skill testea unitariamente.
- `typescript` define los tipos que esta skill usa en tests.
- `integration-testing` testea las mismas unidades pero con dependencias reales.
- `framework-qa-validation` define la estrategia de testing de la que esta skill forma la base.

## Qué debe hacer el agente cuando esta skill está activa

1. Configurar el proyecto de tests unitarios según el stack:
   - **Python**: pytest con conftest.py, pytest-asyncio, pytest-mock.
   - **Angular (Frontend)**: Angular CLI (`ng generate`) con Karma/Jasmine o Vitest.
   - **Bun (TypeScript Backend)**: Vitest (preferido) o Jest con configuración para Bun.
2. Definir la convención de naming de tests (`MethodName_Scenario_ExpectedResult`).
3. Estructurar los tests con el patrón AAA (Arrange/Act/Assert).
4. Decidir entre mock, fake o stub para cada dependencia.
5. Definir la cobertura esperada por capa (handlers, services, utils, components, pipes, directives).
6. Escribir tests unitarios para cada unidad de código.
7. Configurar el runner de tests en CI.
8. Asegurar que los tests son deterministas (sin flaky tests).

## Entradas esperadas

Esta skill asume que ya existe:
- código de producción que testear (`backend-api`, `angular`, `file-upload`);
- tipos TypeScript definidos (`typescript`);
- convenciones de proyecto (`project-architecture`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- configuración de proyecto de tests unitarios;
- patrón AAA para structurar tests;
- mocks, fakes y stubs para aislar dependencias;
- convención de naming;
- cobertura por capa;
- tests de handlers/services/endpoints (Python / Bun TypeScript);
- tests de componentes, pipes, directivas y servicios (Angular);
- configuración de CI para tests unitarios.

La fase no incluye todavía:
- tests de integración con BD real (`integration-testing`);
- tests E2E (`playwright`);
- tests de carga o stress;
- tests de seguridad.

## Principios que siempre debe respetar

- Un test unitario DEBE ser rápido (< 10ms por test).
- Un test unitario DEBE ser determinista (mismo input, mismo resultado, siempre).
- Un test unitario DEBE testear comportamiento, no implementación.
- Un test unitario DEBE aislar la unidad de sus dependencias (mock/fake/stub).
- Un test unitario NUNCA debe depender de una BD, API externa o filesystem.
- El naming DEBE seguir `MethodName_Scenario_ExpectedResult`.
- Los tests DEBEN estar organizados por feature/ módulo, no por tipo.
- La cobertura DEBE medirse por capa, no por líneas globales.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- el framework de testing y su configuración;
- el patrón de structuración de tests (AAA);
- la estrategia de mocks/fakes/stubs;
- la convención de naming;
- la cobertura esperada por capa.

Esta skill delega:
- los tests de integración a `integration-testing`;
- los tests E2E a `playwright`;
- la estrategia general de QA a `framework-qa-validation`;
- la configuración de CI a `ci-cd`.

## Qué debe definir el diseño

### 1. Python Backend (pytest)

#### Estructura de directorios

```
src/
├── features/
│   ├── auth/
│   │   ├── handlers.py
│   │   ├── services.py
│   │   └── tests/
│   │       ├── test_handlers.py
│   │       └── test_services.py
│   └── users/
│       ├── handlers.py
│       ├── services.py
│       └── tests/
│           ├── test_handlers.py
│           └── test_services.py
└── shared/
    └── utils/
        ├── format_currency.py
        └── tests/
            └── test_format_currency.py
```

#### Configuración

```ini
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["src"]
markers = [
    "unit: Unit tests (no DB, no external APIs)",
    "slow: Tests that take > 1s",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 70
show_missing = true
per_file_ignores = ["*/__init__.py"]
```

#### Ejemplo de test

```python
# src/features/auth/tests/test_handlers.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.features.auth.handlers import create_user

class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_user_valid_request_creates_user_and_returns_id(self):
        # Arrange
        repo = AsyncMock()
        repo.create.return_value = 1
        request = {"email": "test@test.com", "name": "John"}

        # Act
        result = await create_user(request, repo)

        # Assert
        assert result.id == 1
        repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_conflict(self):
        # Arrange
        repo = AsyncMock()
        repo.create.side_effect = ValueError("duplicate email")
        request = {"email": "test@test.com", "name": "John"}

        # Act & Assert
        with pytest.raises(ValueError, match="duplicate email"):
            await create_user(request, repo)
```

### 2. Angular Frontend (TestBed / Jasmine / Karma)

#### Configuración

Angular incluye Karma + Jasmine por defecto. Para ejecutar:

```bash
ng test                      # watch mode
ng test --no-watch           # single run (CI)
ng test --code-coverage      # con cobertura
```

Alternativa moderna (Vitest):

```bash
npm install --save-dev vitest @analogjs/vitest-angular
```

#### Estructura de directorios

```
src/app/
├── features/
│   ├── auth/
│   │   ├── login/
│   │   │   ├── login.component.ts
│   │   │   ├── login.component.spec.ts      # test co-localizado
│   │   │   └── login.service.ts
│   │   │   └── login.service.spec.ts
│   │   ├── auth.pipe.ts
│   │   ├── auth.pipe.spec.ts
│   │   └── auth.guard.ts
│   │   └── auth.guard.spec.ts
│   └── users/
│       ├── user-list/
│       │   ├── user-list.component.ts
│       │   ├── user-list.component.spec.ts
│       │   └── user-list.component.html
│       └── user.service.ts
│       └── user.service.spec.ts
└── shared/
    └── utils/
        ├── format-currency.pipe.ts
        └── format-currency.pipe.spec.ts
```

#### Testing de Componentes (TestBed + ComponentFixture)

```typescript
// src/app/features/auth/login/login.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { LoginComponent } from './login.component';
import { AuthService } from '../auth.service';
import { of, throwError } from 'rxjs';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let authServiceSpy: jasmine.SpyObj<AuthService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('AuthService', ['login']);

    await TestBed.configureTestingModule({
      declarations: [LoginComponent],
      imports: [ReactiveFormsModule],
      providers: [
        { provide: AuthService, useValue: spy }
      ]
    }).compileComponents();

    authServiceSpy = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should call authService.login on valid submit', () => {
    // Arrange
    authServiceSpy.login.and.returnValue(of({ token: 'abc123' }));
    component.loginForm.setValue({ email: 'test@test.com', password: 'pass123' });

    // Act
    component.onSubmit();

    // Assert
    expect(authServiceSpy.login).toHaveBeenCalledWith('test@test.com', 'pass123');
  });

  it('should show error message on failed login', () => {
    // Arrange
    authServiceSpy.login.and.returnValue(throwError(() => new Error('Invalid credentials')));
    component.loginForm.setValue({ email: 'test@test.com', password: 'wrong' });

    // Act
    component.onSubmit();

    // Assert
    expect(component.errorMessage).toBe('Invalid credentials');
  });
});
```

#### Testing de Servicios Angular

```typescript
// src/app/features/users/user.service.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UserService } from './user.service';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UserService]
    });
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify(); // Ensure no outstanding HTTP calls
  });

  it('should return users list', () => {
    // Arrange
    const mockUsers = [{ id: 1, name: 'John' }];

    // Act
    service.getUsers().subscribe(users => {
      // Assert
      expect(users.length).toBe(1);
      expect(users[0].name).toBe('John');
    });

    const req = httpMock.expectOne('/api/users');
    expect(req.request.method).toBe('GET');
    req.flush(mockUsers);
  });
});
```

#### Testing de Pipes

```typescript
// src/app/features/auth/auth.pipe.spec.ts
import { DateFormatPipe } from './date-format.pipe';

describe('DateFormatPipe', () => {
  let pipe: DateFormatPipe;

  beforeEach(() => {
    pipe = new DateFormatPipe();
  });

  it('should transform ISO date to localized string', () => {
    // Arrange
    const isoDate = '2026-07-15T10:30:00Z';

    // Act
    const result = pipe.transform(isoDate);

    // Assert
    expect(result).toContain('2026');
  });

  it('should return empty string for null input', () => {
    expect(pipe.transform(null)).toBe('');
  });
});
```

#### Testing de Directivas

```typescript
// src/app/shared/directives/highlight.directive.spec.ts
import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HighlightDirective } from './highlight.directive';

@Component({
  template: '<div appHighlight>Test content</div>'
})
class TestComponent {}

describe('HighlightDirective', () => {
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [HighlightDirective, TestComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
  });

  it('should add background color on mouseenter', () => {
    // Arrange
    const el: HTMLElement = fixture.nativeElement.querySelector('div');

    // Act
    el.dispatchEvent(new Event('mouseenter'));
    fixture.detectChanges();

    // Assert
    expect(el.style.backgroundColor).toBe('yellow');
  });
});
```

#### Testing de Guards (CanActivate)

```typescript
// src/app/features/auth/auth.guard.spec.ts
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { AuthGuard } from './auth.guard';
import { AuthService } from './auth.service';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let authServiceSpy: jasmine.SpyObj<AuthService>;
  let routerSpy: jasmine.SpyObj<Router>;

  beforeEach(() => {
    authServiceSpy = jasmine.createSpyObj('AuthService', ['isAuthenticated']);
    routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        AuthGuard,
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    });
    guard = TestBed.inject(AuthGuard);
  });

  it('should allow activation when authenticated', () => {
    authServiceSpy.isAuthenticated.and.returnValue(true);
    expect(guard.canActivate()).toBeTrue();
  });

  it('should redirect to login when not authenticated', () => {
    authServiceSpy.isAuthenticated.and.returnValue(false);
    expect(guard.canActivate()).toBeFalse();
    expect(routerSpy.navigate).toHaveBeenCalledWith(['/login']);
  });
});
```

#### Testing con ComponentHarness (Angular CDK)

`ComponentHarness` (de `@angular/cdk/testing`) permite tests más estables y centrados en la API pública del componente (no en selectores CSS frágiles). Recomendado para componentes con DOM complejo, tablas, formularios o componentes reutilizables.

```bash
# Instalación
ng add @angular/cdk
```

```typescript
// src/app/features/users/user-list/user-list.harness.ts
import { ComponentHarness, HarnessPredicate } from '@angular/cdk/testing';
import { UserListComponent } from './user-list.component';

export class UserListHarness extends ComponentHarness {
  static readonly hostSelector = 'app-user-list';

  /** Fábrica de predicado para filtrar instancias por atributos. */
  static with(options: { title?: string } = {}): HarnessPredicate<UserListHarness> {
    return new HarnessPredicate(UserListHarness, options)
      .addOption('title', options.title,
        (harness, title) => HarnessPredicate.stringMatches(harness.getTitle(), title));
  }

  private _title = this.locatorFor('[data-testid="user-list-title"]');
  private _rows = this.locatorForAll('[data-testid="user-row"]');
  private _searchInput = this.locatorFor('[data-testid="user-search"]');

  async getTitle(): Promise<string> {
    return (await this._title()).text();
  }

  async getRowCount(): Promise<number> {
    return (await this._rows()).length;
  }

  async search(term: string): Promise<void> {
    const input = await this._searchInput();
    await input.sendKeys(term);
  }
}
```

```typescript
// src/app/features/users/user-list/user-list.component.spec.ts
import { TestBed, ComponentFixture } from '@angular/core/testing';
import { TestbedHarnessEnvironment } from '@angular/cdk/testing/testbed';
import { UserListComponent } from './user-list.component';
import { UserService } from '../user.service';
import { UserListHarness } from './user-list.harness';
import { of } from 'rxjs';
import { provideHttpClient } from '@angular/common/http';

describe('UserListComponent (harness)', () => {
  let fixture: ComponentFixture<UserListComponent>;
  let harness: UserListHarness;
  let userServiceSpy: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    userServiceSpy = jasmine.createSpyObj('UserService', ['getUsers']);
    userServiceSpy.getUsers.and.returnValue(of([
      { id: 1, name: 'John' },
      { id: 2, name: 'Jane' },
    ]));

    await TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [
        { provide: UserService, useValue: userServiceSpy },
        provideHttpClient(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(UserListComponent);
    await fixture.whenStable();
    const loader = TestbedHarnessEnvironment.loader(fixture);
    harness = await loader.getHarness(UserListHarness);
  });

  it('should render two users on init', async () => {
    // Assert
    expect(await harness.getRowCount()).toBe(2);
  });

  it('should filter rows by search term', async () => {
    // Act
    await harness.search('John');

    // Assert
    expect(await harness.getRowCount()).toBe(1);
  });
});
```

Reglas para ComponentHarness:
- **SIEMPRE** exponer la API pública del componente (acciones y lecturas), no selectores CSS internos.
- **SIEMPRE** usar `data-testid` en el template del componente para anclar el harness al DOM estable.
- **NUNCA** acceder a `nativeElement` desde el harness; usar `locatorFor` / `locatorForAll`.
- **PREFERIR** harness sobre `querySelector` cuando el componente tiene más de 2 elementos interactivos o se reutiliza en múltiples lugares.
- Un harness es código de producción (acompaña al componente), no código de test desechable.

### 3. Bun TypeScript Backend (Vitest preferido)

Bun tiene soporte nativo para Jest-like API. Vitest es la opción preferida por su velocidad con Bun.

#### Configuración

```bash
# Instalación
bun add --dev vitest
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.spec.ts', 'src/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      exclude: ['node_modules/', 'src/**/*.spec.ts'],
    },
  },
});
```

#### Scripts

```json
// package.json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

#### Estructura de directorios

```
src/
├── features/
│   ├── auth/
│   │   ├── auth.handler.ts
│   │   ├── auth.handler.spec.ts
│   │   ├── auth.service.ts
│   │   └── auth.service.spec.ts
│   └── users/
│       ├── users.handler.ts
│       ├── users.handler.spec.ts
│       ├── users.service.ts
│       └── users.service.spec.ts
└── shared/
    └── utils/
        ├── formatCurrency.ts
        └── formatCurrency.spec.ts
```

#### Ejemplo de test de servicio

```typescript
// src/features/auth/auth.service.spec.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let mockRepo: { findByEmail: ReturnType<typeof vi.fn>; create: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockRepo = {
      findByEmail: vi.fn(),
      create: vi.fn(),
    };
    service = new AuthService(mockRepo);
  });

  describe('login', () => {
    it('should return token when credentials are valid', async () => {
      // Arrange
      mockRepo.findByEmail.mockResolvedValue({ id: 1, email: 'test@test.com', passwordHash: 'hashed' });

      // Act
      const result = await service.login('test@test.com', 'password123');

      // Assert
      expect(result.token).toBeDefined();
      expect(mockRepo.findByEmail).toHaveBeenCalledWith('test@test.com');
    });

    it('should throw when credentials are invalid', async () => {
      // Arrange
      mockRepo.findByEmail.mockResolvedValue(null);

      // Act & Assert
      await expect(service.login('test@test.com', 'wrong'))
        .rejects.toThrow('Invalid credentials');
    });
  });
});
```

#### Ejemplo de test de handler/endpoint

```typescript
// src/features/users/users.handler.spec.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getUsersHandler } from './users.handler';

describe('getUsersHandler', () => {
  let mockUserService: { list: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    mockUserService = { list: vi.fn() };
  });

  it('should return users list with 200', async () => {
    // Arrange
    const users = [{ id: 1, name: 'John' }];
    mockUserService.list.mockResolvedValue(users);

    // Act
    const response = await getUsersHandler(mockUserService);

    // Assert
    expect(response.status).toBe(200);
    expect(response.data).toEqual(users);
  });

  it('should return 500 on unexpected error', async () => {
    // Arrange
    mockUserService.list.mockRejectedValue(new Error('DB connection failed'));

    // Act
    const response = await getUsersHandler(mockUserService);

    // Assert
    expect(response.status).toBe(500);
  });
});
```

### 4. Mocks vs Fakes vs Stubs

| Tipo | Definición | Cuándo usar | Ejemplo |
|------|-----------|-------------|---------|
| **Mock** | Objeto que verifica interacciones | Verificar que se llamó un método | `vi.fn()`, `jasmine.createSpyObj()`, `AsyncMock()` |
| **Fake** | Implementación funcional simplificada | Cuando se necesita comportamiento real | `InMemoryUserRepository` |
| **Stub** | Objeto que retorna datos fijos | Cuando solo se necesitan datos de entrada | `vi.fn().mockReturnValue(data)` |

Regla general:
- **Mocks**: Para verificar que el sistema bajo test interactuó correctamente con la dependencia.
- **Fakes**: Para repositorios, cuando se necesita comportamiento CRUD real pero en memoria.
- **Stubs**: Para datos de entrada cuando el test no verifica interacciones.

### 5. Test naming convention

```
MethodName_Scenario_ExpectedResult

Ejemplos Python:
test_create_user_valid_request_creates_user_and_returns_id
test_create_user_duplicate_email_raises_conflict
test_create_user_invalid_name_raises_validation_error

Ejemplos Angular:
LoginComponent_validForm_submitsSuccessfully
UserService_getUsers_returnsUserList
DateFormatPipe_nullInput_returnsEmptyString
HighlightDirective_mouseenter_appliesHighlightColor

Ejemplos Bun/TypeScript:
AuthService_login_validCredentials_returnsToken
getUsersHandler_success_returnsUserList
formatCurrency_positiveAmount_returnsFormattedString
```

Reglas:
- Nombre del método underspecified.
- Escenario describe las condiciones de entrada.
- Resultado esperado describe el efecto observable.
- El nombre debe leerse como una oración natural.

### 6. Cobertura por capa

| Capa | Cobertura mínima | Cobertura objetivo | Notas |
|------|-------------------|-------------------|-------|
| Handlers/Use Cases | 80% | 95% | Lógica de negocio crítica |
| Services | 70% | 90% | Orquestación y reglas |
| Repository/Data Access | No unit test | 0% | Se testea en integration tests |
| Utils | 90% | 100% | Funciones puras, alta cobertura |
| Angular Components | 70% | 85% | Templates simples, lógica en clase |
| Angular Pipes | 80% | 95% | Funciones puras de transformación |
| Angular Guards | 80% | 95% | Lógica de autorización |
| Angular Directives | 60% | 80% | Testing de DOM interaction |

Regla: La cobertura mide calidad, no cantidad. No perseguir 100% global; perseguir alta cobertura en lógica crítica.

### 7. Tests deterministas

Reglas para evitar flaky tests:
- NUNCA usar `Thread.Sleep`, `Task.Delay` o `setTimeout` en tests unitarios.
- NUNCA depender de `DateTime.Now`, `Date.now()` o `Guid.NewGuid()` directamente; inyectar para poder controlar.
- NUNCA usar archivos o BD reales en tests unitarios.
- NUNCA depender de orden de ejecución entre tests.
- SIEMPRE limpiar el estado entre tests (setup/teardown, beforeEach, afterEach o constructor).
- SIEMPRE usar timeouts explícitos en assertions asíncronos.

## Preguntas guía

### 1. Sobre framework
- ¿Se usa pytest para Python?
- ¿Se usa pytest-asyncio para tests asíncronos?
- ¿Se usa unittest.mock o pytest-mock para mocking?

### 2. Sobre cobertura
- ¿Cuál es la cobertura mínima aceptable por proyecto?
- ¿Se exigen coberturas diferentes por capa?
- ¿Se bloquea el PR si la cobertura baja?

### 3. Sobre mocks
- ¿Se prefieren mocks o fakes?
- ¿Se usa un Fake genérico o se crean fakes por feature?
- ¿Los mocks se comparten entre tests o se crean en cada test?

### 4. Sobre naming
- ¿Se usa `MethodName_Scenario_ExpectedResult` en español o inglés?
- ¿Los nombres de archivo siguen la misma convención?
- ¿Se agrupan tests por feature o por tipo?

### 5. Sobre TDD
- ¿Se exige TDD (test antes que código)?
- ¿Se permite escribir tests después del código?
- ¿Cómo se maneja deuda técnica de tests?

## Salidas esperadas de esta skill

### A. Proyecto de tests configurado
- `Python`: pytest con conftest.py, pytest-asyncio, pytest-mock.

### B. Fakes compartidos
- `InMemoryRepository<T>` para reemplazar BD en tests.

### C. Tests por feature
- Al menos 1 test de handler por caso de uso (happy path + error path).
- Al menos 1 test de util por función pura.

### D. Configuración de CI
- Step de test unitarios en el pipeline.
- Reporte de cobertura por capa.
- Fallback si la cobertura baja del umbral.

### E. Consumidores de esta skill
- `integration-testing` usa los mismos patrones pero con dependencias reales;
- `framework-qa-validation` define la cobertura global esperada;
- `ci-cd` ejecuta los tests unitarios en el pipeline.

## Criterios de calidad

- Los tests son rápidos (< 10ms por test).
- Los tests son deterministas (sin flaky tests).
- Los tests siguen AAA pattern (Arrange/Act/Assert).
- Los tests usan naming convention `MethodName_Scenario_ExpectedResult`.
- La cobertura por capa cumple los umbrales definidos.
- Los mocks/fakes/stubs se usan correctamente según la regla.
- Los tests están organizados por feature, no por tipo.
- Los tests no dependen de BD, API externa ni filesystem.
- La configuración de CI ejecuta los tests unitarios.

## Comportamiento esperado del agente

Cuando el usuario escriba un test que dependa de una BD real, el agente debe proponer un mock o fake y explicar por qué los tests unitarios no deben tocar la BD.  
Cuando el usuario nombre un test `Test1` o `Works`, el agente debe proponer el naming convention `MethodName_Scenario_ExpectedResult`.  
Cuando el usuario persiga 100% de cobertura global, el agente debe explicar que la cobertura debe medirse por capa y que perseguir 100% en componentes de UI es contraproducente.  
Cuando el usuario tenga un test flaky, el agente debe ayudar a identificar la fuente de no-determinismo y proponer una corrección.

## Checklist final de la skill

- ¿Se configuró el proyecto de tests unitarios?
- ¿Se definió la convención de naming?
- ¿Los tests siguen AAA pattern?
- ¿Se definieron los umbrales de cobertura por capa?
- ¿Se crearon fakes compartidos (InMemoryRepository, MockServer)?
- ¿Los tests son rápidos y deterministas?
- ¿Se configuró el runner de tests en CI?
- ¿Los tests están organizados por feature?
- ¿Se documentó cuándo usar mock vs fake vs stub?
- ¿Se verificó que ningún test depende de BD, API externa o filesystem?