---
name: keycloak
description: 'Keycloak integration patterns: OIDC authentication, token validation, role-based access control, multi-tenant realms, user management, token refresh, session management. Trigger: When implementing Keycloak as IdP, configuring OAuth2/OIDC, or managing authentication with Keycloak.'
version: 1.1
metadata:
  phase:
    - construction
  layer:
    - backend
  enforcement: mandatory
  depends_on:
    - authentication
    - authorization
  consumed_by:
    - agent-backend
    - agent-fullstack
  agent_roles:
  - control-agent
  validation_profile: security
  mcp_usage: context7
---

## Purpose

Define the patterns for Keycloak integration in the framework. Covers OIDC authentication flows, JWT token validation, role-based access control (RBAC), multi-tenant realm management, user provisioning, token refresh strategies, and session management. This skill ensures consistent security patterns when using Keycloak as the Identity Provider.

## When to use this skill

Activate this skill when:

- Setting up Keycloak as the Identity Provider
- Implementing OIDC/OAuth2 authentication flows
- Configuring JWT token validation
- Implementing role-based access control with Keycloak roles
- Managing multi-tenant realms in Keycloak
- Implementing token refresh in frontend (React or Angular) and backend (FastAPI)
- Syncing users between Keycloak and application database

**Do not** activate when:

- Using custom JWT/OAuth2 without Keycloak (use `oauth2-jwt`)
- Only implementing basic RBAC (use `authorization`)
- Working with frontend-only auth patterns (use `react` or `angular`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `authentication` | Predecesora | Patrones generales de auth (login, sesiones, BFF, WebAuthn); Keycloak es el IdP recomendado |
| `oauth2-jwt` | Complementaria | JWT/OAuth2 custom sin IdP — si no usas Keycloak, usa esta |
| `authorization` | Complementaria | RBAC implementation details |
| `security` | Complementaria | General security patterns |
| `react` / `angular` | Consumidora | Frontend Keycloak integration (según el framework elegido por el proyecto) |
| `backend-api` | Consumidora | Backend token validation |

## Critical Rules

1. **Always validate tokens server-side** — Never trust frontend-only validation
2. **Use JWKS endpoint** — Fetch public keys from Keycloak for token verification
3. **Multi-tenant via realms** — One realm per tenant, or shared realm with tenant roles
4. **Token refresh before expiry** — Refresh at 80% of token lifespan
5. **Roles in token** — Include roles in JWT claims for efficient authorization
6. **HTTPS mandatory** — Keycloak must run on HTTPS in production

## What the agent must do

1. **Configure Keycloak connection** — URL, realm, client_id, client_secret
2. **Implement token validation** — JWKS endpoint, signature verification, claims extraction
3. **Set up RBAC** — Map Keycloak roles to application permissions
4. **Configure token refresh** — Refresh tokens before expiry
5. **Implement user sync** — Sync Keycloak users to application database
6. **Add React fetch wrapper (or Angular HTTP interceptor)** — Typed `apiFetch` / interceptor for token injection

## Code patterns

### FastAPI Keycloak Configuration

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class KeycloakSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "my-app"
    KEYCLOAK_CLIENT_ID: str = "fastapi-backend"
    KEYCLOAK_CLIENT_SECRET: str
    
    @property
    def jwks_url(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    
    @property
    def issuer(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.KEYCLOAK_REALM}"

settings = KeycloakSettings()
```

### Token Validation with JWKS

```python
import jwt
from jwt import PyJWKSet
import httpx
from fastapi import Depends, HTTPException, Request
from typing import Optional
import cachetools

class KeycloakTokenValidator:
    def __init__(self, settings: KeycloakSettings):
        self.settings = settings
        self.jwks_cache = cachetools.TTLCache(maxsize=1, ttl=3600)
    
    async def get_jwks(self) -> dict:
        if "jwks" in self.jwks_cache:
            return self.jwks_cache["jwks"]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.settings.jwks_url)
            response.raise_for_status()
            jwks = response.json()
            self.jwks_cache["jwks"] = jwks
            return jwks
    
    async def validate_token(self, token: str) -> dict:
        # Get JWKS
        jwks = await self.get_jwks()
        
        # Verify signature and decode (PyJWT selecciona la key por kid del header)
        try:
            signing_key = PyJWKSet.from_dict(jwks).get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.settings.issuer,
                audience=self.settings.KEYCLOAK_CLIENT_ID
            )
            return payload
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

