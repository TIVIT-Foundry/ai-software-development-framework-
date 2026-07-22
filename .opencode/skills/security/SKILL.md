---
name: security
description: 'Security patterns for applications: input validation, authorization,
  CORS, SQL injection prevention, XSS, CSP. Covers OWASP Top 10 controls for
  React, Bun, Keycloak, and Python FastAPI. Trigger: When implementing
  validation, authorization, CORS, security headers, or securing APIs and UI.'
version: 2.0
metadata:
  phase:
  - construction
  layer:
  - backend
  - frontend
  enforcement: mandatory
  depends_on: []
  consumed_by:
  - authentication
  - authorization
  - database-security
  - backend-api
  - react
  agent_roles:
  - control-agent
  - design-agent
  validation_profile: security-review
mcp_usage: none
---

## Stack de referencia de esta skill

| Capa | Tecnologías |
|------|-------------|
| Frontend | React (18+, Vite) |
| Backend | Bun (TypeScript) |
| Auth | Keycloak (OAuth2/OIDC) |
| Backend API | Python FastAPI |
| Validación | Zod (Bun), Pydantic (FastAPI) |
| DB | PostgreSQL (parameterized queries) |

## Critical Rules

| Rule | Type | Rationale |
|------|------|-----------|
| Use parameterized queries always | ALWAYS | SQL injection prevention |
| Validate on backend, not just frontend | ALWAYS | Frontend can be bypassed |
| Use centralized authorization checks | ALWAYS | No scattered permission logic |
| Sanitize user-generated content on display | ALWAYS | XSS prevention |
| Never log sensitive data (passwords, tokens, PII) | NEVER | Data breach risk |
| Never expose stack traces in API responses | NEVER | Information disclosure |
| Use HTTPS everywhere | ALWAYS | Transport security |
| Set security headers (CSP, HSTS, X-Frame-Options) | ALWAYS | Defense in depth |
| JWT tokens must have short expiry + refresh rotation | ALWAYS | Token theft mitigation |
| Never store tokens in localStorage | NEVER | XSS can steal tokens |

---

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `authentication` | Complementaria | Security se enfoca en protección de la aplicación (CORS, CSP, input validation, headers). Authentication maneja el proceso de login y verificación de identidad con Keycloak. |
| `authorization` | Complementaria | Security define las defensas perimetrales. Authorization maneja RBAC, permisos y control de acceso granular. |
| `framework-security` | Predecesora | Governance de seguridad del framework. Security implementa los patrones que framework-security define. |

## When to use this skill

Activate this skill when:
- Implementing CORS configuration, CSP headers, or security headers
- Setting up input validation (Zod, Pydantic) for API endpoints
- Preventing SQL injection, XSS, or command injection
- Configuring rate limiting
- Implementing audit logging for security events
- Managing secrets (environment variables, vault integration)
- Auditing OWASP Top 10 compliance across the stack

Do not activate when:
- Implementing login/logout flows → use `authentication`
- Setting up roles or permissions → use `authorization`
- Designing governance-level security policies → use `framework-security`

## 1. SQL Injection Prevention

Parameterized queries prevent SQL injection across all stacks:

```python
# Python SQLAlchemy — parameterized
result = await db.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})

# NEVER f-string in SQL
result = await db.execute(text(f"SELECT * FROM users WHERE id = {user_id}"))
```

```typescript
// Bun — node-postgres / $1 placeholder
const result = await pool.query(
  'SELECT * FROM users WHERE email = $1 AND status = $2',
  [email, 1]
);

// PELIGRO: template strings
const result = await pool.query(`SELECT * FROM users WHERE email = '${email}'`);
```

---

## 2. Input Validation

| Layer | Tool | Error Format |
|-------|------|--------------|
| Backend (Bun) | Zod | `{ code: "VAL_001", path: ["field"], message: "..." }` |
| Backend (Python) | Pydantic | Pydantic validation error |
| Frontend (React) | react-hook-form + Zod | Inline form field error |

### Bun — Zod validation middleware

