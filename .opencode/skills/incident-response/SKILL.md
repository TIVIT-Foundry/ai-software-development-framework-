---
name: incident-response
description: 'Production incident response: severity classification, runbooks, escalation matrix, on-call rotation, incident command, postmortems (blameless), status communication, automated triage. Trigger: When incidents occur in production, designing incident response processes, or creating runbooks.'
version: 1.0
metadata:
  phase:
    - operations
  layer:
    - operations
  enforcement: mandatory
  depends_on:
    - observabilidad
    - disaster-recovery
  consumed_by:
    - framework-operations-evolution
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: none
---

## Purpose

Define the incident response pattern for production systems built with the framework. Covers severity classification, runbook creation, escalation matrix, on-call rotation, incident command structure, blameless postmortems, status communication, and automated triage. When your observability detects an issue, this skill ensures you respond effectively.

## Severity Classification

| Level | Name | Description | Response Time | Example |
|-------|------|-------------|---------------|---------|
| **SEV0** | Critical | Complete service outage, data loss, security breach | 15 min | Database down, PII leak, all users affected |
| **SEV1** | High | Major functionality broken, no workaround | 30 min | Login broken, payments failing |
| **SEV2** | Medium | Partial functionality degraded, workaround exists | 2 hours | Search slow, reports delayed |
| **SEV3** | Low | Minor issue, cosmetic, single user | 24 hours | Typo in UI, non-critical bug |
| **SEV4** | Informational | Investigation, planned maintenance | Next sprint | Performance investigation |

## Runbook Template

Every service must have a runbook:

```markdown
# Runbook: {service-name}

## Service Overview
- **Repository**: github.com/org/{repo}
- **Owner Team**: {team-name}
- **SLO**: 99.9% availability, P95 latency < 200ms

## Dashboards
- [Grafana Dashboard]({grafana-url})
- [Langfuse Traces]({langfuse-url})
- [Prometheus Alerts]({prometheus-url})

## Common Alerts

### ALERT: High Error Rate (>1% 5xx in 5 min)
1. Check Grafana for error distribution
2. Check Langfuse for recent deployment correlation
3. Check database connection pool (pg_stat_activity)
4. **Rollback**: `helm rollback {service} {revision}`
5. **Escalate if**: >5 min without resolution → SEV1

### ALERT: P95 Latency Spike (>500ms for 5 min)
1. Check pg_stat_statements for slow queries
2. Check Redis latency
3. Check kafka consumer lag
4. **Mitigation**: Scale replicas: `kubectl scale deployment {service} --replicas=4`
5. **Escalate if**: >10 min without resolution → SEV2

## Recovery Procedures

### Database Failover
```bash
kubectl exec -it {primary-pod} -- pg_ctl promote
kubectl patch svc {service}-db -p '{"spec":{"selector":{"role":"standby"}}}'
```

### Cache Clear
```bash
redis-cli -h {host} FLUSHDB
```

### Rollback Deployment
```bash
helm rollback {service} $(($(helm history {service} | wc -l) - 2))
```

## Contact Information
| Role | Name | Phone | Slack |
|------|------|-------|-------|
| Primary On-Call | {name} | {phone} | @{slack} |
| Secondary On-Call | {name} | {phone} | @{slack} |
| Team Lead | {name} | {phone} | @{slack} |
```

## Escalation Matrix

```
SEV4/SEV3: Team handles during business hours
    ↓ (no response in SLA)
SEV2: Team Lead notified + on-call engineer
    ↓ (15 min without resolution)
SEV1: Engineering Manager + Tech Lead + on-call
    ↓ (30 min without resolution)
SEV0: VP Engineering + Incident Commander + full team
```

```python
class EscalationManager:
    def __init__(self):
        self.escalation_chain = {
            Severity.SEV0: [
                Role.INCIDENT_COMMANDER,
                Role.VP_ENGINEERING,
                Role.TECH_LEAD,
                Role.ON_CALL_PRIMARY,
                Role.ON_CALL_SECONDARY
            ],
            Severity.SEV1: [
                Role.TECH_LEAD,
                Role.ON_CALL_PRIMARY,
                Role.ON_CALL_SECONDARY
            ],
            Severity.SEV2: [
                Role.TEAM_LEAD,
                Role.ON_CALL_PRIMARY
            ]
        }
    
    async def escalate(self, incident: Incident):
        level = self.escalation_chain[incident.severity]
        for role in level:
            person = await self.find_on_call(role)
            notified = await self.notify(
                person, 
                f"SEV{incident.severity.value}: {incident.title}"
            )
            if notified:
                incident.escalated_to = person
                break
```

## Incident Command Structure

```
Incident Commander (IC)
├── Communications Lead  → Status updates, stakeholder comms
├── Operations Lead      → Technical investigation, mitigation
└── Scribe              → Timeline, action log, postmortem notes
```

