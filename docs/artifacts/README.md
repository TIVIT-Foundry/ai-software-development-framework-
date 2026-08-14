# docs/artifacts/ — Artefactos de las skills framework-*

Convención de salida de las skills `framework-*` del flujo N0-N49. El orchestrator verifica la existencia del artefacto de entrada como prerequisito de la siguiente skill (Artifact Gate del protocolo).

## Mapa skill → artefacto

| Skill | Artefacto |
|-------|-----------|
| framework-governance | `docs/governance.md` + `docs/constitution.md` (raíz de docs, no en artifacts/) |
| framework-discovery | `docs/artifacts/discovery.md` |
| framework-conception | `docs/artifacts/conception.md` |
| framework-architecture | `docs/artifacts/architecture.md` (+ ADRs en `docs/adr/`) |
| framework-core-design | `docs/artifacts/core.md` |
| framework-pack-design | `docs/artifacts/pack.md` |
| framework-security | `docs/artifacts/security.md` |
| framework-data-memory-compliance | `docs/artifacts/data-memory.md` |
| framework-platform | `docs/artifacts/platform.md` |
| framework-scaffold-implementation | (repositorio scaffold — ver skill) |
| framework-qa-validation | `docs/artifacts/qa.md` (gate go/no-go) |
| framework-operations-evolution | `docs/artifacts/operations.md` |

## Reglas

- Cada skill produce UN documento autónomo en esta carpeta (o la ruta indicada en la tabla).
- Los artefactos son la fuente para el handoff entre fases: la skill siguiente los consume sin reinterpretar el dominio.
- `progress.html` (dashboard) y `progress-state.json` también viven aquí (generados por `generate-progress.py`).
- Formato libre, pero cada artefacto debe incluir: decisiones tomadas (con alternativas evaluadas), decisiones abiertas con responsable, y traza de ida y vuelta hasta la regla de governance que origina la decisión.
