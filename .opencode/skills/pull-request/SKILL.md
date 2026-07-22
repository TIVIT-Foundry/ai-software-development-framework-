---
name: pull-request
description: 'Creates Pull Requests following conventional commits conventions and manages changelog entries. Trigger: When creating PRs, adding changelog entries, or working with CHANGELOG.md.'
version: 1.0
metadata:
  phase:
  - construction
  - operations
  - closure
  layer:
  - process
  enforcement: mandatory
  depends_on:
  - code-review
  consumed_by: []
  agent_roles:
  - delivery-agent
  validation_profile: documentation
mcp_usage: none
---

## PR Creation Process
1. Analyze changes: `git diff main...HEAD`
2. Determine affected components: Backend, Frontend, Database
3. Fill template sections
4. Create PR with your Git provider's CLI or UI

## PR Template Structure
```markdown
## Descripción
## Tipo de cambio
## Componentes afectados
## Issue relacionado
## Checklist
## Screenshots (if UI changes)
## Notas adicionales
```

## Title Conventions (Conventional Commits)
Format: `type(scope): description`

### Types
| Type | Usage |
|------|-------|
| `feat` | New functionality |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting |
| `refactor` | Refactoring without behavior change |
| `perf` | Performance improvement |
| `test` | Tests |
| `chore` | Maintenance, dependencies |

### Scopes
| Scope | Usage |
|-------|-------|
| `api` | Backend (Bun/FastAPI) |
| `ui` | Frontend genérico |
| `react` | Frontend React (components, hooks, routes) |
| `db` | Database |
| `auth` | Authentication |
| `authz` | Authorization |
| `infra` | Infrastructure |

### Examples
```
feat(api): add user profile endpoint
fix(react): resolve button alignment in header
refactor(db): optimize user query performance
chore: update dependencies
```

## Gestión de Changelog