**Roles during incident:**

| Role | Responsibility | Who |
|------|---------------|-----|
| **Incident Commander** | Coordinates response, makes decisions, escalates | Most senior on-call |
| **Communications Lead** | Sends status updates every 30 min | Designated in rotation |
| **Operations Lead** | Leads technical investigation and mitigation | Most familiar with affected system |
| **Scribe** | Documents everything in real-time | Junior team member (great learning) |

## Blameless Postmortem Template

```markdown
# Postmortem: {incident-title}

## Summary
- **Incident ID**: INC-{YYYY}-{NNN}
- **Date**: {date}
- **Duration**: {start} — {end} ({duration})
- **Severity**: SEV{n}
- **Status**: Resolved | Monitoring | Open
- **Incident Commander**: {name}
- **Scribe**: {name}

## Timeline (UTC)
| Time | Event | Actor |
|------|-------|-------|
| 14:03 | Alert fired: 5xx rate > 5% | Prometheus |
| 14:05 | On-call acknowledged | @oncall |
| 14:08 | Investigation started | @oncall |
| 14:15 | Root cause identified: bad deploy | @techlead |
| 14:18 | Rollback initiated | @techlead |
| 14:22 | Service recovered | @oncall |
| 14:30 | Monitoring confirms stable | @oncall |

## Root Cause
[What caused the incident — technical details]

## Impact
- **Users affected**: {number} ({percentage}%)
- **Duration**: {minutes} minutes
- **Data loss**: None | {description}
- **Revenue impact**: ${amount}

## What Went Well
- Alert fired within 60 seconds of anomaly
- On-call responded within 2 minutes
- Rollback decision made quickly

## What Went Wrong
- Deploy bypassed canary stage due to pipeline misconfiguration
- No automated rollback triggered
- Communication to stakeholders delayed 15 minutes

## Action Items
| # | Action | Owner | Priority | Due |
|---|--------|-------|----------|-----|
| 1 | Fix canary deployment pipeline | @devops | P0 | 1 day |
| 2 | Add automated rollback on error rate spike | @sre | P1 | 1 week |
| 3 | Update runbook with this incident pattern | @team | P2 | 2 weeks |
| 4 | Add integration test for deployment pipeline | @qa | P2 | 2 weeks |

## Lessons Learned
[What the team learned — this becomes knowledge for future incidents]
```

## Status Communication Template

```markdown
## Incident Update — {incident-title}
**Status**: {Investigating | Identified | Mitigating | Resolved}
**Severity**: SEV{n}
**Time**: {timestamp} UTC

### Current Situation
[Brief description of what's happening]

### User Impact
[Who is affected and how]

### Actions Taken
- {time}: [Action taken]

### Next Steps
- [Expected next action with ETA]

### Next Update
{+30 min from now} UTC
```

## Automated Triage

```python
class IncidentAutoTriage:
    async def triage(self, alert: Alert) -> Incident:
        # Classify severity from alert metrics
        severity = self.classify_severity(alert)
        
        # Auto-create incident
        incident = await self.create_incident(
            title=f"{severity.name}: {alert.name}",
            severity=severity,
            source=alert.source,
            metrics=alert.metrics
        )
        
        # Auto-assign based on service ownership
        owner = await self.service_catalog.get_owner(alert.service)
        incident.assignee = owner.on_call_primary
        
        # Create Slack channel for coordination
        channel = await self.create_incident_channel(incident)
        
        # Post initial status
        await self.post_initial_status(incident, channel)
        
        # Start timer for SLA tracking
        await self.start_sla_timer(incident)
        
        return incident
    
    def classify_severity(self, alert: Alert) -> Severity:
        if alert.error_rate > 0.10:  # >10% errors
            return Severity.SEV0
        if alert.latency_p99 > 2000:  # >2s P99
            return Severity.SEV1
        if alert.error_rate > 0.01:  # >1% errors
            return Severity.SEV2
        if alert.resource_usage > 0.90:  # >90% resource
            return Severity.SEV2
        return Severity.SEV3
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| SEV0 alert fires | "I'll check tomorrow" | 15 min SLA — escalate immediately |
| Root cause unknown | Keep investigating silently | Post status "Investigating" every 30 min |
| Incident resolved | Close ticket, move on | Write postmortem within 48h |
| Same incident recurs | Treat as new | Link to previous postmortem, check action items |
| Blame culture emerges | "Who did this?" | "What process allowed this?" |

## Verification checklist

- [ ] Runbook exists for every production service
- [ ] Escalation matrix defined and published
- [ ] On-call rotation configured (PagerDuty/Opsgenie)
- [ ] Incident command roles assigned
- [ ] Postmortem template used for all SEV0/SEV1
- [ ] Status communication template ready
- [ ] Automated triage for Prometheus alerts
- [ ] SLA timers configured and monitored
