---
name: design-system
description: 'Visual design system: colors, typography, spacing, component wrappers,
  and theming. Trigger: When styling components, choosing colors, or applying visual
  patterns.'
version: 1.0
metadata:
  phase:
  - inception
  - construction
  layer:
  - frontend
  enforcement: mandatory
  depends_on: []
  consumed_by:
  - angular
  - agent-frontend
  - agent-fullstack
  agent_roles:
  - design-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Use Angular component styles (SCSS) | ALWAYS | Scoped styles, encapsulation via ViewEncapsulation |
| Use design tokens (not raw values) | ALWAYS | Consistency |
| Use design system icons | ALWAYS | Visual consistency |
| Hardcode colors outside tokens | NEVER | Maintainability |
| Use component wrappers, not UI library directly | ALWAYS | Consistent project-level styling |
| Wrap new UI library components following wrapper pattern | ALWAYS | Design consistency |
| Prefer standalone components | ALWAYS | Lazy loading, tree-shaking, simpler imports |

## Color Tokens

### Primary Colors
```css
--color-primary: #007788;
--color-primary-hover: #5b8def;
--color-link: #1890ff;
```

### Semantic Colors
```css
--color-success-bg: #f6ffed; --color-success: #52c41a;
--color-warning-bg: #fff7e6; --color-warning: #fa8c16;
--color-error-bg: #fff2f0;   --color-error: #ff4d4f;
--color-info-bg: #e6f7ff;    --color-info: #1890ff;
```

### Text Colors (Grays)
```css
--color-text-title: #262626;
--color-text-primary: #4a5568;
--color-text-secondary: #595959;
--color-text-muted: #8c8c8c;
--color-text-disabled: #bfbfbf;
```

### UI Colors (Grays)
```css
--color-bg-page: #f5f5f5;
--color-bg-card: #ffffff;
--color-border: #d9d9d9;
--color-border-light: #e8e8e8;
```

### Status Badge Colors
| Status | Background | Text |
|--------|------------|------|
| Draft | `#e5e7eb` | `#374151` |
| Pending | `#fef3c7` | `#92400e` |
| In Progress | `#dbeafe` | `#1e40af` |
| Approved | `#d1fae5` | `#065f46` |
| Rejected | `#fee2e2` | `#991b1b` |

## Typography
| Role | Size | Weight |
|------|------|--------|
| H1 | 24px | 600 |
| H2 | 20px | 600 |
| H3 | 16px | 600 |
| Body | 14px | 400 |
| Small | 13px | 400 |
| Caption | 12px | 400 |

## Spacing (Base 4px)
| Token | Value |
|-------|-------|
| `xs` | 4px |
| `sm` | 8px |
| `md` | 12px |
| `lg` | 16px |
| `xl` | 24px |

## Border Radius
| Context | Value |
|---------|-------|
| Badges / Tags | 4px |
| Cards / Inputs | 8px |
| Avatars / Chips | 50% |

## Shadows
| Context | Value |
|---------|-------|
| Card | `0 1px 2px rgba(0,0,0,0.03)` |
| Hover | `0 2px 8px rgba(0,0,0,0.08)` |
| Elevated | `0 4px 12px rgba(0,0,0,0.15)` |

## Layout Constants
```css
--header-height: 56px;
--sidebar-width: 220px;
--sidebar-collapsed-width: 80px;
```

## Component Wrapper Pattern (Angular)
```ts
// project-button.component.ts — Standalone wrapper for consistent project styling
import { Component, Input } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-project-button',
  standalone: true,
  imports: [MatButtonModule],
  template: `
    <button mat-flat-button [color]="color" [class]="'size-' + size">
      <ng-content />
    </button>
  `,
  styles: [`
    .size-large { padding: var(--spacing-md) var(--spacing-lg); font-size: 16px; }
    .size-small { padding: var(--spacing-xs) var(--spacing-sm); font-size: 12px; }
  `],
})
export class ProjectButtonComponent {
  @Input() color: 'primary' | 'accent' | 'warn' = 'primary';
  @Input() size: 'small' | 'large' = 'large';
}
```

