---
name: hu-template
description: 'Template for writing User Stories (Historias de Usuario) in a standard
  format. Input for API First specs. Follows standard format with acceptance criteria.
  Trigger: When writing user stories, creating HUs, defining requirements.'
version: 1.0
metadata:
  phase:
  - inception
  layer:
  - process
  enforcement: mandatory
  depends_on: []
  consumed_by:
  - api-first-spec
  - html-prototype
  agent_roles:
  - design-agent
  - orchestrator-agent
  validation_profile: documentation
mcp_usage: none
---

## Purpose
HU (WHAT the user wants) → API First (HOW to implement it) → Implementation

## HU Template
```markdown
## {REPO_CODE}-{SEQ}: {Descriptive Title}
**Epic:** {Epic Name} | **Layer:** {FRONT / API / BACK / FULL} | **Repo:** {REPO_CODE}

### Historia
**Como** {rol/actor} **Quiero** {acción} **Para** {beneficio}

### Criterios de Aceptación
- [ ] CA1: {Verifiable criterion}

### Reglas de Negocio
| Regla | Descripción |
|-------|-------------|
| RN-001 | {Rule} |

### Datos de Prueba
| Escenario | Input | Output Esperado |
|-----------|-------|-----------------|
| Happy path | {data} | {result} |
| Error | {invalid data} | {message} |

**Prioridad:** {Alta/Media/Baja} | **Estimación:** {S/M/L/XL} | **Sprint:** {number}
```

## HU Numbering and Grouping

### Single-Repo Projects
- **Repo Code** = project code (e.g., `200-034`)
- **Layer** = `FULL` (DB + BACK + FRONT in same repo)
- **Numbering** = `{PROJECT_CODE}-{SEQ}` — single continuous sequence

### Multi-Repo Projects
Convention: `{REPO_CODE}-{SEQUENTIAL}` (three-digit, continuous per repo, never resets)

| Layer | Repo Role |
|-------|-----------|
| **FRONT HOST** | Shell / host app |
| **FRONT DOMAIN** | Domain micro-frontend |
| **API GATEWAY** | Ocelot / BFF / Gateway |
| **BACK CROSS** | Cross-cutting domain API |
| **BACK DOMAIN** | Domain-specific API |

## Acceptance Criteria — SMART
| Attribute | Description |
|-----------|-------------|
| **S**pecific | Clear and unambiguous |
| **M**easurable | Verifiable |
| **A**chievable | Technically feasible |
| **R**elevant | Adds value |
| **T**estable | QA can verify it |

| Bad | Good |
|--------|---------|
| "The system is fast" | "Loads in under 2s" |
| "Works well" | "Shows success message" |

## HU to API First Mapping
| HU Section | API First Section |
|------------|-------------------|
| Criterios de Aceptación | Endpoints |
| Reglas de Negocio | Business Rules + DB |
| Datos de Prueba | Request/Response examples |
| Dependencias (catálogos) | Required Catalogs |

## Ejemplo de HU completa

