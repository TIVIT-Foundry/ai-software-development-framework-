# SLOs del Framework TIVIT Foundry

**Proyecto:** TIVIT Foundry — Framework Agéntico  
**Área:** Laboratorio Interno de IA

---

## Objetivo

Definir SLOs/SLIs para el framework como producto interno: calidad del catálogo, tiempos de ejecución y fiabilidad del scaffold.

## SLIs

| Indicador | Métrica | Objetivo |
|-----------|---------|----------|
| Validadores | Porcentaje de ejecuciones con 13/13 OK | ≥ 99% |
| Scaffold | Porcentaje de specs que generan código compilable | ≥ 95% |
| Skills | Porcentaje de skills con frontmatter válido | 100% |
| Referencias rotas | Número de links rotos en `.opencode/` | 0 |
| Tiempo de generación | Tiempo medio de scaffold por módulo | ≤ 30s |

## SLOs

| SLO | Ventana | Objetivo |
|-----|---------|----------|
| Disponibilidad de validadores | Mensual | ≥ 99% |
| Calidad del catálogo | Por release | 0 skills huérfanas |
| Alineación de stack | Por release | 0 referencias a stacks obsoletos en output por defecto |

## Compromisos

- Cada release del framework debe pasar `run-all.ps1`.
- Cada nueva skill debe incluir frontmatter completo y ejemplos de stack certificado.
- El scaffold se prueba con al menos un módulo de ejemplo antes de mergear.
