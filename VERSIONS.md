# VERSIONS.md — Matriz de compatibilidad de TIVIT Foundry

**Proyecto:** TIVIT Foundry — Framework Agéntico  
**Última actualización:** 17 de julio de 2026

---

## Versión del framework

| Versión | Fecha | Skills | Notas |
|---------|-------|--------|-------|
| 3.0.0 | 2026-07-21 | 103 | Migración de frontend: Angular → React (Vite), ver ADR-004 |
| 2.0.0 | 2026-07-17 | 102 | Catálogo expandido, scaffold Angular + backend dual |
| 1.0.0 | 2026-07-16 | 76 | Versión inicial consolidada |

## Stack certificado

| Capa | Tecnología | Versión mínima | Versión recomendada |
|------|-----------|----------------|---------------------|
| AI/ML Core | Python | 3.11 | 3.12 |
| Backend general | Bun | 1.1 | 1.1+ |
| Framework HTTP Python | FastAPI | 0.110 | Latest |
| Framework HTTP Bun | Elysia / Hono | Latest | Latest |
| Frontend | React | 18 | 18+ |
| Frontend build | Vite | 5 | Latest |
| Base de datos | PostgreSQL | 15 | 16 |
| Extensión vectorial | pgvector | 0.7 | Latest |
| Caché/Colas | Redis | 7.0 | 7.2 |
| Mensajería | Apache Kafka | 3.5 | 3.7 |
| Auth | Keycloak | 24 | Latest |
| IaC | Terraform | 1.7 | Latest |
| Contenedores | Docker | 24 | Latest |
| Orquestación | Kubernetes | 1.29 | Latest |
| CI/CD | GitHub Actions | N/A | Latest |
| CI/CD | GitLab CI | 16 | Latest |
| Observabilidad | Prometheus | 2.50 | Latest |
| Observabilidad | Grafana | 10.4 | Latest |
| Trazas | OpenTelemetry | 1.24 | Latest |
| LLM Observability | Langfuse | 2.0 | Latest |

## Notas de compatibilidad

- React 18+ es obligatorio para `useTransition`/`useId` y concurrent features. Next.js es la variante aceptada cuando se necesita SSR/SSG (ver skill `react`).
- PostgreSQL 15+ requerido para `pgvector` y funciones modernas.
- Bun se usa como runtime general; Python se mantiene para el core AI/ML.
