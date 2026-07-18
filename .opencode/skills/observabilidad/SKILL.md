---
name: observabilidad
description: 'Observability: three pillars (logs, metrics, traces), OpenTelemetry,
  structured logging, dashboard design, alerting rules, SLO/SLI, distributed tracing,
  log aggregation (Prometheus/Grafana/Loki), LLM observability with Langfuse.
  Trigger: When designing or implementing observability, monitoring, alerting,
  distributed tracing, or LLM cost/quality tracking.'
version: 1.0
metadata:
  phase:
  - operations
  layer:
  - infrastructure
  enforcement: recommended
  depends_on: []
  consumed_by:
  - agent-backend
  - agent-fullstack
  - agent-qa
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: documentation
  mcp_usage: optional
---

## Propósito

Diseñar la estrategia de observabilidad del sistema basada en los tres pilares (logs, métricas, traces), instrumentación con OpenTelemetry, dashboards accionables y alertas con umbrales definidos.

## Objetivo

1. ¿Qué señales (logs, métricas, traces) necesita el sistema?
2. ¿Cómo se instrumenta cada capa (API, backend, DB, frontend) con OpenTelemetry?
3. ¿Cómo se diseña logging estructurado con correlación de trazas?
4. ¿Qué dashboards y alertas son necesarias por rol?
5. ¿Cómo se definen SLOs y SLIs para cada servicio?
6. ¿Cómo se agregan y retienen logs según criticidad?

## Relación con otras skills

- `backend-api` expone endpoints que deben estar instrumentados.
- `error-handling` genera logs estructurados que esta skill consume para alertas.
- `ci-cd` despliega la infraestructura de observabilidad (Grafana, Loki, Prometheus).
- `framework-platform` define la topología que esta skill instrumenta.
- `costos-llm` se beneficia de la correlación de traces para atribución de costos.

## Qué debe hacer el agente

1. Instrumentar cada servicio con OpenTelemetry (SDK Python, FastAPI auto-instrumentation).
2. Instrumentar LangChain/LangGraph con `LangChainInstrumentor` para traces por nodo/llamada.
3. Configurar Langfuse para observabilidad LLM: traces, costos, calidad y scores.
4. Escribir logs estructurados en JSON con `trace_id`, `span_id`, `service`, `level`.
5. Exportar métricas RED (Rate, Errors, Duration) por endpoint.
6. Diseñar dashboards por rol (operador, desarrollador, negocio, LLM).
7. Definir SLOs (ej: 99.9% de requests en menos de 500ms) y SLIs medibles.
8. Configurar alertas con severidad (warning, critical) y destinatarios.
9. Agregar tags de correlación: `tenant_id`, `feature_id`, `user_id`.
10. Definir política de retención por tipo de señal y entorno.
11. Integrar Langfuse con LangChain callback handler para captura automática de costos.

## Alcance

Incluye: instrumentación OpenTelemetry, logs estructurados, métricas RED, dashboards Grafana, alertas Prometheus, SLO/SLI, tracing distribuido, Langfuse para LLM observability, LangChain/LangGraph instrumentation.
No incluye: profiling de CPU/memoria avanzado, APM comercial (Datadog/Dynatrace), compliance SOC2.

## Principios

- Los tres pilares se complementan: logs para eventos, métricas para tendencias, traces para caminos.
- Toda señal debe tener `service`, `environment` y `trace_id` como tags mínimos.
- Las alertas deben tener acción asociada, no solo notificación.
- Los dashboards cuentan una historia: no son tableros de métricas crudas.
- Un SLO sin SLI medible no es operativo.
- La instrumentación no debe afectar latencia de producción (sampling adaptativo).

## Technical Design

### OpenTelemetry — Python/FastAPI