```
## HUB-042: Gestión de perfil de usuario — Actualizar contraseña
**Epic:** Gestión de Cuenta | **Layer:** FULL | **Repo:** HUB

### Historia
**Como** usuario autenticado del sistema
**Quiero** cambiar mi contraseña desde la sección de perfil
**Para** mantener la seguridad de mi cuenta sin depender del administrador

### Criterios de Aceptación
- [ ] CA-01: El usuario puede acceder al formulario de cambio de contraseña desde su perfil
- [ ] CA-02: El formulario solicita: contraseña actual, nueva contraseña, confirmar nueva contraseña
- [ ] CA-03: Si la contraseña actual es incorrecta, muestra error "La contraseña actual no coincide"
- [ ] CA-04: Si la nueva contraseña no cumple la política de seguridad, muestra errores específicos
- [ ] CA-05: Si la confirmación no coincide, muestra error "Las contraseñas no coinciden"
- [ ] CA-06: En éxito, muestra mensaje "Contraseña actualizada correctamente" y redirige al perfil
- [ ] CA-07: La sesión activa se mantiene después del cambio de contraseña
- [ ] CA-08: El botón "Guardar" muestra estado de carga mientras se procesa
- [ ] CA-09: El botón "Guardar" se deshabilita si hay errores de validación en los campos
- [ ] CA-10: El usuario puede cancelar y volver al perfil sin cambios

### Reglas de Negocio
| Regla | Descripción |
|-------|-------------|
| RN-001 | Nueva contraseña: mínimo 8 caracteres, 1 mayúscula, 1 número, 1 especial |
| RN-002 | Nueva contraseña no puede ser igual a la actual |
| RN-003 | Nueva contraseña no puede ser igual a las últimas 5 contraseñas usadas |
| RN-004 | El usuario solo puede cambiar su propia contraseña, no la de otros |
| RN-005 | Tras 5 intentos fallidos en 15 minutos, bloquear cambio por 30 minutos |
| RN-006 | La contraseña se almacena con hash bcrypt, nunca en texto plano |

### Datos de Prueba
| Escenario | Input | Output Esperado |
|-----------|-------|-----------------|
| Happy path | actual: "Pass123!", nueva: "Nueva@456", confirma: "Nueva@456" | 200 OK, mensaje éxito |
| Contraseña actual incorrecta | actual: "Wrong123", nueva: "Nueva@456" | 400, "La contraseña actual no coincide" |
| Contraseña débil | actual: "Pass123!", nueva: "123" | 400, errores de política de seguridad |
| Confirmación no coincide | actual: "Pass123!", nueva: "Nueva@456", confirma: "Otra456" | 400, "Las contraseñas no coinciden" |
| Contraseña repetida | actual: "Pass123!", nueva: "Pass123!" | 400, "Debe ser diferente a la actual" |
| Sin autenticación | — | 401, "No autenticado" |
| Límite de intentos | 5 intentos fallidos en 15 min | 429, "Demasiados intentos. Intente en 30 minutos" |

### Dependencias
- Catálogo de políticas de seguridad (mínimos por rol)
- Historial de contraseñas (últimas 5)
- Tabla de bloqueo temporal (intentos fallidos)

**Prioridad:** Alta | **Estimación:** M | **Sprint:** 3
```

## Criterios de aceptación — patrones

Los criterios de aceptación deben ser SMART: Specific, Measurable, Achievable, Relevant, Testable.

### Patrón 1: Condicional (Given-When-Then)

```
CA-N: {Contexto} → {Acción} → {Resultado}
```

| Elemento | Descripción | Ejemplo |
|----------|-------------|---------|
| Given | Estado inicial | "Dado que el usuario tiene 3 artículos en el carrito" |
| When | Acción realizada | "Cuando hace clic en 'Pagar'" |
| Then | Resultado esperado | "Entonces se redirige a la página de checkout" |

Ejemplo: `CA-01: Dado un usuario con items en carrito, cuando confirma la compra, entonces se genera una orden con estado "Pendiente"`

### Patrón 2: Tabla de decisiones

Para reglas con múltiples combinaciones de entrada:

```
CA-N: Tabla de decisiones para [funcionalidad]

| Condición | Caso 1 | Caso 2 | Caso 3 | Caso 4 |
|-----------|--------|--------|--------|--------|
| Rol = Admin | Sí | Sí | No | No |
| Recurso existe | Sí | No | Sí | No |
| Resultado | 200 OK | 404 | 403 | 404 |
```

### Patrón 3: Rango y límites

Para validaciones numéricas o de rango:

```
CA-N: Rangos de [campo]

| Valor | Resultado |
|-------|-----------|
| Mínimo - 1 (ej: 0) | Error "Debe ser ≥ 1" |
| Mínimo (ej: 1) | OK |
| Valor típico (ej: 50) | OK |
| Máximo (ej: 100) | OK |
| Máximo + 1 (ej: 101) | Error "Debe ser ≤ 100" |
| Vacío | Error "Campo requerido" |
```

### Patrón 4: Estados visuales

Para componentes UI:

```
CA-N: Estados visuales de [componente]

| Estado | Comportamiento |
|--------|----------------|
| Loading | Skeleton/spinner visible, botones deshabilitados |
| Vacío | Mensaje "No hay datos" + ilustración + CTA |
| Error toast | Notificación con mensaje de error + botón reintentar |
| Éxito | Mensaje de confirmación + transición suave |
| Offline | Banner "Sin conexión" + datos cacheados visibles |
```

### Patrón 5: Seguridad y permisos

```
CA-N: Permisos para [acción]

| Rol | Resultado |
|-----|-----------|
| Sin autenticar | 401, redirige a login |
| Autenticado sin permiso | 403, mensaje "No tienes permiso" |
| Autenticado con permiso | Acción ejecutada correctamente |
| Admin | Acción ejecutada, log audit registrado |
```

