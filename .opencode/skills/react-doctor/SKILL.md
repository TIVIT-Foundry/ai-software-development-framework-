---
name: react-doctor
description: 'Automated static analysis gate for React codebases using the react-doctor CLI (npx react-doctor@latest) — deterministic scan for anti-patterns across state & effects, performance, architecture, security, and accessibility. Complements the manual checklist in code-review, does not replace it. Trigger: before opening a PR that touches react/react-services code, or when wiring the CI quality gate for a React project.'
version: 1.0
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

[React Doctor](https://www.react.doctor/) es una herramienta externa (paquete npm, ~600K descargas/semana) que escanea código React de forma determinista — no es un linter genérico, busca anti-patrones específicos de React: `useEffect` innecesarios, prop drilling evitable con Context, problemas de accesibilidad, seguridad y arquitectura. Funciona con Next.js, Vite, TanStack, React Native, Expo.

Esta skill NO reimplementa esa lógica — documenta cómo invocarla y cómo interpretar su salida dentro del flujo de este framework.

## Critical Rules

| Rule | Type | Rationale |
|------|------|-----------|
| Correr antes de abrir PR, no solo en CI | ALWAYS | Feedback inmediato, evita ping-pong de review |
| No usarlo como sustituto de code-review | ALWAYS | Detecta patrones deterministas, no diseño/lógica de negocio |
| En CI, revisar solo lo introducido por el PR, no el backlog existente | ALWAYS | Evita bloquear PRs por deuda técnica preexistente no relacionada |
| Documentar excepciones (falsos positivos) inline, no silenciar globalmente | RECOMMENDED | Mantiene trazabilidad de por qué se ignoró un hallazgo |

## Instalación y uso

```bash
# Local, antes de PR (no requiere instalación previa)
npx react-doctor@latest

# Contra un directorio específico (monorepo)
npx react-doctor@latest --path apps/web

# Como agent skill instalable directamente en Claude Code
npx react-doctor@latest --install-skill claude-code
```

### Integración CI/CD

React Doctor soporta GitHub Actions de forma nativa (comenta en el PR solo los issues que introduce el diff, no el backlog completo) y un scaffold gate-only para GitLab CI. Wire esto en la skill `ci-cd` como un job adicional, no como reemplazo de `unit-testing`/`playwright`:

```yaml
# .github/workflows/react-doctor.yml (fragmento)
- name: React Doctor
  run: npx react-doctor@latest --format github-pr-comment
```

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

## Verification checklist

- [ ] `npx react-doctor@latest` corre sin errores de configuración contra el paquete frontend
- [ ] Cero hallazgos "Error/Critical" sin excepción documentada
- [ ] Si está en CI, el job comenta solo el diff del PR (no todo el backlog)
- [ ] El resultado se referencia en el resumen del PR (skill `pull-request`) cuando hubo hallazgos relevantes
