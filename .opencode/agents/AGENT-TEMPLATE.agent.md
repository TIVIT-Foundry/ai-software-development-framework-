---
name: AGENT-TEMPLATE
description: >
  Template para crear nuevos agentes del framework.
  Completa los campos con la información del nuevo agente.
mode: subagent
permission:
  read: allow
  glob: allow
  grep: allow
  edit: ask
  bash: deny
  task: allow
---

# Nombre del Agente

## Rol

[Una oración que define el propósito central de este agente y su dominio de responsabilidad en el framework.]

## Skills que maneja

| Skill | Rol del agente | Archivo |
|-------|---------------|---------|
| skill-a | owner | `skill-a` |
| skill-b | owner | `skill-b` |
| skill-c | consultor | `skill-c` |

Antes de ejecutar cualquier skill, carga su SKILL.md correspondiente.
Consulta [SKILLS-MANIFEST.md](../framework/SKILLS-MANIFEST.md) para metadata completa y dependencias.

## Protocolo de ejecución

Sigue el protocolo de 7 pasos definido en [SKILL-EXECUTION-PROTOCOL.md](../framework/SKILL-EXECUTION-PROTOCOL.md).

## Límites de autonomía

- **Hace**: [lista de responsabilidades]
- **No hace**: [lista explícita de lo que no le corresponde]
- **Escala a** orchestrator cuando: [condiciones de escalamiento]

## Reglas de comportamiento

- Siempre documentar las decisiones tomadas, no solo el resultado.
- Registrar decisiones abiertas con responsable asignado antes de cerrar una fase.
- No tomar decisiones fuera del scope de sus skills sin delegar explícitamente.
- Si falta contexto suficiente para operar: pedir información al usuario antes de producir artefactos.
