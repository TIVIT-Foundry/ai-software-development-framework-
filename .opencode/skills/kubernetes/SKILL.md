---
name: kubernetes
description: 'Kubernetes deployment patterns: manifests, Helm charts, namespaces, ConfigMaps, Secrets, HPA, probes, and multi-tenant isolation. Trigger: When deploying services to Kubernetes, creating manifests, or designing namespaces per tenant.'
version: 1.1
metadata:
  phase:
    - operations
  layer:
    - infrastructure
  enforcement: recommended
  depends_on:
    - framework-platform
    - docker-local
  consumed_by:
    - terraform
    - ci-cd
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how services are packaged and deployed to Kubernetes in the framework, including manifests, Helm charts, namespace isolation, secrets management, and autoscaling.

## When to use this skill

Activate when:
- Deploying FastAPI, Bun, or React/Angular services to Kubernetes
- Designing namespace strategy per tenant/environment
- Adding HPA, PDBs, or network policies

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `framework-platform` | input | Platform decisions |
| `docker-local` | input | Local containers to promote to K8s |
| `terraform` | consumer | Provisions the cluster |
| `ci-cd` | consumer | Deploys manifests |

## Critical Rules

1. Use **namespaces per environment/tenant**: `{project}-{env}`.
2. Store Secrets in external secret operators (Vault, AWS Secrets Manager) or sealed secrets.
3. Define readiness and liveness probes on every workload.
4. Set resource requests and limits for CPU/memory.
5. Use HPA for horizontal scaling; VPA cautiously.
6. Apply NetworkPolicies for namespace isolation.
7. Use Helm for reusable charts; raw manifests only for simple cases.

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Deployment | `k8s/{service}/deployment.yaml` | Workload spec |
| Service | `k8s/{service}/service.yaml` | ClusterIP/LoadBalancer |
| ConfigMap | `k8s/{service}/configmap.yaml` | Non-sensitive config |
| Secret | `k8s/{service}/secret.yaml` | Sensitive data |
| HPA | `k8s/{service}/hpa.yaml` | Autoscaling |
| Helm chart | `helm/{service}/` | Reusable package |

## Example: Deployment snippet

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-fastapi
  namespace: foundry-prod
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: api
          image: registry/api-fastapi:v1.2.0
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: api-config
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
```

## Checklist

- [ ] Namespace created per env/tenant
- [ ] Probes configured
- [ ] Resource requests/limits set
- [ ] HPA enabled for stateless services
- [ ] Secrets not committed in plain text
- [ ] NetworkPolicies applied for sensitive workloads
