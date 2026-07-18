---
name: agent-qa
description: 'Meta-skill: activates all testing skills in sequence for QA and quality
  assurance work. Trigger: When creating test plans, writing tests, or reviewing quality.'
version: 1.0
metadata:
  phase:
  - quality
  layer:
  - backend
  - frontend
  enforcement: recommended
  depends_on:
  - playwright
  - api-first-testing
  consumed_by: []
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: skill-contract
  mcp_usage: governed
---

## Purpose
Meta-skill for QA workflows. Activates testing-related skills and guides test creation.

## QA Workflow

| Step | Skill | Artifacts |
|------|-------|-----------|
| 1 | `api-first-spec` | Feature spec (for test derivation) |
| 2 | `api-first-testing` | E2E test plan from spec |
| 3 | `playwright` | Playwright tests |
| 4 | `code-review` | Test code review |
| 5 | `performance` | Performance test considerations |

## Test Types

| Type | Tool | When |
|------|------|------|
| Unit | pytest | Individual functions |
| Integration | httpx | API contract testing |
| E2E | Playwright | Full user flows |
| Performance | k6 / JMeter / Locust | Load testing |
| Accessibility | Axe + Playwright | A11y compliance |

## Test Planning Checklist
- [ ] Happy path test for each endpoint
- [ ] Validation error tests (400)
- [ ] Auth/authz tests (401/403)
- [ ] Not found tests (404)
- [ ] Pagination tests
- [ ] Export tests (if applicable)
- [ ] Edge cases from business rules

## Quality Gates
| Gate | Threshold |
|------|-----------|
| Unit test coverage | ≥ 80% |
| Critical flows E2E | 100% |
| Zero known security issues | Mandatory |
| Zero accessibility (WCAG AA) critical | Mandatory |

## Test Data Management

| Need | Approach |
|------|----------|
| Isolated test data | Use `beforeEach` to seed per-test data, never share state between tests |
| Realistic data volumes | For performance tests, use production-like data volumes in staging |
| Authentication in tests | Use API tokens or test user fixtures — never real credentials |
| Cleanup | Always clean up test data after run (DB transactions rollback, API resource teardown) |

## CI Integration Notes

- **Playwright tests**: Run in `--shard` mode for parallel execution. Configure in `playwright.config.ts`.
- **API tests**: Run before E2E. They catch contract breaks faster.
- **Coverage reports**: Fail CI if coverage drops below threshold. Enforce in pipeline config.
- **Flaky test handling**: Tag flaky tests with `@flaky`, set retries to 2 in Playwright config.

## Common Pitfalls

- **Testing implementation, not behavior**: Test what the user sees and does, not internal functions (those are unit tests).
- **Hardcoded waits**: Use `waitFor` selectors, not `setTimeout`. Hardcoded waits are fragile and slow.
- **Test pollution**: One test modifying shared state breaks others. Isolate via `beforeEach` + fresh data.
- **Skipping a11y**: Accessibility is not optional. Run `@axe-core/playwright` on every page.
- **No error scenarios**: Only testing the happy path misses 90% of real bugs. Always test validation errors, auth failures, and empty states.

## Quality Gates

Los siguientes gates deben verificarse antes de considerar la meta-skill completada:

| Gate | Título | Descripción |
|------|--------|-------------|
| 1 | Cobertura unitaria ≥80% | Los tests unitarios cubren ≥80% de handlers y services |
| 2 | Tests de integración validan contratos | Los tests de integración validan contratos entre capas |
| 3 | E2E cubre flujos críticos | Los tests E2E cubren los flujos críticos del usuario |
| 4 | Sin vulnerabilidades de severidad alta/crítica | No hay vulnerabilidades de seguridad de severidad alta/crítica |
| 5 | Tests de carga validan SLOs P95 | Los tests de carga validan SLOs de latencia P95 |
| 6 | Accesibilidad axe-core sin violaciones WCAG 2.2 AA | Los tests de accesibilidad (axe-core) pasan sin violaciones WCAG 2.2 AA |

## Ejemplo de invocación

