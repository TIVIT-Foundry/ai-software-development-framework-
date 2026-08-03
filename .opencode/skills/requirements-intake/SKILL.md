---
name: requirements-intake
description: 'Structured intake template ("Documento Cero") that converts whatever the client provides — a formal spec, loose notes, or nothing at all — into a signed-off functional baseline before any HU is written. Trigger: When a client hands over informal, incomplete, or non-existent functional documentation, before drafting hu-template stories.'
version: 1.0
metadata:
  phase:
  - inception
  layer:
  - business
  enforcement: recommended
  depends_on: []
  consumed_by:
  - hu-template
  agent_roles:
  - design-agent
  - orchestrator-agent
  validation_profile: documentation
mcp_usage: none
---

## Propósito

Convertir el input funcional del cliente — sea un documento formal, notas sueltas en un chat, o nada — en un **Documento Cero**: una línea base estructurada, sección por sección, que el equipo analiza, el cliente confirma (o no responde y se documenta el default propuesto), y que queda firmada como fuente de verdad antes de escribir la primera HU.

Sin esta skill, el equipo interpreta el input del cliente de forma ambigua, repregunta constantemente durante el desarrollo, y no hay un punto de referencia auditable cuando el alcance cambia a mitad de proyecto.

## Cuándo usar esta skill

Activar cuando:
- El cliente entrega un documento funcional informal o incompleto (2 páginas vagas, un chat, una llamada).
- El cliente no entrega ningún documento y solo hay una conversación verbal.
- Se necesita una línea base firmada antes de iniciar `hu-template` para evitar consultas repetidas durante el desarrollo.

**No activar** cuando el cliente ya entrega un documento formal completo y sin ambigüedad (ej. spec técnica ya validada) — en ese caso se puede ir directo a `hu-template`, aunque sigue siendo buena práctica pasar por esta skill como checklist de completitud.

## Template del Documento Cero

```markdown
# Documento Cero — {Proyecto/Módulo}
**Cliente:** {nombre} | **Fecha de envío:** {fecha} | **Plazo de análisis:** {1-3 días hábiles}

## 1. Contexto de negocio
{Por qué se construye esto, qué problema resuelve}

## 2. Actores
| Actor | Rol | Necesidad principal |
|-------|-----|---------------------|

## 3. Alcance funcional
{Qué incluye y qué NO incluye explícitamente esta fase}

## 4. Reglas de negocio
| Regla | Descripción | Origen (cliente / propuesta del equipo) |
|-------|-------------|------------------------------------------|

## 5. Casos borde
{Situaciones no obvias que el cliente no mencionó pero el equipo identificó}

## 6. Requerimientos no funcionales
{Performance, seguridad, idiomas, disponibilidad, volumetría esperada}

## 7. Criterios de aceptación de alto nivel
{Qué demuestra que el proyecto/módulo cumple el objetivo — se refinan luego en cada HU}

## 8. Glosario
| Término | Significado en este proyecto |
|---------|-------------------------------|

## 9. Preguntas abiertas
| # | Pregunta | Respuesta del cliente | Fecha | Si no responde: default asumido |
|---|----------|------------------------|-------|-----------------------------------|

## 10. Historial de cambios (adenda)
| Fecha | Cambio solicitado | Confirmado por | Impacto |
|-------|--------------------|-----------------|---------|
```

## Proceso

1. **Borrador**: el equipo llena las secciones 1-8 con lo que el cliente ya proporcionó, dejando explícito lo que falta.
2. **Análisis**: el equipo se compromete a un plazo corto (1-3 días hábiles) para completar la sección 9 con preguntas concretas sobre cada vacío — no preguntas genéricas tipo "cuéntame más".
3. **Confirmación**: se envía al cliente. Si responde, se registra su respuesta. Si no responde en el plazo acordado, se documenta explícitamente el default que el equipo asume (nunca se deja un vacío silencioso).
4. **Línea base**: el documento queda congelado como fuente de verdad. A partir de aquí se derivan las HUs (`hu-template`).
5. **Cambios posteriores**: cualquier cambio de alcance durante el desarrollo se discute con el cliente y se agrega como fila nueva en la sección 10 (Historial de cambios), fechada y con quién lo confirmó — nunca como un mensaje suelto de chat sin registrar. Esto da la trazabilidad tipo "sello" que evita disputas de alcance ("tú dijiste esto", "no, dijiste lo otro").

## Critical Rules

| Rule | Type | Rationale |
|------|------|-----------|
| Todo vacío del cliente se resuelve con un default explícito documentado, nunca con un supuesto silencioso | ALWAYS | Un supuesto no registrado es indistinguible de un error cuando el proyecto avanza |
| El plazo de análisis se comunica al cliente antes de empezar, no después | ALWAYS | Evita fricción y gestiona expectativas de tiempo |
| Cualquier cambio de alcance en producción se agrega a la sección 10, no se resuelve solo por chat | ALWAYS | Es la base de la trazabilidad — sin esto, `governance-constitution` no tiene evidencia de qué se acordó |
| No escribir HUs (`hu-template`) sin que el Documento Cero esté al menos en estado "línea base congelada" | RECOMMENDED | Evita retrabajo cuando las HUs quedan huérfanas de un cambio de alcance no registrado |

## Relación con otras skills

- `framework-discovery` — si el input del cliente requiere primero entender el dominio de negocio (vertical, actores del ecosistema, no solo el proyecto puntual), se ejecuta antes de esta skill.
- `hu-template` — consume el Documento Cero confirmado como insumo directo: cada sección de reglas de negocio y criterios de aceptación de alto nivel se descompone en HUs verificables.
- `client-readiness-checklist` — determina si esta skill debe activarse (cliente sin documentación madura) o puede omitirse (cliente ya trae spec formal completa).

## Verification checklist

- [ ] Las 10 secciones del template están completas o marcadas explícitamente como "N/A"
- [ ] Cada pregunta abierta sin respuesta del cliente tiene un default documentado, no un vacío
- [ ] El documento fue compartido con el cliente y hay evidencia de envío (fecha, canal)
- [ ] Las HUs derivadas (`hu-template`) referencian la sección del Documento Cero de la que provienen
- [ ] Existe al menos una fila en la sección 10 por cada cambio de alcance ocurrido después de la línea base
