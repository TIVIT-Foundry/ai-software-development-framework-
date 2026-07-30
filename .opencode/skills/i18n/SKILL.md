---
name: i18n
description: "Internationalization patterns for frontend applications. Covers react-i18next, locale file structure, lazy loading by route, fallback chains, pluralization, RTL support, date/number/currency formatting, and key extraction. Trigger: When implementing multi-language support or localization in a frontend application."
version: 2.1
metadata:
  phase:
  - construction
  layer:
  - frontend
  enforcement: mandatory
  depends_on:
  - react
  - angular
  - typescript
  consumed_by:
  - react
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

Esta skill complementa `react` o `angular` (componentes, según el framework elegido por el proyecto) y `typescript` (tipos). Mientras esos definen la estructura de la UI, esta skill define cómo hacer esa UI multilingüe.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Qué librería de i18n usar y cómo se configura?
2. ¿Cómo se estructura el almacenamiento de traducciones?
3. ¿Cómo se hace lazy loading de traducciones por ruta?
4. ¿Cómo se manejan pluralización, interpolación y género?
5. ¿Cómo se soporta RTL (árabe, hebreo)?
6. ¿Cómo se formatean fechas, números y monedas por locale?

## Relación con otras skills

- `react` o `angular` define los componentes que esta skill internacionaliza (según el framework elegido por el proyecto).
- `typescript` define los tipos de las claves de traducción.
- `api-first-frontend` genera tipos que pueden incluir campos localizados.
- `design-system` define tokens que pueden variar por locale (fuentes RTL, spacing).

## Qué debe hacer el agente cuando esta skill está activa

1. Configurar la librería de i18n (`react-i18next` por defecto).
2. Crear la estructura de carpetas de locales con namespaces por módulo.
3. Definir el tipo TypeScript para las claves de traducción.
4. Implementar el detector de idioma y el fallback chain.
5. Configurar lazy loading de traducciones por ruta/módulo.
6. Implementar el componente de cambio de idioma.
7. Definir la convención de naming de claves de traducción.
8. Configurar formateo de fechas, números y monedas por locale.

## Entradas esperadas

Esta skill asume que ya existe:
- estructura de componentes (`react` o `angular`);
- tipos TypeScript definidos (`typescript`);
- diseño de sistema (`design-system`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- configuración de `react-i18next`;
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
- la librería de i18n (`react-i18next` por defecto);
- la estructura de carpetas y namespaces;
- la convención de naming de claves;
- la estrategia de fallback y lazy loading.

Esta skill delega:
- la estructura general de componentes a `react` o `angular`;
- los tipos TypeScript a `typescript`;
- el contenido traducido a traductores profesionales;
- el contenido dinámico desde backend a `backend-api`.

## Qué debe definir el diseño

### 1. Librería y configuración

**Decisión por defecto**: `react-i18next` con `i18next-http-backend` para carga lazy y `i18next-browser-languagedetector` para detección automática.

```typescript
// src/core/i18n/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    ns: ['common'],
    defaultNS: 'common',
    backend: { loadPath: '/assets/i18n/{{lng}}/{{ns}}.json' },
    interpolation: { escapeValue: false }, // React ya escapa por defecto
    returnEmptyString: false, // clave faltante muestra la clave, no vacío
  });

export default i18n;
```

```tsx
// main.tsx — provider en la raíz de la app
import './core/i18n/i18n';
import { Suspense } from 'react';

<Suspense fallback={<div>Loading...</div>}>
  <App />
</Suspense>;
```

```typescript
// Carga de un namespace adicional por feature (lazy loading por módulo)
import { useTranslation } from 'react-i18next';

export function UsersPage() {
  const { t } = useTranslation('users'); // carga el namespace 'users' bajo demanda
  return <h1>{t('list.title')}</h1>;
}
```

### 1b. Librería y configuración (Angular — @ngx-translate/core)

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
/public/assets/i18n/
├── en/
│   ├── common.json
│   └── users.json
├── es/
│   ├── common.json
│   └── users.json
├── es-MX/
│   └── common.json      ← solo overrides específicos de México
└── pt-BR/
    ├── common.json
    └── users.json
```

Reglas:
- Un archivo JSON por namespace y por idioma.
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
// src/core/i18n/i18n.types.ts
import common from '../../../public/assets/i18n/en/common.json';

type NestedMessages = { [key: string]: string | NestedMessages };

// Tipo recursivo para claves anidadas (e.g., 'auth.login.title')
export type DeepTranslationKey<T extends NestedMessages> = {
  [K in keyof T & string]: T[K] extends NestedMessages
    ? `${K}.${DeepTranslationKey<T[K]>}`
    : K;
}[keyof T & string] | (keyof T & string);

export type CommonTranslationKey = DeepTranslationKey<typeof common>;
```

```typescript
// Tipado global para react-i18next (declara los recursos por namespace)
// src/types/i18next.d.ts
import 'i18next';
import common from '../../public/assets/i18n/en/common.json';
import users from '../../public/assets/i18n/en/users.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof common;
      users: typeof users;
    };
  }
}
```

### 5. Uso en componentes

```tsx
// src/features/auth/LoginPage.tsx
import { useTranslation } from 'react-i18next';

export function LoginPage() {
  const { t, i18n } = useTranslation();

  return (
    <div>
      <h1>{t('auth.login.title')}</h1>
      <input placeholder={t('auth.login.emailPlaceholder')} />
      <input placeholder={t('auth.login.passwordPlaceholder')} type="password" />
      <button>{t('auth.login.submit')}</button>
      <a href="/forgot-password">{t('auth.login.forgotPassword')}</a>
    </div>
  );
}
```

### 5b. Uso en componentes (Angular)

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
    "items_one": "{{count}} item",
    "items_other": "{{count}} items",
    "welcome": "Welcome, {{name}}!",
    "lastLogin": "Last login: {{date, datetime}}",
    "balance": "Balance: {{amount, currency}}"
  }
}
```

```tsx
// Uso en componente — i18next resuelve el plural (_one/_other) automáticamente
import { useTranslation } from 'react-i18next';