**Directiva de estilos del proyecto** (opcional, para inyectar tokens):
```ts
import { Directive, HostBinding } from '@angular/core';

@Directive({ selector: '[appTokenSpacing]', standalone: true })
export class TokenSpacingDirective {
  @HostBinding('style.padding') padding = 'var(--spacing-md)';
}
```

## Theme Configuration (Angular Material)
```ts
// app.config.ts — Application-wide Material theme
import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import {
  MAT_DATE_LOCALE,
  MatNativeDateModule,
} from '@angular/material/core';
import {
  ThemePalette,
  provideTheme,
} from '@angular/material/core';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimationsAsync(),
    importProvidersFrom(MatNativeDateModule),
    { provide: MAT_DATE_LOCALE, useValue: 'es-MX' },
  ],
};
```

**SCSS theme overrides** (`styles/_theme.scss`):
```scss
@use '@angular/material' as mat;

$project-primary: mat.define-palette(mat.$indigo-palette, #007788);
$project-accent:  mat.define-palette(mat.$pink-palette);
$project-warn:    mat.define-palette(mat.$red-palette);

$project-theme: mat.define-light-theme((
  color: (
    primary: $project-primary,
    accent:  $project-accent,
    warn:    $project-warn,
  ),
  typography: mat.define-typography-config(),
));

@include mat.core-theme($project-theme);
@include mat.all-component-themes($project-theme);
```

**PrimeNG alternative** (`app.config.ts`):
```ts
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeng/themes/aura';

export const appConfig: ApplicationConfig = {
  providers: [
    providePrimeNG({
      theme: {
        preset: Aura,
        options: {
          darkModeSelector: '.dark-mode',
          cssLayer: { name: 'primeng', order: 'tailwind-base, primeng, tailwind-utilities' },
        },
      },
    }),
  ],
};
```

## Core Component Catalog
Wrappers to create for consistent styling (Angular Material / PrimeNG equivalents):
- MatInput / p-inputText, MatTextarea / p-textarea, MatAutocomplete / p-autoComplete
- MatSelect / p-dropdown, MatDatePicker / p-calendar, MatTimepicker / p-timepicker
- MatFormField / p-floatlabel, MatInputNumber / p-inputNumber
- MatButton / p-button, MatSlideToggle / p-toggleswitch, MatRadio / p-radiobutton, MatCheckbox / p-checkbox
- MatTable / p-table (generic `T extends object`)
- MatDialog / p-dialog, MatSidenav / p-sidebar
- MatCard / p-card, MatChip / p-chip, MatExpansionPanel / p-accordion, MatTabGroup / p-tabview
- MatProgressBar / p-progressbar, MatAvatar / p-avatar, MatDivider, MatDivider / p-divider
- MatTypography (directive)
- MatDescriptionList / p-description, MatConfirmDialog / p-confirmdialog

## Angular Component Style Patterns
```scss
/* SCSS with design tokens — components use ViewEncapsulation.Emulated by default */
:host {
  display: block;
  padding: var(--spacing-lg);
}
.title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-title);
}
```

## Diseño moderno de UI

### 1. Angular UI Libraries — Primitivas de componentes, integración con Material Design

Las librerías de UI en Angular ofrecen componentes listos para producción con accesibilidad integrada, theming configurable y soporte multi-tema.

**Angular Material (Material Design):**
- Se instala vía `ng add @angular/material` y genera schematics para generar componentes
- Cada componente es un **Módulo standalone** (Angular 15+) o un `NgModule` clásico
- Ejemplo de anatomía: `MatDialog` usa `MatDialogModule` + `MatDialogRef<T>` + `MatDialogConfig`, estilados con SCSS y Material theming

**PrimeNG:**
- Se instala vía `npm install primeng` con themes configurables (Aura, Lara, Nora, etc.)
- Componentes standalone y directivas (`p-` prefix)
- Estilos via CSS Layer con integración Tailwind

**NG-ZORRO (Ant Design para Angular):**
- Se instala vía `ng add ng-zorro-antd`
- Componentes con `nz-` prefix, theming con less o SCSS
- Estructura similar a Ant Design React pero adaptada a Angular

