---
name: feature-flags
description: "Feature flag patterns for progressive rollout, A/B testing, and kill switches. Covers providers (LaunchDarkly, Unleash, custom), toggle patterns, targeting rules, lifecycle management, cleanup, and CI/CD integration. Trigger: When implementing feature flags, progressive rollouts, or A/B testing in a frontend application."
version: 1.1
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: recommended
  depends_on:
  - react
  - angular
  consumed_by:
  - react
  - angular
  - ci-cd
  agent_roles:
  - delivery-agent
  validation_profile: architecture-consistency
  mcp_usage: none
---

# feature-flags

## Propósito

Esta skill define cómo implementar feature flags (toggles) para control de release progresivo, A/B testing y kill switches de forma segura, trazable y con lifecycle de gestión.  
Su función es asegurar que las features puedan activarse/desactivarse sin deploy, que el rollout sea gradual y controlado, y que las flags muertas se limpien periódicamente.

Esta skill complementa `react` o `angular` (componentes, hooks/directivas, contexto/servicios, según el framework elegido por el proyecto) y `ci-cd` (pipelines). Mientras aquellos definen la UI y el deploy, esta skill define qué features son visibles para quiénes y cuándo.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué proveedor de feature flags usar (LaunchDarkly, Unleash, custom)?
2. ¿Qué tipos de flags existen y cuándo usar cada uno?
3. ¿Cómo se implementan targeting rules por usuario, tenant y porcentaje?
4. ¿Cómo se gestiona el lifecycle de una flag (crear, activar, deprecar, eliminar)?
5. ¿Cómo se limpian las flags muertas?

## Relación con otras skills

- `react` o `angular` define los componentes/hooks/directivas que esta skill condiciona con flags (según el framework elegido por el proyecto).
- `ci-cd` puede usar flags para gates de deploy y canary releases.
- `authentication` proporciona la identidad del usuario para targeting rules.
- `authorization` puede determina qué flags ve cada rol.
- `framework-operations-evolution` gestiona el lifecycle de flags en producción.

## Qué debe hacer el agente cuando esta skill está activa

1. Evaluar y seleccionar el proveedor de feature flags (LaunchDarkly, Unleash, custom).
2. Definir los tipos de flags y cuándo usar cada uno (boolean, multivariate, kill switch).
3. Crear el componente `<FeatureFlag>` y el hook `useFeatureFlag` para React, o la directiva `*featureFlag` y el servicio `FeatureFlagsService` para Angular, según el framework elegido por el proyecto.
4. Definir las targeting rules (por usuario, tenant, porcentaje, entorno).
5. Establecer el lifecycle de flags (draft → active → deprecated → removed).
6. Definir la convención de naming de flags.
7. Configurar la integración con CI/CD para reportar flags activas.
8. Establecer un proceso de cleanup periódico de flags muertas.

## Entradas esperadas

