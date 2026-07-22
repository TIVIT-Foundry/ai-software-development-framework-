# ADR-001 — Selección de Angular como framework frontend

**Estado:** Superseded por [ADR-004](ADR-004-react.md) (2026-07-21)  
**Fecha:** 2026-07-17  
**Autor:** Manuel Aliaga — TIVIT Foundry

> Esta decisión ya no está vigente. El framework migró de Angular a React — ver ADR-004 para el contexto y las razones del cambio. Este documento se conserva como registro histórico y no debe usarse como referencia para nuevos proyectos.

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