```python
# __init__.py or main.py — OTel setup
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

resource = Resource.create({
    "service.name": "my-api",
    "service.version": "1.0.0",
    "deployment.environment": "production",
})

trace_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPExporter(endpoint="http://otel-collector:4317")
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Auto-instrument outbound HTTP
HTTPXClientInstrumentor().instrument()

# Auto-instrument SQLAlchemy queries
SQLAlchemyInstrumentor().instrument(engine=engine)
```

**Puertos OTel Collector:**
| Protocolo | Puerto | Uso |
|-----------|--------|-----|
| OTLP gRPC | 4317 | Exportación principal de traces y métricas |
| OTLP HTTP | 4318 | Alternativa HTTP |
| Prometheus | 8889 | Métricas para scraping por Prometheus |

### Structured logging — Python structlog

```python
# Structured logging con correlación OTel
import structlog
from opentelemetry import trace

def add_trace_context(logger, method_name, event_dict):
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        add_trace_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger(service="my-api", version="1.0.0")

# Uso
log.info("order_created", order_id="ord-42", tenant_id="tenant-1", amount=99.9)
log.error("payment_timeout", order_id="ord-42", error_type="TimeoutException")
```

### RED metrics per endpoint

```prometheus
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{service="my-api",method="GET",path="/users",status="200"}

# HELP http_request_duration_seconds Request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{service="my-api",le="0.1"} 1200

# HELP http_requests_in_flight Concurrent requests
# TYPE http_requests_in_flight gauge
http_requests_in_flight{service="my-api"} 5
```

### SLO / SLI definition

| SLI | Definition | SLO Target | Measurement Window |
|-----|-----------|------------|--------------------|
| Availability | (successful requests / total requests) × 100 | ≥ 99.9% | Rolling 30 days |
| Latency (p95) | 95th percentile of request duration | ≤ 500ms | Rolling 7 days |
| Error rate | (5xx responses / total) × 100 | ≤ 0.1% | Rolling 1 hour |
| Freshness | Time since last successful data sync | ≤ 5 min | Per data source |

### Alerting rules (Prometheus)

```yaml
groups:
  - name: my-api
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
          service: my-api
        annotations:
          summary: Error rate > 1% for 5 minutes

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: p95 latency > 500ms for 10 minutes
```

### Trace correlation

```json
{
  "timestamp": "2026-05-27T10:00:00Z",
  "level": "error",
  "service": "order-api",
  "trace_id": "abc123def456",
  "span_id": "span789",
  "tenant_id": "tenant-42",
  "user_id": "user-7",
  "message": "Payment timeout",
  "error": {
    "type": "TimeoutException",
    "stack": "..."
  }
}
```

### Langfuse — LLM Observability

Langfuse captura traces, costos, calidad y latencia de llamadas LLM de forma nativa, integrándose con LangChain/LangGraph.

```python
# Langfuse SDK para Python — configuración
from langfuse import Langfuse
from langfuse.callback import CallbackHandler

# Cliente singleton (reusar en toda la app)
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com",  # o self-hosted
)

# Handler para LangChain callbacks
langfuse_handler = CallbackHandler(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com",
)
```

**Traces con Langfuse:**

```python
# Trace manual con spans e scores
from langfuse import Langfuse

langfuse = Langfuse()

trace = langfuse.trace(
    name="order-resolution",
    user_id="user-7",
    metadata={"tenant_id": "tenant-42"},
    tags=["production", "order-flow"],
)

# Span para una llamada LLM
span = trace.span(
    name="llm-call",
    input={"prompt": "Resolve order dispute"},
    model="gpt-4o",
)

# Score de calidad (asíncrono)
langfuse.score(
    trace_id=trace.id,
    name="user-satisfaction",
    value=0.9,
    comment="Dispute resolved correctly",
)

langfuse.flush()
```

**Costos y métricas LLM:**