```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).regex(/^[a-zA-ZÀ-ÿ\s]+$/),
  password: z.string().min(8).max(128),
});

// Middleware de validación
function validate(schema: z.ZodSchema) {
  return async (req: Request): Promise<Response | void> => {
    const result = await schema.safeParseAsync(await req.json());
    if (!result.success) {
      return new Response(JSON.stringify({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          details: result.error.issues.map(i => ({
            path: i.path.join('.'),
            message: i.message,
          })),
        },
      }), { status: 422 });
    }
    (req as any).validatedBody = result.data;
  };
}

// Uso en ruta
app.post('/api/users', validate(CreateUserSchema), async (req) => {
  const body = (req as any).validatedBody;
  // body ya está tipado y validado
});
```

### Python FastAPI — Pydantic

```python
from pydantic import BaseModel, EmailStr, field_validator

class CreateUser(BaseModel):
    email: EmailStr
    name: str
    password: str

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 1 or len(v) > 100:
            raise ValueError('Name must be 1-100 characters')
        return v

@app.post("/api/users")
async def create_user(user: CreateUser):
    # user está validado y tipado automáticamente
    ...
```

---

## 3. XSS Prevention

### React — Sanitización automática + DOMPurify

React escapa por defecto todo contenido interpolado en JSX (`{expression}`). Para contenido HTML dinámico, usar `dangerouslySetInnerHTML` únicamente con `DOMPurify`:

```tsx
import DOMPurify from 'dompurify';

interface ArticleProps {
  content: string; // HTML crudo, potencialmente inseguro
}

export function Article({ content }: ArticleProps) {
  // SEGURO: sanitización explícita del contenido HTML
  const safeHtml = DOMPurify.sanitize(content);

  // PELIGRO: nunca usar dangerouslySetInnerHTML sin sanitizar
  // <div dangerouslySetInnerHTML={{ __html: content }} /> ← NUNCA

  return <div dangerouslySetInnerHTML={{ __html: safeHtml }} />;
}
```

**Template injection prevention:**
```tsx
// PELIGRO: binding directo a contenido del usuario en atributos de seguridad
// <a href={userProvidedUrl}>Link</a>

// SEGURO: validar contra whitelist antes de usar como href
function getSafeUrl(url: string): string {
  const allowedDomains = ['https://app.example.com', 'https://docs.example.com'];
  try {
    const parsed = new URL(url);
    return allowedDomains.includes(parsed.origin) ? url : 'about:blank';
  } catch {
    return 'about:blank';
  }
}
```

**Content Security Policy (CSP) — Mitigación global XSS:**
```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://keycloak.example.com;
```

### CSP en apps React (Vite)

El CSP de una SPA se aplica a nivel de servidor/reverse-proxy (nginx, CDN), no en el build de Vite — ver `api-gateway` para la configuración de nginx. Para desarrollo local, se puede fijar vía meta tag en `index.html`:

```html
<!-- index.html — solo como fallback para dev; en producción el header HTTP tiene prioridad -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'" />
```

### Bun — CSP middleware

```typescript
// security-headers.ts
export function securityHeaders(req: Request): Response | void {
  // Middleware que agrega headers de seguridad a cada respuesta
  const csp = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self' https://keycloak.example.com",
    "frame-ancestors 'none'",
  ].join('; ');

  return new Response(undefined, {
    headers: {
      'Content-Security-Policy': csp,
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'geolocation=(), camera=(), microphone=(), payment=()',
    },
  });
}
```

**Regla de oro XSS: Validar entrada (server-side), escapar salida (server + client), CSP (defense in depth). Una sola capa no es suficiente.**

---

## 4. React Security Patterns

### Route Guards — Protección de rutas

```tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useKeycloak } from './keycloak-context';

interface RequireAuthProps {
  roles?: string[];
}

export function RequireAuth({ roles }: RequireAuthProps) {
  const { isLoggedIn, userRoles, login } = useKeycloak();
  const location = useLocation();

  if (!isLoggedIn) {
    login();
    return null;
  }

  if (roles && roles.length > 0) {
    const hasRole = roles.some((role) => userRoles.includes(role));
    if (!hasRole) return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}

// Registro en router.tsx
const router = createBrowserRouter([
  {
    element: <RequireAuth roles={['admin']} />,
    children: [{ path: 'admin/*', element: <AdminRoutes /> }],
  },
  {
    element: <RequireAuth />,
    children: [{ path: 'dashboard/*', element: <DashboardRoutes /> }],
  },
]);
```

### Fetch Wrapper — JWT injection y refresh

