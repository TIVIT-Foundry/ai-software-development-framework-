# ADR-001 — Selección de Angular como framework frontend

**Estado:** Vigente en paralelo con [ADR-004](ADR-004-react.md) (ver [ADR-005](ADR-005-angular-coexistence.md), 2026-07-30)  
**Fecha:** 2026-07-17  
**Autor:** Manuel Aliaga — TIVIT Foundry

> Esta decisión fue superseded por ADR-004 (2026-07-21) cuando el framework migró de Angular a React, y luego reinstaurada como opción vigente por ADR-005 (2026-07-30), que restauró Angular para coexistir con React — el equipo del proyecto elige uno de los dos por proyecto. Las razones originales de esta decisión (documentadas abajo) siguen siendo válidas como justificación de Angular como opción; ver ADR-004 para las razones del cambio a React como default, y ADR-005 para el contexto de la coexistencia. Este documento se conserva sin modificar su contenido histórico.

## Contexto

El framework necesitaba estandarizar el frontend para los proyectos generados por agentes AI. Las opciones evaluadas fueron React, Vue y Angular.

## Decisión

Se elige **Angular** como framework frontend estándar.

## Razones

1. **Opinión integrada:** Angular incluye routing, formularios, inyección de dependencias y signals de forma nativa.
2. **TypeScript first:** Todo el código es TypeScript sin configuración adicional.
3. **Standalone components:** Reduce la complejidad de NgModules.
4. **Soporte empresarial:** Google respalda Angular con ciclos de release predecibles.
5. **Alineación TIVIT:** El stack real de proyectos internos usa Angular.

## Consecuencias

- Las skills `react` y `react-hooks` fueron eliminadas.
- Se crearon `angular` y `angular-services`.
- El scaffold genera componentes Angular, no React.

## Alternativas consideradas

- **React:** Mayor ecosistema, pero requiere más decisiones arbitrarias (router, estado, forms).
- **Vue:** Menor adopción interna en TIVIT.