```bash
# Activar la meta-skill en sesión de OpenCode
/agent-qa "Ejecutar suite completa de tests para el módulo de usuarios"

# Activar manualmente nivel por nivel (modo granular)
# Nivel 38: unit-testing
# Nivel 39: integration-testing
# Nivel 40: load-testing
# Nivel 41: security-testing
# Nivel 42: accesibilidad
# Nivel 43: framework-qa-validation
# Nivel 44: playwright
```

## Output esperado

Al invocar `agent-qa`, el sistema produce:

1. **Plan de pruebas** derivado de la especificación del módulo
2. **Tests unitarios** generados o actualizados
3. **Tests de integración** con TestContainers
4. **Tests E2E** con Playwright (Page Object Model)
5. **Reporte de cobertura** por capa (DB, Backend, Frontend)
6. **Reporte de vulnerabilidades** (si aplica)
7. **Sign-off** del go/no-go gate para promoción a producción

## Flujo de testing completo

El framework ejecuta el ciclo de testing en 5 niveles secuenciales. Cada nivel debe estar verde antes de pasar al siguiente.

### Nivel 1 — Tests Unitarios

| Aspecto | Detalle |
|---------|---------|
| Herramientas | pytest |
| Cobertura base | ≥ 80% en handlers, services, utilities |
| Qué testear | Lógica de negocio, validaciones, transformaciones, edge cases |
| Qué NO testear | Conexiones reales a BD, APIs externas, sistema de archivos |
| Patrón | AAA (Arrange-Act-Assert), mocks solo para bordes de capa |
| Ejecución | `npm run test:unit` o equivalente, < 30s todo el suite |

Checklist unitario:
- [ ] Happy path y al menos un caso de error por función
- [ ] Valores límite (empty string, null, max length, negativos)
- [ ] Mocks sustituyen solo la capa inmediata inferior
- [ ] Sin dependencias de red, BD, o sistema de archivos
- [ ] Tests son independientes entre sí (no comparten estado mutable)

### Nivel 2 — Tests de Integración

| Aspecto | Detalle |
|---------|---------|
| Herramientas | TestContainers, httpx |
| Alcance | Contratos entre capas (DB → API, API → servicio externo) |
| Base de datos | Contenedor real (PostgreSQL) con migraciones |
| Autenticación | Token de prueba generado en setup, fixture de usuario autenticado |
| Aislamiento | Rollback de transacción por test o truncate de tablas |

Checklist integración:
- [ ] Cada endpoint tiene test de respuesta exitosa (200/201)
- [ ] Cada endpoint tiene test de validación (400)
- [ ] Cada endpoint tiene test de autenticación (401)
- [ ] Cada endpoint tiene test de autorización (403)
- [ ] Cada endpoint tiene test de no encontrado (404)
- [ ] Paginación funciona correctamente (page, pageSize, total)
- [ ] Idempotencia en endpoints POST/PUT (misma llamada dos veces produce mismo resultado)

### Nivel 3 — Tests E2E (Playwright)

| Aspecto | Detalle |
|---------|---------|
| Herramientas | Playwright con Page Object Model |
| Flujos críticos | Login, CRUD principal, export, navegación completa |
| Estados | Loading, empty, error, success, sin datos |
| Responsive | Mobile (375px), Tablet (768px), Desktop (1280px) |
| Ejecución | `npx playwright test --shard=1/4`, paralelo por worker |

Checklist E2E:
- [ ] Login flow completo (credenciales válidas, inválidas, expiradas)
- [ ] CRUD del recurso principal (crear, leer, actualizar, eliminar)
- [ ] Validaciones de formulario visibles al usuario
- [ ] Paginación y navegación entre páginas
- [ ] Estados vacíos muestran mensaje informativo
- [ ] Cerrar sesión limpia el estado
- [ ] Navegación con botón "Atrás" del navegador no rompe la app

### Nivel 4 — Tests de Seguridad

| Aspecto | Detalle |
|---------|---------|
| SAST | SonarQube / Semgrep — análisis estático en CI |
| DAST | OWASP ZAP — escaneo de vulnerabilidades en staging |
| Dependencias | Snyk / Dependabot — sin vulnerabilidades alta/crítica |
| Secretos | GitLeaks / truffleHog — ningún secreto en el código |
| Manual | Revisión de OWASP Top 10: inyección, XSS, CSRF, IDOR |