### Ejemplos de CA buenos vs malos

| Malo (vago) | Bueno (SMART) |
|-------------|---------------|
| "La pantalla debe ser rápida" | "La pantalla carga en < 2s medido desde click hasta contenido renderizado" |
| "El usuario puede buscar" | "Los resultados aparecen mientras escribe tras 300ms de debounce, máx 10 resultados" |
| "Manejar errores" | "Si la API responde 500, muestra toast 'Error inesperado' con botón Reintentar" |
| "Debe ser seguro" | "El endpoint rechaza peticiones sin token JWT válido con 401 en < 50ms" |

## HU técnicas vs funcionales

### HU Funcional

Describe una necesidad de negocio desde la perspectiva del usuario. Es el insumo principal para el product owner y el equipo de diseño.

| Atributo | Descripción |
|----------|-------------|
| Actor | Usuario de negocio (cliente, operador, administrador) |
| Lenguaje | Lenguaje de negocio, sin tecnicismos |
| Objetivo | Resolver un problema de negocio |
| Ejemplo | "Como vendedor, quiero generar un reporte de ventas del mes para analizar tendencias" |

### HU Técnica

Describe una necesidad técnica habilitante. No tiene valor directo para el usuario de negocio, pero es necesaria para implementar funcionalidades.

| Atributo | Descripción |
|----------|-------------|
| Actor | Sistema, desarrollador, DevOps |
| Lenguaje | Técnico (API, BD, caché, deployment) |
| Objetivo | Habilitar, mejorar, o mantener la plataforma |
| Ejemplo | "Como sistema, quiero cachear las consultas de catálogos en Redis para reducir la carga en BD en 60%" |

### Comparación directa

| Aspecto | HU Funcional | HU Técnica |
|---------|--------------|------------|
| Actor | Usuario real (Persona) | Sistema / Técnico |
| Valor de negocio | Directo, visible | Indirecto, habilitante |
| Priorización | Product Owner | Tech Lead / Arquitecto |
| Estimación | Story points (S/M/L/XL) | Horas / Días |
| Criterios | Experiencia de usuario | Performance, seguridad, mantenibilidad |
| Visibilidad | Visible en UI | Invisible para el usuario |
| Dependencias | Ninguna | Puede depender de otras HU técnicas |
| Ejemplo | "Exportar reporte en Excel" | "Implementar cola de procesamiento asíncrono para reports pesados" |

### Cuándo usar cada una

| Situación | Tipo Recomendado |
|-----------|------------------|
| Nueva funcionalidad visible para el usuario | Funcional |
| Mejora de performance | Técnica |
| Refactor de código | Técnica |
| Bug fix visible al usuario | Funcional |
| Bug de infraestructura (500 silent, error en logs) | Técnica |
| Migración de base de datos | Técnica |
| Integración con API externa | Técnica (con HU funcional wrapper si tiene UI) |
| Nuevo endpoint para app mobile | Funcional (para la app) |
| Implementar caching | Técnica |
| Deuda técnica | Técnica |

### Template para HU Técnica

```markdown
## {REPO_CODE}-{SEQ}: {Título Técnico}
**Epic:** {Epic Name} | **Layer:** {BACK/INFRA/FULL} | **Repo:** {REPO_CODE} | **Tipo:** Técnica

### Historia
**Como** {rol técnico} **Quiero** {acción técnica} **Para** {beneficio técnico}

### Justificación Técnica
{Explicación de por qué es necesaria, qué problema resuelve, alternativas consideradas}

### Criterios de Aceptación
- [ ] CA-01: {Criterio técnico verificable}
- [ ] CA-02: {Por ejemplo: latencia, cobertura, seguridad}

### Reglas de Negocio / Técnicas
| Regla | Descripción |
|-------|-------------|
| RT-001 | {Regla técnica específica} |

### Definición de Done
- [ ] Implementación completa
- [ ] Tests unitarios (≥ 80% cobertura en el cambio)
- [ ] Tests de integración pasan
- [ ] Documentación técnica actualizada
- [ ] Sin vulnerabilidades nuevas
- [ ] Deuda técnica no incrementada (SonarQube)

**Prioridad:** {Alta/Media/Baja} | **Estimación:** {días} | **Sprint:** {number}
```
