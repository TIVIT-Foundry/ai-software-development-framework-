---
name: performance
description: 'Performance patterns: pagination, caching, query optimization, large
  data handling. Covers backend (Python/FastAPI, Bun) and frontend (React). Trigger:
  When implementing pagination, caching, query optimization, or large data handling.'
version: 2.1
metadata:
  phase:
  - construction
  layer:
  - database
  - backend
  - frontend
  enforcement: recommended
  depends_on:
  - database-modeling
  - backend-api
  consumed_by:
  - agent-backend
  - agent-fullstack
  agent_roles:
  - design-agent
  - control-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Tabla de contenidos

- Critical Rules
- Pagination API Response
- Frontend Pagination (React + @tanstack/react-query)
- Frontend Pagination (Angular Signals + HttpClient)
- Query Optimization (PostgreSQL)
- Caching Strategy
- Caching Implementation
- Frontend Caching (React)
- Frontend Caching (Angular)
- Large Data Handling
- Database Indexing (PostgreSQL)
- pgvector Optimization
- Response Compression
- CDN Caching Headers
- React Performance Patterns
- Angular Performance Patterns
- Core Web Vitals
- SLOs, Latency Targets & Throughput Benchmarks

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Always paginate list endpoints | ALWAYS | Prevent memory issues |
| Use `SELECT` only needed columns | ALWAYS | Reduce data transfer |
| Index foreign keys and search columns | ALWAYS | Query performance |
| Cache reference data, not transactional | ALWAYS | Stale data risk |
| Never return unbounded lists | NEVER | Memory / network overload |
| Run `EXPLAIN ANALYZE` before deploying new queries | ALWAYS | Catch sequential scans early |
| Use connection pooling (PgBouncer) in production | ALWAYS | Prevent connection exhaustion |

## Pagination API Response
```json
{
  "success": true,
  "data": { "items": [...] },
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalRecords": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

## Frontend Pagination (React + @tanstack/react-query)
```typescript
// hook-based state, refetches automatically when page/filters change
export function useEntityList() {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<Filters>({});

  const query = useQuery({
    queryKey: ['entities', page, filters],
    queryFn: () => apiFetch<PaginatedResponse<Entity>>(`/api/entities?${buildQuery({ page, ...filters })}`),
  });

  return { ...query, page, setPage, filters, setFilters };
}
```

## Frontend Pagination (Angular Signals + HttpClient)
```typescript
// signal-based state with Angular signals
@Component({ ... })
export class EntityListComponent {
  private http = inject(HttpClient);
  page = signal(1);
  filters = signal<Filters>({});

  entities = toSignal(
    toObservable(computed(() => ({ page: this.page(), filters: this.filters() }))).pipe(
      switchMap(({ page, filters }) =>
        this.http.get<PaginatedResponse<Entity>>('/api/entities', { params: { page, ...filters } })
      )
    ),
    { initialValue: { data: { items: [] }, pagination: null } }
  );
}
```

## Query Optimization (PostgreSQL)

```sql
-- EXPLAIN ANALYZE to profile queries before deploying
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT id, name, status FROM core.entity WHERE status = 'active' AND created_at > NOW() - INTERVAL '30 days';

-- EXISTS instead of COUNT for existence check
SELECT EXISTS (SELECT 1 FROM core.entity WHERE id = $1 AND record_status = 'A');

-- LIMIT 1 for single-row check
SELECT id FROM core.entity WHERE name = $1 LIMIT 1;

-- Partial index for filtered queries (PostgreSQL native)
CREATE INDEX idx_entity_active ON core.entity (created_at)
WHERE record_status = 'A';

-- Covering index (INCLUDE) to avoid heap lookups
CREATE INDEX idx_entity_search ON core.entity (name)
INCLUDE (status, email, created_at);

-- NEVER: SELECT *
-- NEVER: Unbounded query without WHERE
```

### pg_stat_statements — Query Monitoring

Enable in `postgresql.conf`:
```ini
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

