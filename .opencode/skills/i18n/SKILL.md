---
name: i18n
description: "Internationalization patterns for frontend applications. Covers @ngx-translate/core, locale file structure, lazy loading by route, fallback chains, pluralization, RTL support, date/number/currency formatting, and key extraction. Trigger: When implementing multi-language support or localization in a frontend application."
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: mandatory
  depends_on:
  - angular
  - typescript
  consumed_by:
  - angular
  - api-first-frontend
  agent_roles:
  - delivery-agent
  validation_profile: skill-contract
  mcp_usage: none
---

# i18n

## Propósito

Esta skill define cómo implementar internacionalización (i18n) y localización (l10n) en aplicaciones frontend de forma escalable, mantenible y compatible con multi-tenancy.  
Su función es asegurar que la aplicación pueda soportar múltiples idiomas, formatos regionales y direcciones de texto sin duplicar lógica ni componentes.

Esta skill complementa `angular` (componentes) y `typescript` (tipos). Mientras esos definen la estructura de la UI, esta skill define cómo hacer esa UI multilingüe.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué librería de i18n usar y cómo se configura?
2. ¿Cómo se estructura el almacenamiento de traducciones?
3. ¿Cómo se hace lazy loading de traducciones por ruta?
4. ¿Cómo se manejan pluralización, interpolación y género?
5. ¿Cómo se soporta RTL (árabe, hebreo)?
6. ¿Cómo se formatean fechas, números y monedas por locale?

## Relación con otras skills

- `angular` define los componentes que esta skill internacionaliza.
- `typescript` define los tipos de las claves de traducción.
- `api-first-frontend` genera tipos que pueden incluir campos localizados.
- `design-system` define tokens que pueden variar por locale (fuentes RTL, spacing).

## Qué debe hacer el agente cuando esta skill está activa

1. Configurar la librería de i18n (@ngx-translate/core por defecto).
2. Crear la estructura de carpetas de locales con namespaces por módulo.
3. Definir el tipo TypeScript para las claves de traducción.
4. Implementar el detector de idioma y el fallback chain.
5. Configurar lazy loading de traducciones por ruta/módulo.
6. Implementar el componente de cambio de idioma.
7. Definir la convención de naming de claves de traducción.
8. Configurar formateo de fechas, números y monedas por locale.

## Entradas esperadas