Esta skill asume que ya existe:
- estructura de componentes y hooks (`react`);
- autenticación que identifica al usuario (`authentication`);
- autorización que define roles (`authorization`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- selección de proveedor de feature flags;
- tipos de flags y patrones de uso;
- directiva wrapper `*featureFlag`;
- targeting rules y rollout rules;
- lifecycle de flags;
- convención de naming;
- integración con CI/CD;
- proceso de cleanup.

La fase no incluye todavía:
- implementación del backend del proveedor (si es custom);
- A/B testing con tracking de métricas avanzado;
- feature flags en el backend (esta skill cubre frontend).

## Principios que siempre debe respetar

- Las flags NUNCA deben reemplazar la autorización (una flag no es un permiso).
- Las flags de kill switch DEBEN ser evaluadas lo antes posible en el render.
- Las flags MUERTAS (deprecated) DEBEN eliminarse en el siguiente sprint.
- El valor por defecto de una flag DEBE ser el comportamiento seguro (off para features nuevas).
- Las targeting rules DEBEN ser auditables (quién ve qué y por qué).
- El naming de flags DEBE seguir una convención consistente y predecible.
- Las flags NO deben anidarse (flag dentro de flag es un antipatrón).

## Qué decide esta skill y qué delega

Esta skill sí decide:
- el proveedor de feature flags;
- los tipos de flags y su uso;
- el componente wrapper `<FeatureFlag>` y el hook `useFeatureFlag`;
- la convención de naming;
- el lifecycle de gestión;

Esta skill delega:
- la estructura de componentes y hooks a `react`;
- la autenticación del usuario a `authentication`;
- la autorización de roles a `authorization`;
- la integración con pipelines a `ci-cd`.

## Qué debe definir el diseño

### 1. Tipos de feature flags

| Tipo | Uso | Valor por defecto | Ejemplo |
|------|-----|-------------------|---------|
| **Release flag** | Controlar si una feature nueva está visible | `false` | `enable-new-dashboard` |
| **Kill switch** | Desactivar una feature en producción rápidamente | `true` | `disable-payments` |
| **Experiment flag** | A/B testing con variantes | `control` | `checkout-layout-variant` |
| **Ops flag** | Comportamiento operativo (logging, rate limiting) | Varía | `verbose-logging` |
| **Permission flag** | Activar feature para usuarios específicos | `false` | `beta-ai-assistant` |

Regla: Si una flag existe solo para permisos, usar `authorization` en vez.

### 2. Proveedor de feature flags

**Decisión por defecto**: Unleash (open source) para self-hosted, LaunchDarkly para SaaS.

| Proveedor | Pros | Contras | Uso recomendado |
|-----------|------|---------|-----------------|
| LaunchDarkly | SaaS, SDKs completos, SDK edge | Costoso, SaaS | Proyectos con presupuesto |
| Unleash | Open source, self-hosted, flexible | Requiere infra propia | Proyectos que exigen self-host |
| Custom (Env + DB) | Sin dependencias, simple | Sin UI, sin targeting | Proyectos simples, MVPs |
|plit | SaaS, experimentation, analytics | Costoso, overkill para flags simples | Proyectos con A/B testing serio |

**Implementación custom mínima** (para MVPs):

```typescript
// src/features/flags/config.ts
export interface FeatureFlags {
  'enable-new-dashboard': boolean;
  'disable-payments': boolean;
  'checkout-layout-variant': 'control' | 'variant-a' | 'variant-b';
  'verbose-logging': boolean;
  'beta-ai-assistant': boolean;
}

export const DEFAULT_FLAGS: FeatureFlags = {
  'enable-new-dashboard': false,
  'disable-payments': false,
  'checkout-layout-variant': 'control',
  'verbose-logging': false,
  'beta-ai-assistant': false,
};
```

### 3. Contexto + hook `useFeatureFlag`

```tsx
// src/features/flags/FeatureFlagsContext.tsx
import { createContext, useContext, type ReactNode } from 'react';
import { DEFAULT_FLAGS, type FeatureFlags } from './config';

const FeatureFlagsContext = createContext<FeatureFlags>(DEFAULT_FLAGS);

export function FeatureFlagsProvider({ flags, children }: { flags: FeatureFlags; children: ReactNode }) {
  return <FeatureFlagsContext.Provider value={flags}>{children}</FeatureFlagsContext.Provider>;
}

export function useFeatureFlag<K extends keyof FeatureFlags>(flag: K): FeatureFlags[K] {
  return useContext(FeatureFlagsContext)[flag];
}

export function useIsFeatureEnabled(flag: keyof FeatureFlags): boolean {
  const value = useContext(FeatureFlagsContext)[flag];
  return typeof value === 'boolean' ? value : value !== 'control';
}
```

### 4. Componente wrapper `<FeatureFlag>`

```tsx
// src/features/flags/FeatureFlag.tsx
import type { ReactNode } from 'react';
import { useContext } from 'react';
import { FeatureFlagsContext } from './FeatureFlagsContext';
import type { FeatureFlags } from './config';

interface FeatureFlagProps {
  flag: keyof FeatureFlags;
  variant?: string;
  fallback?: ReactNode;
  children: ReactNode;
}

export function FeatureFlag({ flag, variant, fallback = null, children }: FeatureFlagProps) {
  const value = useContext(FeatureFlagsContext)[flag];

  const isActive =
    (typeof value === 'boolean' && value) || (typeof value === 'string' && variant && value === variant);

  return isActive ? <>{children}</> : <>{fallback}</>;
}
```

Uso:

```tsx
{/* Renderiza contenido solo si la flag está activa */}
<FeatureFlag flag="enable-new-dashboard">
  <NewDashboard />
</FeatureFlag>

{/* Con variante para A/B testing */}
<FeatureFlag flag="checkout-layout-variant" variant="variant-a">
  <CheckoutVariantA />
</FeatureFlag>

{/* Con fallback explícito */}
<FeatureFlag flag="enable-new-dashboard" fallback={<OldDashboard />}>
  <NewDashboard />
</FeatureFlag>
```

### 5. Evaluación de targeting rules

```typescript
// src/features/flags/evaluate-flags.ts
import { DEFAULT_FLAGS, type FeatureFlags } from './config';

interface TargetingRule {
  flag: keyof FeatureFlags;
  userIds?: string[];
  tenantIds?: string[];
  roles?: string[];
  percentage?: number;
}

interface EvaluateFlagsInput {
  userId?: string;
  tenantId?: string;
  roles?: string[];
  rules?: TargetingRule[];
  remoteFlags?: Partial<FeatureFlags>;
}

function hashPercentage(userId: string, flag: string): number {
  const hash = [...userId + flag].reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return hash % 100;
}

export function evaluateFlags(config: EvaluateFlagsInput = {}): FeatureFlags {
  const { userId, tenantId, roles, rules = [], remoteFlags = {} } = config;
  const evaluated: FeatureFlags = { ...DEFAULT_FLAGS, ...remoteFlags };

  for (const rule of rules) {
    const matchesUser = !rule.userIds || (userId ? rule.userIds.includes(userId) : false);
    const matchesTenant = !rule.tenantIds || (tenantId ? rule.tenantIds.includes(tenantId) : false);
    const matchesRole = !rule.roles || (roles ? roles.some((r) => rule.roles!.includes(r)) : false);
    const matchesPercentage =
      !rule.percentage || (userId ? hashPercentage(userId, rule.flag as string) < rule.percentage : false);

    if (matchesUser && matchesTenant && matchesRole && matchesPercentage) {
      (evaluated as Record<string, boolean | string>)[rule.flag] = true;
    }
  }

  return evaluated;
}
```

Uso en `main.tsx` / raíz de la app:

```tsx
// src/main.tsx
import { evaluateFlags } from './features/flags/evaluate-flags';
import { FeatureFlagsProvider } from './features/flags/FeatureFlagsContext';

const flags = evaluateFlags({
  userId: 'user-123',
  tenantId: 'tenant-abc',
  roles: ['admin'],
  rules: [
    { flag: 'enable-new-dashboard', percentage: 10 },
    { flag: 'beta-ai-assistant', userIds: ['user-123'] },
  ],
  remoteFlags: { 'disable-payments': false },
});

<FeatureFlagsProvider flags={flags}>
  <App />
</FeatureFlagsProvider>;
```

### 6. Directiva wrapper `*featureFlag` (Angular)

```typescript
// src/features/flags/feature-flag.directive.ts
import { Directive, Input, OnInit, TemplateRef, ViewContainerRef } from '@angular/core';
import { FeatureFlagsService } from './feature-flags.service';

@Directive({
  selector: '[featureFlag]',
  standalone: true,
})
export class FeatureFlagDirective implements OnInit {
  @Input('featureFlag') flag!: string;
  @Input('featureFlagVariant') variant?: string;
  @Input('featureFlagFallback') fallbackRef?: TemplateRef<unknown>;

  private hasView = false;

  constructor(
    private templateRef: TemplateRef<unknown>,
    private viewContainer: ViewContainerRef,
    private flagsService: FeatureFlagsService,
  ) {}

  ngOnInit(): void {
    this.evaluate();
  }

  private evaluate(): void {
    const value = this.flagsService.getFlag(this.flag);

    if (typeof value === 'boolean' && value) {
      this.renderTemplate();
      return;
    }

    if (typeof value === 'string' && this.variant && value === this.variant) {
      this.renderTemplate();
      return;
    }

    this.clearView();

    if (this.fallbackRef) {
      this.viewContainer.createEmbeddedView(this.fallbackRef);
      this.hasView = true;
    }
  }

  private renderTemplate(): void {
    if (!this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    }
  }

  private clearView(): void {
    if (this.hasView) {
      this.viewContainer.clear();
      this.hasView = false;
    }
  }
}
```

Uso en template:

```html
<!-- Renderiza contenido solo si la flag está activa -->
<div *featureFlag="'enable-new-dashboard'">
  <app-new-dashboard />
</div>

<!-- Con variante para A/B testing -->
<div *featureFlag="'checkout-layout-variant'; variant: 'variant-a'">
  <app-checkout-variant-a />
</div>

<!-- Con fallback explícito -->
<ng-template #fallback>
  <app-old-dashboard />
</ng-template>
<div *featureFlag="'enable-new-dashboard'; fallbackRef: fallback">
  <app-new-dashboard />
</div>
```

### 7. Servicio `FeatureFlagsService` (Angular)

```typescript
// src/features/flags/feature-flags.service.ts
import { Injectable, InjectionToken, inject } from '@angular/core';
import { DEFAULT_FLAGS, FeatureFlags } from './config';

export const FEATURE_FLAGS_CONFIG = new InjectionToken<Partial<FeatureFlags>>('FEATURE_FLAGS_CONFIG');

@Injectable({ providedIn: 'root' })
export class FeatureFlagsService {
  private config = inject(FEATURE_FLAGS_CONFIG, { optional: true }) ?? {};
  private flags: FeatureFlags = { ...DEFAULT_FLAGS, ...this.config };

  getFlag<K extends keyof FeatureFlags>(flag: K): FeatureFlags[K] {
    return this.flags[flag];
  }

  isFeatureEnabled(flag: keyof FeatureFlags): boolean {
    const value = this.flags[flag];
    return typeof value === 'boolean' ? value : value !== 'control';
  }

  setFlags(flags: Partial<FeatureFlags>): void {
    this.flags = { ...this.flags, ...flags };
  }
}
```

### 8. InjectionToken + Provider con soporte para targeting (Angular)

```typescript
// src/features/flags/feature-flags.provider.ts
import { Provider } from '@angular/core';
import { DEFAULT_FLAGS, FeatureFlags } from './config';
import { FEATURE_FLAGS_CONFIG } from './feature-flags.service';

interface TargetingRule {
  flag: keyof FeatureFlags;
  userIds?: string[];
  tenantIds?: string[];
  roles?: string[];
  percentage?: number;
}

interface FeatureFlagsProviderConfig {
  userId?: string;
  tenantId?: string;
  roles?: string[];
  rules?: TargetingRule[];
  remoteFlags?: Partial<FeatureFlags>;
}

function hashPercentage(userId: string, flag: string): number {
  const hash = [...userId + flag].reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return hash % 100;
}

export function provideFeatureFlags(config: FeatureFlagsProviderConfig = {}): Provider {
  const { userId, tenantId, roles, rules = [], remoteFlags = {} } = config;
  const evaluated = { ...DEFAULT_FLAGS, ...remoteFlags };

  for (const rule of rules) {
    const matchesUser = !rule.userIds || (userId ? rule.userIds.includes(userId) : false);
    const matchesTenant = !rule.tenantIds || (tenantId ? rule.tenantIds.includes(tenantId) : false);
    const matchesRole = !rule.roles || (roles ? roles.some(r => rule.roles!.includes(r)) : false);
    const matchesPercentage = !rule.percentage ||
      (userId ? hashPercentage(userId, rule.flag as string) < rule.percentage : false);

    if (matchesUser && matchesTenant && matchesRole && matchesPercentage) {
      (evaluated as any)[rule.flag] = true;
    }
  }

  return {
    provide: FEATURE_FLAGS_CONFIG,
    useValue: evaluated,
  };
}
```

Uso en `app.config.ts`:

```typescript
// src/app/app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideFeatureFlags } from '../features/flags/feature-flags.provider';

export const appConfig: ApplicationConfig = {
  providers: [
    provideFeatureFlags({
      userId: 'user-123',
      tenantId: 'tenant-abc',
      roles: ['admin'],
      rules: [
        { flag: 'enable-new-dashboard', percentage: 10 },
        { flag: 'beta-ai-assistant', userIds: ['user-123'] },
      ],
      remoteFlags: {
        'disable-payments': false,
      },
    }),
  ],
};
```

### 9. Convención de naming de flags

| Prefijo | Tipo | Ejemplo |
|---------|------|---------|
| `enable-` | Release flag | `enable-new-dashboard` |
| `disable-` | Kill switch | `disable-payments` |
| `exp-` | Experiment (A/B test) | `exp-checkout-layout` |
| `ops-` | Ops flag | `ops-verbose-logging` |
| `beta-` | Permission flag | `beta-ai-assistant` |

Reglas:
- Usar kebab-case: `enable-new-dashboard`, no `enableNewDashboard`.
- Incluir el módulo/feature en el nombre: `enable-orders-export`, no `enable-export`.
- El nombre debe ser autoexplicativo.
- Flags de kill switch empiezan con `disable-`.

### 10. Lifecycle de una feature flag

```
┌────────┐    ┌────────┐    ┌────────────┐    ┌──────────┐    ┌─────────┐
│ DRAFT  │───>│ ACTIVE │───>│ DEPRECATED │───>│ REMOVED  │───>│ CLEANUP │
└────────┘    └────────┘    └────────────┘    └──────────┘    └─────────┘
   │               │              │                 │              │
   │ IMplementing  │ Rolling out  │ Migrate users   │ Code removed │ Git clean
   │ in code       │ to users     │ to new path     │ from code    │
```

Reglas por estado:
- **DRAFT**: La flag existe en código pero valor por defecto es `false`. No visible en UI.
- **ACTIVE**: La flag está en producción, evaluándose por targeting rules. Visible en UI.
- **DEPRECATED**: La flag sigue funcionando pero se anuncia su remoción. Timeline definido.
- **REMOVED**: La flag se elimina del proveedor pero el código aún tiene el fallback.
- **CLEANUP**: Se elimina el código condicional y el fallback, quedando solo el camino "on".

**Tiempo máximo por estado**:
- ACTIVE → DEPRECATED: 2 semanas después de rollout completo.
- DEPRECATED → REMOVED: 1 sprint (2 semanas).
- REMOVED → CLEANUP: 1 sprint.

### 11. Integración con CI/CD

```yaml
# .github/workflows/feature-flags-report.yml
name: Feature Flags Report
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check feature flags
        run: |
          echo "## Feature Flags in this PR" >> $GITHUB_STEP_SUMMARY
          grep -r "enable-\|disable-\|exp-\|ops-\|beta-" src/ --include="*.ts" --include="*.tsx" | \
            sed 's/.*:/- /' >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "⚠️ Remove deprecated flags before merging" >> $GITHUB_STEP_SUMMARY
```

## Preguntas guía

### 1. Sobre proveedor
- ¿Se usa LaunchDarkly, Unleash o implementación custom?
- ¿Se necesita UI de gestión de flags o basta con código?
- ¿Se requiere evaluación en el edge (CDN) o solo en cliente?

### 2. Sobre tipos de flags
- ¿Qué features nuevas necesitan release flags?
- ¿Qué features necesitan kill switches?
- ¿Se planea A/B testing? ¿Con qué métricas?

### 3. Sobre targeting
- ¿Se necesita targeting por usuario individual?
- ¿Se necesita targeting por tenant (multi-tenancy)?
- ¿Se necesita rollout por porcentaje?

### 4. Sobre lifecycle
- ¿Quién aprueba la activación de una flag?
- ¿Cuánto tiempo puede estar una flag en ACTIVE antes de deprecar?
- ¿Quién es responsable del cleanup de flags muertas?

### 5. Sobre testing
- ¿Cómo se testea una feature con flag en off?
- ¿Cómo se testea una feature con flag en on?
- ¿Los tests E2E cubren ambas variantes?

## Salidas esperadas de esta skill

### A. Configuración de feature flags
- Archivo `src/features/flags/config.ts` con tipos y valores por defecto.
- Archivo `src/features/flags/FeatureFlagsContext.tsx` con el contexto y los hooks `useFeatureFlag`/`useIsFeatureEnabled`.
- Archivo `src/features/flags/FeatureFlag.tsx` con el componente wrapper `<FeatureFlag>`.
- Archivo `src/features/flags/evaluate-flags.ts` con `evaluateFlags` (targeting rules).

### B. Documentación de lifecycle
- Diagrama de estados de lifecycle.
- Tiempos máximos por estado.
- Proceso de cleanup.

### C. Integración CI/CD
- Workflow de reporte de flags en PRs.
- Gate de flags deprecated antes de merge.

### D. Consumidores de esta skill
- `react` consume el componente `<FeatureFlag>` y los hooks `useFeatureFlag`/`useIsFeatureEnabled`; `angular` consume la directiva `*featureFlag` y el servicio `FeatureFlagsService`;
- `ci-cd` usa el reporte de flags activas;
- `playwright` testea ambas variantes (flag on/off) en E2E tests.

## Criterios de calidad

- Las flags siguen la convención de naming (prefijo + kebab-case).
- El componente `<FeatureFlag>` tiene fallback explícito.
- Los hooks `useFeatureFlag`/`useIsFeatureEnabled` retornan el tipo correcto, no `any`.
- Los valores por defecto son seguros (off para features nuevas).
- Las targeting rules son auditables.
- El lifecycle de flags está documentado con tiempos máximos.
- Existe proceso de cleanup de flags muertas.
- Los tests E2E cubren flag on y flag off.
- La integración con CI/CD reporta flags en PRs.

## Comportamiento esperado del agente

Cuando el usuario use un `if (isBetaUser)` hardcodeado, el agente debe proponer el componente `<FeatureFlag>` y explicar la ventaja.  
Cuando el usuario anide flags (`flag1 && flag2`), el agente debe advertir que es un antipatrón y proponer una flag compuesta o simplificar.  
Cuando el usuario deje una flag activa permanentemente, el agente debe sugerir cleanup y eliminar el código condicional.  
Cuando el usuario use flags para autorización (`if (flag) grantAdmin()`), el agente debe detener y redirigir a `authorization`.

## Checklist final de la skill

- ¿Se seleccionó el proveedor de feature flags?
- ¿Se definieron los tipos de flags y su uso?
- ¿Se creó el componente `<FeatureFlag>` con fallback?
- ¿Se crearon los hooks `useFeatureFlag`/`useIsFeatureEnabled` con tipado estricto?
- ¿Se configuró `evaluateFlags` con targeting rules?
- ¿Las flags siguen la convención de naming?
- ¿Se documentó el lifecycle de flags con tiempos máximos?
- ¿Se configuró la integración con CI/CD?
- ¿Los tests E2E cubren flag on y flag off?
- ¿Se definió el proceso de cleanup de flags muertas?