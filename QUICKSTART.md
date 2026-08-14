# TIVIT Foundry — Guía Rápida

**Proyecto**: TIVIT Foundry — Laboratorio Interno de IA
**Organización**: TIVIT (Latin America Technology)
**Autor**: Manuel Aliaga — Ingeniero de IA, TIVIT Foundry

## Visión general

El Framework Agéntico es un conjunto de **114 skills** y **4 agentes** que se integran con **OpenCode** (CLI de IA). No es una aplicación que ejecutas — es un sistema de conocimiento que OpenCode carga para trabajar de forma estructurada, siguiendo patrones de diseño, arquitectura, seguridad y testing alineados al stack de TIVIT.

---

## Paso 0: Antes de clonar — ¿qué tan listo está el cliente/proyecto?

Antes de tocar código, corré mentalmente (o con el agente) el checklist de `client-readiness-checklist`: ¿el cliente trae documentación funcional formal, informal, o nada? ¿es un proyecto greenfield o hay que adaptarse a un stack legado? ¿ya hay accesos y arquitectura definida?

- Si la documentación funcional es informal o inexistente, el primer paso real del proyecto es `requirements-intake` ("Documento Cero"): un template que el equipo llena con el cliente para convertir cualquier input ambiguo en una línea base confirmada, antes de escribir la primera Historia de Usuario. No es obligatorio si el cliente ya trae una spec formal completa.
- Si es un proyecto brownfield en un stack legado (COBOL, Java monolítico, etc.), el checklist te lleva al flujo de reanálisis en vez de al flujo greenfield estándar de abajo.

Esto evita el error más caro: arrancar el flujo greenfield de este documento con un cliente que en realidad necesitaba el flujo de reanálisis, o con requerimientos tan ambiguos que el equipo termina repreguntando durante todo el desarrollo.

---

## Paso 1: Clonar el framework en tu proyecto

```powershell
# Opción A: Clonar como subdirectorio
git clone <repo-url> .opencode-framework

# Opción B: Copiar solo la carpeta .opencode a tu proyecto existente
cp -r .opencode-framework/.opencode ./mi-proyecto/
cp .opencode-framework/opencode.json ./mi-proyecto/
cp .opencode-framework/AGENTS.md ./mi-proyecto/
```

## Paso 2: Estructura de tu proyecto

Tu proyecto termina con esta estructura:

```
mi-proyecto/
├── AGENTS.md              ← OpenCode carga esto al iniciar
├── opencode.json          ← Configuración de OpenCode
├── .opencode/
│   ├── skills/            ← 114 skills organizadas por dominio
│   ├── agents/            ← 4 agentes especializados
│   ├── framework/         ← Documentos de gobierno
│   ├── validators/        ← Scripts de validación (PowerShell)
│   ├── scaffold/          ← Templates de generación
│   └── mcp-metadata.json  ← Servidores MCP configurados
├── src/                   ← Tu código
│   ├── backend/           ← Python FastAPI (AI/ML core)
│   ├── api/               ← Bun TypeScript (backend general)
│   └── web/               ← React o Angular (frontend, según el proyecto)
└── database/
    └── migrations/        ← Migraciones PostgreSQL
```

## Paso 3: Flujo de trabajo diario

### 3.1 Iniciar OpenCode

```powershell
# Desde la raíz de tu proyecto
opencode
```

OpenCode carga `AGENTS.md` y detecta las 114 skills + 4 agentes. Ya estás listo.

### 3.2 Flujo típico — Crear un módulo nuevo

**Tú dices:**
> Quiero crear un módulo de gestión de usuarios con login, registro, roles admin/user, y listado paginado.

**El orchestrator (agente principal) analiza tu solicitud y responde:**

> Voy a planificar esto. El flujo será:
> 1. Fase A-B (Gobierno): definir constitución, discovery del módulo, concepción funcional
> 2. Fase C (Scaffold): estructura del proyecto
> 3. Fase D (Especificación): spec de la API
> 4. Fase E (Backend): base de datos, endpoints, auth
> 5. Fase F (Frontend): componentes React (hooks) o Angular (services), según el proyecto
> 6. Fase G (Calidad): tests, revisión, adversarial review
> 
> Empecemos con la Fase A. ¿Confirmas?

**Tú confirmas.** El orchestrator delega a los agentes especializados:

```
Fase A-B (confirmación por skill — tú ves y apruebas cada paso):
  ├── N0: requirements-intake → design agent   (condicional — solo si el
  │     cliente no trae documentación funcional formal, ver Paso 0)
  │     "Genero el Documento Cero con las 10 secciones a partir de lo
  │      que el cliente entregó, listo para confirmar con él"
  │     [Tú confirmas]
  ├── N1: framework-governance → control agent
  │     "Defino las reglas del proyecto: multi-tenant, RBAC, audit"
  │     [Tú confirmas]
  ├── N2: framework-discovery → design agent
  │     "Analizo: actores (admin, usuario), procesos (registro, login, CRUD),
  │      datos (users, roles, sessions)"
  │     [Tú confirmas]
  ├── N3: framework-conception → design agent
  │     "Capacidades: autenticación, autorización, gestión de usuarios.
  │      MVP: login + registro + CRUD básico"
  │     [Tú confirmas]
   └── N4: hu-template → design agent
         "HU del MVP: login, CRUD básico, roles..."
         [Tú confirmas]

Fase C-H (confirmación por bundle — más rápido):
  Fase C (Scaffold) → 1 confirmación
  Fase D (Especificación) → 1 confirmación
  Fase E (Backend) → 1 confirmación
  ...
```

