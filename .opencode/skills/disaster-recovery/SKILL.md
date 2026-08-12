---
name: disaster-recovery
description: "Disaster recovery and business continuity patterns. Covers backup/restore strategies, failover, RTO/RPO targets, multi-region strategies, DR drills, chaos engineering basics, and recovery procedures. Trigger: When designing disaster recovery plans, defining RTO/RPO, or implementing failover strategies."
version: 1.0
metadata:
  phase:
  - operations
  layer:
  - infrastructure
  enforcement: recommended
  depends_on:
  - framework-platform
  - infrastructure-as-code
  consumed_by:
  - framework-operations-evolution
  - incident-response
  - postgresql-backup
  agent_roles:
  - delivery-agent
  - control-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# disaster-recovery

## Propósito

Esta skill define cómo diseñar e implementar estrategias de recuperación ante desastres (DR) y continuidad de negocio (BC).  
Su función es asegurar que la aplicación pueda recuperarse de fallos mayores (región caída, BD corrupta, despliegue roto) dentro de los objetivos de tiempo (RTO) y datos (RPO) definidos.

Esta skill complementa `framework-operations-evolution` (operación continua) y `framework-platform` (diseño de infraestructura). Mientras aquellos manejan incidentes operativos y diseño de plataforma, esta skill maneja escenarios de desastre y recuperación.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cuál es el RTO (Recovery Time Objective) y RPO (Recovery Point Objective) por componente?
2. ¿Qué estrategia de DR usar (backup/restore, pilot light, warm standby, multi-region)?
3. ¿Cómo se hace failover manual vs automático?
4. ¿Cómo se hace rollback de un despliegue roto?
5. ¿Con qué frecuencia se hacen DR drills?

## Relación con otras skills

- `framework-platform` define la infraestructura que esta skill protege.
- `framework-operations-evolution` define los SLOs que esta skill garantiza.
- `infrastructure-as-code` provisiona la infraestructura que esta skill replica en DR.
- `database-seeding` provee los datos de seed para el entorno de DR.
- `database-migrations` aplica el esquema en el entorno de DR.

## Qué debe hacer el agente cuando esta skill está activa

1. Definir RTO y RPO por componente crítico.
2. Seleccionar la estrategia de DR según RTO/RPO y presupuesto.
3. Definir procedimientos de failover (manual y automático).
4. Definir procedimientos de rollback de despliegue.
5. Configurar replicación de base de datos para DR.
6. Documentar procedimientos de recuperación paso a paso.
7. Definir el calendario de DR drills.
8. Definir el proceso de comunicación durante un desastre.

## Entradas esperadas

