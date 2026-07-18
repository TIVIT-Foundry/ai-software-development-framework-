---
name: costos-llm
description: 'LLM cost management: token cost tracking per tenant, model tiering (cheap
  vs expensive), semantic caching with pgvector, response caching, prompt compression,
  batch vs streaming cost analysis, budget alerts, cost attribution per feature,
  Langfuse observability, LangChain/LangGraph cost callbacks. Trigger: When designing
  or optimizing LLM token costs for agentic applications.'
version: 2.0
metadata:
  phase:
  - operations
  layer:
  - infrastructure
  enforcement: optional
  depends_on:
  - observabilidad
  - framework-platform
  - framework-data-memory-compliance
  - backend-api
  consumed_by:
  - agent-backend
  - agent-fullstack
  agent_roles:
  - design-agent
  - control-agent
  validation_profile: documentation
  mcp_usage: optional
---

## Propósito

Diseñar la estrategia de gestión de costos de modelos LLM en aplicaciones agénticas Python/FastAPI con LangChain/LangGraph: atribución por tenant y feature, caching semántico con PostgreSQL + pgvector, tiering de modelos, compresión de prompts, alertas presupuestarias y observabilidad centralizada con Langfuse.

## Objetivo

1. ¿Cómo se mide y atribuye el costo de tokens por tenant y feature?
2. ¿Qué estrategias de caching semántico con pgvector reducen costos?
3. ¿Cómo se selecciona el modelo adecuado por tarea (tiering)?
4. ¿Cómo se comprimen prompts sin perder calidad?
5. ¿Cuándo conviene batch vs streaming desde el punto de vista de costo?
6. ¿Cómo se configuran alertas de presupuesto y thresholds?
7. ¿Cómo Langfuse centraliza el tracking de costos y la observabilidad LLM?
8. ¿Cómo LangChain/LangGraph callbacks automatizan el tracking por llamada?

## Relación con otras skills

- `observabilidad` proporciona traces y métricas donde se etiquetan costos por tenant y feature.
- `framework-platform` define tagging de recursos y costos por workload.
- `framework-data-memory-compliance` define qué datos personales deben excluirse de logs de tokens.
- `backend-api` implementa los endpoints que consumen LLM y necesitan tracking.

## Stack de referencia

| Capa | Tecnología |
|------|------------|
| API | Python + FastAPI |
| Orquestación LLM | LangChain / LangGraph |
| Base de datos | PostgreSQL + pgvector |
| Observabilidad LLM | Langfuse |
| Cache semántico | pgvector (similitud coseno) |
| Cost tracking | Langfuse + callbacks LangChain |

## Qué debe hacer el agente

1. Instrumentar cada llamada LLM con tags de `tenant_id`, `feature_id`, `model`, `prompt_tokens`, `completion_tokens`.
2. Registrar costo por llamada usando precio por token del modelo en uso.
3. Implementar semantic cache con PostgreSQL + pgvector (similitud coseno) para queries duplicadas o similares.
4. Definir tiering de modelos: tareas críticas → modelo grande, tareas simples → modelo pequeño.
5. Aplicar prompt compression dinámica (eliminar historial, resumir contexto).
6. Configurar alertas de presupuesto: warning al 80%, critical al 100%.
7. Integrar Langfuse para tracking centralizado de costos y observabilidad LLM.
8. Configurar callbacks de LangChain/LangGraph para tracking automático por llamada.
9. Generar reportes de costos por feature, tenant y modelo.
10. Evaluar batch vs streaming: batch más barato si latencia no es crítica.

## Alcance

Incluye: token tracking, caching semántico con pgvector, tiering de modelos, compresión de prompts, batch vs streaming, budget alerts, Langfuse observability, LangChain cost callbacks, reportes de costo.
No incluye: negociación de precios con proveedores, fine-tuning propio, modelos open-source self-hosted.

## Principios

- Cada token cuesta dinero real: medir antes de optimizar.
- El modelo más caro solo para tareas que realmente lo necesitan.
- El cache semántico con pgvector es la herramienta de mayor impacto en reducción de costos.
- La atribución por tenant permite facturar y detectar abusos.
- Las alertas deben ser por tenant y globales.
- Prompt compression debe medirse: no sacrificar calidad por costo.
- Langfuse como fuente única de verdad para costos y trazabilidad LLM.