Checklist seguridad:
- [ ] SonarQube sin blockers ni vulnerabilities de severidad alta
- [ ] ZAP Active Scan sin alerts de High/Critical
- [ ] Dependencias sin CVEs conocidos de severidad ≥ 7.0
- [ ] Secret scan (GitLeaks) pasa limpio
- [ ] Headers de seguridad presentes (CSP, X-Frame-Options, HSTS)
- [ ] Pruebas de inyección SQL en inputs de búsqueda (si aplica)

### Nivel 5 — Tests de Accesibilidad

| Aspecto | Detalle |
|---------|---------|
| Herramientas | axe-core + Playwright, Lighthouse, WCAG Contrast Checker |
| Nivel | WCAG 2.2 AA |
| Cobertura | Toda pantalla navegable, componentes críticos |
| Automatizado | `@axe-core/playwright` en cada E2E |
| Manual | Navegación por teclado, lector de pantalla (NVDA/VoiceOver) |

Checklist accesibilidad:
- [ ] axe-core sin violaciones en cada pantalla
- [ ] Navegación por teclado completa (Tab, Enter, Escape, flechas)
- [ ] Skip to content link presente
- [ ] Contraste de color ≥ 4.5:1 (texto normal), ≥ 3:1 (texto grande)
- [ ] Todos los campos tienen label asociado (explícito o aria-label)
- [ ] Mensajes de error están asociados al campo vía aria-describedby
- [ ] Imágenes decorativas tienen alt="" (vacío)
- [ ] Imágenes informativas tienen alt descriptivo
- [ ] Roles ARIA correctos (no sobrecargar con roles innecesarios)

## Prompts por nivel de testing

Cada nivel tiene un prompt listo para usar con el agente de código:

### Prompt — Tests Unitarios
```
Genera tests unitarios para el módulo [módulo] usando [framework de test].
Sigue el patrón AAA (Arrange-Act-Assert).
Cubre: happy path, validaciones, edge cases, valores límite.
Usa mocks solo para la capa inmediata inferior.
Nombra cada test como: [método]_[escenario]_[resultadoEsperado]
Incluye casos de error: datos inválidos, nulos, vacíos, duplicados.
```

### Prompt — Tests de Integración
```
Genera tests de integración para los endpoints de [módulo] usando [framework].
Usa TestContainers para la base de datos real.
Cubre por cada endpoint: 200, 400, 401, 403, 404.
Incluye paginación: page=1, pageSize=10, ordenamiento, filtros.
Aísla cada test con rollback de transacción.
Los tests deben ser independientes y ejecutables en paralelo.
```

### Prompt — Tests E2E
```
Genera tests E2E con Playwright para el flujo de [funcionalidad].
Usa Page Object Model: separa page object, test, y fixtures.
Prueba en 3 viewports: mobile (375px), tablet (768px), desktop (1280px).
Cubre: login, CRUD, empty states, loading states, error states.
No uses sleep ni setTimeout. Usa waitForSelector o waitForResponse.
Los selectors deben ser resilientes: data-testid o roles, no CSS frágil.
```

### Prompt — Tests de Seguridad
```
Ejecuta análisis SAST con Semgrep/SonarQube en el código de [módulo].
Escanea dependencias con Snyk/Dependabot buscando CVEs ≥ 7.0.
Revisa OWASP Top 10: inyección, XSS, CSRF, IDOR, auth bypass.
Verifica headers de seguridad: CSP, HSTS, X-Frame-Options, X-Content-Type-Options.
Busca secretos hardcodeados: API keys, tokens, passwords, connection strings.
```

### Prompt — Tests de Accesibilidad
```
Ejecuta axe-core en cada pantalla de [módulo] dentro del flujo E2E.
Verifica contraste de color (4.5:1 normal, 3:1 grande).
Prueba navegación por teclado: Tab, Enter, Escape, flechas.
Asegura labels en todos los campos de formulario.
Confirma skip-to-content link al inicio de cada página.
Verifica roles ARIA: no duplicados, no redundantes, semántica correcta.
```

## Quality gates checklist

Versión detallada de los quality gates. Cada gate debe verificarse explícitamente antes del go/no-go.

