# ADR-002 — Backend dual: Python/FastAPI para AI/ML y Bun/TypeScript para servicios generales

**Estado:** Aceptado  
**Fecha:** 2026-07-17  
**Autor:** Manuel Aliaga — TIVIT Foundry

## Contexto

El framework necesitaba definir el runtime backend. Se evaluó usar un único stack vs. mantener dos runtimes especializados.

## Decisión

Se adopta un **backend dual**:

- **Python/FastAPI** para el core AI/ML, orquestación de LLMs, RAG y data science.
- **Bun/TypeScript** para servicios backend generales, BFFs y microservicios no-ML.

## Razones

1. **Python es estándar en AI/ML:** LangChain, embeddings, modelos y pgvector se integran naturalmente.
2. **Bun ofrece velocidad y DX:** Ideal para APIs de alto rendimiento con TypeScript.
3. **Flexibilidad por vertical:** Algunos packs usarán FastAPI; otros Bun.
4. **Contratos compartidos:** Ambos implementan el mismo OpenAPI spec.

## Consecuencias

- Se creó la skill `bun-backend`.
- El scaffold soporta `--backend python` y `--backend bun`.
- `api-contracts` asegura tipos alineados en ambos lados.

## Alternativas consideradas

- **Solo Python:** Simplifica, pero pierde rendimiento y DX en servicios generales.
- **Solo Bun:** Dificulta integración con librerías de ML maduras.