```sql
-- Top 10 slowest queries by total time
SELECT
  queryid,
  calls,
  ROUND(total_exec_time::numeric, 2) AS total_ms,
  ROUND(mean_exec_time::numeric, 2) AS avg_ms,
  ROUND(stddev_exec_time::numeric, 2) AS stddev_ms,
  rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Queries with highest cache miss ratio
SELECT queryid, calls, shared_blks_hit, shared_blks_read,
       ROUND(shared_blks_hit::numeric / NULLIF(shared_blks_hit + shared_blks_read, 0) * 100, 2) AS cache_hit_pct
FROM pg_stat_statements
WHERE calls > 100
ORDER BY shared_blks_read DESC
LIMIT 10;
```

### VACUUM Tuning

```ini
# postgresql.conf — autovacuum tuning for high-write tables
autovacuum_vacuum_scale_factor = 0.05    # default 0.2 — vacuum after 5% of tuples changed
autovacuum_analyze_scale_factor = 0.02   # default 0.1 — analyze after 2% changed
autovacuum_vacuum_cost_delay = 2ms       # default 2ms — reduce for aggressive vacuuming
autovacuum_max_workers = 6               # default 3 — scale with CPU cores
```

```sql
-- Per-table autovacuum tuning for high-churn tables
ALTER TABLE core.entity SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_analyze_scale_factor = 0.005,
  autovacuum_vacuum_cost_delay = 0
);

-- Check bloat and dead tuples
SELECT schemaname, relname, n_live_tup, n_dead_tup,
       ROUND(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 2) AS dead_pct,
       last_vacuum, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### Connection Pooling — PgBouncer

```ini
# pgbouncer.ini
[databases]
myapp = host=127.0.0.1 port=5432 dbname=myapp

[pgbouncer]
pool_mode = transaction          # recommended for FastAPI/async
default_pool_size = 20
max_client_conn = 1000
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 5
server_idle_timeout = 300
client_idle_timeout = 0
```

```python
# FastAPI — async SQLAlchemy with PgBouncer
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:6432/myapp"  # PgBouncer port

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # match PgBouncer default_pool_size
    max_overflow=5,
    pool_timeout=10,
    pool_recycle=300,
    pool_pre_ping=True,     # detect stale connections
)
```

## Caching Strategy

| Cache | TTL | Use for |
|-------|-----|---------|
| Reference data | 1 hour | Status lists, categories |
| User permissions | 5 min | Role/permission data |
| Configuration | 10 min | Feature flags |
| Session data | 15 min | User preferences |
| **NO cache** | — | Transactional data |

## Caching Implementation

### Python/FastAPI — Redis Cache-Aside

```python
from redis.asyncio import Redis
import json

redis = Redis(host="localhost", port=6379, decode_responses=True)

async def get_reference_data() -> list[dict]:
    cache_key = "reference:status-list"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    data = await db.fetch_all("SELECT id, name FROM core.status ORDER BY sort_order")
    await redis.setex(cache_key, 3600, json.dumps(data))  # 1 hour TTL
    return data
```

### Python/FastAPI — In-Memory LRU Cache (non-async, single-worker)

```python
from functools import lru_cache
import time

@lru_cache(maxsize=256)
def get_config_snapshot(config_key: str) -> dict:
    """Cached in-process — acceptable for config that changes rarely."""
    return db.fetch_one("SELECT * FROM core.config WHERE key = $1", config_key)

# TTL-aware variant
_config_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 600  # 10 min

async def get_config(key: str) -> dict:
    if key in _config_cache:
        ts, data = _config_cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
    data = await db.fetch_one("SELECT * FROM core.config WHERE key = $1", key)
    _config_cache[key] = (time.time(), data)
    return data
```

### Bun — Redis Cache-Aside

```typescript
import { Redis } from "ioredis";

const redis = new Redis({ host: "localhost", port: 6379 });

export async function getEntity(id: number): Promise<Entity | null> {
  const cacheKey = `entity:${id}`;
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const entity = await db.query("SELECT * FROM core.entity WHERE id = $1", [id]);
  if (!entity) return null;

  await redis.setex(cacheKey, 600, JSON.stringify(entity)); // 10 min
  return entity;
}