## Technical Design

### 1. Langfuse — Tracking centralizado de costos y observabilidad

Langfuse es la herramienta central para registrar cada llamada LLM, asociar costos, tags de tenant/feature y generar dashboards de observabilidad.

```python
# langfuse_config.py — configuración de Langfuse
from langfuse import Langfuse
from langfuse.callback import CallbackHandler

# Cliente Langfuse global
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

# Callback handler para LangChain — tracking automático
langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)
```

```python
# Decorator para tracking de costos con Langfuse
from functools import wraps
from langfuse import observe

def track_llm_cost(tenant_id: str, feature_id: str):
    def decorator(func):
        @wraps(func)
        @observe(name=f"{feature_id}-llm-call")
        async def wrapper(*args, **kwargs):
            # Langfuse captura automáticamente la llamada LLM
            result = await func(*args, **kwargs)

            # Enrichir con metadata de negocio
            langfuse.trace(
                name=f"{feature_id}-cost",
                metadata={
                    "tenant_id": tenant_id,
                    "feature_id": feature_id,
                    "model": result.model,
                    "prompt_tokens": result.usage.prompt_tokens,
                    "completion_tokens": result.usage.completion_tokens,
                },
                session_id=tenant_id,
            )
            return result
        return wrapper
    return decorator
```

### 2. LangChain/LangGraph — Callback para tracking automático

LangChain provee `CallbackHandler` que Langfuse consume para registrar cada llamada LLM sin código adicional.

```python
# langchain_cost_callback.py — callback automático para LangChain
from langchain_core.callbacks import BaseCallbackHandler
from langfuse.callback import CallbackHandler as LangfuseCallbackHandler
from app.config import settings


class CostTrackingCallback(BaseCallbackHandler):
    """Callback que delega tracking a Langfuse y registra costos en DB."""

    def __init__(self, tenant_id: str, feature_id: str):
        super().__init__()
        self.tenant_id = tenant_id
        self.feature_id = feature_id
        self.langfuse_handler = LangfuseCallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )

    def on_llm_end(self, response, *, run_id, **kwargs):
        """Se ejecuta al finalizar cada llamada LLM."""
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            prompt_tokens = token_usage.get("prompt_tokens", 0)
            completion_tokens = token_usage.get("completion_tokens", 0)
            model = response.llm_output.get("model_name", "unknown")

            cost = calculate_cost(model, prompt_tokens, completion_tokens)

            # Registrar en PostgreSQL para reporting
            log_cost_to_db(
                tenant_id=self.tenant_id,
                feature_id=self.feature_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=cost,
            )

            # Alertas de presupuesto
            check_budget(self.tenant_id, self.feature_id)
```

```python
# Uso en LangChain — tracking automático por llamada
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def process_with_cost_tracking(
    tenant_id: str,
    feature_id: str,
    messages: list[HumanMessage],
):
    callbacks = [CostTrackingCallback(tenant_id, feature_id)]

    llm = ChatOpenAI(
        model="gpt-4o",
        callbacks=callbacks,  # Tracking automático
    )
    return await llm.ainvoke(messages)
```

```python
# LangGraph — tracking en nodos del grafo
from langgraph.graph import StateGraph, END
from langfuse.callback import CallbackHandler as LangfuseHandler


async def run_graph_with_tracking(
    tenant_id: str,
    feature_id: str,
    input_state: dict,
):
    # Handler por ejecución del grafo
    handler = LangfuseHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
        user_id=tenant_id,
        tags=[feature_id, tenant_id],
    )

    graph = build_agent_graph()  # Tu grafo LangGraph
    result = await graph.ainvoke(
        input_state,
        config={"callbacks": [handler]},
    )
    return result
```

### 3. Semantic cache con PostgreSQL + pgvector

Reemplaza el diccionario en memoria por persistencia real en PostgreSQL con pgvector.

```sql
-- Migración: crear tabla de cache semántico
CREATE TABLE IF NOT EXISTS llm_semantic_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    query_text TEXT NOT NULL,
    query_embedding vector(1536) NOT NULL,  -- Dimensión según modelo de embeddings
    response TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cost DECIMAL(10, 8) NOT NULL,
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_hit_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Índice para búsqueda por tenant + similitud coseno
CREATE INDEX idx_cache_embedding_tenant
    ON llm_semantic_cache
    USING ivfflat (query_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Índice para limpieza de entradas expiradas
CREATE INDEX idx_cache_expires ON llm_semantic_cache (expires_at);
```

