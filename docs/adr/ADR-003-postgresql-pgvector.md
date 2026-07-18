# ADR-003 — PostgreSQL + pgvector como base de datos principal

**Estado:** Aceptado  
**Fecha:** 2026-07-17  
**Autor:** Manuel Aliaga — TIVIT Foundry

## Contexto

Se necesitaba unificar el almacenamiento transaccional y vectorial para evitar operar múltiples bases de datos.

## Decisión

Usar **PostgreSQL con la extensión pgvector** como base de datos principal.

## Razones

1. **Unificación:** Datos transaccionales y embeddings en un solo motor.
2. **Consistencia operativa:** Backup, monitoreo y seguridad unificados.
3. **Rendimiento:** Índices HNSW e IVFFlat para búsqueda vectorial.
4. **Madurez:** pgvector es la extensión vectorial más adoptada en PostgreSQL.

## Consecuencias

- Se creó la skill `pgvector`.
- No se usa MongoDB, DynamoDB ni otras NoSQL como base principal.
- Las skills de base de datos eliminaron contenido NoSQL.

## Alternativas consideradas

- **MongoDB + Atlas Vector Search:** Requiere segundo motor y más operación.
- **Pinecone/Weaviate:** SaaS externo, difícil de justificar para datos internos.
