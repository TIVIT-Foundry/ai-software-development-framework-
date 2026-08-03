---
name: client-readiness-checklist
description: 'Checklist run during commercial onboarding to determine what a new client/project needs before the framework can operate — functional documentation maturity, greenfield vs. brownfield status, access/credentials, and infrastructure tier. Trigger: When a new client or project is being evaluated for adoption, before framework-discovery starts.'
version: 1.0
metadata:
  phase:
  - discovery
  layer:
  - business
  enforcement: recommended
  depends_on: []
  consumed_by:
  - framework-discovery
  - project-bootstrap
  agent_roles:
  - orchestrator-agent
  - design-agent
  validation_profile: documentation
mcp_usage: none
---

## Propósito

Determinar, antes de arrancar `framework-discovery`, qué tan preparado está un cliente o proyecto para operar bajo el framework, y qué le falta levantar al equipo. Sin esto, cada proyecto nuevo se evalúa de forma ad hoc y el equipo descubre vacíos (documentación inexistente, sistema legado, sin accesos) a mitad de la ejecución en vez de al inicio.

## Cuándo usar esta skill

Activar cuando:
- Se evalúa un cliente o proyecto nuevo para adopción del framework (onboarding comercial).
- Se necesita decidir si aplica el flujo estándar greenfield o el flujo de reanálisis para sistemas existentes.
- Se debe estimar el nivel de infraestructura y presupuesto antes de comprometer un alcance.

## Checklist

| Punto | Estado | Qué determina |
|-------|--------|----------------|
| **Documentación funcional** | ✅ Formal y completa / ⚠️ Informal o parcial / ❌ Inexistente | Si es ⚠️ o ❌, activa `requirements-intake` antes de escribir HUs |
| **Estado del proyecto** | ✅ Greenfield (desde cero) / ⚠️ Brownfield en stack conocido / ❌ Brownfield en stack legado (COBOL, Java, etc.) | Si es ❌, aplica el flujo de reanálisis (ver abajo) antes de tocar código |
| **Accesos del cliente** | ✅ Repos, entornos y credenciales entregados / ⚠️ Parcial / ❌ Ninguno | Bloquea `project-bootstrap` y `ci-cd` hasta resolverse |
| **Arquitectura ya definida** | ✅ Cliente trae arquitectura / ⚠️ Parcial / ❌ Ninguna | Si ✅, se puede saltar directo a `project-architecture`; si ❌, pasa por `framework-discovery` → `framework-architecture` completo |
| **Nivel de infraestructura** | Básica / Media / Avanzada (según presupuesto y throughput de tokens esperado) | Alimenta a `framework-platform` y `costos-llm` para dimensionar despliegue y modelo |

### Flujo de reanálisis (stack legado)

Cuando el proyecto existente está en un stack no cubierto por el framework (ej. COBOL, Java monolítico):

1. Estudio completo de la plataforma actual: qué hace, qué reglas de negocio codifica, qué integraciones tiene.
2. Identificar qué skills existentes aplican tal cual, cuáles necesitan adaptarse, y cuáles hay que crear desde cero para ese stack.
3. Definir reglas de flujo y convenciones nuevas específicas del proyecto (naming, estructura, endpoints) antes de generar código.
4. Recién entonces se integra al framework como un proyecto adoptado, igual que uno nacido desde cero.

Este flujo es más lento que un proyecto greenfield — debe comunicarse así en la estimación, no tratarse como un proyecto estándar con overhead adicional.

### Nivel de infraestructura (placeholder)

La definición detallada de tiers básico/medio/avanzado (modelos, throughput de tokens, tamaño de equipo, costo) es un tema en evaluación — ver `framework-platform` (portabilidad cloud/on-premise) y `costos-llm` (que hoy excluye explícitamente modelos self-hosted/open-source de su alcance). Esta skill solo registra qué tier pidió o necesita el cliente; el diseño técnico del tier se resuelve en esas otras skills.

## Critical Rules

| Rule | Type | Rationale |
|------|------|-----------|
| No comprometer alcance ni fecha antes de completar este checklist | ALWAYS | Un proyecto brownfield legado o sin accesos cambia radicalmente el esfuerzo real |
| Registrar el estado real, no el deseado | ALWAYS | "El cliente dice que tiene arquitectura definida" y "el cliente tiene arquitectura definida" no son lo mismo — verificar antes de asumir |
| Un checklist con puntos ❌ no bloquea el proyecto, pero sí debe reflejarse en el plan de trabajo | RECOMMENDED | El objetivo es visibilidad, no burocracia |

## Relación con otras skills

- `requirements-intake` — se activa si el punto "Documentación funcional" queda en ⚠️ o ❌.
- `framework-discovery` — consume el resultado completo de este checklist como contexto de entrada.
- `project-bootstrap` — consume el punto de "Accesos del cliente" y "Arquitectura ya definida" para decidir qué tan directo puede ir al setup técnico.

## Verification checklist

- [ ] Los 5 puntos del checklist tienen un estado asignado (no en blanco)
- [ ] Si "Documentación funcional" no es ✅, se registró si se activó `requirements-intake`
- [ ] Si "Estado del proyecto" es ❌ (legado), el plan de trabajo refleja el flujo de reanálisis, no un cronograma greenfield estándar
- [ ] El nivel de infraestructura solicitado quedó registrado, aunque el diseño técnico se resuelva después