### 3.3 ¿Qué genera cada fase?

| Fase | ¿Qué produce? | Archivos de ejemplo |
|------|--------------|-------------------|
| **Documento Cero** (N0, condicional) | Línea base de requerimientos confirmada | `docs/documento-cero-{modulo}.md` |
| **Governance** | Reglas del proyecto | `constitution.md` |
| **Discovery** | Análisis del dominio | Documento de actores, procesos, datos |
| **Conception** | Definición funcional | Capacidades, flujos, criterios MVP |
| **Scaffold** | Estructura del proyecto | `src/`, `database/`, `.env.example` |
| **Spec** | Especificación API | `specs/users-api.md` con ERD, endpoints, errores |
| **Backend** | Código del servidor | `handlers/`, `dtos/`, `routes/`, funciones PL/pgSQL |
| **Frontend** | Componentes React o Angular | `UsersList.tsx`/`UsersListComponent.ts`, `LoginPage.tsx`/`LoginPageComponent.ts` |
| **Calidad** | Tests + revisión + evidencia de aceptación | Unit tests, integration tests, adversarial review, reporte JSON de `acceptance-test-automation` (pass/fail/ambiguo por criterio) |
| **Operación** | CI/CD + deploy | `github-actions.yml`, `docker-compose.yml` |

### 3.4 Ejemplo concreto de output

**Tú dices:** "Crea el endpoint de login"

**El agente (delivery) carga la skill `authentication`, consulta a `keycloak` y genera:**

```python
# backend/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException
from app.auth.keycloak import KeycloakTokenValidator

router = APIRouter(prefix="/auth", tags=["auth"])
validator = KeycloakTokenValidator(settings)

@router.post("/login")
async def login(credentials: LoginRequest):
    # Valida contra Keycloak via OIDC
    token = await validator.authenticate(
        username=credentials.username,
        password=credentials.password
    )
    return {"access_token": token.access_token, 
            "refresh_token": token.refresh_token,
            "expires_in": token.expires_in}
```

```tsx
// web/src/features/auth/LoginPage.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../core/auth/auth.store';

const loginSchema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

export function LoginPage() {
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();
  const { register, handleSubmit } = useForm({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (values: z.infer<typeof loginSchema>) => {
    await login(values.username, values.password);
    navigate('/dashboard');
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('username')} />
      <input type="password" {...register('password')} />
      <button type="submit">Sign in</button>
    </form>
  );
}
```

## Paso 4: Modos de ejecución (tú controlas el ritmo)

| Modo | Cuándo usarlo | Cómo se siente |
|------|--------------|---------------|
| **Hybrid (default)** | Proyectos nuevos | Fases iniciales: revisas cada decisión. Resto: más rápido con bundles |
| **Meta-Skills** | Módulos repetitivos | "Crea otro CRUD como el de usuarios" → 1 confirmación |
| **Per-Skill** | Auditoría, aprendizaje | Ves y apruebas cada uno de los 49 pasos |

## Paso 5: Skills bajo demanda

No necesitas pasar por todo el flujo. Puedes invocar skills específicas directamente:

```
"Necesito crear stored procedures para el módulo de inventario"
  → Activa database-sp

"Revisa la seguridad de este endpoint"
  → Activa security + review-adversarial

"Configura el CI/CD para este proyecto"
  → Activa ci-cd

"Genera la especificación de la API de órdenes"
  → Activa api-first-spec
```

## Paso 6: Validación

```powershell
# Verifica que el framework está íntegro
.\.opencode\validators\run-all.ps1

# Output esperado:
#   OK check-dependencies
#   OK check-refs
#   OK check-secrets       (secretos hardcodeados y URLs hardcodeadas en código)
#   ... 15/15 passed
```

## Paso 7: El ciclo diario

```
Mañana:
  1. Abres OpenCode en tu proyecto
  2. El agente carga el estado del workflow (.workflow/state.json)
  3. Te pregunta: "¿Retomar donde quedamos ayer?"
  4. Continúas exactamente donde estabas

Durante el día:
  - Tú pides features → el orchestrator planifica → los agentes ejecutan
  - Tú confirmas en puntos clave (HITL)
  - Las decisiones se guardan en memoria (memory-protocol)
  - El código generado sigue la constitución (governance-constitution)

Al final del día:
  - El agente guarda summary de la sesión
  - Las decisiones importantes persisten para mañana
  - Nada se pierde entre sesiones
```

---

## Resumen: ¿Qué hace el framework por ti?

| Sin el framework | Con el framework |
|-----------------|-----------------|
| "Crea un endpoint" → output genérico | "Crea un endpoint" → código FastAPI con tipos Pydantic, manejo de errores, JWT Keycloak, tests |
| Cada sesión empieza de cero | La memoria persiste — decisiones y contexto sobreviven |
| El agente inventa patrones | El agente sigue patrones validados del framework |
| Sin estándares de código | Constitution con 9 artículos + anti-patterns bloqueados |
| Review manual | Adversarial review con 3+ perspectivas automáticas |
| Stack inconsistente | Stack forzado: Python/React-o-Angular/Bun/PostgreSQL |
| Sin trazabilidad | Evidencia en cadena para compliance |
| Setup manual cada vez | `.workflow/state.json` — resume automático |
