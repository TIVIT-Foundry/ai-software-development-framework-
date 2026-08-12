# SKILL-EXECUTION-PROTOCOL.md — Protocolo de Ejecución de Skills

**TIVIT Foundry — Framework Agéntico**
**Versión:** 2.0.0
**Última actualización:** 17 de julio de 2026

---

## Propósito

Este documento define el protocolo estándar que cada agente debe seguir al ejecutar una skill. Es la columna vertebral del framework: todos los agentes lo referencian y lo aplican. Versión 2.0 incorpora workflow engine patterns (conditional gates, fan-out/fan-in, state persistence) y delegation patterns del ecosistema Gentle-AI y Spec Kit.

---

## Protocolo de 7 Pasos

### Paso 1: Carga de Contexto

1. Leer el `SKILL.md` de la skill a ejecutar
2. Extraer frontmatter: `name`, `description`, `phase`, `layer`, `enforcement`, `depends_on`, `consumed_by`
3. Verificar que las skills en `depends_on` ya fueron ejecutadas (si aplica)
4. Cargar el SKILLS-MANIFEST.md para entender la posición de la skill en el framework

**Regla:** Si `enforcement: mandatory` y falta una dependencia, DETENER y reportar al orchestrator.

### Paso 2: Validación de Prerequisitos

1. Verificar que el contexto de entrada existe (discovery, concepción, spec, etc.)
2. Verificar que los artefactos de entrada de skills dependientes están completos
3. Si hay `consumed_by` skills que esperan esta output, verificar compatibilidad

**Checklist:**
- [ ] Skill cargada correctamente
- [ ] Dependencias satisfechas
- [ ] Contexto de entrada disponible
- [ ] Artefactos de entrada completos

### Paso 3: Planificación

1. Identificar los artefactos de salida que esta skill debe generar
2. Mapear cada artefacto a una acción concreta
3. Definir orden de ejecución si hay múltiples artefactos
4. Identificar puntos de decisión que requieren input humano (HITL)

**Regla:** Si `enforcement: mandatory`, TODOS los artefactos de salida son obligatorios.

### Paso 4: Ejecución

1. Generar cada artefacto siguiendo las instrucciones del SKILL.md
2. Aplicar las reglas y restricciones definidas en la skill
3. Marcar cada artefacto como completado
4. Si hay HITL, pausar y esperar confirmación antes de continuar

**Regla de output:** Cada artefacto debe ser un archivo concreto, no una descripción vaga.

### Paso 5: Validación Interna

1. Verificar que cada artefacto cumple con los criterios de calidad de la skill
2. Verificar coherencia entre artefactos (que no se contradigan)
3. Verificar que se respetaron las restricciones del framework-governance
4. Ejecutar checks de seguridad si aplica (framework-security)

**Checklist de validación:**
- [ ] Todos los artefactos generados
- [ ] Criterios de calidad cumplidos
- [ ] Coherencia interna verificada
- [ ] Governance respetado
- [ ] Seguridad validada

### Paso 6: Handoff

1. Preparar resumen ejecutivo de lo generado
2. Identificar qué skills consumidoras pueden activarse ahora
3. Notificar al orchestrator con el estado de la ejecución
4. Si hay bundle completo, esperar confirmación del usuario

**Formato de handoff:**
```
SKILL: [nombre]
ESTADO: COMPLETADA | PARCIAL | BLOQUEADA
ARTEFACTOS: [lista de archivos generados]
SIGUIENTES: [skills que pueden activarse]
BLOQUEOS: [si hay alguno]
```

### Paso 7: Registro

1. Registrar la ejecución en el log de trazabilidad
2. Actualizar el estado de la skill en el workflow
3. Documentar decisiones tomadas (ADR si aplica)
4. Marcar dependencias como satisfechas para skills futuras

---

## Workflow Engine Patterns (v2.0)

### State Persistence & Resume

Cada workflow mantiene estado persistente para permitir resume después de interrupciones:

```
.workflow/
├── state.json          # Estado actual del workflow
├── completed/          # Steps completados
├── artifacts/          # Artefactos generados
└── errors/             # Errores encontrados
```

```json
{
  "workflow_id": "feature-user-auth",
  "current_step": "N25-authentication",
  "bundle": "bundle-backend",
  "mode": "hybrid",
  "steps_completed": ["N17", "N18", "N19", "N24"],
  "steps_failed": [],
  "artifacts": {
    "N17-api-first-backend": ["handlers/auth_handler.py", "dtos/auth_dto.py"],
    "N18-database-modeling": ["database/core/tables/users.sql"]
  },
  "started_at": "2026-07-17T10:00:00Z",
  "last_checkpoint": "2026-07-17T10:45:00Z"
}
```

### Conditional Gates

Antes de avanzar entre steps, se evalúan gates condicionales:

| Gate | Condición | Acción si falla |
|------|-----------|-----------------|
| **Simplicity Gate** | La solución es la más simple posible | Replanificar |
| **Test Gate** | Tests existen y pasan antes del código, **por cada capa/stack presente** (backend, frontend, Bun, DB): si el cambio toca lógica frontend, el gate exige su job de tests en CI (Vitest/RTL o `ng test`), no solo backend | Escribir tests primero por stack |
| **Constitution Gate** | Respeta los 9 artículos de la constitución | Revisar con `governance-constitution` |
| **Security Gate** | No hay vulnerabilidades OWASP Top 10 | Ejecutar `security-testing` |
| **Dependency Gate** | Skills en `depends_on` completadas | Ejecutar dependencias faltantes |
| **Artifact Gate** | Artefactos de entrada existen y son válidos | Solicitar al usuario |