```typescript
import { useKeycloakAuthStore } from './keycloak-auth.store';

let isRefreshing = false;
let refreshWaiters: ((token: string | null) => void)[] = [];

export async function secureFetch(path: string, init: RequestInit = {}): Promise<Response> {
  // No inyectar token en peticiones externas
  if (!path.startsWith('/api/')) return fetch(path, init);

  const { accessToken, refresh, login } = useKeycloakAuthStore.getState();
  const withAuth = (token: string | null): RequestInit => ({
    ...init,
    headers: { ...init.headers, ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });

  const res = await fetch(path, withAuth(accessToken));
  if (res.status !== 401 || path.includes('/auth/refresh')) return res;

  const newToken = await waitForRefresh(refresh, login);
  return newToken ? fetch(path, withAuth(newToken)) : res;
}

async function waitForRefresh(
  refresh: () => Promise<string>,
  login: () => void,
): Promise<string | null> {
  if (!isRefreshing) {
    isRefreshing = true;
    refresh()
      .then((token) => {
        refreshWaiters.forEach((resolve) => resolve(token));
        refreshWaiters = [];
      })
      .catch(() => {
        login();
        refreshWaiters.forEach((resolve) => resolve(null));
        refreshWaiters = [];
      })
      .finally(() => {
        isRefreshing = false;
      });
  }
  return new Promise((resolve) => refreshWaiters.push(resolve));
}
```

---

## 5. Keycloak / OAuth2 Patterns

### Token management y refresh

```typescript
// keycloak-init.ts
import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'https://keycloak.example.com',
  realm: 'my-app',
  clientId: 'my-app-client',
});

export async function initKeycloak(): Promise<boolean> {
  try {
    const authenticated = await keycloak.init({
      onLoad: 'check-sso',
      silentCheckSsoRedirectUri:
        window.location.origin + '/assets/silent-check-sso.html',
      pkceMethod: 'S256', // PKCE obligatorio
    });

    // Auto-refresh before token expiry
    setInterval(() => {
      keycloak.updateToken(30).then(refreshed => {
        if (refreshed) {
          console.log('Token refreshed');
        }
      }).catch(() => {
        keycloak.login();
      });
    }, 10000);

    return authenticated;
  } catch (error) {
    console.error('Keycloak init failed', error);
    return false;
  }
}
```

### Role-based access — Store centralizado

```typescript
import { create } from 'zustand';
import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({ /* config */ });

interface AuthState {
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  getRoles: () => string[];
  getToken: () => string | undefined;
  getSubject: () => string | undefined;
  getTenantId: () => string | undefined;
  logout: () => void;
}

export const useAuthStore = create<AuthState>(() => ({
  hasRole: (role) => keycloak.getUserRoles().includes(role),
  hasAnyRole: (roles) => roles.some((role) => keycloak.getUserRoles().includes(role)),
  getRoles: () => keycloak.getUserRoles(),
  getToken: () => keycloak.token,
  getSubject: () => keycloak.tokenParsed?.sub,
  getTenantId: () => keycloak.tokenParsed?.['tenant-id'],
  logout: () => keycloak.logout({ redirectUri: window.location.origin }),
}));
```

### Token introspection (Bun backend)

```typescript
// keycloak-introspection.ts
const KEYCLOAK_INTROSPECT_URL = 'https://keycloak.example.com/realms/my-app/protocol/openid-connect/token/introspect';

export async function introspectToken(token: string): Promise<{
  active: boolean;
  sub: string;
  realm_access?: { roles: string[] };
  resource_access?: Record<string, { roles: string[] }>;
  exp: number;
  scope: string;
}> {
  const body = new URLSearchParams({
    token,
    client_id: Bun.env.KEYCLOAK_CLIENT_ID!,
    client_secret: Bun.env.KEYCLOAK_CLIENT_SECRET!,
  });

  const response = await fetch(KEYCLOAK_INTROSPECT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });

  if (!response.ok) {
    throw new Error('Token introspection failed');
  }

  return response.json();
}
```

---

## 6. Bun Security Patterns

### Middleware de seguridad (helmet-equivalent)

