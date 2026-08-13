---
name: redis
description: 'Redis patterns for caching, sessions, distributed locks, rate limiting and lightweight queues. Trigger: When adding cache, session storage, rate limiting, or pub/sub to a backend service.'
version: 1.0
metadata:
  phase:
    - construction
  layer:
    - backend
  enforcement: recommended
  depends_on:
    - project-architecture
    - backend-api
  consumed_by:
    - api-resilience
    - authentication
    - real-time
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define how Redis is used across the framework for caching, sessions, rate limiting, distributed locks, and lightweight message queues.

## When to use this skill

Activate when:
- Adding cache to FastAPI or Bun backend
- Storing session tokens or refresh tokens
- Implementing rate limiting
- Using distributed locks or job queues

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `api-resilience` | consumer | Rate limiting and circuit breaker state |
| `authentication` | consumer | Session and refresh token storage |
| `real-time` | consumer | Pub/sub for live updates |
| `bun-backend` | consumer | Bun backend cache layer |

## Critical Rules

1. Use Redis as **cache/session/auxiliary store**, never as primary database.
2. Set explicit TTLs on every cached key.
3. Use key prefixes per tenant/module: `{tenant}:{module}:{key}`.
4. Serialize values as JSON unless binary is required.
5. Handle Redis failures gracefully (degrade, don't crash).
6. Use `ioredis` (Node/Bun) or `redis-py` (Python).

## Common patterns

| Pattern | Key convention | TTL |
|---------|---------------|-----|
| Cache | `cache:{module}:{id}` | 300s |
| Session | `session:{user_id}` | 3600s |
| Rate limit | `ratelimit:{client_id}` | 60s |
| Lock | `lock:{resource}` | 30s |
| Queue | `queue:{name}` | none |

## Outputs produced

| Artifact | Path | Description |
|----------|------|-------------|
| Cache service | `src/shared/cache.py` / `cache.ts` | Redis client wrapper |
| Rate limiter | `src/shared/rate_limiter.*` | Sliding window implementation |
| Config | `.env.example` | `REDIS_URL` |

## Examples

### Python (FastAPI)

```python
from redis.asyncio import Redis
redis = Redis.from_url(os.getenv("REDIS_URL"))

async def get_cached_user(user_id: int):
    key = f"cache:users:{user_id}"
    data = await redis.get(key)
    if data:
        return json.loads(data)
    user = await db.get_user(user_id)
    await redis.setex(key, 300, json.dumps(user))
    return user
```

### Bun (TypeScript)

```typescript
import Redis from 'ioredis';
const redis = new Redis(process.env.REDIS_URL!);

export async function getCachedUser(userId: number) {
  const key = `cache:users:${userId}`;
  const data = await redis.get(key);
  if (data) return JSON.parse(data);
  const user = await db.getUser(userId);
  await redis.setex(key, 300, JSON.stringify(user));
  return user;
}
```

## Checklist

- [ ] Redis URL configured via environment
- [ ] Key prefixes include tenant/module
- [ ] TTLs defined for all cache keys
- [ ] Graceful degradation on Redis failure
- [ ] Tests use fake Redis or Testcontainers
