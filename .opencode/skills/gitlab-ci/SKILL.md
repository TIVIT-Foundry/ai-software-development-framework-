---
name: gitlab-ci
description: 'CI/CD pipelines with GitLab CI: stages, jobs, runners, environments, vault integration, and deployment gates. Trigger: When implementing or maintaining CI/CD on GitLab CI/CD.'
version: 1.0
metadata:
  phase:
    - operations
  layer:
    - infrastructure
  enforcement: recommended
  depends_on:
    - ci-cd
  consumed_by:
    - project-bootstrap
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Provide concrete GitLab CI patterns for the framework: stages, jobs, runners, environments, secrets via CI/CD variables or Vault, and deployment gates.

## When to use this skill

Activate when:
- The project hosts code on GitLab
- A new `.gitlab-ci.yml` is needed
- Shared runners or custom runners must be configured

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `ci-cd` | parent | Generic CI/CD strategy |
| `terraform` | consumer | Applies Terraform plans |
| `security-testing` | consumer | Runs SAST/DAST in pipeline |

## Critical Rules

1. Use GitLab CI/CD variables or HashiCorp Vault for secrets.
2. Define stages: `lint`, `test`, `build`, `security`, `deploy`.
3. Use `rules:` to avoid duplicate pipeline runs.
4. Protect deployment jobs to `main` and tags.
5. Use cache for `node_modules`, `.bun`, and pip wheels.
6. Run `terraform plan` in MRs; require approval for `apply` in protected branches.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Pipeline | `.gitlab-ci.yml` | Main pipeline |
| Includes | `ci/*.gitlab-ci.yml` | Modular job definitions |
| Templates | `ci/templates/` | Reusable job templates |

## Example: `.gitlab-ci.yml`

```yaml
stages:
  - lint
  - test
  - build
  - security
  - deploy

variables:
  BUN_VERSION: "1.1"

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - node_modules/
    - .bun/

lint:
  stage: lint
  image: oven/bun:${BUN_VERSION}
  script:
    - bun install
    - bun run lint
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
```

## Checklist

- [ ] `.gitlab-ci.yml` committed to repo root
- [ ] CI/CD variables or Vault secrets configured
- [ ] Deployment jobs protected to main/tags
- [ ] Caching enabled for dependencies
- [ ] Security scan fails on CRITICAL/HIGH
- [ ] `terraform plan` runs on MRs