```python
# semantic_cache_pgvector.py — cache semántico con PostgreSQL + pgvector
from pgvector.psycopg import register_vector
import psycopg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class SemanticCachePGVector:
    """Cache semántico persistente usando PostgreSQL + pgvector."""

    def __init__(
        self,
        session: AsyncSession,
        similarity_threshold: float = 0.92,
        ttl_hours: int = 24,
        embedding_fn=None,  # Callable: str -> list[float]
    ):
        self.session = session
        self.threshold = similarity_threshold
        self.ttl_hours = ttl_hours
        self.embedding_fn = embedding_fn  # Inyectar función de embeddings (cualquier modelo)

    async def get(self, query: str, tenant_id: str) -> dict | None:
        """Buscar cache semántico por similitud coseno."""
        query_embedding = await self.embedding_fn(query)

        result = await self.session.execute(
            text("""
                SELECT id, response, model, prompt_tokens, completion_tokens, cost,
                       1 - (query_embedding <=> :embedding::vector) AS similarity
                FROM llm_semantic_cache
                WHERE tenant_id = :tenant_id
                  AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY query_embedding <=> :embedding::vector
                LIMIT 1
            """),
            {
                "tenant_id": tenant_id,
                "embedding": str(query_embedding),
            },
        )
        row = result.mappings().first()

        if row and row["similarity"] >= self.threshold:
            # Actualizar hit count
            await self.session.execute(
                text("""
                    UPDATE llm_semantic_cache
                    SET hit_count = hit_count + 1, last_hit_at = NOW()
                    WHERE id = :id
                """),
                {"id": row["id"]},
            )
            await self.session.commit()

            return {
                "response": row["response"],
                "model": row["model"],
                "prompt_tokens": row["prompt_tokens"],
                "completion_tokens": row["completion_tokens"],
                "cost": row["cost"],
                "similarity": row["similarity"],
            }
        return None

    async def set(
        self,
        query: str,
        response: str,
        tenant_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ):
        """Almacenar en cache semántico."""
        query_embedding = await self.embedding_fn(query)

        await self.session.execute(
            text("""
                INSERT INTO llm_semantic_cache
                    (tenant_id, query_text, query_embedding, response, model,
                     prompt_tokens, completion_tokens, cost, expires_at)
                VALUES
                    (:tenant_id, :query_text, :embedding::vector, :response, :model,
                     :prompt_tokens, :completion_tokens, :cost,
                     NOW() + INTERVAL ':ttl_hours hours')
            """),
            {
                "tenant_id": tenant_id,
                "query_text": query,
                "embedding": str(query_embedding),
                "response": response,
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost": cost,
                "ttl_hours": self.ttl_hours,
            },
        )
        await self.session.commit()

    async def cleanup_expired(self):
        """Eliminar entradas expiradas del cache."""
        await self.session.execute(
            text("DELETE FROM llm_semantic_cache WHERE expires_at < NOW()")
        )
        await self.session.commit()
```

```python
# embeddings_provider.py — función de embeddings model-agnostic
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import Protocol


class EmbeddingProvider(Protocol):
    async def embed_query(self, text: str) -> list[float]: ...


def get_embedding_provider(provider: str = "openai") -> EmbeddingProvider:
    """Factory para provider de embeddings — funciona con cualquier modelo."""
    if provider == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif provider == "huggingface":
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    else:
        raise ValueError(f"Provider no soportado: {provider}")


# Función inyectable para el cache
async def embed_query(text: str) -> list[float]:
    provider = get_embedding_provider(settings.EMBEDDING_PROVIDER)
    return await provider.aembed_query(text)
```

### 4. Token tracking — middleware pattern (Python/FastAPI)