Esta skill asume que ya existe:
- diseño de infraestructura (`framework-platform`);
- infraestructura como código (`infrastructure-as-code`);
- SLOs definidos (`framework-operations-evolution`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- definición de RTO y RPO por componente;
- selección de estrategia de DR;
- procedimientos de failover y rollback;
- replicación de BD para DR;
- DR drills y playbooks;
- comunicación durante desastres;

La fase no incluye todavía:
- diseño de infraestructura (cubierta por `framework-platform`);
- operationes de día a día (cubiertas por `framework-operations-evolution`);
- testing de carga bajo DR (cubierta por `load-testing`).

## Principios que siempre debe respetar

- Todo componente crítico DEBE tener un RTO y RPO definidos.
- Los DR drills DEBEN ejecutarse al menos una vez por trimestre.
- El failover DEBE estar documentado paso a paso (playbook).
- El rollback de despliegue DEBE ser automatizado y reversible.
- Los datos DEBE ser posible restaurarlos desde backup dentro del RPO.
- La estrategia de DR DEBE ser proporcional al impacto del downtime (no sobre-diseñar).
- Los DR drills DEBEN incluir escenarios reales (no solo simulación en papel).

## Qué decide esta skill y qué delega

Esta skill sí decide:
- los RTO y RPO por componente;
- la estrategia de DR (backup/restore, pilot light, warm standby, multi-region);
- los procedimientos de failover y rollback;
- el calendario de DR drills;

Esta skill delega:
- la infraestructura a `framework-platform`;
- los SLOs operativos a `framework-operations-evolution`;
- el provisionamiento a `infrastructure-as-code`;
- los datos de seed a `database-seeding`.

## Qué debe definir el diseño

### 1. Estrategias de DR

| Estrategia | RTO | RPO | Costo | Complejidad | Uso recomendado |
|------------|-----|-----|-------|-------------|-----------------|
| **Backup/Restore** | 24h | 24h | Bajo | Baja | Apps no críticas |
| **Pilot Light** | 1-4h | 1h | Medio | Media | **Por defecto** para apps empresariales |
| **Warm Standby** | 15-30min | 5min | Alto | Alta | Apps críticas con SLA alto |
| **Multi-Region Active-Active** | < 1min | 0 | Muy alto | Muy alta | Apps que no pueden caer |

**Decisión por defecto**: Pilot Light para la mayoría de aplicaciones empresariales.

### 2. RTO y RPO por componente

| Componente | RTO | RPO | Estrategia |
|------------|-----|-----|------------|
| Base de datos principal | 15min | 5min | Replicación síncrona |
| API/Application | 10min | 0 | Auto-scaling en región DR |
| Blob storage | 1h | 15min | Replicación cross-region |
| Cache (Redis/ElastiCache) | 5min | N/A (cache) | Replicación cross-region |
| CDN | < 1min | 0 | Multi-region por defecto |
| Search index | 30min | 1h | Rebuild desde BD |
| Email/notifications | 1h | 0 | Queue persistente |

### 3. Replicación de base de datos para DR

```hcl
# Terraform: Replicación cross-region para PostgreSQL (AWS RDS)
resource "aws_db_instance" "primary" {
  identifier             = "app-db"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.medium"
  allocated_storage      = 100
  storage_encrypted      = true
  backup_retention_period = 7
}

resource "aws_db_instance" "dr" {
  provider               = aws.dr
  identifier             = "app-db-dr"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.medium"
  replicate_source_db    = aws_db_instance.primary.arn
  storage_encrypted      = true
}
```

### 4. Procedimiento de failover

```markdown
# DR Playbook: Failover a región secundaria

## Escenario: Región primaria caída

### Paso 1: Confirmar desastre (5 min)
- [ ] Verificar que la caída no es temporal (check status page)
- [ ] Confirmar con equipo de operaciones que failover es necesario
- [ ] Notificar al equipo de comunicación

### Paso 2: Activar región DR (10 min)
- [ ] Ejecutar: `terraform apply -var="environment=dr" -auto-approve`
- [ ] Verificar que la BD DR está accesible
- [ ] Verificar que la aplicación responde en la región DR
- [ ] Ejecutar: `database-migrations` en la región DR

### Paso 3: Redirigir tráfico (5 min)
- [ ] Cambiar DNS a la región DR
- [ ] Verificar que el tráfico llega a la región DR
- [ ] Monitorear errores y latencia

### Paso 4: Validar (10 min)
- [ ] Ejecutar smoke tests contra la región DR
- [ ] Verificar que los datos están actualizados (within RPO)
- [ ] Verificar que las notificaciones funcionan

### Paso 5: Comunicar (5 min)
- [ ] Notificar al equipo interno: failover completado
- [ ] Notificar a usuarios si hubo downtime visible
- [ ] Registrar incidente en el post-mortem

## Tiempo total estimado: 35 min (dentro del RTO de 1h)
```

### 5. Rollback de despliegue

```bash
#!/bin/bash
# scripts/rollback-deployment.sh

ENVIRONMENT=${1:-production}
PREVIOUS_VERSION=${2:-"previous"}

echo "⚠️  ROLLBACK deployment for $ENVIRONMENT to $PREVIOUS_VERSION"

# Step 1: Get previous version
PREVIOUS_IMAGE=$(aws ecs describe-services \
  --cluster "app-$ENVIRONMENT" \
  --service "app-service" \
  --query 'services[0].taskDefinition' \
  --output text)

# Step 2: Update ECS to previous version
aws ecs update-service \
  --cluster "app-$ENVIRONMENT" \
  --service "app-service" \
  --task-definition "$PREVIOUS_IMAGE" \
  --force-new-deployment

# Step 3: Wait for stabilization
echo "Waiting for deployment to stabilize..."
aws ecs wait services-stable \
  --cluster "app-$ENVIRONMENT" \
  --services "app-service"

# Step 4: Verify
HEALTH=$(curl -s "https://$ENVIRONMENT.app.com/health" | jq '.status')
if [ "$HEALTH" == '"healthy"' ]; then
    echo "✅ Rollback successful. Application is healthy."
else
    echo "❌ Rollback failed. Application is unhealthy. Escalate immediately."
    exit 1
fi
```

### 6. DR Drill calendarizado

| Drill | Frecuencia | Duración | Escenario |
|-------|-----------|----------|-----------|
| Backup restore | Mensual | 2h | Restaurar BD desde backup |
| Pilot light failover | Trimestral | 4h | Failover completo a región DR |
| Rollback de deployment | Mensual | 30min | Rollback de la última versión |
| Regional outage | Semestral | 8h | Simulación completa de caída de región |
| Chaos engineering | Trimestral | 2h | Matar instancia/random para probar auto-healing |

### 7. Comunicación durante desastre

| Audiencia | Canal | Contenido |
|-----------|-------|-----------|
| Equipo interno | Slack #incidents | Detalles técnicos, pasos de recuperación |
| Management | Email + call | Impacto estimado, RTO, ETA de recuperación |
| Usuarios | Status page | Mensaje breve: "Estamos experimentando problemas" |
| Partners | Email | Impacto en integraciones, ETA |

## Preguntas guía

### 1. Sobre RTO/RPO
- ¿Cuál es el máximo tiempo aceptable de downtime (RTO)?
- ¿Cuál es la máxima pérdida de datos aceptable (RPO)?
- ¿Hay requisitos regulatorios para RPO/RTO?

### 2. Sobre estrategia
- ¿Se usa Pilot Light, Warm Standby o Multi-Region?
- ¿El failover es automático o manual?
- ¿El failback a la región primaria está automatizado?

### 3. Sobre base de datos
- ¿Se usa replicación síncrona o asíncrona?
- ¿Los backups automáticos van a otra región?
- ¿Se hace backup de la BD antes de cada migración?

### 4. Sobre DR drills
- ¿Con qué frecuencia se hacen drills?
- ¿Los drills incluyen escenarios reales o solo simulación?
- ¿Se documenta el resultado de cada drill?

### 5. Sobre rollback
- ¿El rollback de despliegue está automatizado?
- ¿Se puede rollback a cualquier versión anterior?
- ¿El rollback incluye la BD o solo la aplicación?

## Salidas esperadas de esta skill

### A. Plan de DR documentado
- RTO y RPO por componente.
- Estrategia de DR seleccionada.
- Playbook de failover paso a paso.
- Playbook de rollback paso a paso.

### B. Replicación configurada
- BD replicada a región DR (Terraform/Pulumi).
- Blob storage replicado.
- Cache replicado.

### C. Scripts de rollback
- Script de rollback de despliegue.
- Script de failover a región DR.
- Script de failback a región primaria.

### D. Calendario de drills
- Backup restore mensual.
- Pilot light failover trimestral.
- Regional outage semestral.

### E. Consumidores de esta skill
- `framework-operations-evolution` define los SLOs que esta skill garantiza;
- `infrastructure-as-code` provisiona la infraestructura DR;
- `framework-platform` define la topología que esta skill replica;
- `ci-cd` ejecuta los scripts de rollback.

## Criterios de calidad

- RTO y RPO están definidos por componente crítico.
- La estrategia de DR está seleccionada y justificada.
- Los playbooks de failover y rollback existen y están documentados.
- La replicación de BD está configurada.
- Los DR drills están calendarizados (mínimo trimestral).
- El rollback de despliegue está automatizado.
- La comunicación durante desastres está definida.
- Se ha ejecutado al menos un DR drill.

## Comportamiento esperado del agente

Cuando el usuario no tenga RTO/RPO definidos, el agente debe proponer valores por defecto (RTO: 1h, RPO: 5min para BD) y solicitar confirmación.  
Cuando el usuario quiera DR sin replicación de BD, el agente debe explicar que el RPO será igual al intervalo de backup y proponer replicación.  
Cuando el usuario quiera failover automático sin DR drills, el agente debe advertir que el failover automático sin pruebas es un riesgo.  
Cuando el usuario solo haga simulación en papel sin DR drills reales, el agente debe insistir en al menos un drill real por trimestre.

## Checklist final de la skill

- ¿Se definieron RTO y RPO por componente crítico?
- ¿Se seleccionó la estrategia de DR?
- ¿Los playbooks de failover y rollback existen?
- ¿La replicación de BD está configurada?
- ¿Los DR drills están calendarizados?
- ¿El rollback de despliegue está automatizado?
- ¿Se ha ejecutado al menos un DR drill?
- ¿La comunicación durante desastres está definida?
- ¿Se probó el rollback a una versión anterior?
- ¿Se verificó que el RPO cumple con las replicas configuradas?