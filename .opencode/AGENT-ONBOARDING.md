# AGENT-ONBOARDING.md — Arranque y autoconfiguración del agente

> Este documento se carga automáticamente en cada sesión (via `instructions` de
> `opencode.json`). Es el checklist de arranque: qué verificar y cómo orientarse
> antes de producir cualquier artefacto. Si tu herramienta no lo cargó, léelo
> por ruta directa antes de empezar.

## 1. ¿Estoy en un proyecto con el framework?

- [ ] Existe `.opencode/` con `framework/`, `skills/`, `validators/`, `agents/`.
- [ ] Existe `AGENTS.md` en la raíz con el stack de referencia.
- Si falta: NO asumir convenciones del framework — informar al usuario.

## 2. ¿La versión del framework está actualizada?

- [ ] Comparar `VERSIONS.md` (del proyecto) vs `.workflow/framework-version.txt`
      (versión instalada). Si `framework-version.txt` no existe, la instalación
      es anterior a 4.2.0.
- [ ] Si la versión instalada < `VERSIONS.md`: avisar al usuario y ofrecer
      `powershell -File .opencode/scripts/update-framework.ps1` (hace backup +
      sync + validators). **No** sincronizar sin confirmación: puede haber
      personalizaciones locales.

## 3. ¿La integridad del framework está OK?

- [ ] Ejecutar `.opencode/validators/run-all.ps1` (16 checks). Si algo falla:
      reportarlo ANTES de trabajar y no ocultar el fallo.
- [ ] Cruce rápido: las skills del catálogo (SKILLS-MANIFEST) que tu herramienta
      no lista como cargables = frontmatter YAML roto (p. ej. apóstrofe sin
      escapar). Fallback: leer el SKILL.md por ruta directa funciona igual.

## 4. ¿Dónde quedó el trabajo? (orientación)

En orden de prioridad:
1. `.workflow/state.json` → `resume_hint` + `current_step` + `steps_completed`
   (es la fuente de verdad del estado).
2. `docs/artifacts/progress.html` → dashboard visual (módulos + fases + dónde
   quedó la IA). Si no existe o está viejo: regenerar con
   `python .opencode/scripts/generate-progress.py .`.
3. `.workflow/framework-notes.md` → errores conocidos del framework/piloto
   (N1..Nn) que pueden afectar el trabajo actual.
4. `docs/governance.md` + `docs/constitution.md` → reglas del proyecto
   (excepciones, deuda, aprobadores).

## 5. ¿Qué skill activar?

- Consultar `.opencode/framework/SKILL-ROUTING.md` (routing por tipo de cambio
  y por fase N0-N49) y `SKILLS-MANIFEST.md` (enforcement).
- Si la skill es `mandatory` y no se puede ejecutar: documentar bloqueo, no
  saltarla en silencio.
- Meta-skills (`agent-*`) solo cuando el usuario las pide explícitamente.

## 6. Al cerrar una fase o bundle (protocolo, paso 7)

- [ ] Registrar el estado en `.workflow/state.json` (pasos completados/fallidos,
      checkpoint).
- [ ] Actualizar `docs/artifacts/progress-state.json` solo si hace falta
      responsable/fecha/notas (la heurística deriva el estado sola).
- [ ] Regenerar el dashboard: `python .opencode/scripts/generate-progress.py .`
- [ ] Reportar al usuario con el formato de handoff del protocolo.

## Reglas rápidas

- El autor del framework (Manuel Aliaga) NO es el owner del proyecto — el owner
  se confirma por HITL (framework-governance).
- Nunca editar `.opencode/framework/**` ni `.opencode/agents/**` sin confirmación.
- Contrato de respuestas API: éxito `{success:true, data}` · error
  `{success:false, error:{code,message,details}, meta}` — los clientes generados
  lanzan `ApiError` en `!ok` o `2xx+success:false`.
- JWT: PyJWT (python-jose está deprecado en el framework).
- SQLAlchemy async + `onupdate=func.now()`: `session.refresh()` post-flush
  (ver database-modeling).
