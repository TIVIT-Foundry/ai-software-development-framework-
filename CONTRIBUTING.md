# CONTRIBUTING.md — Contribuir al Framework TIVIT Foundry

**Proyecto:** TIVIT Foundry — Laboratorio Interno de IA  
**Organización:** TIVIT (Latin America Technology)  
**Autor:** Manuel Aliaga — Ingeniero de IA, TIVIT Foundry

---

## Cómo proponer una nueva skill

1. Abre un issue o discute en el canal interno de TIVIT Foundry.
2. Verifica que no existe otra skill que cubra el patrón.
3. Sigue la plantilla de `skill-creator`.
4. Cumple las reglas de frontmatter (nombre, descripción con "Trigger:", `phase`, `layer`, `enforcement`, `depends_on`, `consumed_by`).
5. Mantén `SKILL.md` bajo 200 líneas de contenido instructivo.
6. Coloca templates largos en `assets/`.
7. Actualiza `SKILLS-MANIFEST.md`, `SKILL-ROUTING.md` y los agentes afectados.
8. Ejecuta `.opencode\validators\run-all.ps1` antes de solicitar revisión.

## Cómo proponer un cambio a una skill existente

1. Identifica el impacto: ¿cambia artefactos de salida, dependencias o agentes?
2. Actualiza el `version` del frontmatter si el contrato cambia.
3. Sincroniza `depends_on`/`consumed_by` en skills relacionadas.
4. Actualiza `SKILLS-MANIFEST.md` si cambia fase, capa o enforcement.

## Cómo proponer un nuevo agente

1. Usa `.opencode/agents/AGENT-TEMPLATE.agent.md` como base.
2. Define claramente owner skills, consulta skills y stack skills.
3. Actualiza `AGENT-MODEL.md` y `opencode.json` si aplica.
4. No cree agentes sin aprobación de TIVIT Foundry.

## Convenciones de commit

- Usa mensajes descriptivos en español o inglés según el repo.
- Incluye el nombre de la skill afectada: `feat(skill): descripción`.
- No commitees secrets, `.tfstate`, ni entornos virtuales.

## Validación obligatoria

```powershell
.opencode\validators\run-all.ps1
```

Todo cambio debe dejar los 15 validadores en verde.

## Propiedad intelectual

Toda contribución es propiedad de TIVIT. No compartas fuera de la organización.
