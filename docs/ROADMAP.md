# Roadmap — TIVIT Foundry

**Estado:** Vigente
**Última actualización:** 3 de agosto de 2026
**Cadencia de revisión:** mensual (ver "Cadencia de revisión" al final)

## Hoy (v1 — en producción)

Lo que ya está construido y operando:

| Área | Estado |
|------|--------|
| Catálogo de skills | 114 skills organizadas por dominio (framework, backend, frontend, database, testing, API/spec, seguridad, operaciones, IA/LLM, proceso, arquitectura) |
| Agentes | 4 agentes con responsabilidades y permisos separados: orchestrator (coordina), design (artefactos), control (gobernanza/QA), delivery (implementa) |
| Stack dual backend | Python 3.12/FastAPI o Bun/TypeScript, elegible por proyecto vía `--backend` |
| Stack dual frontend | React 18+ (Vite, o Next.js para SSR/SEO) o Angular 17+, elegible por proyecto vía `--frontend` |
| Validadores estructurales | 15 validadores automáticos (`run-all.ps1`) que auditan contrato de skills, secretos hardcodeados (incluye URLs), dependencias circulares, consistencia de stack, y más |
| Intake de requerimientos | Template estructurado ("Documento Cero") que convierte input funcional ambiguo o inexistente del cliente en una línea base confirmada, con historial de cambios auditable |
| Onboarding de clientes/proyectos | Checklist que determina madurez de documentación, greenfield vs. brownfield (incluye flujo de reanálisis para stacks legados), accesos y nivel de infraestructura antes de comprometer alcance |
| QA funcional automatizada | Ejecución de criterios de aceptación confirmados contra la implementación real — cubre tanto flujos web/API estándar como fixtures de dominio no estándar (audio, documentos, imágenes), con evidencia estructurada pass/fail/ambiguo por criterio |
| Gates de frontend | Escaneo determinístico pre-PR (React Doctor / Angular Doctor) para anti-patrones, accesibilidad y salud de código |
| Trazabilidad | ADRs para decisiones de arquitectura, dependencias declaradas por skill, reporte de convergencia spec-vs-código antes de cada PR |

## Próximo (v1.x — en evaluación activa)

Gaps identificados y priorizados, sin fecha comprometida todavía:

- **Soberanía digital**: opciones de modelos locales/cuantizados y tiers de infraestructura (básica/media/avanzada) según presupuesto del cliente. Hoy la gestión de costos de LLM excluye explícitamente modelos self-hosted de su alcance; el checklist de onboarding ya deja un placeholder para registrar la intención del cliente, pero el diseño técnico del tier está pendiente.
- **Integración de evidencia con trackers externos**: la capa de QA funcional automatizada produce evidencia estructurada (JSON + reporte), pero no la envía todavía a un tracker externo (Jira u otro) — queda pendiente de decisión de herramienta/licenciamiento antes de construir esa integración.

## Visión (v2 — condicionada a adopción)

- **Portabilidad multi-agente**: adaptar el framework para operar sobre múltiples agentes de codificación (no solo el actual), evitando depender de un único sistema de desarrollo. Esto es intencionalmente una visión, no un compromiso de fecha — antes de invertir en esta fase se necesita primero recopilar feedback de adopción del framework actual en varios proyectos, para no diseñar la portabilidad sobre supuestos sin validar en producción.

## Cadencia de revisión

El roadmap se revisa mensualmente junto con el avance de nuevas versiones del framework. Los ítems de "Próximo" se promueven a construcción activa cuando hay una necesidad concreta de cliente o proyecto que los justifique; los ítems de "Visión" se re-evalúan en cada revisión mensual a la luz del feedback de adopción acumulado.