validator = KeycloakTokenValidator(settings)

async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.replace("Bearer ", "")
    return await validator.validate_token(token)
```

### Role-Based Access Control

```python
from fastapi import Depends, HTTPException
from typing import List

def require_roles(required_roles: List[str]):
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        user_roles = user.get("realm_access", {}).get("roles", [])
        
        for role in required_roles:
            if role not in user_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required role: {role}"
                )
        
        return user
    
    return role_checker

# Usage
@router.get("/admin/users")
async def get_users(user: dict = Depends(require_roles(["admin"]))):
    return {"users": [...]}
```

### Token Refresh Endpoint

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter()

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token",
            data={
                "grant_type": "refresh_token",
                "client_id": settings.KEYCLOAK_CLIENT_ID,
                "client_secret": settings.KEYCLOAK_CLIENT_SECRET,
                "refresh_token": request.refresh_token
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        data = response.json()
        return TokenResponse(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=data["expires_in"]
        )
```

### React Fetch Wrapper with Refresh-on-401

```typescript
// core/auth/keycloak-auth.store.ts
import { create } from 'zustand';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

interface KeycloakAuthState {
  accessToken: string | null;
  refreshToken: string | null;
  initialize: () => void;
  login: (username: string, password: string) => Promise<void>;
  refresh: () => Promise<string>;
  logout: () => void;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Auth request failed (${res.status})`);
  return res.json() as Promise<T>;
}