```python
# cost_tracking_middleware.py — middleware FastAPI para tracking de costos
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time


class LLMCostTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware que registra el costo de llamadas LLM por request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Si el request incluyó llamadas LLM, registrar métricas
        if hasattr(request.state, "llm_costs"):
            total_cost = sum(c["cost"] for c in request.state.llm_costs)
            total_tokens = sum(
                c["prompt_tokens"] + c["completion_tokens"]
                for c in request.state.llm_costs
            )

            # Enrichir span de Langfuse
            if hasattr(request.state, "langfuse_trace"):
                request.state.langfuse_trace.update(
                    metadata={
                        "total_llm_cost": total_cost,
                        "total_tokens": total_tokens,
                        "llm_calls": len(request.state.llm_costs),
                        "duration_seconds": duration,
                    }
                )

        return response
```

```python
# cost_decorator.py — decorator reutilizable para tracking de costos
from functools import wraps
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Precios por modelo (input/output por 1M tokens) — actualizar según proveedor
MODEL_PRICES = {
    "gpt-4o": {"input": Decimal("2.50"), "output": Decimal("10.00")},
    "gpt-4o-mini": {"input": Decimal("0.15"), "output": Decimal("0.60")},
    "claude-sonnet-4-20250514": {"input": Decimal("3.00"), "output": Decimal("15.00")},
    "claude-haiku": {"input": Decimal("0.25"), "output": Decimal("1.25")},
}


def track_llm_cost(tenant_id: str, feature_id: str):
    """Decorator para tracking de costos con logging a Langfuse + PostgreSQL."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Extraer usage del resultado
            usage = getattr(result, "usage", None)
            model = getattr(result, "model", "unknown")

            if usage:
                prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
                completion_tokens = getattr(usage, "completion_tokens", 0) or 0

                # Calcular costo
                prices = MODEL_PRICES.get(model, {"input": Decimal("0"), "output": Decimal("0")})
                cost = (prompt_tokens * prices["input"] + completion_tokens * prices["output"]) / 1_000_000

                # Registrar en DB
                await log_cost_to_db(
                    tenant_id=tenant_id,
                    feature_id=feature_id,
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost=float(cost),
                )

                # Log para Langfuse (el callback handler ya lo captura)
                logger.info(
                    f"LLM cost: tenant={tenant_id} feature={feature_id} "
                    f"model={model} tokens={prompt_tokens + completion_tokens} "
                    f"cost=${cost:.6f}"
                )

            return result
        return wrapper
    return decorator
```

### 5. Model tiering matrix

| Tier | Models | Use Case | Cost Multiplier |
|------|--------|----------|----------------|
| Premium | Claude Sonnet 4, GPT-4o | Complex reasoning, code gen, analysis | 1x (baseline) |
| Standard | Claude Haiku, GPT-4o-mini | Classification, extraction, summarization | 0.1x - 0.2x |
| Economy | Claude Instant, GPT-3.5-turbo | Simple routing, keyword extraction | 0.02x - 0.05x |
| Free | pgvector embeddings (cualquier modelo) | Semantic cache keys, vector search | ~0.001x |

### 6. Prompt compression

```python
# prompt_compression.py — compresión dinámica de prompts
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


def compress_prompt(messages: list, max_tokens: int = 4000) -> list:
    """
    Estrategia: mantener system prompt, comprimir historial conversacional.
    """
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    history = [m for m in messages if not isinstance(m, SystemMessage)]

    estimated_tokens = estimate_tokens(messages)

    if estimated_tokens > max_tokens and len(history) > 4:
        # Resumir historial antiguo, conservar últimos 2 intercambios
        old_history = history[:-4]
        recent_history = history[-4:]

        summary = generate_summary(old_history)  # LLM call para resumir
        compressed = [
            *system_msgs,
            SystemMessage(content=f"Resumen de conversación previa: {summary}"),
            *recent_history,
        ]
        return compressed

    return messages


def estimate_tokens(messages: list) -> int:
    """Estimación rough de tokens: ~4 caracteres por token."""
    total_chars = sum(len(m.content) for m in messages if hasattr(m, "content"))
    return total_chars // 4
```

### 7. Budget alerts

