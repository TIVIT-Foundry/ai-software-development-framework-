---
name: authentication
description: 'Authentication patterns: token-based auth, session management, identity
  propagation. Covers Keycloak as IdP, OAuth2/OIDC with PyJWT + passlib + FastAPI,
  React fetch wrappers and route guards, or Angular HTTP interceptors and route guards
  (per project''s frontend choice). Trigger: When implementing login, logout,
  tokens, session management, or auth flow.'
version: 2.1
metadata:
  phase:
  - construction
  layer:
  - backend
  - frontend
  enforcement: mandatory
  depends_on:
  - security
  consumed_by:
  - api-gateway
  - app-bootstrap
  - authorization
  - backend-api
  - keycloak
  - oauth2-jwt
  - real-time
  agent_roles:
  - design-agent
  - control-agent
  validation_profile: security-review
mcp_usage: none
---

## Tabla de contenidos

- Critical Rules
- Relation to other skills
- When to use this skill
- Authentication Patterns
- Standard Auth Flow (JWT)
- Keycloak as Identity Provider (Recommended)
  - Configuración Keycloak
  - Keycloak + FastAPI Integration
  - Token Refresh con Keycloak
- Microservice Identity Propagation
- Python FastAPI JWT (PyJWT + passlib)
- Identity Header Pattern (Internal APIs)
- Auth Endpoints to Exclude from Validation
- OpenAPI Security Schemes
- Patrones modernos de autenticación
  - 1. Passkeys / WebAuthn
  - 2. JWKS Endpoints
  - 3. BFF Pattern (Backend-For-Frontend)
  - 4. Token Management Patterns

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Validate tokens at gateway/middleware, not in each endpoint | ALWAYS | Single validation point |
| Never store tokens in localStorage (prefer httpOnly cookies) | ALWAYS | XSS protection |
| Propagate user identity via internal header to microservices | ALWAYS | Consistent identity |
| Use short-lived access tokens + refresh token rotation | ALWAYS | Limit token exposure |
| Never log tokens, passwords, or auth credentials | NEVER | Security breach risk |
| Verify token expiration and signature server-side | ALWAYS | Cannot trust client |

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `security` | Complementaria | Authentication maneja el login/registro/identidad. Security maneja la protección de la aplicación (CORS, CSP, XSS). |
| `authorization` | Consumidora | Authentication verifica quién eres. Authorization decide qué puedes hacer después del login. |
| `keycloak` | Complementaria | Authentication usa Keycloak como IdP para implementar OAuth2/OIDC. |

## When to use this skill

Activate this skill when:
- Implementing login, logout, or token refresh flows
- Setting up Keycloak as an Identity Provider (OIDC)
- Configuring JWT token validation and JWKS endpoints
- Implementing BFF (Backend-For-Frontend) patterns for auth
- Setting up passkeys / WebAuthn authentication
- Configuring silent refresh and token rotation in React
- Propagating user identity across microservices

Do not activate when:
- Setting up CORS, CSP, or security headers → use `security`
- Implementing RBAC, permissions, or role checks → use `authorization`
- Designing governance-level security policies → use `framework-security`

## Authentication Patterns

| Pattern | Use Case |
|---------|----------|
| **Keycloak (OIDC)** | **Identity Provider principal — SSO, MFA, user federation, admin console** |
| JWT (Bearer) | Stateless APIs, microservices (validación local de tokens Keycloak) |
| OAuth2 / OIDC | Third-party identity providers (Google, Azure AD, Cognito) |
| API Key | Server-to-server communication |
| Session Cookie (httpOnly) | Traditional web apps |
| Custom encrypted token | Internal service mesh |

## Standard Auth Flow (JWT)
```
Client → [POST /auth/login] → Auth Service → Validates credentials →
Returns { accessToken, refreshToken } → Client stores securely →
Client → [GET /resource, Authorization: Bearer {token}] → API validates token → Response
```

## Keycloak as Identity Provider (Recommended)

Keycloak es el IdP estándar del framework. Proporciona SSO, MFA, user federation (LDAP/AD), admin console y clientes OIDC nativos.

### Configuración Keycloak

```
Realm:          mi-app-realm
Client ID:      mi-app-frontend   (public, auth-code flow)
Client ID:      mi-app-backend    (confidential, service account)
Roles:          realm-level + client-level
Groups:         mapeo a roles del dominio
```

### Keycloak + FastAPI Integration

**Instalación:**
```bash
pip install python-keycloak
```