export const useKeycloakAuthStore = create<KeycloakAuthState>((set, get) => ({
  accessToken: null,
  refreshToken: null,

  initialize: () => {
    const storedAccess = localStorage.getItem('access_token');
    const storedRefresh = localStorage.getItem('refresh_token');
    if (storedAccess && storedRefresh) {
      set({ accessToken: storedAccess, refreshToken: storedRefresh });
    }
  },

  login: async (username, password) => {
    const response = await postJson<TokenResponse>('/api/auth/login', { username, password });
    setTokens(response, set);
  },

  refresh: async () => {
    const refreshToken = get().refreshToken;
    if (!refreshToken) throw new Error('No refresh token available');

    const response = await postJson<TokenResponse>('/api/auth/refresh', { refresh_token: refreshToken });
    setTokens(response, set);
    return response.access_token;
  },

  logout: () => {
    set({ accessToken: null, refreshToken: null });
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
}));

function setTokens(response: TokenResponse, set: (partial: Partial<KeycloakAuthState>) => void): void {
  set({ accessToken: response.access_token, refreshToken: response.refresh_token });
  localStorage.setItem('access_token', response.access_token);
  localStorage.setItem('refresh_token', response.refresh_token);
}
```

```typescript
// core/api/keycloak-fetch.ts — apiFetch with automatic refresh-and-retry on 401
import { useKeycloakAuthStore } from '../auth/keycloak-auth.store';

export async function keycloakFetch(input: RequestInfo, init: RequestInit = {}): Promise<Response> {
  const { accessToken, refresh, logout } = useKeycloakAuthStore.getState();

  const withAuth = (token: string | null): RequestInit => ({
    ...init,
    headers: { ...init.headers, ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });

  const res = await fetch(input, withAuth(accessToken));

  const isRefreshCall = typeof input === 'string' && input.includes('/auth/refresh');
  if (res.status === 401 && !isRefreshCall) {
    try {
      const newToken = await refresh();
      return fetch(input, withAuth(newToken));
    } catch {
      logout();
      return res;
    }
  }

  return res;
}
```
```

### Angular HTTP Interceptor

```typescript
import { Injectable, inject, signal } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptorFn,
  HttpErrorResponse,
  HttpClient
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject, from, firstValueFrom } from 'rxjs';
import { switchMap, catchError, filter, take } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class KeycloakAuthService {
  private accessToken = signal<string | null>(null);
  private refreshToken = signal<string | null>(null);
  
  private isRefreshing = false;
  private refreshTokenSubject = new BehaviorSubject<string | null>(null);
  
  private http = inject(HttpClient);
  
  async initialize(): Promise<void> {
    // Check for existing tokens in storage
    const storedAccess = localStorage.getItem('access_token');
    const storedRefresh = localStorage.getItem('refresh_token');
    
    if (storedAccess && storedRefresh) {
      this.accessToken.set(storedAccess);
      this.refreshToken.set(storedRefresh);
    }
  }
  
  getToken(): string | null {
    return this.accessToken();
  }
  
  async login(username: string, password: string): Promise<void> {
    const response = await firstValueFrom(
      this.http.post<TokenResponse>('/api/auth/login', { username, password })
    );
    
    this.setTokens(response);
  }
  
  async refresh(): Promise<string> {
    const refresh = this.refreshToken();
    if (!refresh) {
      throw new Error('No refresh token available');
    }
    
    const response = await firstValueFrom(
      this.http.post<TokenResponse>('/api/auth/refresh', { refresh_token: refresh })
    );
    
    this.setTokens(response);
    return response.access_token;
  }
  
  private setTokens(response: TokenResponse): void {
    this.accessToken.set(response.access_token);
    this.refreshToken.set(response.refresh_token);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
  }
  
  logout(): void {
    this.accessToken.set(null);
    this.refreshToken.set(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

export const keycloakInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(KeycloakAuthService);
  const token = authService.getToken();
  
  if (!token) {
    return next(req);
  }
  
  const authReq = req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });
  
  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !req.url.includes('/auth/refresh')) {
        return from(authService.refresh()).pipe(
          switchMap(newToken => {
            const retryReq = req.clone({
              setHeaders: { Authorization: `Bearer ${newToken}` }
            });
            return next(retryReq);
          }),
          catchError(() => {
            authService.logout();
            return throwError(() => error);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
```

### User Sync Service

```python
from keycloak import KeycloakAdmin
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate

class KeycloakUserSync:
    def __init__(self, settings: KeycloakSettings):
        self.keycloak_admin = KeycloakAdmin(
            server_url=settings.KEYCLOAK_URL,
            username="admin",
            password=settings.KEYCLOAK_ADMIN_PASSWORD,
            realm_name=settings.KEYCLOAK_REALM
        )
    
    def sync_user_to_db(self, keycloak_user_id: str, db: Session) -> User:
        # Get user from Keycloak
        kc_user = self.keycloak_admin.get_user(keycloak_user_id)
        
        # Check if exists in DB
        existing = db.query(User).filter(User.keycloak_id == keycloak_user_id).first()
        
        if existing:
            # Update existing user
            existing.email = kc_user["email"]
            existing.first_name = kc_user.get("firstName", "")
            existing.last_name = kc_user.get("lastName", "")
            existing.enabled = kc_user["enabled"]
            db.commit()
            return existing
        
        # Create new user
        new_user = User(
            keycloak_id=keycloak_user_id,
            username=kc_user["username"],
            email=kc_user["email"],
            first_name=kc_user.get("firstName", ""),
            last_name=kc_user.get("lastName", ""),
            enabled=kc_user["enabled"]
        )
        db.add(new_user)
        db.commit()
        return new_user
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Token validation | Decode without verify | JWKS signature verification |
| Role check | String comparison | Realm roles from token |
| Token refresh | After expiry | At 80% of lifespan |
| Multi-tenant | Shared realm | Separate realms or tenant roles |
| Frontend auth | Store in memory | HttpOnly cookies or secure storage |

## Verification checklist

- [ ] Keycloak URL and realm configured
- [ ] JWKS endpoint accessible
- [ ] Token validation with signature verification
- [ ] RBAC with realm roles
- [ ] Token refresh implemented
- [ ] React fetch wrapper configured
- [ ] HTTPS enabled in production
- [ ] User sync service implemented