// Invalidation on update
export async function updateEntity(id: number, data: Partial<Entity>): Promise<void> {
  await db.query("UPDATE core.entity SET ... WHERE id = $1", [id]);
  await redis.del(`entity:${id}`);
  // Invalidate list caches
  const keys = await redis.keys("entities:list:*");
  if (keys.length) await redis.del(...keys);
}
```

### Cache Invalidation Strategies

| Strategy | When to use | Example |
|----------|-------------|---------|
| **TTL-based** | Predictable change frequency | Session → 15 min, Catalog → 1h |
| **Write-through** | Critical data that cannot be stale | Update cache atomically with DB |
| **Write-behind** | High write throughput, tolerance for inconsistency | Buffer writes, periodic flush |
| **Explicit invalidation** | Event-driven changes | Invalidate on UPDATE/DELETE |

## Frontend Caching (React)

```typescript
// @tanstack/react-query caches by queryKey natively — no custom interceptor needed
export function useStatusList() {
  return useQuery({
    queryKey: ['catalogs', 'status'],
    queryFn: () => apiFetch<Status[]>('/api/catalogs/status'),
    staleTime: 5 * 60_000, // reference data: long stale time, 5 min
    gcTime: 30 * 60_000,
  });
}
```

## Frontend Caching (Angular)

```typescript
// Angular HttpClient with response caching interceptor
@Injectable()
export class CachingInterceptor implements HttpInterceptor {
  private cache = new Map<string, { response: HttpResponse<unknown>; timestamp: number }>();

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (req.method !== 'GET') return next.handle(req);

    const cached = this.cache.get(req.urlWithParams);
    if (cached && Date.now() - cached.timestamp < 300_000) { // 5 min
      return of(cached.response.clone());
    }

    return next.handle(req).pipe(
      tap(event => {
        if (event instanceof HttpResponse) {
          this.cache.set(req.urlWithParams, { response: event.clone(), timestamp: Date.now() });
        }
      })
    );
  }
}

// Usage: reference data with long stale time
statusList$ = this.http.get<Status[]>('/api/catalogs/status').pipe(
  shareReplay({ bufferSize: 1, refCount: true })  // cache last emission
);
```

## Large Data Handling
| Scenario | Technique |
|----------|-----------|
| Large exports | Stream / chunked response |
| Long lists in UI | Virtual scrolling (`@tanstack/react-virtual`) |
| Infinite lists | Cursor-based pagination (`useInfiniteQuery`) |
| Heavy computations | Background jobs / queues (BullMQ / Redis) |
| Large file uploads | Chunked upload + presigned URLs (S3) |

## Database Indexing (PostgreSQL)

```sql
-- Index foreign keys used in JOINs
CREATE INDEX idx_{table}_{column} ON core.{table} ({column});

-- Covering index with frequently selected columns
CREATE INDEX idx_entity_list ON core.entity (status, created_at)
INCLUDE (name, email, updated_at);

-- Partial index for filtered queries (PostgreSQL native)
CREATE INDEX idx_entity_active ON core.entity (created_at)
WHERE record_status = 'A';

-- GIN index for full-text search
CREATE INDEX idx_entity_search_fts ON core.entity
USING GIN (to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- BRIN index for large time-series tables (naturally ordered by time)
CREATE INDEX idx_events_created ON core.events USING BRIN (created_at);

-- Check unused indexes to remove
SELECT schemaname, relname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND schemaname = 'core'
ORDER BY pg_relation_size(indexrelid) DESC;
```

## pgvector Optimization

### Index Selection: IVFFlat vs HNSW

| Property | IVFFlat | HNSW |
|----------|---------|------|
| Build time | Faster | Slower |
| Query latency | Higher | Lower (2-5x faster) |
| Memory usage | Lower | Higher |
| Build requirement | Needs `ANALYZE` first | Works immediately |
| Update cost | Reindex needed periodically | Incremental |
| Recommended for | Write-heavy, large datasets | Read-heavy, latency-sensitive |

```sql
-- IVFFlat index (requires rows to exist first, then ANALYZE)
CREATE INDEX idx_embedding_ivfflat ON core.document
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- lists ≈ sqrt(rows), tune: 100 for ~10k rows, 1000 for ~1M rows

ANALYZE core.document;

-- HNSW index (recommended for most use cases)
CREATE INDEX idx_embedding_hnsw ON core.document
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);  -- m: connections per node, ef_construction: build quality

