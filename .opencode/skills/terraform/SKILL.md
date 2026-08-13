---
name: terraform
description: 'Infrastructure as Code with Terraform: modules, state, workspaces, variables, and multi-environment provisioning. Trigger: When provisioning cloud infrastructure, managing environments, or implementing IaC for AWS/GCP/Azure.'
version: 1.0
metadata:
  phase:
    - construction
    - operations
  layer:
    - infrastructure
  enforcement: recommended
  depends_on:
    - framework-platform
    - infrastructure-as-code
  consumed_by:
    - docker-local
    - ci-cd
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define Terraform conventions for provisioning the framework's cloud infrastructure: compute, networking, databases, caches, queues, Kubernetes, and observability.

## When to use this skill

Activate when:
- Bootstrapping cloud infrastructure for a new project
- Adding a new environment (dev/staging/prod)
- Refactoring IaC into reusable modules

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `framework-platform` | input | Platform architecture decisions |
| `infrastructure-as-code` | sibling | Generic IaC patterns |
| `docker-local` | consumer | Local env that maps to Terraform resources |
| `ci-cd` | consumer | Pipeline applies Terraform plans |

## Critical Rules

1. Use **remote state with locking** (S3+DynamoDB on AWS, GCS on GCP, Blob+Storage Table on Azure).
2. Organize code in modules: `modules/{vpc,eks,rds,redis,kafka,observability}`.
3. Use workspaces or separate state keys per environment.
4. Never commit `.tfstate` files.
5. Tag all resources with `project`, `environment`, `owner`, `cost-center`.
6. Run `terraform plan` in CI; require approval for `apply` in prod.

## Project structure

```
infra/terraform/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── eks/
│   ├── rds/
│   ├── redis/
│   ├── kafka/
│   └── observability/
└── global/
    └── remote-state/
```

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Root module | `environments/{env}/main.tf` | Environment composition |
| Child modules | `modules/{name}/` | Reusable resources |
| Variables | `environments/{env}/variables.tf` | Env-specific inputs |
| Outputs | `environments/{env}/outputs.tf` | Connection strings, endpoints |

## Examples

### Remote state backend

```hcl
terraform {
  backend "s3" {
    bucket         = "tivit-foundry-tfstate"
    key            = "projects/{project}/{env}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tivit-foundry-tflocks"
    encrypt        = true
  }
}
```

### Resource tagging

```hcl
locals {
  common_tags = {
    project     = var.project
    environment = var.environment
    owner       = var.owner
    cost-center = var.cost_center
  }
}
```

## Checklist

- [ ] Remote state backend configured
- [ ] State locking enabled
- [ ] Modules are reusable and environment-agnostic
- [ ] Sensitive outputs marked as `sensitive`
- [ ] CI pipeline runs `terraform fmt`, `validate`, `plan`
- [ ] No secrets in `.tfvars` committed to repo
