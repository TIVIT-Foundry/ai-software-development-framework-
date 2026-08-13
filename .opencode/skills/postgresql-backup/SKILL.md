---
name: postgresql-backup
description: 'PostgreSQL backup, restore, and disaster recovery: logical backups, PITR, replication, verification, and runbooks. Trigger: When designing backup strategy, testing restores, or recovering from database incidents.'
version: 1.0
metadata:
  phase:
    - operations
  layer:
    - database
  enforcement: recommended
  depends_on:
    - database-modeling
    - disaster-recovery
  consumed_by:
    - incident-response
  agent_roles:
    - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define backup and restore procedures for PostgreSQL, including logical backups, continuous archiving for PITR, replica promotion, and restore verification.

## When to use this skill

Activate when:
- Defining backup strategy for a new system
- Testing disaster recovery procedures
- Restoring data after incident or migration

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `database-modeling` | depends_on | Schema knowledge |
| `disaster-recovery` | parent | DR strategy |
| `incident-response` | consumer | Recovery runbooks |

## Critical Rules

1. Take logical backups daily (`pg_dump`) and retain 7-30 days.
2. Enable WAL archiving for PITR in production.
3. Store backups in separate region/account from primary DB.
4. Test restores quarterly and document RTO/RPO.
5. Encrypt backups at rest and in transit.
6. Automate backup verification with `pg_restore --schema-only` or checksums.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Backup script | `pg_dump` (runbook de esta skill) | Scheduled backup |
| Restore runbook | `docs/operations/runbooks/postgres-restore.md` | Recovery steps |
| Terraform/Pulumi | `infra/modules/rds/backup.tf` | Automated backups |
| Verification job | CI cron job | Restore test |

## Example: pg_dump

```bash
pg_dump -Fc -v -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" \
  | gzip > "/backups/${PGDATABASE}_$(date +%Y%m%d_%H%M%S).dump.gz"
```

## Checklist

- [ ] Daily logical backups scheduled
- [ ] WAL archiving enabled in prod
- [ ] Backups stored in separate region
- [ ] Restore tested quarterly
- [ ] RTO/RPO documented
- [ ] Encryption at rest and in transit