export function Dashboard({ itemCount, userName }: { itemCount: number; userName: string }) {
  const { t } = useTranslation();

  return (
    <>
      <p>{t('notifications.items', { count: itemCount })}</p>
      <p>{t('notifications.welcome', { name: userName })}</p>
    </>
  );
}
```

### 7. Soporte RTL

```typescript
// src/core/i18n/rtl.ts
export const RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur'];

export function isRTL(language: string): boolean {
  return RTL_LANGUAGES.includes(language);
}

export function getDirection(language: string): 'rtl' | 'ltr' {
  return isRTL(language) ? 'rtl' : 'ltr';
}
```

```tsx
// Uso en componente raíz
import { useTranslation } from 'react-i18next';
import { getDirection } from './core/i18n/rtl';

export function App() {
  const { i18n } = useTranslation();
  const direction = getDirection(i18n.language);

  return (
    <div dir={direction}>
      <RouterProvider router={router} />
    </div>
  );
}
```

### 8. Formateo de fechas, números y monedas

```typescript
// src/core/i18n/formatters.ts
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
// Formatters registrados en i18next para usar como {{value, format}} en las claves
import i18n from './i18n';
import { formatDate, formatNumber, formatCurrency } from './formatters';

i18n.services.formatter?.add('datetime', (value, lng) => formatDate(value, lng ?? 'en'));
i18n.services.formatter?.add('currency', (value, lng) => formatCurrency(value, lng ?? 'en', 'USD'));
```

### 9. Componente de cambio de idioma

```tsx
// src/shared/components/LanguageSwitcher.tsx
import { useTranslation } from 'react-i18next';

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' },
  { code: 'pt-BR', name: 'Português (BR)' },
];

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  return (
    <select
      data-testid="language-switcher"
      value={i18n.language}
      onChange={(e) => i18n.changeLanguage(e.target.value)}
    >
      {LANGUAGES.map((lang) => (
        <option key={lang.code} value={lang.code}>{lang.name}</option>
      ))}
    </select>
  );
}
```

### 9b. Componente de cambio de idioma (Angular)

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

```tsx
// router.tsx — code-splitting por ruta; cada página carga su propio namespace con useTranslation('ns')
import { lazy } from 'react';

const AuthRoutes = lazy(() => import('./features/auth/auth.routes'));
const DashboardRoutes = lazy(() => import('./features/dashboard/dashboard.routes'));
const SettingsRoutes = lazy(() => import('./features/settings/settings.routes'));

const router = createBrowserRouter([
  { path: 'auth/*', element: <AuthRoutes /> },
  { path: 'dashboard/*', element: <DashboardRoutes /> },
  { path: 'settings/*', element: <SettingsRoutes /> },
]);
```

```typescript
// Carga manual de un namespace bajo demanda (fuera de un componente)
import i18n from './core/i18n/i18n';

