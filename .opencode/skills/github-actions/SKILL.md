---
name: github-actions
description: 'CI/CD pipelines with GitHub Actions: workflows, reusable actions, environments, secrets, gates, and matrix builds. Trigger: When implementing or maintaining CI/CD on GitHub Actions.'
version: 1.2
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

Provide concrete GitHub Actions patterns for the framework's CI/CD: lint, test, build, security scan, Terraform plan/apply, and deployment gates.

## When to use this skill

Activate when:
- The project hosts code on GitHub
- A new pipeline is needed for Python/FastAPI, Bun/TypeScript, or React/Angular
- Reusable workflows must be standardized

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `ci-cd` | parent | Generic CI/CD strategy |
| `terraform` | consumer | Applies Terraform plans |
| `security-testing` | consumer | Runs SAST/DAST in pipeline |

## Critical Rules

1. Store secrets in GitHub Secrets, never in workflow files.
2. Use `GITHUB_TOKEN` with least-privilege permissions.
3. Pin third-party actions to a commit SHA, not a floating tag.
4. Use environments with required reviewers for production deployments.
5. Separate `pr.yml`, `main.yml`, and `release.yml` workflows.
6. Cache dependencies (`bun`, `npm`, `pip`) to reduce build time.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| PR workflow | `.github/workflows/pr.yml` | Lint + test + security scan |
| Main workflow | `.github/workflows/main.yml` | Build + deploy to staging |
| Release workflow | `.github/workflows/release.yml` | Deploy to prod with gate |
| Reusable workflows | `.github/workflows/reusable-*.yml` | Shared logic |

## Example: PR workflow

```yaml
name: PR
on:
  pull_request:
    branches: [main]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
      - run: bun run lint
      - run: bun test
```

## Checklist

- [ ] Workflows committed to `.github/workflows/`
- [ ] Secrets configured in repository settings
- [ ] Production environment has required reviewers
- [ ] Third-party actions pinned by SHA
- [ ] Caching enabled for dependencies
- [ ] Security scan job fails on CRITICAL/HIGH
