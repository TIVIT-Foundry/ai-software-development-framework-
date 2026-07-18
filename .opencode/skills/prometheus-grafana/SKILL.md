---
name: prometheus-grafana
description: 'Metrics, dashboards and alerting with Prometheus and Grafana: exporters, recording rules, alertmanager, SLOs and SLIs. Trigger: When setting up metrics collection, dashboards, or alerts for services.'
version: 1.0
metadata:
  phase:
    - operations
  layer:
    - infrastructure
  enforcement: recommended
  depends_on:
    - observabilidad
  consumed_by:
    - framework-operations-evolution
    - incident-response
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how Prometheus and Grafana are used to collect metrics, build dashboards, and trigger alerts aligned with SLOs and SLIs.

## When to use this skill

Activate when:
- Adding metrics to a new service
- Creating Grafana dashboards
- Defining SLOs/SLIs and alert rules

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `observabilidad` | parent | Generic observability strategy |
| `opentelemetry` | sibling | Distributed tracing |
| `incident-response` | consumer | Alerts feed runbooks |

## Critical Rules

1. Instrument applications with Prometheus client libraries.
2. Use consistent metric naming: `{service}_{subsystem}_{metric}_{unit}`.
3. Define SLIs before SLOs; SLOs before alerts.
4. Use recording rules for expensive queries.
5. Route alerts by severity to the correct channel/runbook.
6. Dashboards as code (Grafana JSON or Terraform).

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Metrics | `src/shared/metrics.*` | Application metrics |
| Dashboards | `observability/grafana/dashboards/` | JSON dashboards |
| Rules | `observability/prometheus/rules/` | Recording/alerting rules |
| Alerts | `observability/prometheus/alerts/` | Alertmanager config |

## Example: Counter metric

```python
from prometheus_client import Counter
requests_total = Counter(
    'api_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
```

## Checklist

- [ ] Metrics exposed on `/metrics`
- [ ] SLIs and SLOs documented
- [ ] Dashboards committed as JSON
- [ ] Alert rules with severity labels
- [ ] Runbooks linked in Alertmanager annotations