**Patrón de wrapper en Angular:**
- Crear componentes standalone en `src/app/shared/components/` que envuelvan el componente de la UI library
- Aplicar tokens del proyecto via SCSS y configuración de theming
- Los wrappers exponen una API simplificada y consistente para el equipo

**Estructura de archivos:**
```
src/
  app/
    shared/
      components/          ← wrappers del proyecto (project-button, search-dialog)
      ui/                  ← primitivas o wrappers reutilizables (ui-button, ui-table)
    features/
    core/
```

**Regla del framework:** Los componentes de `ui/` encapsulan la UI library y NO contienen lógica de negocio. Los wrappers en `shared/components/` aplican tokens, comportamiento y estilos del proyecto.

### 2. Tailwind CSS como vehículo de tokens — clases utilitarias que mapean a design tokens

Tailwind CSS actúa como **capa de entrega** entre los design tokens y el código de los componentes. En vez de escribir `padding: var(--spacing-lg)`, se usa `p-lg` (clase utilitaria que internamente resuelve el token).

**Configuración en `tailwind.config.ts`:**
```ts
import type { Config } from 'tailwindcss';

export default {
  theme: {
    extend: {
      colors: {
        primary:        'var(--color-primary)',
        'primary-hover':'var(--color-primary-hover)',
        success:        'var(--color-success)',
        warning:        'var(--color-warning)',
        error:          'var(--color-error)',
        info:           'var(--color-info)',
      },
      spacing: {
        xs: 'var(--spacing-xs)',
        sm: 'var(--spacing-sm)',
        md: 'var(--spacing-md)',
        lg: 'var(--spacing-lg)',
        xl: 'var(--spacing-xl)',
      },
      borderRadius: {
        badge:  '4px',
        card:   '8px',
        avatar: '50%',
      },
      fontSize: {
        h1: ['24px', { lineHeight: '1.3', fontWeight: '600' }],
        h2: ['20px', { lineHeight: '1.4', fontWeight: '600' }],
        h3: ['16px', { lineHeight: '1.5', fontWeight: '600' }],
        body: ['14px', { lineHeight: '1.6' }],
        small: ['13px', { lineHeight: '1.5' }],
        caption: ['12px', { lineHeight: '1.5' }],
      },
    },
  },
} satisfies Config;
```

**Flujo de token a clase:**
```
Design Token (JSON/YAML) → tokens.css (CSS custom properties) → tailwind.config.ts → className="p-lg text-primary"
```

**Reglas:**
- NUNCA usar valores hardcodeados en clases (`p-4`, `text-[#007788]`). SIEMPRE usar los aliases definidos en `theme.extend`
- Los tokens semánticos (`primary`, `success`, `error`) tienen prioridad sobre tokens primitivos (`blue-500`, `red-600`)

### 3. CSS Custom Properties como puente de tokens — cómo tokens.css mapea a Tailwind config

El archivo `tokens.css` es el **único origen de verdad en runtime** para los valores visuales. Tailwind lo referencia, pero los valores se resuelven en el navegador vía CSS custom properties.

**Estructura de `tokens.css`:**
```css
@layer tokens {
  :root {
    /* ── Colores primarios ── */
    --color-primary:        #007788;
    --color-primary-hover:  #0099aa;
    --color-link:           #1890ff;

    /* ── Colores semánticos ── */
    --color-success-bg: #f6ffed; --color-success: #52c41a;
    --color-warning-bg: #fff7e6; --color-warning: #fa8c16;
    --color-error-bg:   #fff2f0; --color-error:   #ff4d4f;
    --color-info-bg:    #e6f7ff; --color-info:    #1890ff;

    /* ── Tipografía ── */
    --font-family-sans: 'Inter', system-ui, -apple-system, sans-serif;
    --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;

    /* ── Espaciado ── */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 12px;
    --spacing-lg: 16px;
    --spacing-xl: 24px;

    /* ── Layout ── */
    --header-height: 56px;
    --sidebar-width: 220px;
    --sidebar-collapsed-width: 80px;
  }

  /* ── Tema oscuro ── */
  .dark {
    --color-primary:       #33b8c4;
    --color-primary-hover: #5cd4de;
    --color-bg-page:       #1a1a1a;
    --color-bg-card:       #2a2a2a;
    --color-text-title:    #e5e5e5;
    --color-text-primary:  #d4d4d4;
    --color-border:        #404040;
  }
}
```

