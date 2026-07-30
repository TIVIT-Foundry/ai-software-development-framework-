---
name: angular-doctor
description: 'Automated static analysis gate for Angular codebases using the angular-doctor CLI (npx angular-doctor@latest) — Angular-aware linting (components, directives, pipes, performance, architecture), dead code detection via knip, and a 0-100 health score. Complements the manual checklist in code-review, does not replace it. Trigger: before opening a PR that touches angular/angular-services code, or when wiring the CI quality gate for an Angular project.'
version: 1.0
metadata:
  phase:
  - quality
  layer:
  - testing/frontend
  enforcement: recommended
  depends_on:
  - angular
  consumed_by:
  - code-review
  agent_roles:
  - control-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Qué es

[Angular Doctor](https://github.com/antonygiomarxdev/angular-doctor) es una herramienta externa (paquete npm) que escanea un proyecto Angular buscando issues de lint específicos de Angular (componentes, directivas, pipes, performance, arquitectura, TypeScript) y código muerto (archivos, exports y tipos sin uso, vía `knip`), produciendo un health score 0-100 con diagnósticos accionables. Soporta workspaces Angular CLI y npm/pnpm.

Esta skill NO reimplementa esa lógica — documenta cómo invocarla y cómo interpretar su salida dentro del flujo de este framework.

## Critical Rules

| Rule | Type | Rationale |
|------|------|-----------|
| Correr antes de abrir PR, no solo en CI | ALWAYS | Feedback inmediato, evita ping-pong de review |
| No usarlo como sustituto de code-review | ALWAYS | Detecta patrones deterministas, no diseño/lógica de negocio |
| En workspaces multi-proyecto, apuntar con `--project` al módulo tocado | ALWAYS | Evita ruido de proyectos no relacionados con el PR |
| Documentar excepciones (falsos positivos) inline, no silenciar globalmente | RECOMMENDED | Mantiene trazabilidad de por qué se ignoró un hallazgo |

## Instalación y uso

```bash
# Local, antes de PR (no requiere instalación previa)
npx angular-doctor@latest

# Contra un proyecto específico dentro de un workspace Angular CLI o npm/pnpm
npx angular-doctor@latest --project apps/admin

# Como agent skill instalable directamente en Claude Code
npx angular-doctor@latest --install-skill claude-code
```

### Integración CI/CD

Angular Doctor se integra a GitHub Actions posteando el health score y los diagnósticos como comentario de PR, y puede usarse como quality gate (fallar el pipeline por debajo de un score mínimo). Wire esto en la skill `ci-cd` como job adicional, no como reemplazo de `unit-testing`/`playwright`:

```yaml
# .github/workflows/angular-doctor.yml (fragmento)
- name: Angular Doctor
  run: npx angular-doctor@latest --project ${{ env.PROJECT }} --min-score 80
```

## Categorías que detecta

| Categoría | Ejemplos |
|-----------|----------|
| Componentes/Directivas/Pipes | Lifecycle hooks mal usados, `ChangeDetectionStrategy` faltante, pipes impuros innecesarios |
| Performance | `ngDoCheck` costoso, falta de `OnPush`/signals, `@for` sin `track` |
| Arquitectura | NgModules innecesarios en vez de standalone components, acoplamiento entre features |
| Código muerto | Archivos, exports y tipos sin ningún import real (vía `knip`) |
| Health score | Agregado 0-100 de todo lo anterior, útil como gate numérico en CI |

Esto se solapa parcialmente con la tabla "Frontend (Angular)" de `code-review` — la diferencia es que `angular-doctor` es determinista, automatizable en CI, y produce un score agregado; `code-review` cubre juicio humano sobre diseño y lógica de negocio.

## Interpretación de resultados

| Resultado | Acción |
|---|---|
| Health score por debajo del mínimo acordado (ej. 80) | Blocker — no mergear hasta subir el score o documentar excepción explícita |
| Diagnóstico individual de severidad alta | Igual tratamiento que un warning de `code-review`: debe discutirse |
| Código muerto detectado | Eliminar si se confirma sin uso; si es API pública intencional, excluir explícitamente de `knip` |

## Verification checklist

- [ ] `npx angular-doctor@latest` corre sin errores de configuración contra el proyecto/workspace correcto
- [ ] Health score cumple el mínimo acordado para el módulo, o hay excepción documentada
- [ ] Código muerto reportado fue eliminado o excluido explícitamente con justificación
- [ ] El resultado se referencia en el resumen del PR (skill `pull-request`) cuando hubo hallazgos relevantes