```typescript
// middleware/security.ts
import type { NextHandler } from 'bun';

export async function securityMiddleware(req: Request, server: any): Promise<Response | void> {
  // Rate limiting simple (ver sección Rate Limiting más abajo)
  // Headers de seguridad
  const securityHeaders: Record<string, string> = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), camera=(), microphone=(), payment=()',
    'Content-Security-Policy': [
      "default-src 'self'",
      "script-src 'self'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data:",
      "font-src 'self'",
      "connect-src 'self' https://keycloak.example.com",
    ].join('; '),
  };

  // Eliminar X-Powered-By y headers de tecnología
  const response = await fetch(req);
  const newResponse = new Response(response.body, response);
  for (const [key, value] of Object.entries(securityHeaders)) {
    newResponse.headers.set(key, value);
  }
  newResponse.headers.delete('X-Powered-By');
  return newResponse;
}
```

### Input validation con Zod en Bun

```typescript
import { z } from 'zod';

// Schema de validación reutilizable
const UserSchema = z.object({
  email: z.string().email().max(255).toLowerCase(),
  name: z.string().min(1).max(100).regex(/^[a-zA-ZÀ-ÿ\s'-]+$/),
  role: z.enum(['user', 'admin', 'editor']),
});

const PaginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sort: z.enum(['created_at', 'name', 'email']).default('created_at'),
  order: z.enum(['asc', 'desc']).default('desc'),
});

// Uso en handler
const server = Bun.serve({
  async fetch(req) {
    const url = new URL(req.url);

    if (req.method === 'POST' && url.pathname === '/api/users') {
      const body = await req.json();
      const result = UserSchema.safeParse(body);

      if (!result.success) {
        return Response.json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            details: result.error.issues.map(i => ({
              path: i.path.join('.'),
              message: i.message,
            })),
          },
        }, { status: 422 });
      }

      // result.data está tipado y validado
      const user = await createUser(result.data);
      return Response.json({ success: true, data: user });
    }

    return new Response('Not Found', { status: 404 });
  },
});
```

### Command Injection Prevention (Bun)

```typescript
// PELIGRO: shell: true con input del usuario
Bun.spawn(['sh', '-c', `ping ${userInput}`]); // ← NUNCA

// SEGURO: argumentos separados, sin shell
Bun.spawn(['ping', userInput], { stdout: 'pipe' });

// SEGURO: validar input contra whitelist
const VALID_HOSTS = ['10.0.0.1', '10.0.0.2'];
if (!VALID_HOSTS.includes(userInput)) {
  throw new Error('Host no permitido');
}
```

---

## 7. CORS Configuration

### Bun — CORS middleware

```typescript
// middleware/cors.ts
const ALLOWED_ORIGINS = [
  'https://app.example.com',
  'https://staging.example.com',
];

export function corsMiddleware(req: Request): Response | void {
  const origin = req.headers.get('Origin') || '';

  if (req.method === 'OPTIONS') {
    // Preflight request
    const headers: Record<string, string> = {
      'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : '',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH',
      'Access-Control-Allow-Headers': 'Authorization, Content-Type, X-Tenant-ID',
      'Access-Control-Max-Age': '86400',
    };
    return new Response(null, { status: 204, headers });
  }
}

// En el handler de response, agregar el header CORS
function addCorsHeaders(response: Response, origin: string): Response {
  if (ALLOWED_ORIGINS.includes(origin)) {
    response.headers.set('Access-Control-Allow-Origin', origin);
    response.headers.set('Vary', 'Origin');
  }
  return response;
}
```

### Python FastAPI

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)
```

---

## 8. Rate Limiting

### Bun — Rate limiter con store en memoria

```typescript
// middleware/rate-limiter.ts
const rateLimitStore = new Map<string, { count: number; resetAt: number }>();

export function rateLimit(
  windowMs: number,
  maxRequests: number,
) {
  return (req: Request): Response | void => {
    const ip = req.headers.get('x-forwarded-for') || 'unknown';
    const now = Date.now();
    const key = `${ip}:${req.url}`;

    const current = rateLimitStore.get(key);

    if (!current || now > current.resetAt) {
      rateLimitStore.set(key, { count: 1, resetAt: now + windowMs });
      return;
    }

    if (current.count >= maxRequests) {
      return Response.json(
        { success: false, error: { code: 'RATE_LIMITED', message: 'Too many requests' } },
        {
          status: 429,
          headers: {
            'Retry-After': String(Math.ceil((current.resetAt - now) / 1000)),
            'X-RateLimit-Limit': String(maxRequests),
            'X-RateLimit-Remaining': '0',
          },
        },
      );
    }

    current.count++;
  };
}