**Patrón de puente:**
| Capa | Responsabilidad | Ejemplo |
|------|-----------------|---------|
| `tokens.css` | Define valores como `--color-primary` | `#007788` |
| `tailwind.config.ts` | Mapea `primary` → `var(--color-primary)` | `colors: { primary: 'var(--color-primary)' }` |
| Componente | Usa la clase Tailwind | `class="bg-primary text-white"` |

**Regla:** Cambiar un color → cambiar `tokens.css`. Tailwind y componentes Angular se actualizan automáticamente sin tocar ningún componente.

### 4. Formatos de design tokens — Style Dictionary, estándar DTCG, tokens JSON

**Formatos de origen (source of truth):**

| Formato | Uso | Extensión |
|---------|-----|-----------|
| JSON (DTCG) | Token crudo editable, compatible con herramientas | `.tokens.json` |
| YAML | Alternativa legible para diseñadores | `.tokens.yaml` |
| CSS Custom Properties | Runtime, puente hacia Tailwind | `tokens.css` |

**Estándar DTCG (Design Tokens Community Group):**
```json
{
  "$metadata": {
    "$theme": "light"
  },
  "color": {
    "primary": {
      "$value": "#007788",
      "$type": "color",
      "$description": "Color primario del proyecto IA Digital"
    },
    "primary-hover": {
      "$value": "#0099aa",
      "$type": "color",
      "$description": "Color primario al hacer hover"
    }
  },
  "spacing": {
    "lg": {
      "$value": "16px",
      "$type": "dimension"
    }
  }
}
```

**Style Dictionary — transformación y compilación:**
```js
// config.js
module.exports = {
  source: ['tokens/**/*.tokens.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables',
        options: { outputReferences: true }
      }]
    },
    tailwind: {
      transformGroup: 'js',
      buildPath: 'src/styles/',
      files: [{
        destination: 'tailwind-tokens.js',
        format: 'javascript/module',
        options: { outputReferences: true }
      }]
    }
  }
};
```

**Pipeline de tokens:**
```
tokens/*.tokens.json  →  Style Dictionary  →  tokens.css
                                          →  tailwind-tokens.js  →  tailwind.config.ts
                                          →  tokens.ios.swift     (plataformas futuras)
                                          →  tokens.android.kt    (plataformas futuras)
```

**Regla:** Los archivos `tokens.css` y `tailwind-tokens.js` son **generados**, nunca se editan a mano. El único archivo editable es `tokens/*.tokens.json`.

### 5. Figma → tokens → código — automatización del handoff de diseño

**Flujo de handoff:**

```
Figma (Variables / Styles)
    ↓  Plugin: Figma Tokens (o Token Studio)
    ↓  Exportar como JSON (DTCG)
tokens/*.tokens.json
    ↓  Style Dictionary (build)
tokens.css + tailwind-tokens.js
    ↓  Tailwind + Angular Material / PrimeNG
Componentes Angular
```

**Configuración en Figma:**
1. Usar el plugin **Figma Tokens** (o **Token Studio**) para definir variables como tokens DTCG
2. Organizar por conjuntos: `global` (compartido), `light` (tema claro), `dark` (tema oscuro)
3. Sincronizar con repositorio vía GitHub Push Token o JSON bin push

**Estructura de carpetas de tokens:**
```
tokens/
  global.tokens.json     ← tokens compartidos (spacing, radius, shadows)
  light.tokens.json      ← overrides para tema claro
  dark.tokens.json       ← overrides para tema oscuro
  semantic.tokens.json   ← mapeos semánticos (primary → azul, success → verde)
```