```python
# budget_alerts.py — alertas de presupuesto por tenant y globales
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

BUDGET_THRESHOLDS = {
    "warning": Decimal("0.80"),   # 80% del presupuesto
    "critical": Decimal("1.00"),  # 100% del presupuesto
}


async def check_budget(
    session: AsyncSession,
    tenant_id: str,
    feature_id: str | None = None,
):
    """Verificar umbrales de presupuesto y disparar alertas."""
    # Obtener uso mensual
    query = text("""
        SELECT COALESCE(SUM(cost), 0) AS monthly_cost
        FROM llm_costs
        WHERE tenant_id = :tenant_id
          AND timestamp >= date_trunc('month', CURRENT_DATE)
          AND (:feature_id IS NULL OR feature_id = :feature_id)
    """)
    result = await session.execute(query, {
        "tenant_id": tenant_id,
        "feature_id": feature_id,
    })
    monthly_cost = Decimal(str(result.scalar()))

    # Obtener presupuesto
    budget = await get_tenant_budget(session, tenant_id, feature_id)

    if budget is None:
        return

    usage_ratio = monthly_cost / budget if budget > 0 else Decimal("0")

    if usage_ratio >= BUDGET_THRESHOLDS["critical"]:
        logger.critical(
            f"BUDGET EXCEEDED: tenant={tenant_id} feature={feature_id} "
            f"usage=${monthly_cost} budget=${budget}"
        )
        # Throttle o bloquear feature
        await throttle_feature(session, tenant_id, feature_id)

    elif usage_ratio >= BUDGET_THRESHOLDS["warning"]:
        logger.warning(
            f"BUDGET WARNING: tenant={tenant_id} feature={feature_id} "
            f"usage=${monthly_cost} ({usage_ratio:.0%} of ${budget})"
        )
```

### 8. Cost DB schema y reporting

```sql
-- Tabla de costos LLM
CREATE TABLE IF NOT EXISTS llm_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    feature_id VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cost DECIMAL(10, 8) NOT NULL,
    cached BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_llm_costs_tenant_time ON llm_costs (tenant_id, timestamp DESC);
CREATE INDEX idx_llm_costs_feature ON llm_costs (feature_id, timestamp DESC);

-- Vista de costos mensuales por tenant y feature
CREATE OR REPLACE VIEW v_monthly_llm_costs AS
SELECT
    tenant_id,
    feature_id,
    model,
    SUM(cost) AS total_cost,
    SUM(prompt_tokens) AS total_prompt_tokens,
    SUM(completion_tokens) AS total_completion_tokens,
    COUNT(*) AS total_calls,
    SUM(CASE WHEN cached THEN 1 ELSE 0 END) AS cache_hits,
    date_trunc('month', timestamp) AS month
FROM llm_costs
GROUP BY tenant_id, feature_id, model, date_trunc('month', timestamp);
```

```sql
-- Dashboard: costos por tenant, feature y modelo
SELECT
    tenant_id,
    feature_id,
    model,
    SUM(cost) AS total_cost,
    SUM(prompt_tokens + completion_tokens) AS total_tokens,
    COUNT(*) AS calls,
    ROUND(SUM(cost) / COUNT(*), 6) AS avg_cost_per_call
FROM llm_costs
WHERE timestamp >= date_trunc('month', CURRENT_DATE)
GROUP BY tenant_id, feature_id, model
ORDER BY total_cost DESC;
```

### 9. Langfuse — Dashboard de observabilidad LLM

Langfuse provee dashboards automáticos para:
- Costo por trace, sesión, usuario y tag
- Latencia de llamadas LLM
- Uso de tokens por modelo
- Comparativa de modelos
- Análisis de calidad de respuestas

Configuración de traces con metadata de negocio:

```python
# langfuse_traces.py — enriquecer traces con metadata de negocio
from langfuse import observe


@observe(name="agent-processing")
async def process_agent_request(
    tenant_id: str,
    feature_id: str,
    user_message: str,
):
    # Langfuse captura la llamada LLM automáticamente
    # Agregar metadata para filtrado en dashboard
    from langfuse import langfuse

    langfuse.trace(
        name="agent-request",
        user_id=tenant_id,
        tags=[feature_id, tenant_id],
        metadata={
            "tenant_id": tenant_id,
            "feature_id": feature_id,
            "input_length": len(user_message),
        },
        session_id=f"{tenant_id}-session",
    )

    # Tu lógica de agente con LangChain/LangGraph
    result = await run_agent(user_message)
    return result
```

## Preguntas guía