```yaml
# Métricas que Langfuse captura automáticamente
# (no requiere código adicional con LangChain callback)
llm_metrics:
  cost:
    - model: gpt-4o
      input_per_1k_tokens: 0.0025
      output_per_1k_tokens: 0.01
    - model: gpt-4o-mini
      input_per_1k_tokens: 0.00015
      output_per_1k_tokens: 0.0006
  latency:
    - p50: 800ms
    - p95: 2500ms
    - p99: 5000ms
  quality:
    - hallucination_rate: 0.02
    - rejection_rate: 0.01
    - user_feedback_avg: 0.85
```

**Dashboards Langfuse:**
| Dashboard | Métrica clave | Alerta sugerida |
|-----------|--------------|-----------------|
| Cost per tenant | Costo acumulado por tenant | > $500/día |
| Model latency | p95 por modelo | > 5s |
| Token usage | Tokens in/out por modelo | Spike > 3x baseline |
| Quality scores | Score promedio por traza | < 0.7 |

### LangChain / LangGraph — Instrumentación OTel

```python
# LangChain con OpenTelemetry tracing
from opentelemetry.instrumentation.langchain import LangChainInstrumentor
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

# Instrumentar LangChain/Graph con OTel
instrumentor = LangChainInstrumentor()
instrumentor.instrument()

# Ahora todas las llamadas LLM generan spans OTel
llm = ChatOpenAI(model="gpt-4o")
result = llm.invoke("Hello world")
# → span automático: model="gpt-4o", input_tokens, output_tokens, latency
```

```python
# LangGraph con trazas por nodo
from langgraph.graph import StateGraph, END

def research_node(state):
    # Cada nodo crea un span OTel automáticamente
    return {"docs": retrieved_docs}

def answer_node(state):
    return {"answer": llm.invoke(state["query"])}

graph = StateGraph(State)
graph.add_node("research", research_node)
graph.add_node("answer", answer_node)
# LangChainInstrumentor captura cada nodo como span separado
```

**Dual export — OTel + Langfuse:**

```python
# Usar ambos: OTel para infraestructura, Langfuse para LLM
from opentelemetry.instrumentation.langchain import LangChainInstrumentor
from langfuse.callback import CallbackHandler

# OTel → Jaeger/Tempo para traces de infra
LangChainInstrumentor().instrument()

# Langfuse → dashboards de costos y calidad LLM
langfuse_handler = CallbackHandler(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
)

# Al invocar LangChain, ambas capturan el trace
result = llm.invoke(
    "Hello",
    config={"callbacks": [langfuse_handler]},  # Langfuse
    # OTel se captura automáticamente por el instrumentor
)
```

## Preguntas guía

- ¿Cada servicio tiene `trace_id` en todos sus logs?
- ¿Las métricas RED están expuestas por endpoint y método?
- ¿Cada alerta tiene un runbook asociado?
- ¿Los dashboards responden preguntas concretas de cada rol?
- ¿Los SLOs están definidos en términos medibles?
- ¿Hay política de retención por entorno?
- ¿Langfuse está configurado para capturar traces de LLM?
- ¿Los costos LLM son visibles por tenant y modelo?
- ¿LangChain/LangGraph tiene instrumentación OTel activa?
- ¿Los scores de calidad LLM se registran en Langfuse?

## Salidas esperadas

- Instrumentación OpenTelemetry configurada por servicio Python/FastAPI.
- LangChain/LangGraph instrumentado con traces por nodo.
- Langfuse configurado con traces, costos y scores LLM.
- Logs estructurados en JSON con tags de correlación.
- Métricas RED expuestas (Rate, Errors, Duration).
- Dashboards de Grafana por rol + dashboard Langfuse para LLM.
- Reglas de alerta con severidad y runbook.
- Tabla de SLO/SLI por servicio.

## Criterios de calidad

- 100% de servicios instrumentados con OTel.
- LangChain/LangGraph instrumentado con traces por nodo y llamada LLM.
- Langfuse activo con traces, costos y scores de calidad.
- Logs en JSON con `trace_id`, `service`, `level` obligatorios.
- Cada endpoint expone métricas RED.
- Alertas con severidad, umbral y destinatario definidos.
- SLOs documentados y dashboard principal visible.
- Trazas distribuidas correlacionan request completo.
- Costos LLM visibles por tenant y modelo.