### Gate 1 — Cobertura unitaria ≥ 80%

| Sub-chequeo | Cómo verificarlo |
|-------------|------------------|
| Líneas cubiertas | `npm run test:coverage` reporta ≥ 80% |
| Ramas cubiertas | Branch coverage ≥ 70% |
| Funciones cubiertas | Function coverage ≥ 85% |
| Handlers | Cada handler público tiene al menos 1 test |
| Services | Cada método público tiene test de happy path y error |
| Mappers | Cada mapeo tiene test de transformación correcta |
| Excepciones | Cada excepción personalizada se testea |
| Archivos excluidos | Solo archivos de infra/config (app/main.py, main.ts) excluidos |

### Gate 2 — Tests de integración validan contratos

| Sub-chequeo | Cómo verificarlo |
|-------------|------------------|
| Endpoints cubiertos | 100% de endpoints públicos tienen test de integración |
| Status codes | Cada endpoint prueba 200, 400, 401, 403, 404 |
| Response shape | Body de respuesta coincide con DTO/contrato esperado |
| Headers | Content-Type, Location, Cache-Control presentes según corresponda |
| Paginación | Response incluye page, pageSize, total, totalPages |
| Errores DB | Simular timeout DB → 503, llave duplicada → 409 |
| Multi-tenant | Test con tenant A no ve datos de tenant B |
| Idempotencia | Misma request dos veces → mismo resultado (GET, PUT, DELETE) |

### Gate 3 — E2E cubre flujos críticos

| Sub-chequeo | Cómo verificarlo |
|-------------|------------------|
| Login | Credenciales válidas, inválidas, expiradas, sin permisos |
| CRUD principal | Crear, leer, actualizar, eliminar el recurso principal |
| Búsqueda/filtro | Resultados correctos, sin resultados, paginación |
| Navegación | Menú, breadcrumbs, rutas directas, botón atrás |
| Export | Descarga de archivo con contenido esperado |
| Offline/error | Pantalla de error cuando API no responde |
| Responsive | Flujo completo en mobile (375px) sin rupturas visuales |
| Carga inicial | Skeleton/spinner visible mientras carga, contenido después |

### Gate 4 — Sin vulnerabilidades severas

| Sub-chequeo | Cómo verificarlo |
|-------------|------------------|
| SAST | SonarQube Quality Gate = Passed, 0 blockers |
| DAST | ZAP: 0 High, 0 Critical, Medium < 5 |
| Dependencias | Snyk/Dependabot: 0 Critical, 0 High |
| Secretos | GitLeaks: 0 resultados, sin falsos positivos |
| OWASP Top 10 | Revisión manual de inyección, XSS, CSRF, IDOR |
| Headers | SecurityHeaders.com: A rating o todos headers presentes |
| TLS | SSL Labs: A- o superior |

### Gate 5 — Tests de carga validan SLOs P95

| Sub-chequeo | Cómo verificarlo |
|-------------|------------------|
| Escenario normal | 100 usuarios concurrentes, P95 < 500ms, error rate < 1% |
| Pico esperado | 500 usuarios, P95 < 1000ms, error rate < 2% |
| Escenario extremo | 1000 usuarios, P95 < 2000ms, sistema no colapsa |
| Soak test | 200 usuarios por 2 horas, sin degradación de P95 |
| Endpoints críticos | Login, búsqueda, creación tienen SLO específico |
| Recursos | CPU < 80%, RAM < 85%, conexiones DB < 80% |

### Gate 6 — Accesibilidad axe-core sin violaciones

| Sub-chequeo | Cómo verificarlo |
|-------------|------------------|
| axe-core | 0 violations en todas las pantallas |
| WCAG 2.2 AA | Nivel AA completo, sin incumplimientos |
| Contraste | Texto normal ≥ 4.5:1, texto grande ≥ 3:1 |
| Teclado | Todas las acciones disponibles por teclado |
| Skip to content | Enlace visible al focus, salta navegación |
| Labels | Todos los inputs tienen label o aria-label |
| ARIA | Roles correctos, no redundantes, estados actualizados |
| Screen reader | NVDA/VoiceOver: flujo completo navegable y entendible |
| Zoom | 200% sin pérdida de funcionalidad ni superposición