- ¿Cada llamada LLM tiene tags de tenant y feature en Langfuse?
- ¿El modelo más barato que cumple la tarea está siendo usado?
- ¿Hay cache semántico con pgvector implementado y persistente?
- ¿Los prompts tienen contexto innecesario que se puede comprimir?
- ¿Hay alertas de presupuesto por tenant y globales?
- ¿Langfuse está configurado como fuente única de verdad para costos?
- ¿Los callbacks de LangChain están registrando cada llamada automáticamente?
- ¿El costo por petición es conocido y visible en Langfuse?

## Salidas esperadas

- Middleware de tracking de tokens con atribución a tenant y feature.
- Configuración de Langfuse para observabilidad LLM centralizada.
- Callbacks de LangChain/LangGraph para tracking automático de costos.
- Semantic cache con PostgreSQL + pgvector (persistente, model-agnostic).
- Tiering matrix con modelos asignados por tipo de tarea.
- Estrategia de prompt compression (system prompt fijo + historial resumido).
- Alertas de presupuesto (80% warning, 100% critical).
- Reporte mensual de costos por tenant, feature y modelo.

## Criterios de calidad

- 100% de llamadas LLM registradas en Langfuse con costo y atribución.
- Cache semántico con pgvector reduce >=20% llamadas a modelos grandes.
- Tiering definido: <=30% de llamadas van al tier Premium.
- Alertas configuradas y probadas.
- Costo por petición visible en dashboard de Langfuse.
- Callbacks de LangChain capturan 100% de llamadas sin código adicional.

## Comportamiento esperado del agente

Cuando se detecte una llamada LLM sin tracking, el agente debe instrumentarla con tenant_id y feature_id usando callbacks de LangChain o decorator.
Cuando el mismo prompt se repita sin cache, debe implementar semantic cache con pgvector.
Cuando una tarea simple use un modelo caro (Sonnet para clasificación trivial), debe proponer downgrade a Haiku/Mini.
Cuando no haya alertas de presupuesto, debe configurarlas con umbrales por tenant.
Cuando Langfuse no esté configurado, debe proponer su integración como herramienta de observabilidad.

## Plantilla de respuesta

```
1. Langfuse setup (credenciales, trace enrichment, dashboard config).
2. LangChain cost callbacks (CostTrackingCallback + handler Langfuse).
3. Token tracking instrumentation (middleware/decorator).
4. Semantic cache con PostgreSQL + pgvector (tabla, índices, TTL).
5. Model tiering matrix (Premium / Standard / Economy).
6. Prompt compression strategy.
7. Budget alert rules (per tenant and global).
8. Cost dashboard query (by tenant, feature, model).
```

## Ejemplos

### Ejemplo 1 — Semantic cache savings con pgvector

```
Before cache: 10k requests/day x 1500 tokens x premium model = $45/day
After cache (35% hit rate): 6.5k LLM calls + 3.5k cache hits = $29.25/day
Savings: 35% ($15.75/day, ~$472/month)
Cache storage: ~50MB PostgreSQL (10k entries x 1536 dims)
```

### Ejemplo 2 — Model tiering savings

```
Feature: Ticket classification (simple intent detection)
Before: GPT-4o -> $0.015/request
After: GPT-4o-mini -> $0.002/request
Savings: 87% on that feature
```

### Ejemplo 3 — Langfuse observability

```
Dashboard Langfuse muestra:
- 12,450 llamadas LLM este mes
- Costo total: $892.50
- Top feature por costo: document-generation ($345.20)
- Cache hit rate: 32%
- Latencia promedio: 1.2s (P99: 4.8s)
```

## Checklist

- [ ] Langfuse configurado con credenciales y trace enrichment.
- [ ] LangChain callbacks registrando 100% de llamadas LLM.
- [ ] Token tracking en todas las llamadas LLM (tenant, feature, modelo).
- [ ] Semantic cache con pgvector (tabla, índices IVFFlat, TTL).
- [ ] Embeddings provider inyectable (model-agnostic, no solo OpenAI).
- [ ] Tiering matrix documentada y aplicada por feature.
- [ ] Prompt compression implementada para historial largo.
- [ ] Alertas de budget configuradas (80% warning, 100% critical).
- [ ] Reporte mensual de costos por tenant y feature.
- [ ] Costo por petición visible en dashboard de Langfuse.
- [ ] Estrategia batch vs streaming definida por caso de uso.
