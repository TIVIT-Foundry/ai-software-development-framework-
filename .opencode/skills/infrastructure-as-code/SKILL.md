---
name: infrastructure-as-code
description: "Infrastructure as Code patterns with Terraform. Covers module structure, state management, drift detection, environment provisioning, and CI/CD integration. Trigger: When provisioning cloud infrastructure, managing environments, or implementing IaC practices."
version: 1.0
metadata:
  phase:
  - operations
  layer:
  - infrastructure
  enforcement: mandatory
  depends_on:
  - framework-platform
  consumed_by:
  - ci-cd
  - disaster-recovery
  - framework-operations-evolution
  - terraform
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# infrastructure-as-code

## Propósito

Esta skill define cómo gestionar la infraestructura como código: versionar, provisionar y gestionar entornos (dev, staging, production) de forma reproducible, auditable y automatizada.  
Su función es asegurar que la infraestructura definida en `framework-platform` se implemente de forma declarativa, sin configuración manual, con drift detection y rollback seguro.

Esta skill complementa `framework-platform` (diseño de topología) y `ci-cd` (pipelines). Mientras `framework-platform` diseña QUÉ infraestructura se necesita y DÓNDE, esta skill implementa CÓMO se provisiona y gestiona.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué herramienta de IaC usar (Terraform)?
2. ¿Cómo se estructuran los módulos de infraestructura?
3. ¿Cómo se gestiona el state (remoto, local, locked)?
4. ¿Cómo se detecta y corrige el drift?
5. ¿Cómo se provisionan entornos (dev, staging, production)?

## Relación con otras skills

- `framework-platform` define la topología de infraestructura que esta skill provisiona.
- `ci-cd` ejecuta los pipelines que aplican y destruyen infraestructura.
- `docker-local` define los contenedores que esta skill despliega.
- `framework-operations-evolution` define los SLOs que la infraestructura debe soportar.

## Qué debe hacer el agente cuando esta skill está activa

1. Seleccionar la herramienta de IaC según el stack cloud (Terraform).
2. Estructurar los módulos de infraestructura por entorno y componente.
3. Configurar el state remoto con locking (S3+DynamoDB, GCS).
4. Definir variables por entorno (dev, staging, production).
5. Implementar drift detection y corrección automática.
6. Configurar pipelines de IaC en CI/CD (plan, apply, destroy).
7. Implementar provisionamiento de entornos efímeros para PRs.
8. Documentar el proceso de rollback de infraestructura.

## Entradas esperadas