Esta skill asume que ya existe:
- estructura de componentes (`angular`);
- tipos TypeScript definidos (`typescript`);
- diseño de sistema (`design-system`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- configuración de @ngx-translate/core;
- estructura de locales con namespaces;
- tipo TypeScript para claves de traducción;
- lazy loading por ruta;
- fallback chains;
- pluralización e interpolación;
- soporte RTL;
- formateo de fechas, números y monedas;
- componente de cambio de idioma;
- extracción automática de claves.

La fase no incluye todavía:
- traducción profesional de contenido (solo infraestructura técnica);
- integración con servicios de traducción externos (Transifex, Lokalise);
- contenido dinámico desde backend (eso requiere endpoints localizados).

## Principios que siempre debe respetar

- Las claves de traducción NUNCA deben ser el texto en sí (`t('user.name')`, no `t('User Name')`).
- Los archivos de locale DEBEN estar organizados por namespace/módulo, no en un archivo gigante.
- Los idiomas DEBEN tener fallback chain explícita (`es-MX` → `es` → `en`).
- El lazy loading DEBEN ser por ruta/módulo, no por idioma completo.
- Los componentes DEBEN funcionar con cualquier idioma sin cambios de layout significativos.
- Los formatos de fecha/número/moneda DEBEN usar Intl API, nunca formateo manual.
- Las claves de traducción DEBEN tener tipo TypeScript estricto (no `string`).
- Las traducciones faltantes DEBEN mostrar la clave, no un string vacío.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la librería de i18n (@ngx-translate/core por defecto);
- la estructura de carpetas y namespaces;
- la convención de naming de claves;
- la estrategia de fallback y lazy loading.

Esta skill delega:
- la estructura general de componentes a `angular`;
- los tipos TypeScript a `typescript`;
- el contenido traducido a traductores profesionales;
- el contenido dinámico desde backend a `backend-api`.

## Qué debe definir el diseño

### 1. Librería y configuración

**Decisión por defecto**: @ngx-translate/core con TranslateModule.

```typescript
// src/app/app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClient } from '@angular/common/http';
import { TranslateModule, TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { AppComponent } from './app.component';

export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}

@NgModule({
  imports: [
    BrowserModule,
    TranslateModule.forRoot({
      defaultLanguage: 'en',
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient],
      },
    }),
  ],
  declarations: [AppComponent],
  bootstrap: [AppComponent],
})
export class AppModule {}
```

```typescript
// src/app/app.module.ts — lazy loading por módulo
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
  imports: [
    TranslateModule.forChild({
      extend: true, // hereda la configuración del root
    }),
  ],
})
export class FeatureModule {}
```

### 2. Estructura de locales

```
/src/assets/i18n/
├── en.json
├── es.json
├── es-MX.json        ← solo overrides específicos de México
└── pt-BR.json
```

Reglas:
- Un archivo JSON por idioma.
- Los archivos de locale regional (`es-MX`) solo contienen overrides, no traducciones completas.
- El locale base (`es`) contiene la traducción completa.
- El fallback chain es: `es-MX` → `es` → `en`.
- Se pueden usar namespaces anidados dentro de cada archivo JSON (estructura jerárquica).

### 3. Convención de naming de claves

```json
{
  "common": {
    "actions": {
      "save": "Save",
      "cancel": "Cancel",
      "delete": "Delete",
      "confirm": "Confirm"
    },
    "validation": {
      "required": "This field is required",
      "email": "Invalid email address"
    }
  },
  "auth": {
    "login": {
      "title": "Sign In",
      "emailPlaceholder": "Enter your email",
      "passwordPlaceholder": "Enter your password",
      "submit": "Sign In",
      "forgotPassword": "Forgot password?"
    }
  }
}
```

Reglas:
- Claves en camelCase: `user.name`, `auth.login.title`.
- Estructura jerárquica: `módulo.pantalla.elemento`.
- Nunca usar el texto en inglés como clave.
- Nunca usar claves numéricas o autogeneradas.

### 4. Tipo TypeScript para claves

```typescript
// src/app/shared/types/i18n.types.ts
import en from '../../../assets/i18n/en.json';

type NestedMessages = { [key: string]: string | NestedMessages };

export type TranslationKey = keyof typeof en;

// Tipo recursivo para claves anidadas (e.g., 'auth.login.title')
export type DeepTranslationKey<T extends NestedMessages> = {
  [K in keyof T & string]: T[K] extends NestedMessages
    ? `${K}.${DeepTranslationKey<T[K]>}`
    : K;
}[keyof T & string] | (keyof T & string);

export type AllTranslationKeys = DeepTranslationKey<typeof en>;
```

```typescript
// Tipado global para ngx-translate (opcional pero recomendado)
// src/types/ngx-translate.d.ts
declare module '@ngx-translate/core' {
  interface TranslateService {
    instant(key: AllTranslationKeys, params?: Record<string, unknown>): string;
    get(key: AllTranslationKeys, params?: Record<string, unknown>): Observable<string>;
  }
}
```

### 5. Uso en componentes

```typescript
// src/app/features/auth/login.component.ts
import { Component, OnInit } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
})
export class LoginComponent implements OnInit {
  constructor(private translate: TranslateService) {
    // Establecer idiomas soportados y fallback
    this.translate.addLangs(['en', 'es', 'pt-BR']);
    this.translate.setDefaultLang('en');
    this.translate.use('en');
  }

  ngOnInit() {}
}
```

```html
<!-- src/app/features/auth/login.component.html -->
<div>
  <h1>{{ 'auth.login.title' | translate }}</h1>
  <input [placeholder]="'auth.login.emailPlaceholder' | translate" />
  <input [placeholder]="'auth.login.passwordPlaceholder' | translate" type="password" />
  <button>{{ 'auth.login.submit' | translate }}</button>
  <a href="/forgot-password">{{ 'auth.login.forgotPassword' | translate }}</a>
</div>
```

### 6. Pluralización e interpolación

```json
{
  "notifications": {
    "items": "{count, plural, =1 {# item} other {# items}}",
    "welcome": "Welcome, {{name}}!",
    "lastLogin": "Last login: {{date, date}}",
    "balance": "Balance: {{amount, currency}}"
  }
}
```

```typescript
// Uso en componente
@Component({ ... })
export class DashboardComponent {
  constructor(private translate: TranslateService) {}

  getCountTranslation(count: number): string {
    return this.translate.instant('notifications.items', { count });
  }

  getWelcome(name: string): string {
    return this.translate.instant('notifications.welcome', { name });
  }
}
```

### 7. Soporte RTL

```typescript
// src/app/shared/utils/rtl.ts
export const RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur'];

export function isRTL(language: string): boolean {
  return RTL_LANGUAGES.includes(language);
}

export function getDirection(language: string): 'rtl' | 'ltr' {
  return isRTL(language) ? 'rtl' : 'ltr';
}
```

```typescript
// Uso en componente raíz
import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { getDirection } from '../shared/utils/rtl';

@Component({
  selector: 'app-root',
  template: `<div [dir]="direction"><router-outlet></router-outlet></div>`,
})
export class AppComponent {
  direction: 'ltr' | 'rtl' = 'ltr';

  constructor(private translate: TranslateService) {
    this.translate.onLangChange.subscribe((event) => {
      this.direction = getDirection(event.lang);
    });
  }
}
```

### 8. Formateo de fechas, números y monedas

```typescript
// src/app/shared/utils/formatters.ts
export function formatDate(date: Date, locale: string): string {
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
}

export function formatNumber(value: number, locale: string): string {
  return new Intl.NumberFormat(locale).format(value);
}

export function formatCurrency(value: number, locale: string, currency: string): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(value);
}
```

```typescript
// Pipe de Angular para usar en templates
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'formatDate' })
export class FormatDatePipe implements PipeTransform {
  transform(date: Date, locale: string): string {
    return formatDate(date, locale);
  }
}

@Pipe({ name: 'formatCurrency' })
export class FormatCurrencyPipe implements PipeTransform {
  transform(value: number, locale: string, currency: string): string {
    return formatCurrency(value, locale, currency);
  }
}
```

### 9. Componente de cambio de idioma

```typescript
// src/app/shared/components/language-switcher/language-switcher.component.ts
import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-language-switcher',
  template: `
    <select
      data-testid="language-switcher"
      [value]="translate.currentLang"
      (change)="onLanguageChange($event)"
    >
      <option *ngFor="let lang of languages" [value]="lang.code">
        {{ lang.name }}
      </option>
    </select>
  `,
})
export class LanguageSwitcherComponent {
  languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Español' },
    { code: 'pt-BR', name: 'Português (BR)' },
  ];

  constructor(public translate: TranslateService) {}

  onLanguageChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    this.translate.use(select.value);
  }
}
```

### 10. Lazy loading por ruta

```typescript
// src/app/app-routing.module.ts
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

const routes: Routes = [
  {
    path: 'auth',
    loadChildren: () =>
      import('./features/auth/auth.module').then((m) => m.AuthModule),
  },
  {
    path: 'dashboard',
    loadChildren: () =>
      import('./features/dashboard/dashboard.module').then((m) => m.DashboardModule),
  },
  {
    path: 'settings',
    loadChildren: () =>
      import('./features/settings/settings.module').then((m) => m.SettingsModule),
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
```

```typescript
// Carga manual de traducciones por módulo (si se necesitan archivos JSON separados)
import { TranslateService } from '@ngx-translate/core';
import { HttpClient } from '@angular/common/http';

export function loadTranslations(http: HttpClient, translate: TranslateService, lang: string) {
  return http.get(`./assets/i18n/${lang}.json`).subscribe((translations) => {
    translate.setTranslation(lang, translations, true);
  });
}
```

## Preguntas guía

### 1. Sobre librería
- ¿Se usa @ngx-translate/core o @angular/localize?
- ¿Se necesita SSR (Angular Universal)?
- ¿Se requiere detección de idioma automática?

### 2. Sobre estructura
- ¿Qué namespaces se necesitan por módulo?
- ¿Los locales regionales (`es-MX`) solo tienen overrides o son completos?
- ¿Las traducciones se cargan desde archivos JSON estáticos o desde API?

### 3. Sobre RTL
- ¿Se necesitan soportar idiomas RTL?
- ¿Los estilos CSS usan logical properties (start/end en vez de left/right)?
- ¿Las imágenes y iconos necesitan flip para RTL?

### 4. Sobre formateo
- ¿Qué monedas se soportan?
- ¿Qué zonas horarias se manejan?
- ¿Los formatos de fecha/número se alinean con el backend?

### 5. Sobre testing
- ¿Los tests verifican traducciones faltantes?
- ¿Se prueba el cambio de idioma en runtime?
- ¿Se prueba el fallback chain?

## Salidas esperadas de esta skill

### A. Configuración de i18n
- Archivo `src/app/app.module.ts` con TranslateModule.forRoot() configurado.
- Archivo `src/app/shared/utils/rtl.ts` con detección de RTL.
- Archivo `src/app/shared/utils/formatters.ts` con formateo de fechas/números/monedas.
- Pipes de Angular para formatos (`FormatDatePipe`, `FormatCurrencyPipe`).

### B. Estructura de locales
- Carpeta `/src/assets/i18n/{lang}.json` con archivos base en inglés.
- Al menos un locale adicional completo (español).
- Fallback chains configuradas.

### C. Tipo TypeScript para claves
- Archivo `src/app/shared/types/i18n.types.ts` con tipado estricto de claves.

### D. Componentes de i18n
- `<app-language-switcher>` con data-testid.
- Uso de `TranslateService` y pipe `translate` en al menos una página de ejemplo.

### E. Consumidores de esta skill
- `angular` consume los servicios y pipes de i18n;
- `api-first-frontend` puede generar tipos con campos localizados;
- `playwright` verifica que el selector de idioma funciona y que no hay claves sin traducir.

## Criterios de calidad

- Las claves de traducción usan naming jerárquico, no texto en inglés.
- Los archivos de locale están organizados por namespace/módulo.
- El tipo TypeScript de claves es estricto (no `string`).
- El fallback chain está configurado correctamente.
- El lazy loading funciona por ruta/módulo.
- Los formatos de fecha/número/moneda usan Intl API.
- El soporte RTL está configurado si se requieren idiomas RTL.
- Las traducciones faltantes muestran la clave, no un string vacío.
- Los tests verifican traducciones y cambio de idioma.

## Comportamiento esperado del agente

Cuando el usuario use texto hardcodeado en componentes, el agente debe proponer la extracción a clave de traducción y explicar la convención de naming.  
Cuando el usuario pregunte si necesita una nueva versión de locale para un dialecto, el agente debe proponer un locale regional con solo los overrides necesarios.  
Cuando el usuario tenga textos en el backend, el agente debe explicar que i18n del frontend cubre la UI, no el contenido dinámico del servidor.  
Cuando el usuario no considere RTL, el agente debe preguntar si se requieren idiomas RTL y proponer logical CSS properties.

## Checklist final de la skill

- ¿Se configuró @ngx-translate/core con TranslateModule.forRoot()?
- ¿Se creó la estructura de locales por módulo?
- ¿Las claves usan naming jerárquico?
- ¿El tipo TypeScript cobija todas las claves?
- ¿El lazy loading funciona por ruta/módulo?
- ¿Los formatos de fecha/número/moneda usan Intl API?
- ¿El fallback chain está configurado?
- ¿Se probó el cambio de idioma en runtime?
- ¿Se verificó que no hay claves sin traducir?
- ¿Se consideró soporte RTL si aplica?

## Flujo de traducción asistida por IA

Las traducciones iniciales se generan con un LLM y luego se refinan con revisión humana:

**Estructura del archivo de mensajes base (`src/assets/i18n/en.json`)**:

```json
{
  "common": {
    "actions": {
      "save": "Save",
      "cancel": "Cancel",
      "delete": "Delete",
      "confirm": "Confirm"
    }
  },
  "auth": {
    "login": {
      "title": "Sign In",
      "emailPlaceholder": "Enter your email",
      "passwordPlaceholder": "Enter your password",
      "submit": "Sign In"
    }
  }
}
```

**Script de traducción asistida (`scripts/i18n-translate.ts`)**:

```typescript
import { writeFileSync, readFileSync } from 'fs';
import { execSync } from 'child_process';

const SOURCE_LOCALE = 'en';
const TARGET_LOCALES = ['es', 'pt-BR'];
const MESSAGES_DIR = 'src/assets/i18n';

function translateWithLLM(source: Record<string, unknown>, targetLocale: string): Record<string, unknown> {
  const sourceJson = JSON.stringify(source, null, 2);
  const prompt = `You are a professional translator. Translate the following JSON from ${SOURCE_LOCALE} to ${targetLocale}.
Preserve ALL keys exactly as they are. Only translate the string values.
Return ONLY valid JSON, no markdown, no explanation.
Context: this is a business application UI.
Use formal tone. Respect regional conventions for ${targetLocale}.

${sourceJson}`;

  const result = execSync(
    `echo ${Buffer.from(prompt).toString('base64')} | base64 -d | llm translate`,
    { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 }
  );

  return JSON.parse(result);
}

function main() {
  const source = JSON.parse(readFileSync(`${MESSAGES_DIR}/${SOURCE_LOCALE}.json`, 'utf-8'));

  for (const locale of TARGET_LOCALES) {
    console.log(`Translating ${SOURCE_LOCALE} → ${locale}...`);
    const translated = translateWithLLM(source, locale);
    writeFileSync(
      `${MESSAGES_DIR}/${locale}.json`,
      JSON.stringify(translated, null, 2) + '\n',
      'utf-8'
    );
    console.log(`✓ ${locale} done`);
  }
}

main();
```

**Workflow de traducción asistida**:

1. El desarrollador añade claves nuevas solo en `en.json`.
2. Ejecuta `npm run i18n:translate` para generar los archivos `es.json` y `pt-BR.json` con traducción LLM.
3. Un revisor humano valida las traducciones generadas, corrigiendo contexto, tono y terminología específica del dominio.
4. Las traducciones aprobadas se commitean al repositorio.
5. El CI valida que todas las claves de `en.json` existen en los otros locales (sin claves faltantes).

**Validación en CI (`scripts/i18n-validate.ts`)**:

```typescript
import { readFileSync } from 'fs';

const SOURCE = 'en';
const LOCALES = ['es', 'pt-BR'];
const DIR = 'src/assets/i18n';

type Nested = { [k: string]: string | Nested };

function getKeys(obj: Nested, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === 'string' ? [`${prefix}${k}`] : getKeys(v as Nested, `${prefix}${k}.`)
  );
}

function validate() {
  const sourceKeys = getKeys(JSON.parse(readFileSync(`${DIR}/${SOURCE}.json`, 'utf-8')));
  const errors: string[] = [];

  for (const locale of LOCALES) {
    const target = JSON.parse(readFileSync(`${DIR}/${locale}.json`, 'utf-8'));
    const targetKeys = new Set(getKeys(target));

    for (const key of sourceKeys) {
      if (!targetKeys.has(key)) {
        errors.push(`Missing key "${key}" in ${locale}`);
      }
    }
  }

  if (errors.length > 0) {
    console.error(errors.join('\n'));
    process.exit(1);
  }

  console.log('All locales have matching keys ✓');
}

validate();
```

**Package.json scripts**:

```json
{
  "scripts": {
    "i18n:translate": "ts-node scripts/i18n-translate.ts",
    "i18n:validate": "ts-node scripts/i18n-validate.ts",
    "i18n:check": "npm run i18n:validate"
  }
}
```

## Integración de tokens RTL con design-system

La coordinación entre `i18n` y `design-system` se realiza a través de **tokens lógicos de dirección** que cambian según el locale:

**Tokens CSS lógicos en design-system**:

```css
/* tokens/direction.css */
:root {
  --space-inline-start: var(--space-4);
  --space-inline-end: var(--space-4);
  --space-block-start: var(--space-2);
  --space-block-end: var(--space-2);
  --border-inline-start-radius: var(--radius-sm);
  --border-inline-end-radius: var(--radius-sm);
  --float-reference: left;
}

[dir='rtl'] {
  --float-reference: right;
}
```

**Mapeo RTL → tokens del design-system**:

```typescript
// src/app/shared/utils/rtl-tokens.ts
import { isRTL } from './rtl';

type DirectionTokens = {
  space: {
    inlineStart: string;
    inlineEnd: string;
  };
  border: {
    inlineStartRadius: string;
    inlineEndRadius: string;
  };
  textAlign: 'left' | 'right' | 'start';
};

const LTR_TOKENS: DirectionTokens = {
  space: { inlineStart: 'var(--space-4)', inlineEnd: 'var(--space-2)' },
  border: { inlineStartRadius: 'var(--radius-sm)', inlineEndRadius: '0' },
  textAlign: 'start',
};

const RTL_TOKENS: DirectionTokens = {
  space: { inlineStart: 'var(--space-2)', inlineEnd: 'var(--space-4)' },
  border: { inlineStartRadius: '0', inlineEndRadius: 'var(--radius-sm)' },
  textAlign: 'start',
};

export function getDirectionTokens(locale: string): DirectionTokens {
  return isRTL(locale) ? RTL_TOKENS : LTR_TOKENS;
}
```

**Uso en componentes con tokens de dirección**:

```typescript
import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { getDirection } from '../utils/rtl';

@Component({
  selector: 'app-card-with-icon',
  template: `
    <div
      [style.paddingInlineStart]="'var(--space-inline-start)'"
      [style.paddingInlineEnd]="'var(--space-inline-end)'"
      [style.borderInlineStartRadius]="'var(--border-inline-start-radius)'"
      [style.borderInlineEndRadius]="'var(--border-inline-end-radius)'"
      [dir]="direction"
    >
      <span>{{ 'dashboard.cardTitle' | translate }}</span>
    </div>
  `,
})
export class CardWithIconComponent {
  direction: 'ltr' | 'rtl' = 'ltr';

  constructor(private translate: TranslateService) {
    this.translate.onLangChange.subscribe((event) => {
      this.direction = getDirection(event.lang);
    });
  }
}
```

**Reglas de integración con design-system**:

1. Usar **propiedades lógicas CSS** (`margin-inline-start`, `padding-inline-end`, `border-inline-start-radius`) en vez de propiedades físicas (`margin-left`, `padding-right`).
2. Los **tokens de spacing del design-system** deben usar alias lógicos (`--space-inline-start`) que se resuelven según `dir`.
3. Los **iconos direccionales** (flechas, breadcrumbs) deben usar `transform: scaleX(-1)` en contexto RTL o variantes SVG específicas.
4. El **layout del design-system** (flex, grid) debe usar `flex-direction` relativo al `dir` heredado, nunca hardcodear `row` con `direction: ltr`.
5. Las **fuentes tipográficas** pueden variar por locale (ej: fuentes Devanagari, Arabic, CJK); el design-system debe proveer un token `--font-family-body` que cambie según locale.