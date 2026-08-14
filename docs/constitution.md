# Constitución del Framework — TIVIT Foundry

**Versión:** 1.0
**Fecha:** 2026-08-14
**Alcance:** framework agéntico (repo fuente) y proyectos adoptantes (copiar a `docs/constitution.md` del proyecto y adaptar los valores).

> Esta constitución materializa los 9 artículos definidos por la skill `governance-constitution`.
> El **Constitution Gate** del protocolo (SKILL-EXECUTION-PROTOCOL.md) valida contra este documento.
> Los proyectos adoptantes la copian y adaptan al contexto del proyecto.

## Article 1: Core Principles

Principios **NON-NEGOTIABLE** (ver `framework-governance`):

1. **Multi-tenancy por defecto**: toda capacidad asume aislamiento por tenant salvo excepción aprobada y registrada.
2. **Trazabilidad**: cada mutación deja rastro de auditoría y cada paso agéntico es trazable.
3. **Model-agnostic**: el core no se acopla a un único LLM ni proveedor; el router es intercambiable.
4. **Portabilidad**: la lógica propia no depende de una nube o plataforma no portable.
5. **7 capas**: ninguna solución omite una de las 7 capas del framework.
6. **Contrato de respuestas**: toda API responde `{success, data, error, meta}`; los clientes generados lanzan `ApiError` en `!ok` o `2xx + success:false`.
7. **Sin secrets en código**: secretos solo por variable de entorno o vault; nunca en el repo.

**Gate Phase -1**: antes de escribir código, el diseño debe respetar TODOS los principios. Si alguno se viola, detener y rediseñar.

## Article 2: Stack & Dependencies

- **Stack certificado**: ver `VERSIONS.md` — Python 3.11+/FastAPI (AI/ML core), Bun 1.1+ (backend general), React 18+ o Angular 17+ (frontend por proyecto), PostgreSQL 15+ + pgvector, Redis 7.0+, Kafka 3.5+, Keycloak 24+, Terraform 1.7+, Kubernetes 1.29+, Prometheus 2.50+/Grafana 10.4+, OpenTelemetry 1.24+, Langfuse 2.0+.
- **Library-First Rule**: funcionalidad nueva se implementa como librería reutilizable antes de integrarse a una aplicación.
- **Dependency Addition Gate**: agregar una dependencia exige: (1) justificación documentada, (2) comparación con 2+ alternativas, (3) chequeo de compatibilidad de licencia.

## Article 3: API-First

- Toda feature con superficie REST se especifica antes de implementar: `api-first-spec` → `api-first-backend` → `api-first-frontend`.
- Contratos compartidos en `api-contracts` (Pydantic + TypeScript + OpenAPI).
- Versionado URI `/api/v{N}` y deprecación con sunset header (ver `api-versioning`).
- El feature-spec cubre features sin API nueva (UI-only o data-only).

## Article 4: Test-First (NON-NEGOTIABLE)

**NON-NEGOTIABLE**: todo código se escribe test-first.

1. Escribir el test que define el comportamiento esperado.
2. Ejecutarlo — debe FALLAR (red).
3. Escribir el código mínimo para pasarlo (green).
4. Refactorizar manteniendo tests verdes.

**Gate**: ningún código se acepta sin tests que cubran happy path, edge cases y condiciones de error, y que corran en CI **por cada stack tocado** (Test Gate del protocolo). Cobertura mínima: 70%.

## Article 5: Integration Testing

- Toda interfaz externa requiere tests de integración: operaciones de base de datos, endpoints de API, consumidores/productores de colas, file I/O y llamadas a servicios externos (mockeadas con contract tests).
- Los tests de integración corren contra dependencias reales (TestContainers), no mocks.
- Contract tests entre servicios (ver `integration-testing`).

## Article 6: Observability

- Todo servicio expone: health endpoint, métricas y logging estructurado.
- Las trazas (OpenTelemetry) propagan correlation IDs entre límites de servicio.
- Las llamadas LLM se trackean en Langfuse (trazas, costos, calidad).
- Error budgets definidos como SLOs (ver `SLOs.md` y `observabilidad`).

## Article 7: Versioning & Breaking Changes

- Versionado semántico MAJOR.MINOR.PATCH.
- Breaking changes: aviso de deprecación por UNA versión mayor antes de remover.
- Versionado de API por URI: `/api/v{N}/resource`.
- `CHANGELOG.md` actualizado en cada release.
- Versión del framework en `VERSIONS.md`: sube solo cuando cambia el catálogo o el contrato entre capas; los docs de gobierno versionan por separado (misma tabla).

## Article 8: Simplicity

- Preferir soluciones simples sobre ingeniosas.
- Si un dev junior no entiende el código tras una lectura, es demasiado complejo.
- DRY es guía, no religión: algo de duplicación es aceptable si mejora claridad.
- Guía de tamaño: máximo ~30 líneas por función; ~500 líneas por archivo.

## Article 9: Anti-Abstraction

- NO crear abstracciones para casos de uso hipotéticos futuros.
- Una implementación concreta antes que una interfaz.
- Las interfaces solo se justifican con 2+ implementaciones productivas.
- Si no estás seguro de necesitar una abstracción, no la necesitas.

## Phase -1 Gates

| Gate | Pregunta | Condición de paso |
|------|----------|-------------------|
| **Simplicity** | ¿Es la solución más simple posible? | Sin abstracciones, patrones o complejidad innecesaria |
| **Anti-Abstraction** | ¿Necesitamos cada abstracción? | Todas justificadas por casos actuales (no futuros) |
| **Integration-First** | ¿Cómo se testeará end-to-end? | Plan de tests de integración existe antes de implementar |
| **Test-First** | ¿Los tests están definidos antes del código? | Esqueleto de tests existe y falla |

## Forbidden Patterns

Los siguientes patrones NO deben aparecer jamás:

1. **God Classes**: clases con >10 métodos públicos o >500 líneas.
2. **Magic Numbers**: literales numéricos sin nombre en lógica de negocio.
3. **Silent Failures**: catch de excepciones sin loguear o re-lanzar cuando aplica.
4. **Hardcoded Secrets**: API keys, passwords o tokens en código.
5. **SELECT \* en producción**: siempre listas de columnas explícitas.
6. **N+1 Queries**: siempre eager-load o batch query.