**Configuración del cliente Keycloak:**
```python
from keycloak import KeycloakOpenID, KeycloakAdmin

# Cliente OIDC para validación de tokens (backend)
keycloak_openid = KeycloakOpenID(
    server_url="https://keycloak.example.com",
    client_id="mi-app-backend",
    client_secret="${KEYCLOAK_CLIENT_SECRET}",
    realm_name="mi-app-realm",
)

# Admin client (para gestión de usuarios/grupos si necesario)
keycloak_admin = KeycloakAdmin(
    server_url="https://keycloak.example.com",
    username="${KEYCLOAK_ADMIN_USER}",
    password="${KEYCLOAK_ADMIN_PASSWORD}",
    realm_name="mi-app-realm",
)
```

**Validación de tokens JWT con JWKS de Keycloak:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

security = HTTPBearer()

# Cache de JWKS (rotar periódicamente)
_jwks_cache: dict = {}

async def get_keycloak_jwks() -> dict:
    """Obtener JWKS de Keycloak (con cache)."""
    if not _jwks_cache:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://keycloak.example.com/realms/mi-app-realm/protocol/openid-connect/certs"
            )
            _jwks_cache.update(resp.json())
    return _jwks_cache

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validar token JWT de Keycloak."""
    token = credentials.credentials
    try:
        # Opción 1: Validación directa con JWKS (PyJWT 2.x acepta el JWKS como key)
        import jwt
        from jwt.exceptions import InvalidTokenError
        jwks = await get_keycloak_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience="mi-app-backend",
            options={"verify_iss": True, "iss": "https://keycloak.example.com/realms/mi-app-realm"},
        )
        return {
            "user_id": payload["sub"],
            "email": payload.get("email"),
            "roles": payload.get("realm_access", {}).get("roles", []),
            "groups": payload.get("groups", []),
        }
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Opción 2: Usar python-keycloak (validación introspection)
async def get_current_user_introspect(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validar token via introspection de Keycloak."""
    token = credentials.credentials
    try:
        # python-keycloak valida internamente con JWKS + introspection
        user_info = keycloak_openid.userinfo(token)
        return {
            "user_id": user_info["sub"],
            "email": user_info.get("email"),
            "roles": user_info.get("realm_access", {}).get("roles", []),
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
```

### Token Refresh con Keycloak

Keycloak maneja refresh tokens con rotación por defecto. El backend puede delegar el refresh al IdP o implementar BFF.

**Patrón BFF con Keycloak (recomendado):**
```python
from fastapi import Request, Response

@app.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    """Refresh via Keycloak. El refresh token se envía como cookie httpOnly."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        tokens = keycloak_openid.refresh_token(refresh_token)
        # Setear nuevos tokens como cookies
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=tokens["expires_in"],
        )
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=tokens["refresh_expires_in"],
        )
        return {"status": "refreshed"}
    except Exception:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        raise HTTPException(status_code=401, detail="Refresh failed — re-login required")

@app.post("/auth/logout")
async def logout(response: Response):
    """Logout: revocar tokens en Keycloak + limpiar cookies."""
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            keycloak_openid.logout(refresh_token)
        except Exception:
            pass  # Token ya revocado o expirado
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"status": "logged_out"}
```

**Patrón directo (sin BFF — frontend maneja tokens):**
```python
@app.post("/auth/refresh-direct")
async def refresh_direct(body: RefreshRequest):
    """Refresh directo: el frontend envía el refresh token en el body."""
    try:
        tokens = keycloak_openid.refresh_token(body.refresh_token)
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_in": tokens["expires_in"],
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh failed")
```

## Microservice Identity Propagation
```
Client → [auth headers] → API Gateway → Validates token → Extracts user claims →
Creates internal identity header → Forwards to internal services →
Internal services read identity from header (no re-validation)
```

## Python FastAPI JWT (PyJWT + passlib)

```python
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return {"user_id": user_id, "scopes": payload.get("scopes", [])}
    except InvalidTokenError:
        raise credentials_exception

# Login endpoint
@router.post("/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "scopes": user.scopes},
        expires_delta=access_token_expires,
    )
    return TokenResponse(access_token=access_token, token_type="bearer")
```

## Identity Header Pattern (Internal APIs)
In FastAPI, identity is typically propagated via dependency injection:

```python
# Auth dependency that reads from internal headers or validates JWT
async def get_identity_context(
    request: Request,
    token: str = Depends(oauth2_scheme)
) -> IdentityContext:
    # Check for internal header first (propagated from gateway)
    internal_id = request.headers.get("X-User-Id")
    if internal_id:
        roles = request.headers.get("X-Roles", "").split(",")
        tenant_id = request.headers.get("X-Tenant-Id")
        return IdentityContext(
            user_id=internal_id,
            roles=roles,
            tenant_id=tenant_id,
        )
    # Otherwise validate JWT and extract claims
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return IdentityContext(
        user_id=payload.get("sub"),
        roles=payload.get("roles", []),
        tenant_id=payload.get("tenant_id"),
    )
```

## Auth Endpoints to Exclude from Validation
- `/health` — health checks
- `/swagger` or `/openapi` — API documentation
- `/auth/login` or `/auth/token` — login endpoints
- Public static assets

## OpenAPI Security Schemes
```yaml
# For standard JWT:
securitySchemes:
  bearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
```

## Patrones modernos de autenticación

### 1. Passkeys / WebAuthn

**Qué son**: Passkeys son credenciales FIDO2 basadas en criptografía asimétrica. El dispositivo del usuario genera un par de claves; la clave privada jamás sale del authenticator (TPM, Secure Enclave, YubiKey). Eliminan contraseñas y phishing.

**Flujo de registro**:
```
1. Client → POST /webauthn/register-start → Server genera challenge + excludeCredentials
2. Client llama navigator.credentials.create({ publicKey: options })
3. Authenticator genera par de claves → devuelve attestation + publicKey
4. Client → POST /webauthn/register-finish → Server verifica attestation → guarda credencial
```

**Flujo de autenticación**:
```
1. Client → POST /webauthn/auth-start → Server genera challenge + allowCredentials
2. Client llama navigator.credentials.get({ publicKey: options })
3. Authenticator firma el challenge con la clave privada → devuelve assertion
4. Client → POST /webauthn/auth-finish → Server verifica firma → emite token/session
```

**Cuándo usar**:
- Aplicaciones con alto requisito de seguridad (finanzas, salud)
- Reemplazo de contraseñas para consumidores (menos soporte, mejor UX)
- Flujos internos corporativos con MFA obligatorio

**Ejemplo Python (registro)**:
```python
from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers.structs import RegistrationCredential

@router.post("/webauthn/register-start")
async def register_start(email: str):
    user = await get_or_create_user(email)
    options = generate_registration_options(
        rp_id="miapp.com",
        rp_name="Mi App",
        user_id=user.id,
        user_name=user.email,
        exclude_credentials=await get_existing_credentials(user.id),
    )
    session["webauthn_challenge"] = options.challenge
    return options

@router.post("/webauthn/register-finish")
async def register_finish(credential: RegistrationCredential):
    challenge = session["webauthn_challenge"]
    verified = verify_registration_response(
        credential=credential,
        expected_challenge=challenge,
        expected_origin="https://miapp.com",
        expected_rp_id="miapp.com",
    )
    await store_credential(verified)
    return {"status": "ok"}
```

---

### 2. JWKS Endpoints

**Qué son**: Un JWKS (JSON Web Key Set) endpoint expone las claves públicas usadas para verificar firmas JWT. Permite rotación sin redistribuir secretos a todos los servicios.

**Rotación de keys**:
1. Generar nuevo par de claves → agregar a JWKS junto a la key anterior
2. Firmar nuevos tokens con la key nueva (usar `kid` en el header JWT)
3. Los servicios verifican con la key que coincide el `kid`
4. Después del periodo de gracia, remover la key vieja del JWKS

**Ejemplo Python (JWKS con rotación)**:
```python
from jwt.algorithms import RSAAlgorithm
from jwt import PyJWK

# Generar nuevos pares de claves (PyJWT + cryptography)
new_private_key = RSAAlgorithm.generate_key(2048)   # PEM bytes
old_private_key = RSAAlgorithm.generate_key(2048)

# JWKS: exponer solo la parte pública con kid
new_jwk = PyJWK.from_pem(new_private_key).to_dict()
new_jwk["kid"] = "key-2026-01"
old_jwk = PyJWK.from_pem(old_private_key).to_dict()
old_jwk["kid"] = "key-2025-06"

jwks = {"keys": [new_jwk, old_jwk]}

@app.get("/.well-known/jwks.json")
async def get_jwks():
    return jwks

# Firmar tokens con la key nueva:
# header = {"kid": "key-2026-01", "alg": "RS256"}
# jwt.encode(payload, new_private_key, algorithm="RS256", headers={"kid": "key-2026-01"})
```

---

### 3. BFF Pattern (Backend-For-Frontend)

**Qué es**: Un BFF actúa como proxy entre el frontend y los servicios de auth/APIs. El frontend NUNCA maneja tokens directamente; el BFF los almacena en cookies httpOnly y los inyecta en llamadas a APIs internas.

**Flujo BFF**:
```
Browser → POST /bff/login (cookie httpOnly set por BFF)
Browser → GET /bff/api/orders → BFF lee token de cookie → inyecta Authorization: Bearer → API interna
Browser → GET /bff/refresh → BFF rota refresh token → nueva cookie
Browser → POST /bff/logout → BFF elimina cookie + revoca tokens
```

**Ventajas**:
- Tokens invisibles para JavaScript (sin XSS sobre tokens)
- Rotación de refresh tokens completamente transparente para el frontend
- Audit trail centralizado de todos los accesos

**Ejemplo FastAPI BFF**:
```python
from fastapi import FastAPI, Request
from httpx import AsyncClient

app = FastAPI()

@app.middleware("http")
async def bff_middleware(request: Request, call_next):
    token = request.cookies.get("access_token")
    if token:
        request.headers.__dict__["_list"].append(
            (b"authorization", f"Bearer {token}".encode())
        )
    response = await call_next(request)
    return response

@app.post("/bff/login")
async def bff_login(response: Response, credentials: LoginRequest):
    tokens = await auth_service.login(credentials)
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return {"status": "ok"}

@app.post("/bff/logout")
async def bff_logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "ok"}
```

**Ejemplo React (BFF — sin manejo de tokens)**:
```typescript
// El frontend solo llama al BFF; las cookies se envían automáticamente
// No hay manejo de tokens en el frontend

// core/api/orders.api.ts
export async function getOrders(): Promise<Order[]> {
  const res = await fetch('/bff/api/orders', { credentials: 'include' });
  if (!res.ok) throw new Error('Failed to load orders');
  return res.json();
}

// logout
export function logout() {
  window.location.href = '/bff/logout';
}
```

---

### 4. Token Management Patterns

#### Refresh Token Rotation

Cada vez que se usa un refresh token, el servidor emite uno nuevo e invalida el anterior. Si se detecta un token revocado en uso, se revocan TODOS los tokens de esa familia (detección de replay).

**Ejemplo Python**:
```python
@router.post("/auth/refresh")
async def refresh_token(refresh_request: RefreshRequest):
    stored = await token_service.get_refresh_token(refresh_request.refresh_token)

    if stored is None or stored.revoked:
        # Detección de replay: revocar toda la familia
        if stored:
            await token_service.revoke_family(stored.family_id)
        raise HTTPException(status_code=401, detail="Token revoked — possible theft")

    if stored.is_expired:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Rotación: revocar el token usado y emitir nuevo par
    await token_service.revoke(stored)
    family_id = stored.family_id
    new_access = jwt_service.generate_access_token(stored.user_id)
    new_refresh = await token_service.create(stored.user_id, family_id)

    return {"access_token": new_access, "refresh_token": new_refresh}
```

#### Storage Strategies

| Estrategia | Seguro contra XSS | Seguro contra CSRF | Persistente | Complejidad |
|------------|-------------------|--------------------|-------------|-------------|
| `localStorage` | No | Sí | Sí | Baja |
| `sessionStorage` | No | Sí | No (tab) | Baja |
| Memoria JS (`state`) | Sí | Sí | No (reload) | Media |
| Cookie httpOnly + SameSite=Strict | Sí | Sí (con SameSite) | Sí | Alta |
| BFF cookie httpOnly | Sí | Sí (CSRF token) | Sí | Alta |

**Recomendación combinada**:
- **Access token** → memoria JS (no persiste entre recargas, pero es el más seguro contra XSS)
- **Refresh token** → cookie httpOnly + SameSite=Strict (rotación obligatoria)
- **Suspensión de sesión** → service worker con silent refresh antes de expiración

#### Silent Refresh (Frontend React)

```typescript
// core/auth/auth.store.ts — estado de autenticación con refresh automático
import { create } from 'zustand';

interface AuthState {
  accessToken: string | null;
  refreshTimeout: ReturnType<typeof setTimeout> | null;
  login: (username: string, password: string) => Promise<void>;
  refresh: () => Promise<void>;
  logout: () => void;
  isAuthenticated: () => boolean;
}

async function postAuth(path: string, body?: unknown): Promise<AuthResponse> {
  const res = await fetch(path, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error('Auth request failed');
  return res.json();
}

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  refreshTimeout: null,

  login: async (username, password) => {
    const res = await postAuth('/auth/login', { username, password });
    set({ accessToken: res.access_token });
    scheduleRefresh(res.expires_in, get, set);
  },

  refresh: async () => {
    try {
      const res = await postAuth('/auth/refresh');
      set({ accessToken: res.access_token });
      scheduleRefresh(res.expires_in, get, set);
    } catch {
      get().logout();
      throw new Error('Session expired');
    }
  },

  logout: () => {
    const timeout = get().refreshTimeout;
    if (timeout) clearTimeout(timeout);
    set({ accessToken: null, refreshTimeout: null });
    fetch('/auth/logout', { method: 'POST', credentials: 'include' });
  },

  isAuthenticated: () => !!get().accessToken,
}));

function scheduleRefresh(
  expiresIn: number,
  get: () => AuthState,
  set: (partial: Partial<AuthState>) => void,
): void {
  const prev = get().refreshTimeout;
  if (prev) clearTimeout(prev);
  // Refrescar 30 segundos antes de expirar
  const timeout = setTimeout(() => get().refresh(), (expiresIn - 30) * 1000);
  set({ refreshTimeout: timeout });
}
```

```typescript
// core/api/fetch-client.ts — adjunta el access token a cada request
import { useAuthStore } from '../auth/auth.store';

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = useAuthStore.getState().accessToken;
  const res = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json() as Promise<T>;
}
```

```tsx
// core/auth/RequireAuth.tsx — Route Guard para proteger rutas
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from './auth.store';

export function RequireAuth() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated());
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}
```

**Registro en el router (router.tsx):**
```tsx
import { createBrowserRouter } from 'react-router-dom';
import { RequireAuth } from './core/auth/RequireAuth';

const router = createBrowserRouter([
  {
    element: <RequireAuth />,
    children: [{ path: 'dashboard', element: <DashboardPage /> }],
  },
  { path: 'login', element: <LoginPage /> },
]);
```

#### Silent Refresh (Frontend Angular)

```typescript
// auth.interceptor.ts — HTTP Interceptor para adjuntar tokens
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private authService = inject(AuthService);

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = this.authService.getAccessToken();
    if (token) {
      const cloned = req.clone({
        setHeaders: { Authorization: `Bearer ${token}` },
      });
      return next.handle(cloned);
    }
    return next.handle(req);
  }
}

// auth.guard.ts — Route Guard para proteger rutas
@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  private authService = inject(AuthService);
  private router = inject(Router);

  canActivate(): boolean {
    if (this.authService.isAuthenticated()) {
      return true;
    }
    this.router.navigate(['/login']);
    return false;
  }
}

// auth.service.ts — Servicio de autenticación con refresh automático
@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private refreshTimeout: ReturnType<typeof setTimeout>;

  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  login(username: string, password: string): Observable<void> {
    return this.http.post<AuthResponse>('/auth/login', { username, password }).pipe(
      tap((res) => {
        this.setTokens(res.access_token, res.refresh_token);
        this.scheduleRefresh(res.expires_in);
      }),
    );
  }

  refresh(): Observable<void> {
    return this.http.post<AuthResponse>('/auth/refresh', {}, { withCredentials: true }).pipe(
      tap((res) => {
        this.setTokens(res.access_token, res.refresh_token);
        this.scheduleRefresh(res.expires_in);
      }),
      catchError(() => {
        this.logout();
        return throwError(() => new Error('Session expired'));
      }),
    );
  }

  private scheduleRefresh(expiresIn: number): void {
    // Refrescar 30 segundos antes de expirar
    clearTimeout(this.refreshTimeout);
    this.refreshTimeout = setTimeout(() => this.refresh().subscribe(), (expiresIn - 30) * 1000);
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  logout(): void {
    this.accessToken = null;
    this.refreshToken = null;
    clearTimeout(this.refreshTimeout);
    this.http.post('/auth/logout', {}, { withCredentials: true }).subscribe();
  }

  private setTokens(access: string, refresh: string): void {
    this.accessToken = access;
    this.refreshToken = refresh;
  }
}
```

**Registro del interceptor y guards (app.config.ts):**
```typescript
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter, withEnabledBlockingInitialNavigation } from '@angular/router';
import { authInterceptor } from './interceptors/auth.interceptor';
import { authGuard } from './guards/auth.guard';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptors([authInterceptor])),
    provideRouter(
      [
        { path: 'dashboard', canActivate: [authGuard], loadComponent: ... },
        { path: 'login', loadComponent: ... },
      ],
      withEnabledBlockingInitialNavigation()
    ),
  ],
};
```