-- HNSW query-time tuning
SET hnsw.ef_search = 100;  -- default 40, increase for higher recall at cost of latency
```

### Dimension Tuning

| Dimensions | Use case | Trade-off |
|------------|----------|-----------|
| 384 | Fast classification, simple similarity | Lower accuracy, faster |
| 768 | General purpose (most embedding models) | Good balance |
| 1536 | High-accuracy semantic search (OpenAI) | Higher storage + slower |

```sql
-- Optimal HNSW parameters by dimension
-- 384-dim:  m=12, ef_construction=100
-- 768-dim:  m=16, ef_construction=200
-- 1536-dim: m=24, ef_construction=300

-- Storage per 1M vectors
-- 384-dim:  ~1.5 GB (halfvec) / ~3 GB (vector)
-- 768-dim:  ~3 GB (halfvec) / ~6 GB (vector)
-- 1536-dim: ~6 GB (halfvec) / ~12 GB (vector)
```

### Similarity Search Performance

```sql
-- Cosine similarity (most common)
SELECT id, content, 1 - (embedding <=> $1::vector) AS similarity
FROM core.document
WHERE 1 - (embedding <=> $1::vector) > 0.7   -- threshold to reduce scanned rows
ORDER BY embedding <=> $1::vector
LIMIT 10;

