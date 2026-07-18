---
name: pgvector
description: 'Vector search and RAG with PostgreSQL pgvector: embeddings storage, similarity indexes, HNSW/IVFFlat, and hybrid search. Trigger: When implementing RAG, semantic search, or vector memory on PostgreSQL.'
version: 1.0
metadata:
  phase:
    - construction
  layer:
    - database
  enforcement: recommended
  depends_on:
    - database-modeling
    - langchain
  consumed_by:
    - memory-protocol
    - framework-data-memory-compliance
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how pgvector is used to store embeddings, build similarity search, and support RAG workflows in PostgreSQL.

## When to use this skill

Activate when:
- Implementing semantic search over documents
- Building vector memory for agents
- Need hybrid search (vector + full-text)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `database-modeling` | depends_on | Table/index design |
| `langchain` | consumer | Embedding/retrieval integration |
| `memory-protocol` | consumer | Persistent agent memory |

## Critical Rules

1. Use `vector` extension and `pgvector` Python package (`pgvector` + `sqlalchemy`).
2. Store embeddings with metadata: `id`, `content`, `embedding`, `tenant_id`, `source`, `created_at`.
3. Index with `hnsw` for high-dimensional cosine similarity (production) or `ivfflat` for balanced workloads.
4. Always filter by `tenant_id` before vector search.
5. Normalize embeddings if using inner product.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Migration | `database/migrations/NNN_add_vector_table.sql` | Extension + table |
| Repository | `src/features/{module}/vector_repo.py` | Vector CRUD/search |
| Index | Migration or SQL | HNSW/IVFFlat index |

## Example: Table and index

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_doc_embeddings_hnsw
ON document_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

## Checklist

- [ ] `vector` extension enabled
- [ ] Embeddings dimension matches model output
- [ ] Tenant isolation in queries
- [ ] HNSW/IVFFlat index created
- [ ] Hybrid search tested (vector + metadata filters)
