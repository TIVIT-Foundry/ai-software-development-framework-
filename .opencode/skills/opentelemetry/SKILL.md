---
name: opentelemetry
description: 'Distributed tracing and instrumentation with OpenTelemetry: SDK setup, span attributes, context propagation, and collector configuration. Trigger: When adding tracing, context propagation, or telemetry instrumentation to services.'
version: 1.1
metadata:
  phase:
    - construction
    - operations
  layer:
    - infrastructure
  enforcement: recommended
  depends_on:
    - observabilidad
  consumed_by:
    - prometheus-grafana
    - incident-response
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how OpenTelemetry is used to instrument FastAPI, Bun, and React/Angular services for distributed tracing, metrics, and logs.

## When to use this skill

Activate when:
- Adding distributed tracing to a service
- Propagating trace context across HTTP/Kafka calls
- Configuring an OpenTelemetry Collector

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `observabilidad` | parent | Generic observability strategy |
| `prometheus-grafana` | consumer | Metrics from OTel |
| `kafka` | consumer | Propagate trace context in messages |

## Critical Rules

1. Use **W3C Trace Context** propagation by default.
2. Add semantic attributes: `service.name`, `service.version`, `deployment.environment`.
3. Do not capture PII in span attributes.
4. Sample traces: 100% in dev, 10% in prod unless debugging.
5. Export to OTLP collector, not directly to vendor backends.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Instrumentation | `src/shared/telemetry.py` / `telemetry.ts` | SDK setup |
| Collector config | `observability/otel-collector.yaml` | Collector pipeline |
| Middleware | `src/shared/otel_middleware.*` | Auto-instrumentation |

## Examples

### FastAPI

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument_app(app)
```

### Bun

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
const sdk = new NodeSDK({ traceExporter: new OTLPTraceExporter() });
sdk.start();
```

## Checklist

- [ ] OTel SDK initialized at startup
- [ ] Trace context propagated across services
- [ ] PII excluded from attributes
- [ ] Sampling configured per environment
- [ ] Collector endpoint configured via env var