## Comportamiento esperado del agente

Cuando un servicio no tenga instrumentación OTel, el agente debe agregarla antes de considerar el servicio operable.
Cuando los logs sean texto plano sin `trace_id`, debe reemplazarlos por logging estructurado.
Cuando no existan dashboards, debe proponer un mínimo por rol (incluido dashboard LLM en Langfuse).
Cuando no haya alertas definidas, debe crear al menos error rate + latency.
Cuando haya flujos LLM sin Langfuse, debe configurar el callback handler y traces.

## Plantilla de respuesta

```
1. Instrumentation setup (OTel Python/FastAPI per service).
2. LangChain/LangGraph OTel instrumentation (per node/LLM call).
3. Langfuse setup (traces, scores, cost tracking per tenant).
4. Log format (JSON schema with required fields + trace correlation).
5. RED metrics per endpoint.
6. Dashboards per role (operator, dev, business, LLM via Langfuse).
7. Alert rules (severity, threshold, runbook).
8. SLO/SLI table per service.
9. Retention policy per environment.
```

## Ejemplos

### Ejemplo 1 — Correlación

```
Request: POST /orders
Trace: abc123
  → API Gateway (span: gw-1)
    → Order Service (span: order-1)
      → Payment Service (span: pay-1)
      → DB Query (span: db-1)
  All logs with trace_id=abc123 are correlated in Grafana/Loki.
```

### Ejemplo 2 — SLO Burn Rate Alert

```yaml
- alert: SLOBurnRate
  expr: (1 - (successful / total)) > (1 - 0.999) * 14.4  # 99.9% SLO, 1h window
  for: 1h
  labels:
    severity: critical
```

## Monitoring Playbooks

Define playbooks de monitoreo proactivo para cada servicio. Un playbook de monitoreo NO es lo mismo que un runbook de incidentes (eso es `incident-response`) — es la guía de qué mirar CADA DÍA para detectar problemas ANTES de que se conviertan en incidentes.

### Daily Health Check Playbook

| Hora | Qué revisar | Dashboard | Acción si anómalo |
|------|------------|-----------|-------------------|
| 09:00 | Error rate (5xx) últimos 24h | Grafana > Service Dashboard | Si >0.5%, investigar antes del daily standup |
| 09:00 | P95 latency últimos 24h | Grafana > Service Dashboard | Si >200ms desviación del baseline, abrir ticket |
| 09:00 | DB connection pool usage | Grafana > Database | Si >80%, planificar scale |
| 10:00 | Kafka consumer lag | Grafana > Kafka | Si >1000 mensajes, verificar consumers |
| 14:00 | Redis memory usage | Grafana > Redis | Si >75%, planificar cache flush o scale |
| 17:00 | Costos LLM del día | Langfuse > Costs | Si >120% del budget diario, revisar tiering |

### Weekly Review Playbook

| Día | Qué revisar | Acción |
|-----|------------|--------|
| Lunes | SLO compliance de la semana anterior | Si SLI < SLO, crear action item |
| Lunes | Error budget consumption | Si >50% consumido, priorizar reliability work |
| Miércoles | Tendencias de latencia (7-day rolling) | Si tendencia al alza, investigar degradación |
| Viernes | Capacidad planning (CPU, memoria, disco) | Si proyección <30 días, planificar scale |

### Dashboard Design

```yaml
# Dashboard layout recomendado
grafana:
  dashboard:
    title: "{Service Name} Overview"
    rows:
      - row: "Golden Signals"
        panels:
          - [latency_p50, latency_p95, latency_p99]
          - [error_rate_5xx, error_rate_4xx]
          - [throughput_requests_per_second]
          - [saturation_cpu, saturation_memory]
      
      - row: "Dependencies"
        panels:
          - [db_connections, db_query_duration]
          - [redis_hit_rate, redis_memory]
          - [kafka_consumer_lag, kafka_producer_errors]
      
      - row: "LLM (si aplica)"
        panels:
          - [llm_tokens_per_minute, llm_cost_per_hour]
          - [llm_latency_p95, llm_error_rate]
      
      - row: "SLO Status"
        panels:
          - [slo_availability_gauge, slo_latency_gauge]
          - [error_budget_remaining, error_budget_burn_rate]
```