**Validaciones en CI:**
- `style-dictionary build` debe pasar sin errores
- Los tokens generados no deben contener valores hardcodeados (solo `var(--...)`)
- Diff en `tokens/*.tokens.json` dispara rebuild de `tokens.css`

**Regla:** Un cambio de color en Figma → PR con cambio en `tokens.json` → CI rebuild → merge automático de CSS generado. Cero intervención manual en CSS.

### 6. Integración con Storybook — documentando componentes con design tokens

Storybook es la **fuente de verdad visual** para el equipo de diseño y desarrollo. Cada componente documentado incluye sus variantes, estados y los tokens que consume.

**Configuración de Storybook con tokens:**
```ts
// .storybook/preview.ts
import type { Preview } from '@storybook/angular';
import '../src/styles/tokens.css';

const preview: Preview = {
  parameters: {
    controls: { expanded: true },
    docs: { source: { type: 'code' } },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: 'var(--color-bg-page)' },
        { name: 'dark',  value: 'var(--color-bg-page-dark, #1a1a1a)' },
      ],
    },
  },
  globalTypes: {
    theme: {
      name: 'Theme',
      description: 'Tema global',
      defaultValue: 'light',
      toolbar: {
        icon: 'circlehollow',
        items: ['light', 'dark'],
        showName: true,
      },
    },
  },
  decorators: [
    (storyFn, context) => {
      const theme = context.globals.theme ?? 'light';
      return `<div class="${theme === 'dark' ? 'dark' : ''}">${storyFn()}</div>`;
    },
  ],
};
export default preview;
```

**Patrón de Story por componente:**
```ts
// project-button.stories.ts
import type { Meta, StoryObj } from '@storybook/angular';
import { ProjectButtonComponent } from './project-button.component';

const meta: Meta<ProjectButtonComponent> = {
  title: 'Shared/ProjectButton',
  component: ProjectButtonComponent,
  tags: ['autodocs'],
  argTypes: {
    color: {
      control: 'select',
      options: ['primary', 'accent', 'warn'],
      description: 'Color del botón (Material palette)',
      table: {
        defaultValue: { summary: 'primary' },
        category: 'Design Token',
      },
    },
    size: {
      control: 'select',
      options: ['small', 'large'],
      description: 'Tamaño del botón',
    },
  },
  parameters: {
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/XXXX?node-id=123',
    },
  },
};
export default meta;

type Story = StoryObj<ProjectButtonComponent>;

export const Primary: Story = {
  args: { color: 'primary', size: 'large' },
  render: (args) => ({
    props: args,
    template: `<app-project-button [color]="color" [size]="size">Primario</app-project-button>`,
  }),
};

export const Warn: Story = {
  args: { color: 'warn', size: 'large' },
  render: (args) => ({
    props: args,
    template: `<app-project-button [color]="color" [size]="size">Eliminar</app-project-button>`,
  }),
};

export const AllVariants: Story = {
  render: () => ({
    template: `
      <div style="display:flex;gap:var(--spacing-md)">
        <app-project-button color="primary" size="large">Primario</app-project-button>
        <app-project-button color="accent" size="large">Accent</app-project-button>
        <app-project-button color="warn" size="large">Eliminar</app-project-button>
      </div>
    `,
  }),
};
```

**Addons recomendados:**
| Addon | Función |
|-------|---------|
| `@storybook/addon-a11y` | Validación de accesibilidad en cada story |
| `@storybook/addon-backgrounds` | Cambio de fondo claro/oscuro con tokens |
| `@storybook/addon-designs` | Link a mockup de Figma directamente |
| `storybook-dark-mode` | Toggle de tema global (light/dark) |
| `@storybook/addon-measure` | Mediciones de spacing con tokens |

**Reglas de Storybook en el framework:**
- Todo componente wrapper en `shared/components/` DEBE tener su `.stories.ts`
- Los componentes primitivos de `ui/` se documentan con `autodocs`
- Las stories deben reference tokens (`var(--spacing-md)`) en vez de valores hardcodeados
- Los cambios de tokens se refluxean automáticamente via `tokens.css` importado globalmente