// Uso
const limiter = rateLimit(60_000, 100); // 100 req/min
```

### Python FastAPI

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.get("/api/recurso")
@limiter.limit("20/minute")
async def get_recurso(request: Request):
    return {"data": "ok"}
```

---

## 9. OWASP Top 10 — Mitigaciones por stack

### A1: Broken Access Control

**React — Route Guards con roles**
```typescript
// Ver sección 4: Route Guards
// canActivate + data.roles + KeycloakService
```

**Bun Backend — JWT validation middleware**
```typescript
import { introspectToken } from './keycloak-introspection';

export async function requireAuth(req: Request): Promise<Response | void> {
  const authHeader = req.headers.get('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return Response.json({ success: false, error: { code: 'UNAUTHORIZED' } }, { status: 401 });
  }

  const token = authHeader.slice(7);
  const result = await introspectToken(token);

  if (!result.active) {
    return Response.json({ success: false, error: { code: 'INVALID_TOKEN' } }, { status: 401 });
  }

  // Adjuntar datos del usuario al request para uso posterior
  (req as any).user = {
    sub: result.sub,
    roles: result.realm_access?.roles ?? [],
    tenantId: (result as any)['tenant-id'],
  };
}

export function requireRole(...roles: string[]) {
  return async (req: Request): Promise<Response | void> => {
    const user = (req as any).user;
    if (!user || !roles.some(r => user.roles.includes(r))) {
      return Response.json({ success: false, error: { code: 'FORBIDDEN' } }, { status: 403 });
    }
  };
}
```

**Python FastAPI — Dependency injection para permisos**
```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer

def require_admin(auth=Security(HTTPBearer())):
    if not auth.credentials.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol Admin")
    return auth

@app.get("/admin/users")
async def get_users(admin = Depends(require_admin)):
    return await user_service.find_all()
```

### A3: Injection

**SQL Injection — Prevención con queries parametrizadas**

```python
# Python SQLAlchemy
result = await db.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": user_email}
)

# PELIGRO: f-strings
result = await db.execute(text(f"SELECT * FROM users WHERE email = '{user_email}'"))
```

```typescript
// Bun — node-postgres
const result = await pool.query(
  'SELECT * FROM users WHERE email = $1 AND status = $2',
  [email, 1]
);

// PELIGRO: template strings
const result = await pool.query(`SELECT * FROM users WHERE email = '${email}'`);
```

**Command Injection — Prevención**
```typescript
// Bun — PELIGRO
Bun.spawn(['sh', '-c', `ping ${userInput}`]);

// SEGURO: argumentos separados
Bun.spawn(['ping', userInput], { stdout: 'pipe' });

// SEGURO: validar contra whitelist
const VALID_HOSTS = ['10.0.0.1', '10.0.0.2'];
if (!VALID_HOSTS.includes(userInput)) throw new Error('Host no permitido');
```

### A5: Security Misconfiguration

**CORS — Configuración restrictiva (ver sección 7)**

**Security Headers (ver secciones 4 y 6)**

### A6: Sensitive Data Exposure

**Cifrado en reposo vs en tránsito**

| Aspecto | En tránsito (TLS) | En reposo |
|---------|-------------------|-----------|
| Qué protege | Datos en red | Datos en DB/disco |
| Implementación | HTTPS / TLS 1.3 | AES-256, Transparent Data Encryption |
| Stack Bun | TLS en `Bun.serve({ tls: {...} })` | SQLAlchemy + column-level encryption |
| Stack Python | `ssl_context` en uvicorn/FastAPI | SQLAlchemy + sqlalchemy-encrypt |

**Nunca loguear PII — Ejemplos por stack**

```typescript
// Bun — Structured logger con redacción
const logger = {
  info(msg: string, data: Record<string, any>) {
    const sanitized = redactPII(data);
    console.log(JSON.stringify({ level: 'info', msg, ...sanitized }));
  },
};

function redactPII(data: Record<string, any>): Record<string, any> {
  const sensitiveKeys = new Set(['email', 'password', 'ssn', 'phone', 'authorization']);
  const result: Record<string, any> = {};
  for (const [key, value] of Object.entries(data)) {
    result[key] = sensitiveKeys.has(key.toLowerCase()) ? '[FILTRADO]' : value;
  }
  return result;
}
```