Esta skill asume que ya existe:
- diseño de topología de infraestructura (`framework-platform`);
- configuración de CI/CD (`ci-cd`);
- contenedores Docker definidos (`docker-local`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- selección de herramienta de IaC;
- estructura de módulos y variables;
- state management remoto con locking;
- drift detection y corrección;
- provisionamiento de entornos;
- pipelines de IaC (plan, apply, destroy);
- rollback de infraestructura;

La fase no incluye todavía:
- diseño de topología de infraestructura (cubierta por `framework-platform`);
- configuración de aplicaciones (cubierta por `app-bootstrap`);
- runtime de contenedores (cubierto por `docker-local` y `framework-platform`).

## Principios que siempre debe respetar

- Toda infraestructura DEBE estar definida en código, nunca manualmente.
- El state DEBE almacenarse remotamente con locking para evitar conflictos.
- Los cambios de infraestructura DEBEN pasar por pipeline (plan → review → apply).
- Los entornos DEBEN ser reproducibles: destruir y recrear DEBE dar el mismo resultado.
- El drift DEBE detectarse y corregirse automáticamente o reportarse.
- Las variables sensibles (secrets, keys) NUNCA deben estar en el código de IaC.
- Los módulos DEBEN ser reutilizables entre entornos (dev, staging, production).
- Los cambios DEBEN ser reversibles: todo apply DEBE tener un plan de rollback.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la herramienta de IaC y su configuración;
- la estructura de módulos y variables;
- el state management;
- la estrategia de drift detection;

Esta skill delega:
- el diseño de topología a `framework-platform`;
- la ejecución de pipelines a `ci-cd`;
- los SLOs de infraestructura a `framework-operations-evolution`.

## Qué debe definir el diseño

### 1. Selección de herramienta

| Herramienta | Cloud | Pros | Contras | Uso recomendado |
|------------|------|------|---------|-----------------|
| **Terraform** | Multi-cloud | Estándar de la industria, módulos, state remoto | HCL, state locking, curva de aprendizaje | **Por defecto** |
| **Pulumi** | Multi-cloud | Lenguajes reales (TS, Python, Go), tests unitarios | Más joven, menos módulos | Equipos que prefieren lenguajes de programación |

**Decisión por defecto**: Terraform.

### 2. Estructura de módulos (Terraform)

```
infra/
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── versions.tf
│   ├── compute/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── versions.tf
│   ├── database/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── versions.tf
│   ├── storage/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── versions.tf
│   └── monitoring/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── versions.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
├── policies/
│   ├── sentinel/
│   └── opa/
└── scripts/
    ├── drift-detect.sh
    └── emergency-rollback.sh
```

### 3. State management (Terraform)

```hcl
# environments/staging/backend.tf
terraform {
  backend "s3" {
    bucket         = "terraform-state-staging"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-staging"
  }
}
```

Reglas:
- State DEBE almacenarse remotamente (nunca local para producción).
- State DEBE tener locking (DynamoDB para AWS, equivalentes cloud).
- State DEBE estar encriptado en reposo.
- State POR ENTORNO (nunca un solo state file para todos los entornos).

### 4. Variables por entorno

```hcl
# environments/staging/terraform.tfvars
environment      = "staging"
vpc_cidr         = "10.1.0.0/16"
instance_type    = "t3.medium"
min_instances    = 2
max_instances    = 4
database_tier    = "db.t3.medium"
database_storage = 50
enable_monitoring = true
log_retention    = 30
```

### 5. Drift detection

```bash
#!/bin/bash
# Ejemplo: drift-detect.sh (el framework incluye uno real en .opencode/scripts/)

ENVIRONMENT=${1:-staging}
cd "environments/$ENVIRONMENT"

# Initialize
terraform init -backend-config=backend.tf

# Plan without changes
terraform plan -detailed-exitcode -out=drift.plan

# Exit codes:
# 0 = No changes (no drift)
# 1 = Error
# 2 = Changes detected (drift!)

EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
    echo "⚠️  Drift detected in $ENVIRONMENT!"
    echo "Run 'terraform plan' to see changes."
    # Optional: auto-correct
    # terraform apply -auto-approve drift.plan
    exit 2
elif [ $EXIT_CODE -eq 0 ]; then
    echo "✅ No drift detected in $ENVIRONMENT."
    exit 0
else
    echo "❌ Error checking drift in $ENVIRONMENT."
    exit 1
fi
```

### 6. Pipeline de IaC en CI/CD

```yaml
# .github/workflows/infrastructure.yml
name: Infrastructure
on:
  pull_request:
    paths: ['infra/**']
  push:
    branches: [main]
    paths: ['infra/**']

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - name: Terraform Init
        run: cd infra/environments/staging && terraform init
      - name: Terraform Plan
        run: cd infra/environments/staging && terraform plan -out=tfplan
      - name: Comment Plan
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: 'Terraform plan output will be posted here'
            })

  apply:
    needs: plan
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - name: Terraform Apply
        run: cd infra/environments/staging && terraform apply -auto-approve
```

### 7. Provisionamiento de entornos efímeros

```hcl
# environments/pr/main.tf
# Entorno efímero para Pull Requests

module "networking" {
  source      = "../../modules/networking"
  environment = "pr-${var.pr_number}"
  vpc_cidr    = "10.100.0.0/16"
}

module "compute" {
  source         = "../../modules/compute"
  environment   = "pr-${var.pr_number}"
  vpc_id        = module.networking.vpc_id
  instance_type = "t3.small"
}

module "database" {
  source          = "../../modules/database"
  environment    = "pr-${var.pr_number}"
  vpc_id         = module.networking.vpc_id
  database_tier  = "db.t3.small"
}
```

### 8. Rollback de infraestructura

```bash
#!/bin/bash
# Ejemplo: emergency-rollback.sh (el framework incluye uno real en .opencode/scripts/)

ENVIRONMENT=${1:-production}
PREVIOUS_STATE=${2:-"terraform.tfstate.backup"}

echo "⚠️  EMERGENCY ROLLBACK for $ENVIRONMENT"
echo "Rolling back to previous state: $PREVIOUS_STATE"

cd "environments/$ENVIRONMENT"

# Restore previous state
cp "$PREVIOUS_STATE" terraform.tfstate

# Apply previous state
terraform init
terraform apply -auto-approve

echo "✅ Rollback complete for $ENVIRONMENT"
```

## Preguntas guía

### 1. Sobre herramienta
- ¿Se usa Terraform?
- ¿Se requiere multi-cloud o un solo proveedor?
- ¿El equipo tiene experiencia con HCL o prefiere lenguajes de programación?

### 2. Sobre state
- ¿Dónde se almacena el state remoto?
- ¿Se usa locking para prevenir conflictos?
- ¿Se usa state por entorno o state por componente?

### 3. Sobre entornos
- ¿Cuántos entornos se necesitan (dev, staging, production)?
- ¿Se necesitan entornos efímeros para PRs?
- ¿Los entornos de staging y production son idénticos?

### 4. Sobre drift
- ¿Con qué frecuencia se detecta drift?
- ¿El drift se corrige automáticamente o se reporta?
- ¿Quién es responsable de corregir drift manual?

### 5. Sobre CI
- ¿Los cambios de infraestructura pasan por PR review?
- ¿Se requiere aprobación manual para apply en production?
- ¿Se puede destruir infraestructura desde CI?

## Salidas esperadas de esta skill

### A. Estructura de módulos
- Directorio `infra/modules/` con módulos reutilizables.
- Directorio `infra/environments/` con configuración por entorno.

### B. State management
- Backend configurado (S3+DynamoDB o equivalente cloud).
- State por entorno con locking.

### C. Pipeline de IaC
- Workflow `.github/workflows/infrastructure.yml` con plan y apply.
- Step de plan que comenta en el PR.

### D. Drift detection
- Script de drift detection que corre periódicamente.
- Alertas si se detecta drift.

### E. Consumidores de esta skill
- `ci-cd` ejecuta los pipelines de IaC;
- `framework-platform` define la topología que esta skill provisiona;
- `framework-operations-evolution` define los SLOs que la infraestructura debe cumplir;
- `docker-local` define las imágenes que esta skill despliega.

## Criterios de calidad

- Toda infraestructura está definida en código (no manual).
- El state se almacena remotamente con locking.
- Los cambios de infraestructura pasan por pipeline (plan → review → apply).
- Los entornos son reproducibles (destroy y recreate da el mismo resultado).
- Las variables sensibles están en secret managers, no en código.
- Los módulos son reutilizables entre entornos.
- Drift detection está configurado y corre periódicamente.
- Existe plan de rollback para cambios de infraestructura.

## Comportamiento esperado del agente

Cuando el usuario pregunte si puede cambiar infraestructura manualmente, el agente debe rechazar y proponer un cambio en Terraform.  
Cuando el usuario no tenga state remoto, el agente debe configurar S3+DynamoDB o equivalente antes de cualquier apply.  
Cuando se detecte drift, el agente debe proponer `terraform plan` para ver los cambios y `terraform apply` para corregir.  
Cuando el usuario quiera crear un entorno efímero, el agente debe generar la configuración con variables parametrizadas por PR number.

## Checklist final de la skill

- ¿Se seleccionó la herramienta de IaC (Terraform)?
- ¿Se creó la estructura de módulos por componente?
- ¿Se configuró el state remoto con locking?
- ¿Se crearon variables por entorno?
- ¿Los cambios pasan por pipeline (plan → apply)?
- ¿Se configuró drift detection?
- ¿Los secretos están en secret managers?
- ¿Los módulos son reutilizables entre entornos?
- ¿Se puede destruir y recrear un entorno con el mismo resultado?
- ¿Existe plan de rollback para emergencies?