### Alert Design

```yaml
# Reglas de alerta con playbooks asociados
alerts:
  - name: HighErrorRate
    condition: error_rate_5xx > 1% for 5m
    severity: SEV2
    playbook: "docs/operations/runbooks/high-error-rate.md"
    runbook_url: "https://wiki.company.com/runbooks/high-error-rate"
    
  - name: CriticalErrorRate
    condition: error_rate_5xx > 10% for 5m
    severity: SEV0
    playbook: "docs/operations/runbooks/critical-error-rate.md"
    auto_triage: true
    
  - name: HighLatency
    condition: p95_latency > 500ms for 10m
    severity: SEV2
    playbook: "docs/operations/runbooks/high-latency.md"
    
  - name: LLMCostOverrun
    condition: llm_cost_hourly > budget * 1.5
    severity: SEV2
    playbook: "docs/operations/runbooks/llm-cost-overrun.md"
    notification: ["slack:#team-ai", "email:ai-lead@company.com"]
    
  - name: DatabaseConnectionPoolExhausted
    condition: db_active_connections > max_connections * 0.9
    severity: SEV1
    playbook: "docs/operations/runbooks/db-pool-exhausted.md"
    auto_mitigation: "kubectl scale deployment api --replicas=+2"
```

### SLI/SLO/Error Budget Tracking

```python
class SLITracker:
    def calculate_burn_rate(self, slo: SLO, window: timedelta) -> float:
        """Calculate how fast we're burning error budget."""
        errors = self.get_errors(window)
        requests = self.get_requests(window)
        error_rate = errors / requests
        budget_consumed = error_rate / (1 - slo.target)
        return budget_consumed
    
    def alert_on_fast_burn(self, burn_rate: float):
        if burn_rate > 10:   # Burning 10x faster than budget allows
            self.alert("FAST BURN: Error budget exhausted in <1 day")
        elif burn_rate > 2:   # Burning 2x faster
            self.alert("ELEVATED BURN: Review reliability backlog")
```

### Multi-Tenant Monitoring

```python
# Asegurar que cada tenant tiene sus propias métricas
class TenantMetricsFilter:
    def get_tenant_dashboard(self, tenant_id: str) -> Dashboard:
        return Dashboard(
            title=f"Tenant: {tenant_id}",
            variables={"tenant": tenant_id},
            panels=[
                self.error_rate_by_tenant(tenant_id),
                self.latency_by_tenant(tenant_id),
                self.cost_by_tenant(tenant_id),
                self.usage_by_tenant(tenant_id)
            ]
        )
```

## Checklist

- [ ] OpenTelemetry SDK configurado en cada servicio Python/FastAPI.
- [ ] LangChain/LangGraph instrumentado con `LangChainInstrumentor`.
- [ ] Langfuse configurado con traces, scores y costos LLM.
- [ ] Callback handler de Langfuse integrado en flujos LLM.
- [ ] Logs en JSON con `trace_id`, `span_id`, `service`, `level`.
- [ ] Métricas RED por endpoint (Rate, Errors, Duration).
- [ ] Trazas distribuidas entre servicios.
- [ ] Dashboards de Grafana por rol (incluido dashboard LLM en Langfuse).
- [ ] Alertas con severity + umbral + destinatario.
- [ ] SLOs definidos con SLIs medibles.
- [ ] Política de retención por entorno y tipo de señal.
- [ ] OTel Collector desplegado como proxy de exportación.
- [ ] Costos LLM visibles por tenant/modelo en Langfuse.
