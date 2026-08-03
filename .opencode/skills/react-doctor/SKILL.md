---
name: react-doctor
description: 'Automated static analysis gate for React codebases using the react-doctor CLI (npx react-doctor@latest) — deterministic scan for anti-patterns across state & effects, performance, architecture, security, and accessibility. Complements the manual checklist in code-review, does not replace it. Trigger: before opening a PR that touches react/react-services code, or when wiring the CI quality gate for a React project.'
version: 1.2
metadata:
  phase:
  - quality
  layer:
  - testing/frontend
  enforcement: recommended
  depends_on:
  - react
  consumed_by:
  - code-review
  agent_roles:
  - control-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Qué es

[React Doctor](https://react.doctor/) es una herramienta externa (paquete npm `react-doctor`, alto volumen de descargas semanales) que escanea código React de forma determinista — no es un linter genérico, busca anti-patrones específicos de React: `useEffect` innecesarios, prop drilling evitable con Context, problemas de accesibilidad, seguridad y arquitectura, además de dead-code y supply-chain de dependencias. Funciona con Next.js, Vite, TanStack, React Native, Expo.

Esta skill NO reimplementa esa lógica — documenta cómo invocarla y cómo interpretar su salida dentro del flujo de este framework.

**Sí produce un score agregado 0-100** (verificado corriendo `npx react-doctor@latest` — el gauge "N / 100" es lo primero que muestra en consola, antes que el detalle de hallazgos). El score también está disponible por separado con `--score` (imprime solo el número, útil para scripts/agentes) y dentro de `--json` (para reportes estructurados). En CI, `react-doctor ci install --commit-status` publica ese score como commit status. No es una skill "sin score" como se documentó en una versión anterior de este archivo — la diferencia real con `angular-doctor` es que aquí el gate por defecto es a nivel de severidad (`--blocking error|warning|none`), no un umbral de score fijo; se puede usar cualquiera de los dos.

## Critical Rules

| Rule | Type | Rationale |
|------|------|-----------|
| Correr antes de abrir PR, no solo en CI | ALWAYS | Feedback inmediato, evita ping-pong de review |
| No usarlo como sustituto de code-review | ALWAYS | Detecta patrones deterministas, no diseño/lógica de negocio |
| En CI, revisar solo lo introducido por el PR, no el backlog existente | ALWAYS | Evita bloquear PRs por deuda técnica preexistente no relacionada |
| Documentar excepciones (falsos positivos) inline, no silenciar globalmente | RECOMMENDED | Mantiene trazabilidad de por qué se ignoró un hallazgo |

## Instalación y uso

```bash
# Local, antes de PR (no requiere instalación previa) — escanea el directorio actual
npx react-doctor@latest

# Contra un directorio específico (monorepo) — el directorio es un argumento posicional
npx react-doctor@latest apps/web

# Solo el score (para scripts/agentes)
npx react-doctor@latest --score

# Reporte estructurado completo
npx react-doctor@latest --json

# Instala la skill del agente + hooks nativos en el repo (setup interactivo, o --yes para no-interactivo)
npx react-doctor@latest install --yes
```

### Integración CI/CD

React Doctor soporta GitHub Actions de forma nativa (auto-detectado) y un scaffold gate-only para GitLab CI (`--provider gitlab-ci`). El comando `ci install` genera el workflow — no escribirlo a mano. Wire esto en la skill `ci-cd` como un job adicional, no como reemplazo de `unit-testing`/`playwright`:

```bash
# Genera el workflow de CI, con gate por severidad y comentario en el PR
npx react-doctor@latest ci install --blocking error --comment --commit-status
```

Por defecto el scope de un scan en PR es `changed` (solo lo que introduce el diff, no el backlog completo) — usar `--scope full` explícitamente para escanear todo el proyecto en cada PR.

## Categorías que detecta

| Categoría | Ejemplos |
|-----------|----------|
| State & Effects | `useEffect` usado como fetch manual, deps mal declaradas, estado derivado duplicado |
| Performance | Memoización innecesaria o faltante, listas sin `key` estable, imports eager evitables |
| Arquitectura | Prop drilling evitable con Context/composición, componentes con demasiadas responsabilidades |
| Seguridad | `dangerouslySetInnerHTML` sin sanitizar, uso inseguro de URLs/redirects |
| Accesibilidad | Falta de labels/ARIA, elementos interactivos no navegables por teclado |

Esto se solapa parcialmente con la tabla "Frontend (React)" de `code-review` y con `a11y-testing` — la diferencia es que `react-doctor` es determinista y automatizable en CI; `code-review` y `a11y-testing` cubren juicio humano y pruebas dinámicas (axe-core en runtime) respectivamente.

## Interpretación de resultados

| Severidad reportada | Acción |
|---|---|
| Error/Critical | Blocker — no mergear hasta resolver o documentar excepción explícita |
| Warning | Igual tratamiento que un warning de `code-review`: debe discutirse |
| Info/Suggestion | Opcional, criterio del reviewer |

| Score | Interpretación |
|---|---|
| 100 | Sin hallazgos (o proyecto React no detectado — verificar que el scan realmente corrió contra código React antes de confiar en un 100) |
| Por debajo del mínimo acordado para el módulo | Blocker si se usa como gate de score (`--blocking` complementario, no sustituto) |

El score es un agregado útil como tendencia/dashboard; el gate real que bloquea merge en este framework sigue siendo "cero Error/Critical sin excepción documentada" — no fijar un umbral de score arbitrario sin haber corrido el scan contra el proyecto real primero.

## Verification checklist

- [ ] `npx react-doctor@latest` corre sin errores de configuración contra el paquete frontend
- [ ] Cero hallazgos "Error/Critical" sin excepción documentada
- [ ] Si está en CI, el job comenta solo el diff del PR (no todo el backlog)
- [ ] El resultado se referencia en el resumen del PR (skill `pull-request`) cuando hubo hallazgos relevantes