Cada proyecto debe tener un `CHANGELOG.md` en su directorio raíz, siguiendo el formato de [keepachangelog.com](https://keepachangelog.com).

### Orden de Secciones (SIEMPRE este orden)

```
## [Unreleased]
### Added / ### Changed / ### Deprecated / ### Removed / ### Fixed / ### Security
```

### Formato de Entradas
- Línea en blanco después del header de sección antes de la primera entrada
- Línea en blanco entre secciones
- Ser específico: qué cambió, no por qué (eso va en el PR)
- Una entrada por PR / una entrada por story
- Sin punto al final
- No empezar con verbos redundantes

### Versionado Semántico

| Tipo de cambio | Bump de versión | Ejemplo |
|----------------|-----------------|---------|
| Bug fixes, parches | PATCH (x.y.**Z**) | 1.0.1 → 1.0.2 |
| Nuevas features (compatibles hacia atrás) | MINOR (x.**Y**.0) | 1.0.2 → 1.1.0 |
| Breaking changes, eliminaciones | MAJOR (**X**.0.0) | 1.1.0 → 2.0.0 |

**CRÍTICO:** Entradas en `### Removed` SOLO pueden aparecer en releases MAJOR.

**NUNCA modificar versiones ya publicadas.** Una vez liberada, la sección del changelog queda congelada.

### Ejemplos de Entradas Incorrectas
- `Fixed bug.` → Demasiado vago, tiene punto
- `Added new feature for users` → Falta link al PR, verbo redundante
- `Add search bar [(#123)]` → Verbo redundante

## Before Creating PR
1. All tests pass locally (`bun run test`)
2. Linting passes (`bun run lint`)
3. CHANGELOG.md updated (if applicable)
4. Branch is up to date with main
5. Commits are clean and descriptive
6. No console.log, console.debug or debug code left
7. Code review checklist completed

## Template de PR completa

```markdown
## Descripción

{Resumen del cambio en 2-3 oraciones. Explica qué problema resuelve y por qué se eligió esta solución.}

**Issue relacionado:** #{número} | **Proyecto:** {nombre-proyecto}

---

## Cambios realizados

### Backend
- [API] Nuevo endpoint `GET /api/v1/usuarios/{id}/perfil` — retorna perfil completo del usuario
- [Service] Refactor `UserService.getProfile()` con cache en Redis (TTL 5 min)
- [DB] Nueva query optimizada con joins en `repositories/user_profile_repository.ts`

### Frontend
- [Page] Nuevo componente `PerfilPage` con info personal y cambio de contraseña
- [Component] `PasswordChangeForm` — formulario con `react-hook-form` y validación inline (`zodResolver`)
- [Hook] `use-user-profile.ts` — query + mutation con `@tanstack/react-query`

### Database
- [Migration] Alembic `versions/2_3_1_add_profile_table.py` — nueva tabla `Profile` y FK a `Users`
- [Seed] `scripts/seed_profile_defaults.py` — perfiles por defecto para usuarios existentes

### Tests
- [Unit] `use-user-profile.test.ts` — 8 tests nuevos (cobertura 85% → 92%)
- [Integration] `profile.endpoint.spec.ts` — 12 tests, todos los códigos HTTP
- [E2E] `profile.spec.ts` — flujo completo: ver perfil, editar, cambiar contraseña

---

## Cambios de Configuración

| Archivo | Cambio |
|---------|--------|
| `.env` | Variable `REDIS_CACHE_PROFILES_TTL=300` |
| `bunfig.toml` | Config de test runner y resolución de módulos |
| `docker-compose.yml` | Añadido servicio Redis |
| `.env.example` | Variable `REDIS_CONNECTION_STRING` |

---

## Breaking Changes

- [ ] No
- [ ] Sí (detallar abajo)

{Si hay breaking changes, describir: qué cambió, cómo migrar, versión anterior vs nueva}

---

## Cómo probar este PR

### Prerrequisitos
- Base de datos actualizada: `bun run db:migrate` (o `alembic upgrade head` para Python)
- Redis corriendo: `docker compose up -d redis`

### Pasos manuales
1. Iniciar backend: `bun run dev:api`
2. Iniciar frontend: `bun run dev:web` (o `npm run dev` / `vite` para React)
3. Autenticarse con usuario `test@example.com` / `Test123!`
4. Navegar a `/perfil`
5. Verificar que los datos del perfil se cargan correctamente
6. Editar nombre y guardar → confirmar mensaje de éxito
7. Cambiar contraseña → confirmar
8. Verificar que los cambios persisten al recargar

### Tests automatizados
```bash
bun run test:unit              # 8 tests nuevos deben pasar
bun run test:integration       # 12 tests nuevos deben pasar
bunx playwright test profile   # Flujo E2E completo
```

---

## Screenshots / Evidencia

| Estado | Screenshot |
|--------|------------|
| Perfil cargado | `screenshots/perfil-cargado.png` |
| Edición en curso | `screenshots/perfil-editando.png` |
| Error validación | `screenshots/perfil-error.png` |
| Éxito | `screenshots/perfil-exito.png` |
| Mobile 375px | `screenshots/perfil-mobile.png` |

> **Nota:** Los screenshots se generan automáticamente con Playwright en CI.

---

## Plan de Rollback

### Si el PR falla en producción:

```bash
# 1. Revertir migración de BD (Alembic)
alembic downgrade -1           # Python: vuelve a revisión anterior
# o para Bun: bun run db:rollback 2.3.1

# 2. Revertir deploy
git revert <merge-commit-hash>
git push origin main

# 3. Verificar
alembic upgrade head           # Vuelve a versión anterior
```

### Tiempo estimado de rollback: < 5 minutos
### Impacto durante rollback: Ventana de ~30s sin servicio

---

## Checklist pre-merge

- [ ] Code review aprobado por al menos 1 reviewer
- [ ] Todos los tests pasan en CI
- [ ] Cobertura no disminuye (actual: 85%, mínima: 80%)
- [ ] SonarQube / Semgrep Quality Gate = Passed
- [ ] Sin vulnerabilidades nuevas (`bun audit` sin alta/crítica)
- [ ] CHANGELOG.md actualizado
- [ ] Screenshots adjuntos (si aplica)
- [ ] Documentación actualizada (README, wiki)
- [ ] Variables de entorno documentadas en `.env.example`
- [ ] Breaking changes comunicados al equipo
```

## Conventional commits — ejemplos por tipo

Cada commit debe seguir el formato `tipo(scope): mensaje`. Usa tiempo presente, imperativo, sin punto final.

### feat — Nueva funcionalidad

```
feat(api): add user profile endpoint
feat(react): implement password strength indicator component
feat(db): create profile table with constraints
feat(auth): add refresh token rotation
feat: add health check endpoint for kubernetes probes
```

### fix — Corrección de bug

```
fix(api): return 404 when user not found in profile endpoint
fix(react): fix button alignment in mobile header
fix(db): add missing index on profile.user_id
fix(auth): handle expired token gracefully instead of 500
fix: resolve CORS error on OPTIONS preflight requests
```

### docs — Documentación

```
docs(api): add openapi annotations to profile endpoints
docs(readme): update setup instructions with Redis requirement
docs: add ADR for cache strategy decision
docs(contributing): add PR checklist section
```

### style — Formato, estilo, linting

```
style(react): format with prettier and sort imports
style: apply eslint --fix across entire codebase
style(db): normalize SQL formatting in migration files
```

### refactor — Refactorización sin cambio funcional

```
refactor(api): extract validation logic into middleware
refactor(react): convert component to hooks-based state
refactor(db): consolidate duplicate queries into CTE
refactor: extract pagination helper into shared library
```

### perf — Mejora de rendimiento

```
perf(api): add Redis caching for profile reads
perf(react): lazy load profile image component
perf(db): add composite index on (user_id, created_at)
perf: reduce image payload with WebP conversion
```

### test — Tests

```
test(api): add unit tests for profile validation
test(react): add playwright E2E for profile flow
test(db): add integration tests for profile queries
test: add load testing scenario for profile endpoint
```

### chore — Mantenimiento, dependencias, tooling

```
chore: update dependencies to latest versions
chore: configure prettier and lefthook pre-commit hook
chore: add docker-compose for local Redis service
chore: set up GitHub Actions CI workflow
chore: bump version to 1.2.0
```

### build — Cambios en el sistema de build

```
build: update vite.config.ts bundle size thresholds
build: switch to esbuild-based builder for faster builds
build: configure Docker multi-stage build for smaller images
```

### ci — Cambios en CI/CD

```
ci: add security scan stage to pipeline
ci: cache bun install in GitHub Actions for faster runs
ci: configure Playwright sharding across 4 parallel runners
```

### Ejemplos compuestos (múltiples cambios)

Cuando un commit toca varios componentes:

```
feat(api,db): add profile feature with table and endpoint

feat(react): implement profile page
- Password strength meter
- Inline validation
- Responsive layout

refactor(react): extract form components into shared library

chore(deps): update react to v18.3
```

### Errores comunes en mensajes de commit

| Incorrecto | Correcto |
|------------|----------|
| `fix bug` | `fix(api): return 400 when email is invalid` |
| `added new feature` | `feat(react): add user search autocomplete` |
| `Cambios varios` | `refactor(db): normalize user_address into separate table` |
| `Update file.ts` | `fix(react): resolve infinite re-render in UserList` |
| `WIP` | (nunca hacer commit de WIP, usar squash) |

## Checklist pre-PR

Lista detallada de 20+ verificaciones antes de crear un Pull Request.

### Código y Build (8 items)

| # | Check | Cómo verificarlo |
|---|-------|------------------|
| 1 | Build compila sin errores | `bun run build` / `vite build` sin warnings que sean errores |
| 2 | TypeScript type check pasa | `bun run typecheck` / `tsc --noEmit` sin errores |
| 3 | Linter pasa sin warnings bloqueantes | `bun run lint` sin errores, sin warnings de severidad error |
| 4 | Tests unitarios pasan | `bun run test:unit` — todos verdes, sin flakes |
| 5 | Tests de integración pasan | `bun run test:integration` — todos verdes |
| 6 | Tests E2E pasan (si existen) | `bunx playwright test` — al menos los del módulo afectado |
| 7 | Cobertura no disminuye | Comparar con rama base: `bun run test:coverage` |
| 8 | Sin dependencias vulnerables | `bun audit` sin high/critical |

### Calidad (6 items)

| # | Check | Cómo verificarlo |
|---|-------|------------------|
| 9 | Sin console.log, debugger, TODO, FIXME sin issue asociado | `git diff main...HEAD \| grep -E "(console\.log|console\.debug|debugger|FIXME|TODO)"` |
| 10 | Sin código comentado | Revisar diff, no debe haber bloques comentados > 3 líneas |
| 11 | Nombres descriptivos | Variables, funciones, clases con nombre auto-explicativo |
| 12 | Sin magic numbers | Números literales → constantes con nombre (`const MAX_RETRIES = 3`) |
| 13 | Manejo de errores consistente | try/catch en operaciones de IO, red, BD; mensajes descriptivos |
| 14 | Logging sin datos sensibles | No loguear passwords, tokens, tarjetas de crédito, PII |

### Database (4 items)

| # | Check | Cómo verificarlo |
|---|-------|------------------|
| 15 | Migraciones con rollback | Alembic: cada revision tiene `upgrade()` y `downgrade()`, el rollback se probó (`alembic downgrade -1`) |
| 16 | Migraciones idempotentes | Ejecutar migration dos veces → mismo resultado (op.create_table if not exists / op.batch_alter_table) |
| 17 | Transacciones controlan errores | SQLAlchemy: `async with session.begin():` con rollback automático en excepción |
| 18 | Parámetros, no concatenación | SQL usa parámetros (`:param` / `$1`), nunca f-strings con `${variable}` |

### Frontend (4 items)

| # | Check | Cómo verificarlo |
|---|-------|------------------|
| 19 | Componentes responsivos | Probar en 375px, 768px, 1280px sin rupturas (breakpoints responsivos con Tailwind/CSS) |
| 20 | Estados cubiertos | Loading, empty, error, success en cada pantalla (`useState` + `@tanstack/react-query`) |
| 21 | Accesibilidad mínima | Labels en inputs, roles ARIA, contraste, teclado (axe-core) |
| 22 | Sin any / tipo implícito | TypeScript strict mode, interfaces para props y estado de hooks |

### PR y Documentación (5 items)

| # | Check | Cómo verificarlo |
|---|-------|------------------|
| 23 | CHANGELOG.md actualizado | Entrada en `[Unreleased]` con categoría correcta |
| 24 | Branch actualizada con main | `git merge main` sin conflictos, o rebase hecho |
| 25 | Commits limpios | Mensajes conventional commits, sin merge commits, sin WIP |
| 26 | Screenshots adjuntos (si UI) | Captura de: estado normal, error, loading, mobile |
| 27 | Variables de entorno documentadas | `.env.example` actualizado con nuevas variables |

### Post-merge (bonus — verificar antes de mergear)

| # | Check | Cómo verificarlo |
|---|-------|------------------|
| 28 | Code review aprobado | Al menos 1 approval, comentarios resueltos |
| 29 | CI/CD pipeline verde | Todos los stages: lint → test → build → deploy (bun) |
| 30 | Breaking changes comunicados | Slack/Teams al equipo, documentación de migración