-- Use halfvec for 50% storage reduction with negligible accuracy loss
CREATE INDEX idx_embedding_half ON core.document
USING hnsw (embedding halfvec_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- Materialized view for frequently queried embedding clusters
CREATE MATERIALIZED VIEW doc_cluster_centroids AS
SELECT cluster_id, AVG(embedding)::vector AS centroid
FROM core.document
GROUP BY cluster_id;
```

## Response Compression

### Python/FastAPI — GzipMiddleware

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=500)  # compress responses > 500 bytes
```

### Bun — Compression Middleware

```typescript
import { compress } from "hono/compress";

app.use("*", compress());
```

## CDN Caching Headers

```
Cache-Control: public, max-age=3600, s-maxage=86400, stale-while-revalidate=300
ETag: "abc123"
Vary: Accept-Encoding
```

| Directive | Meaning |
|-----------|---------|
| `public` | Can be cached by CDN/proxy |
| `max-age=3600` | Browser caches 1h |
| `s-maxage=86400` | CDN caches 24h (overrides max-age for CDN) |
| `stale-while-revalidate=300` | Serve stale while refreshing in background |
| `no-cache` | Revalidate before using cache |
| `no-store` | Never cache |

```python
# FastAPI — CDN headers middleware
from starlette.middleware.base import BaseHTTPMiddleware

class CDNCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        path = request.url.path

        if path.startswith("/api/catalogs"):
            response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400, stale-while-revalidate=300"
            response.headers["ETag"] = compute_etag(response.body)
        elif path.startswith("/api/entities"):
            response.headers["Cache-Control"] = "no-cache"
        return response
```

### HTTP Caching Headers Reference

| Header | Direction | Purpose |
|--------|-----------|---------|
| `Cache-Control` | Response | Cache directives (max-age, no-cache, etc.) |
| `ETag` | Response | Content hash for validation |
| `Last-Modified` | Response | Last modification date |
| `If-None-Match` | Request | Sends previous ETag → 304 if unchanged |
| `If-Modified-Since` | Request | Sends previous date → 304 if unchanged |

## React Performance Patterns

### React.memo + Deliberate Memoization

```tsx
// React.memo skips re-render when props are referentially equal
export const EntityDetail = React.memo(function EntityDetail({ entity, loading }: EntityDetailProps) {
  if (loading) return <Skeleton />;
  if (!entity) return null;

  return (
    <>
      <h2>{entity.name}</h2>
      <p>{entity.description}</p>
    </>
  );
});
```

### Derived State with useMemo + TanStack Query

```tsx
// Derived state recomputed only when its dependencies change
export function Dashboard() {
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());

  const { data: filteredEntities = [] } = useQuery({
    queryKey: ['entities', startDate, endDate],
    queryFn: () => apiFetch<Entity[]>(`/api/entities?${buildQuery({ start: startDate, end: endDate })}`),
  });

  const entityCount = useMemo(() => filteredEntities.length, [filteredEntities]);
  const hasResults = entityCount > 0;

  // ...
}
```

### Code-Splitting with React.lazy

```tsx
// router.tsx — lightweight code-splitting per route
import { lazy } from 'react';

const DashboardPage = lazy(() => import('./features/dashboard/DashboardPage'));
const EntityListPage = lazy(() => import('./features/entities/EntityListPage'));
const ReportsRoutes = lazy(() => import('./features/reports/reports.routes'));

const router = createBrowserRouter([
  { path: 'dashboard', element: withSuspense(<DashboardPage />) },
  { path: 'entities', element: withSuspense(<EntityListPage />) },
  { path: 'reports/*', element: withSuspense(<ReportsRoutes />) }, // lazy-loaded child routes
]);
```

### Zustand — Selectors & Memoization

```typescript
// Selectors re-render the component only when the selected slice changes
interface EntityState {
  items: Entity[];
}

export const useEntityStore = create<EntityState>(() => ({ items: [] }));

// Memoized derived selector (recomputes only when `items` reference changes)
const selectVisibleEntities = (state: EntityState) => state.items.filter((e) => e.status === 'active');
const selectEntityCount = (state: EntityState) => selectVisibleEntities(state).length;
```

```tsx
// Component — selecting a slice avoids re-rendering on unrelated store changes
export function EntityContainer() {
  const entities = useEntityStore(useShallow(selectVisibleEntities));
  const count = useEntityStore(selectEntityCount);

  return (
    <>
      <EntityList items={entities} />
      <span>{count} active</span>
    </>
  );
}
```

| Pattern | Benefit |
|---------|---------|
| `useShallow` selector | No re-render when the selected slice is shallow-equal |
| `React.memo` | Skips re-render when props are referentially equal |
| `@tanstack/react-query` cache | Normalized cache by `queryKey`, no duplicate fetches |
| Zustand slice per feature | Local state for feature components, no boilerplate cleanup |

### Virtual Scrolling with @tanstack/react-virtual

```tsx
import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

export function EntityList({ items }: { items: Entity[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
  });

  return (
    <div ref={parentRef} className="viewport" style={{ height: 600, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={items[virtualRow.index].id}
            className="list-item"
            style={{ position: 'absolute', top: 0, transform: `translateY(${virtualRow.start}px)`, height: 48 }}
          >
            {items[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Angular Performance Patterns

### OnPush Change Detection

```typescript
// Always use OnPush — reduces change detection cycles dramatically
@Component({
  selector: 'app-entity-detail',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (entity(); as e) {
      <h2>{{ e.name }}</h2>
      <p>{{ e.description }}</p>
    } @else if (loading()) {
      <app-skeleton />
    }
  `,
})
export class EntityDetailComponent {
  entity = input.required<Entity | null>();
  loading = input(false);
}
```

### Angular Signals

```typescript
// Computed signals — automatically derive reactive state
@Component({ ... })
export class DashboardComponent {
  private filterService = inject(FilterService);

  // Derived state — no manual subscription needed
  startDate = signal(new Date());
  endDate = signal(new Date());

  filteredEntities = toSignal(
    toObservable(computed(() => ({ start: this.startDate(), end: this.endDate() }))).pipe(
      switchMap(({ start, end }) =>
        this.http.get<Entity[]>('/api/entities', { params: { start, end } })
      )
    ),
    { initialValue: [] }
  );

  // Computed for derived UI state
  entityCount = computed(() => this.filteredEntities().length);
  hasResults = computed(() => this.entityCount() > 0);
}
```

### Lazy Loading with loadComponent

```typescript
// router.routes.ts — lightweight lazy loading
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component')
      .then(m => m.DashboardComponent),
  },
  {
    path: 'entities',
    loadComponent: () => import('./features/entities/entity-list.component')
      .then(m => m.EntityListComponent),
  },
  {
    path: 'reports',
    loadChildren: () => import('./features/reports/reports.routes')
      .then(m => m.REPORT_ROUTES),  // lazy-loaded child routes
  },
];
```

### NgRx — Selectors & Memoization

```typescript
// Feature state — selectors are memoized by default (no recomputation if inputs unchanged)
import { createFeatureSelector, createSelector } from '@ngrx/store';

export const selectEntityFeature = createFeatureSelector<EntityState>('entities');

export const selectVisibleEntities = createSelector(
  selectEntityFeature,
  (state) => state.items.filter(e => e.status === 'active'),
);

export const selectEntityCount = createSelector(
  selectVisibleEntities,
  (items) => items.length,  // derived selector — recomputes only when visible entities change
);

// Component — OnPush + signals from store = minimal change detection
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (entities(); as list) {
      <app-entity-list [items]="list" />
    }
    <span>{{ count() }} active</span>
  `,
})
export class EntityContainerComponent {
  private store = inject(Store);
  entities = this.store.selectSignal(selectVisibleEntities);  // signal binding
  count = this.store.selectSignal(selectEntityCount);
}

// Entity Cache — avoid refetching already-loaded entities
// @ngrx/entity provides normalized cache + ids array for O(1) lookups
```

| Pattern | Benefit |
|---------|---------|
| Memoized selectors | No recomputation when inputs unchanged |
| `selectSignal()` (NgRx 18+) | Signal-based store reads — OnPush-friendly |
| `@ngrx/entity` | Normalized cache, O(1) by id, no duplicate fetches |
| `@ngrx/component-store` | Local state for feature components, automatic cleanup |

### Virtual Scrolling with CDK

```typescript
import { CdkVirtualScrollViewport } from '@angular/cdk/scrolling';

@Component({
  template: `
    <cdk-virtual-scroll-viewport itemSize="48" class="viewport">
      @for (item of items(); track item.id) {
        <div class="list-item">{{ item.name }}</div>
      }
    </cdk-virtual-scroll-viewport>
  `,
  styles: [`
    .viewport { height: 600px; width: 100%; }
    .list-item { height: 48px; display: flex; align-items: center; }
  `],
})
export class EntityListComponent {
  items = input.required<Entity[]>();
}
```

```html
<!-- For very large lists (10k+), use trackBy for ngFor -->
<cdk-virtual-scroll-viewport itemSize="56" class="entity-list">
  <div *cdkVirtualFor="let entity of entities; trackBy: trackById"
       class="entity-row">
    {{ entity.name }}
  </div>
</cdk-virtual-scroll-viewport>
```

## Core Web Vitals

Core Web Vitals are user experience metrics defined by Google. They determine SEO ranking and speed perception.

| Metric | What it measures | Target | Poor threshold |
|--------|------------------|--------|----------------|
| **LCP** (Largest Contentful Paint) | Time until largest content is visible | ≤ 2.5s | > 4.0s |
| **INP** (Interaction to Next Paint) | Interaction latency (replaces FID) | ≤ 200ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | Visual stability (elements jumping) | ≤ 0.1 | > 0.25 |

### LCP — Optimization (React)

```tsx
// 1. Preload critical resources in index.html
// <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin />
// <link rel="preload" href="/hero.webp" as="image" />

// 2. Native loading="lazy"/fetchpriority for below-fold vs. hero images
<img src={heroImage} loading="eager" fetchPriority="high" alt="Hero" />
<img src={item.image} loading="lazy" alt="Item" />

// 3. Inline critical CSS, defer non-critical
// vite.config.ts → build.cssCodeSplit / rollup manualChunks to control bundle size

// 4. Explicit width/height (or aspect-ratio) prevents layout jank while the LCP image loads
<img src={heroImage} width={1200} height={600} fetchPriority="high" alt="Hero" />
```

### LCP — Optimization (Angular)

```typescript
// 1. Preload critical resources in index.html
// <link rel="preload" href="/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin />
// <link rel="preload" href="/hero.webp" as="image" />

// 2. Use ngLazyLoadImage or native loading="lazy" for below-fold images
<img [src]="heroImage()" loading="eager" fetchpriority="high" alt="Hero" />
<img [src]="item.image" loading="lazy" alt="Item" />

// 3. Inline critical CSS, defer non-critical
// angular.json → budgets: increase initial bundle warning to 500kb

// 4. Use Angular's built-in image optimization with NgOptimizedImage
import { NgOptimizedImage } from '@angular/common';

@Component({
  imports: [NgOptimizedImage],
  template: `<img [ngSrc]="heroImage()" width="1200" height="600" priority />`
})
```

### INP — Optimization (React)

```tsx
// 1. React 18+ automatic batching = fewer renders per interaction by default

// 2. useTransition marks non-urgent updates as low priority — keeps input responsive
function FilterPanel() {
  const [filter, setFilter] = useState('');
  const [isPending, startTransition] = useTransition();

  const onFilterChange = (value: string) => {
    setFilter(value); // urgent: input stays responsive

    startTransition(() => {
      // Non-urgent: heavy filtering/analytics deferred without blocking typing
      analytics.trackFilterChange(value);
    });
  };

  return <input value={filter} onChange={(e) => onFilterChange(e.target.value)} />;
}

// 3. Web Workers for CPU-intensive tasks
const worker = new Worker(new URL('./filter.worker', import.meta.url));
worker.postMessage({ items, filter });
worker.onmessage = (e) => setFilteredResults(e.data);
```

### INP — Optimization (Angular)

```typescript
// 1. Unzone.js or Zoneless change detection for instant feedback
// Angular 19+: use provideExperimentalZonelessChangeDetection()

// 2. OnPush + signals = automatic INP optimization
// No zone.js overhead, no unnecessary change detection

// 3. Defer heavy computation
@Component({ ... })
export class FilterComponent {
  private zone = inject(NgZone);

  onFilterChange(value: string) {
    // Zoneless: signals update UI immediately
    this.filter.set(value);

    // Heavy computation off the main thread
    this.zone.runOutsideAngular(() => {
      requestIdleCallback(() => {
        this.analytics.trackFilterChange(value);
      });
    });
  }
}

// 4. Web Workers for CPU-intensive tasks
const worker = new Worker(new URL('./filter.worker', import.meta.url));
worker.postMessage({ items, filter });
worker.onmessage = (e) => this.filteredResults.set(e.data);
```

### CLS — Optimization (React)

```tsx
// 1. Reserve space for images (aspect-ratio or fixed dimensions)
function ProductImage({ imageUrl }: { imageUrl: string | null }) {
  return (
    <div className="image-container">
      {imageUrl ? <img src={imageUrl} alt="Product" /> : <div className="skeleton" />}
    </div>
  );
}
```

```css
.image-container { aspect-ratio: 16 / 9; width: 100%; overflow: hidden; }
.skeleton { width: 100%; height: 100%; background: #e5e7eb; }

/* 2. Font loading: font-display: swap */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-display: swap;
}

/* 3. Avoid layout shifts from async data */
.skeleton-pulse {
  width: 100%;
  height: 48px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  animation: skeleton-loading 1.5s infinite;
}
```

```tsx
// 4. Reserve final dimensions before animating — never animate width/height
//    on elements that change box size during initial render.
function StablePanel({ data }: { data: Data | null }) {
  return (
    <div className="panel" style={{ height: 200 }}> {/* CSS reserves space — animation is cosmetic */}
      {data ? (
        <div className="panel-content panel-content--enter">
          <Content data={data} />
        </div>
      ) : (
        <div className="skeleton" />
      )}
    </div>
  );
}
```

```css
/* Animate opacity/transform only — height is already fixed by .panel */
.panel-content--enter {
  animation: fade-in 200ms ease-out;
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### CLS — Optimization (Angular)

```typescript
// 1. Reserve space for images (aspect-ratio or fixed dimensions)
@Component({
  template: `
    <div class="image-container">
      @if (imageUrl(); as url) {
        <img [src]="url" alt="Product" />
      } @else {
        <div class="skeleton"></div>
      }
    </div>
  `,
  styles: [`
    .image-container { aspect-ratio: 16 / 9; width: 100%; overflow: hidden; }
    .skeleton { width: 100%; height: 100%; background: #e5e7eb; }
  `],
})
```

```css
/* 2. Font loading: font-display: swap */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-display: swap;
}

/* 3. Avoid layout shifts from async data */
.skeleton {
  width: 100%;
  height: 48px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  animation: skeleton-loading 1.5s infinite;
}
```

```typescript
// 4. Angular animations — prevent CLS by reserving final dimensions
//    Use animations on stable containers (after layout settled), never on
//    elements that change box size during initial render.
import { trigger, transition, style, animate } from '@angular/animations';

@Component({
  animations: [
    trigger('panel', [
      // Fixed height in :enter — no layout shift when content arrives
      transition(':enter', [
        style({ opacity: 0, height: '200px' }),  // reserve height upfront
        animate('200ms ease-out', style({ opacity: 1, height: '200px' })),
      ]),
      // Avoid animating width/height on data-bound elements — that causes CLS.
      // Animate opacity/transform only after the element has its final size.
    ]),
  ],
  template: `
    <div @panel class="panel">
      @if (data(); as d) { <app-content [data]="d" /> }
      @else { <div class="skeleton"></div> }
    </div>
  `,
  styles: [`.panel { height: 200px; }`],  // CSS reserves space — animation is cosmetic
})
export class StablePanelComponent {
  data = input<Data | null>(null);
}
```

### Measurement

```typescript
// Install web-vitals: npm install web-vitals
import { onLCP, onINP, onCLS, type Metric } from 'web-vitals';

function reportMetric(name: string, metric: Metric) {
  fetch('/api/vitals', {
    method: 'POST',
    body: JSON.stringify({
      name,
      value: metric.value,
      rating: metric.rating,
      id: metric.id,
    }),
    headers: { 'Content-Type': 'application/json' },
    // Use navigator.sendBeacon for reliability
  });
}

onLCP((metric) => reportMetric('LCP', metric));
onINP((metric) => reportMetric('INP', metric));
onCLS((metric) => reportMetric('CLS', metric));
```

## SLOs, Latency Targets & Throughput Benchmarks

### Backend SLOs

| Metric | Target | Measurement |
|--------|--------|-------------|
| API p50 latency | ≤ 100ms | APM (Prometheus + Grafana) |
| API p95 latency | ≤ 300ms | APM |
| API p99 latency | ≤ 500ms | APM |
| Error rate | ≤ 0.1% | HTTP 5xx / total requests |
| Throughput | ≥ 500 req/s per instance | Load testing (k6) |
| DB query p95 | ≤ 50ms | pg_stat_statements |
| Cache hit ratio | ≥ 90% | Redis INFO stats |
| Connection pool utilization | ≤ 80% | PgBouncer SHOW POOLS |

### Frontend SLOs

| Metric | Target | Tool |
|--------|--------|------|
| LCP | ≤ 2.5s | web-vitals, Lighthouse |
| INP | ≤ 200ms | web-vitals |
| CLS | ≤ 0.1 | web-vitals |
| First Contentful Paint (FCP) | ≤ 1.8s | Lighthouse |
| Total Blocking Time (TBT) | ≤ 200ms | Lighthouse |
| Bundle size (initial) | ≤ 500 KB | `vite-bundle-visualizer` / `rollup-plugin-visualizer` |
| Time to Interactive (TTI) | ≤ 3.5s | Lighthouse |

### Database SLOs

| Metric | Target | How to measure |
|--------|--------|----------------|
| Connection wait time | ≤ 10ms | PgBouncer SHOW POOLS |
| Dead tuple ratio | ≤ 5% | pg_stat_user_tables |
| Cache hit ratio (shared_buffers) | ≥ 99% | pg_stat_database |
| Index scan ratio | ≥ 95% | pg_stat_user_indexes |
| Vacuum lag | ≤ 1 hour | pg_stat_user_tables |

### Load Testing Thresholds (k6)

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  thresholds: {
    http_req_duration: [
      'p(50)<100',   // 50% of requests under 100ms
      'p(95)<300',   // 95% of requests under 300ms
      'p(99)<500',   // 99% of requests under 500ms
    ],
    http_req_failed: ['rate<0.01'],  // <1% error rate
    http_reqs: ['rate>500'],         // >500 req/s throughput
  },
};
```