```python
# Python — Structlog con filtro
import structlog

def drop_pii(logger, name, event_dict):
    sensitive_keys = {"email", "password", "ssn", "phone"}
    for key in list(event_dict.keys()):
        if key.lower() in sensitive_keys:
            event_dict[key] = "[FILTRADO]"
    return event_dict

structlog.configure(processors=[drop_pii, structlog.processors.JSONRenderer()])
```

**Data masking — Mostrar solo parcialmente**
```typescript
function maskEmail(email: string): string {
  return email.replace(/(.)(.*)(@.*)/, (_, a, b, c) =>
    a + '*'.repeat(b.length) + c
  );
}
// "j******@example.com"

function maskCard(number: string): string {
  return '**** **** **** ' + number.slice(-4);
}
```

### A7: Cross-Site Scripting (XSS)

**React — Escapado automático + DOMPurify (ver sección 3)**

**Content Security Policy (ver secciones 3 y 6)**

**Helmet-equivalent para Bun (ver sección 6: middleware de seguridad)**

---

## 10. Security Headers Checklist

| Header | Valor recomendado | Notas |
|--------|-------------------|-------|
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://keycloak.example.com; frame-ancestors 'none'` | Previene XSS, clickjacking, data exfiltration. |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Fuerza HTTPS. |
| `X-Frame-Options` | `DENY` | Previene clickjacking. |
| `X-Content-Type-Options` | `nosniff` | Evita MIME sniffing. |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controla información de referer. |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=(), payment=()` | Restringe APIs del navegador. |
| `Cross-Origin-Embedder-Policy` | `require-corp` | Recursos cross-origin requieren CORS. |
| `Cross-Origin-Opener-Policy` | `same-origin` | Aísla ventanas cross-origin. |
| `Cross-Origin-Resource-Policy` | `same-origin` | Controla inclusión de recursos. |
| `Cache-Control` | `no-store, no-cache, must-revalidate` | Para respuestas con datos sensibles. |
| `Clear-Site-Data` | `"cache","cookies","storage"` | En logout, limpiar datos del cliente. |

---

## 11. Secrets Management

| Environment | Tool |
|-------------|------|
| Local development | `.env.local` (gitignored) |
| CI/CD | GitHub Secrets / Azure Key Vault |
| Production | AWS Secrets Manager / Azure Key Vault / HashiCorp Vault |

**NEVER** store secrets in source code, config files committed to git, or logs.

### Bun — Variables de entorno

```typescript
// Nunca hardcodear secrets
const keycloakRealm = Bun.env.KEYCLOAK_REALM;           // ✅
const keycloakSecret = Bun.env.KEYCLOAK_CLIENT_SECRET;   // ✅

// Nunca
const secret = 'super-secret-key'; // ❌
```

---

## 12. Source Code Repository Security

| Control | GitHub | Azure DevOps | Bitbucket |
|---------|--------|--------------|-----------|
| Branch restrictions | Branch protection rules | Branch policies | Branch permissions |
| Require PR review | Required reviewers | Approval policies | Required approvals |
| Auth method | PAT / SSH / GitHub App | PAT / SSH / Azure AD | PAT / SSH / App passwords |

**CRITICAL (AWS CodeCommit)**: NO "branch protection" feature exists — use **IAM policies** + **Approval Rule Templates** instead.

---

## 13. Audit Logging

Cada operación de seguridad debe dejar traza:

```typescript
// audit-logger.ts
interface AuditEvent {
  timestamp: string;
  action: string;
  actor: string;
  tenantId: string;
  resource: string;
  resourceId?: string;
  outcome: 'success' | 'failure';
  metadata?: Record<string, any>;
}

function logAudit(event: AuditEvent): void {
  console.log(JSON.stringify({
    ...event,
    timestamp: new Date().toISOString(),
    level: 'audit',
  }));
}

// Uso en handlers
logAudit({
  timestamp: '',
  action: 'user.create',
  actor: req.user.sub,
  tenantId: req.user.tenantId,
  resource: 'user',
  resourceId: newUser.id,
  outcome: 'success',
  metadata: { email: newUser.email },
});
```

---

## Verificación

- **Headers online:** Usar https://securityheaders.com para auditar los headers de cualquier entorno. La calificación A+ requiere todos los headers implementados.
- **CSP:** Usar https://csp-evaluator.withgoogle.com para verificar la robustez de la CSP.
- **Keycloak:** Verificar configuración de realms en Keycloak Admin Console.
