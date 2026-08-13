---
name: oauth2-jwt
description: 'OAuth2/JWT authentication and authorization: token issuance, validation, scopes, refresh tokens, and Keycloak integration patterns. Trigger: When implementing token-based auth, OAuth2 flows, or JWT validation in FastAPI/Bun/React/Angular.'
version: 1.1
metadata:
  phase:
    - construction
  layer:
    - backend
    - frontend
  enforcement: recommended
  depends_on:
    - authentication
    - security
  consumed_by:
    - keycloak
    - authorization
  agent_roles:
  - delivery-agent
  validation_profile: security
  mcp_usage: context7
---

## Purpose

Define how OAuth2/JWT is implemented across FastAPI, Bun, and React/Angular services, including token validation, scopes, refresh flows, and secure storage.

## When to use this skill

Activate when:
- Implementing custom OAuth2/JWT auth without Keycloak
- Integrating with an external IdP via OAuth2
- Need to validate JWTs in backend and decode claims in frontend

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `authentication` | parent | Patrones generales de auth (login, sesiones, BFF); oauth2-jwt cubre el JWT custom sin IdP |
| `authorization` | consumer | RBAC from JWT claims |
| `keycloak` | sibling | IdP-specific integration (Keycloak es el IdP recomendado del framework) |
| `security` | cross-cutting | OWASP controls |

## Critical Rules

1. Use RS256 with asymmetric keys; never use HS256 in distributed systems.
2. Validate `iss`, `aud`, `exp`, `nbf` on every token.
3. Store refresh tokens securely (httpOnly cookie or secure storage).
4. Use short-lived access tokens (5-15 min) and long-lived refresh tokens (days).
5. Never decode JWTs in frontend for security decisions; backend must validate.
6. Scope format: `{resource}:{action}` (e.g., `users:read`).

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Token service | `src/shared/auth/token.py` / `token.ts` | Issue/validate JWTs |
| Middleware | `src/shared/auth/jwt_middleware.*` | Protect routes |
| Fetch wrapper | `src/core/api/fetch-client.ts` | Attach tokens |
| Guard | `src/core/auth/RequireAuth.tsx` | Route protection |

## Example: FastAPI dependency

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def require_user(token: str = Depends(oauth2_scheme)):
    payload = decode_and_validate(token)
    return payload["sub"]
```

## Checklist

- [ ] Asymmetric keys (RS256) configured
- [ ] Token validation includes iss/aud/exp
- [ ] Refresh tokens stored securely
- [ ] Scopes defined per resource/action
- [ ] Frontend does not make auth decisions from decoded JWT
- [ ] Logout invalidates refresh tokens