export async function loadNamespace(ns: string): Promise<void> {
  if (!i18n.hasResourceBundle(i18n.language, ns)) {
    await i18n.loadNamespaces(ns);
  }
}
```

### 10b. Lazy loading por ruta (Angular)

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
- ¿Se usa `react-i18next` o `next-intl` (si el proyecto es Next.js)?
- ¿Se necesita SSR (Next.js con `next-intl` o `next-i18next`)?
- ¿Se requiere detección de idioma automática (`i18next-browser-languagedetector`)?

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
- Archivo `src/core/i18n/i18n.ts` con `react-i18next` configurado.
- Archivo `src/core/i18n/rtl.ts` con detección de RTL.
- Archivo `src/core/i18n/formatters.ts` con formateo de fechas/números/monedas.
- Formatters registrados en i18next para usar `{{value, format}}` en las claves.

### B. Estructura de locales
- Carpeta `/public/assets/i18n/{lang}/{ns}.json` con archivos base en inglés.
- Al menos un locale adicional completo (español).
- Fallback chains configuradas.

### C. Tipo TypeScript para claves
- Archivo `src/core/i18n/i18n.types.ts` con tipado estricto de claves.
- Declaración de módulo `src/types/i18next.d.ts` para autocompletado de `t()`.

### D. Componentes de i18n
- `<LanguageSwitcher>` con `data-testid`.
- Uso de `useTranslation()` en al menos una página de ejemplo.

### E. Consumidores de esta skill
- `react` consume el hook `useTranslation` y el componente `<LanguageSwitcher>`; `angular` consume el `TranslateService` y los pipes/componentes equivalentes;
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

- ¿Se configuró `react-i18next` con `HttpBackend` y `LanguageDetector`?
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

**Estructura del archivo de mensajes base (`public/assets/i18n/en/common.json`)**:

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
const MESSAGES_DIR = 'public/assets/i18n';

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
  const source = JSON.parse(readFileSync(`${MESSAGES_DIR}/${SOURCE_LOCALE}/common.json`, 'utf-8'));

  for (const locale of TARGET_LOCALES) {
    console.log(`Translating ${SOURCE_LOCALE} → ${locale}...`);
    const translated = translateWithLLM(source, locale);
    writeFileSync(
      `${MESSAGES_DIR}/${locale}/common.json`,
      JSON.stringify(translated, null, 2) + '\n',
      'utf-8'
    );
    console.log(`✓ ${locale} done`);
  }
}

main();
```

**Workflow de traducción asistida**:

1. El desarrollador añade claves nuevas solo en `en/common.json`.
2. Ejecuta `npm run i18n:translate` para generar los archivos `es/common.json` y `pt-BR/common.json` con traducción LLM.
3. Un revisor humano valida las traducciones generadas, corrigiendo contexto, tono y terminología específica del dominio.
4. Las traducciones aprobadas se commitean al repositorio.
5. El CI valida que todas las claves de `en/common.json` existen en los otros locales (sin claves faltantes).

**Validación en CI (`scripts/i18n-validate.ts`)**:

```typescript
import { readFileSync } from 'fs';

const SOURCE = 'en';
const LOCALES = ['es', 'pt-BR'];
const DIR = 'public/assets/i18n';

type Nested = { [k: string]: string | Nested };

function getKeys(obj: Nested, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === 'string' ? [`${prefix}${k}`] : getKeys(v as Nested, `${prefix}${k}.`)
  );
}

function validate() {
  const sourceKeys = getKeys(JSON.parse(readFileSync(`${DIR}/${SOURCE}/common.json`, 'utf-8')));
  const errors: string[] = [];

  for (const locale of LOCALES) {
    const target = JSON.parse(readFileSync(`${DIR}/${locale}/common.json`, 'utf-8'));
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
// src/core/i18n/rtl-tokens.ts
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

```tsx
import { useTranslation } from 'react-i18next';
import { getDirection } from '../../core/i18n/rtl';

export function CardWithIcon() {
  const { t, i18n } = useTranslation();
  const direction = getDirection(i18n.language);

  return (
    <div
      style={{
        paddingInlineStart: 'var(--space-inline-start)',
        paddingInlineEnd: 'var(--space-inline-end)',
        borderStartStartRadius: 'var(--border-inline-start-radius)',
        borderStartEndRadius: 'var(--border-inline-end-radius)',
      }}
      dir={direction}
    >
      <span>{t('dashboard.cardTitle')}</span>
    </div>
  );
}
```

**Reglas de integración con design-system**:

1. Usar **propiedades lógicas CSS** (`margin-inline-start`, `padding-inline-end`, `border-start-start-radius`) en vez de propiedades físicas (`margin-left`, `padding-right`).
2. Los **tokens de spacing del design-system** deben usar alias lógicos (`--space-inline-start`) que se resuelven según `dir`.
3. Los **iconos direccionales** (flechas, breadcrumbs) deben usar `transform: scaleX(-1)` en contexto RTL o variantes SVG específicas.
4. El **layout del design-system** (flex, grid) debe usar `flex-direction` relativo al `dir` heredado, nunca hardcodear `row` con `direction: ltr`.
5. Las **fuentes tipográficas** pueden variar por locale (ej: fuentes Devanagari, Arabic, CJK); el design-system debe proveer un token `--font-family-body` que cambie según locale.
