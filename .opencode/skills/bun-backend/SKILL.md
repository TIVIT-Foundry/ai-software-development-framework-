---
name: bun-backend
description: 'Backend general con Bun (TypeScript): estructura de proyecto, routing, validación, DI, tests y operación. Trigger: When implementing a Bun/TypeScript backend service, API module, or vertical slice.'
version: 1.1
metadata:
  phase:
    - construction
  layer:
    - backend
  enforcement: recommended
  depends_on:
    - project-architecture
    - api-first-spec
  consumed_by:
    - api-first-backend
    - agent-backend
    - agent-fullstack
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define the architecture and conventions for backend services built with Bun and TypeScript in the framework. Covers project structure, HTTP routing, validation, dependency injection, testing, and local development.

## When to use this skill

Activate when:
- A new backend module is implemented with Bun/TypeScript
- A FastAPI module needs a Bun counterpart or shared contract
- The project declares Bun as the general backend runtime

Do not use when:
- The backend is exclusively Python/FastAPI (use `api-first-backend` instead)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `api-first-spec` | input | Receives OpenAPI/spec contract |
| `api-first-backend` | sibling | Python implementation of the same contract |
| `typescript` | depends_on | TypeScript strict patterns |
| `error-handling` | cross-cutting | Unified error envelope |
| `shared-libs` | cross-cutting | Common middleware and response wrappers |

## Critical Rules

1. Use **Bun 1.1+** as runtime and package manager (`bun.lockb`; Bun 1.2+ usa `bun.lock`).
2. Follow **Vertical Slice** architecture: `features/{module}/{route,service,schema,test}.ts`.
3. Use **Zod** for input validation and type inference.
4. Use **Elysia** or **Hono** as HTTP framework; document the choice in the module README.
5. All responses must follow the framework envelope: `{success, data, error, meta}`.
6. Secrets must be loaded from environment variables via `zod`-validated config.
7. Write tests with **Bun Test** runner; coverage ≥ 70%.

## Project structure

```
backend-bun/
├── src/
│   ├── config/              # env validation, constants
│   ├── shared/              # middleware, response wrapper, errors
│   ├── features/
│   │   └── {module}/
│   │       ├── routes.ts
│   │       ├── service.ts
│   │       ├── schemas.ts
│   │       └── *.test.ts
│   └── index.ts
├── tests/
│   └── integration/
├── package.json
├── tsconfig.json
└── README.md
```

## What the agent must do

1. Read the module spec from `api-first-spec`.
2. Scaffold the vertical slice under `features/{module}/`.
3. Implement Zod schemas in `schemas.ts`.
4. Implement business logic in `service.ts` (no HTTP in this layer).
5. Implement routes in `routes.ts` using the chosen framework.
6. Wire shared error handling and request logging.
7. Add `*.test.ts` with Bun Test.
8. Add `README.md` with run/test commands.

## Configuration

| Variable | Required | Example |
|----------|----------|---------|
| `PORT` | Yes | `3000` |
| `DATABASE_URL` | Yes | `postgresql://...` |
| `LOG_LEVEL` | No | `info` |

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Routes | `src/features/{module}/routes.ts` | HTTP endpoints |
| Service | `src/features/{module}/service.ts` | Business logic |
| Schemas | `src/features/{module}/schemas.ts` | Zod DTOs |
| Tests | `src/features/{module}/*.test.ts` | Unit tests |

## Examples

See `assets/templates/` for starter templates.

## Checklist

- [ ] Bun project initialized with `bun init`
- [ ] Vertical slice folder created per module
- [ ] Zod schemas validated against spec
- [ ] Routes return framework envelope
- [ ] Errors mapped to framework error codes
- [ ] Tests pass with `bun test`