> **Test Gate por capa:** el checklist del Art. 4 de la constitución ("Run in CI pipeline")
> aplica a cada stack con lógica en el cambio. Un PR que modifica `AuthContext`/`LoginPage`
> sin job de tests frontend en CI NO pasa el gate, aunque el backend esté cubierto.

```python
class GateEvaluator:
    async def evaluate(self, gate: Gate, context: WorkflowContext) -> GateResult:
        if gate.name == "simplicity":
            return await self.check_simplicity(context.design)
        elif gate.name == "test":
            return await self.check_tests_exist_before_code(context)
        elif gate.name == "constitution":
            return await self.check_constitution(context)
        # ...
```

### Fan-Out / Fan-In (Parallel Execution)

Skills independientes pueden ejecutarse en paralelo:

```
                    ┌─────────────────┐
                    │   N17: spec     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ database │  │backend   │  │ security │
        │ modeling │  │  api     │  │ testing  │
        │  (N18)   │  │  (N19)   │  │  (N24)   │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    ┌─────────────────┐
                    │  N25: integrate │
                    └─────────────────┘
```

```python
async def fan_out_execute(skills: list[str], context: WorkflowContext):
    """Execute independent skills in parallel."""
    tasks = [
        execute_skill(skill, context) 
        for skill in skills 
        if are_independent(skills)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Fan-in: collect results and check for errors
    errors = [r for r in results if isinstance(r, Exception)]
    if errors:
        for e in errors:
            context.report_error(e)
        return FanInResult.FAILED
    return FanInResult.COMPLETED
```

---

## Delegation Patterns (v2.0)

### Delegation Models

El orchestrator puede delegar en 4 modelos (ver AGENT-MODEL.md):

| Modelo | Descripción | Agentes aplicables |
|--------|-------------|-------------------|
| **Full (sub-agents)** | El orchestrator delega la skill completa a un agente especializado | design, control, delivery |
| **Chained** | Un agente completa su trabajo y pasa el resultado al siguiente | design → delivery → control |
| **Adversarial** | Múltiples agentes revisan el mismo output desde diferentes perspectivas | control (security, reliability, readability) |

### Adversarial Delegation (Judgment Day)

Cuando una skill es crítica (security, compliance), se ejecuta revisión adversarial:

```
                    ┌─────────────────┐
                    │   delivery:     │
                    │   implement     │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │ control  │       │ control  │       │ control  │
   │ security │       │reliability│      │readability│
   │ reviewer │       │ reviewer │       │ reviewer │
   └────┬─────┘       └────┬─────┘       └────┬─────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    ┌─────────────────┐
                    │   orchestrator  │
                    │   arbiter       │
                    │   (conflict     │
                    │   resolution)   │
                    └─────────────────┘
```

### Stop Rules

El orchestrator debe detener la ejecución y escalar cuando:

| Regla | Condición | Acción |
|-------|-----------|--------|
| **4-file rule** | Más de 4 archivos modificados sin confirmación | Pausar, mostrar cambios, pedir confirmación |
| **Multi-file write** | Escritura en más de 3 archivos en un paso | Revisar plan, posible sobre-ingeniería |
| **PR rule** | Cambios acumulados justifican un PR | Crear PR, no seguir acumulando |
| **Incident rule** | Error irrecuperable en skill mandatory | Detener workflow, notificar usuario |
| **Long-session rule** | Sesión > 2 horas sin checkpoint | Guardar estado, sugerir resume |
| **Fresh review rule** | Más de 10 skills ejecutadas sin review | Ejecutar `review-adversarial` |
| **Constitution violation** | Cualquier violación de `governance-constitution` | Detener, reportar a control agent |

---

## Modos de Ejecución

### Modo Individual / Per-Skill (Fases A-B, N0-N9)

- Cada skill se ejecuta por separado
- Se confirma cada skill antes de continuar (49 confirmaciones en flujo completo)
- Máximo control, máximo tiempo

### Modo Bundle (Fases C-H, N10-N49)

- Skills del mismo bundle se ejecutan en secuencia
- Se confirma una vez al completar el bundle (6 confirmaciones)
- Balance control/velocidad

### Modo Meta-Skills (6 confirmaciones)

- Solo cuando el usuario lo pide explícitamente (`agent-backend`, `agent-frontend`,
  `agent-fullstack`, `agent-qa`)
- Cada meta-skill encadena sus skills de dominio y confirma al final del encadenamiento

### Modo Hybrid (default)

- Fases A-B: Individual (confirmación por skill)
- Fases C-H: Bundle (confirmación por bundle)
- 15 confirmaciones totales (16 si N0 está activo — ver SKILLS-MANIFEST)

---

## Manejo de Errores

| Error | Acción |
|-------|--------|
| Skill dependiente no ejecutada | Detener, reportar a orchestrator |
| Artefacto de entrada faltante | Detener, solicitar al usuario |
| Violación de governance | Detener, reportar a control agent |
| Timeout en HITL | Continuar con defaults documentados |
| Error de validación | Reintentar una vez, luego escalar |

---

## Escalamiento

Si un agente no puede resolver un problema:

1. **Primero:** Intentar resolver con las herramientas disponibles
2. **Segundo:** Consultar el SKILL-ROUTING.md para alternativas
3. **Tercero:** Escalar al orchestrator
4. **Cuarto:** Escalar al usuario para decisión

---

## Referencias

- `SKILLS-MANIFEST.md` — Catálogo de skills
- `SKILL-ROUTING.md` — Routing de skills
- `AGENT-MODEL.md` — Modelo de agentes
- `framework-governance/SKILL.md` — Reglas del framework
