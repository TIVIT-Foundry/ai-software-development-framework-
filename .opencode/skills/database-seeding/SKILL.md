---
name: database-seeding
description: "PostgreSQL database seeding patterns for catalogs, reference data, and test fixtures. Covers idempotent MERGE/UPSERT scripts, environment-specific data, multi-tenant seeding, and reproducible fixtures. Trigger: When populating PostgreSQL databases with initial catalogs, reference data, or test fixtures."
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - database
  enforcement: mandatory
  depends_on:
  - database-migrations
  consumed_by:
  - data-access
  - integration-testing
  - unit-testing
  agent_roles:
  - delivery-agent
  - design-agent
  validation_profile: skill-contract
  mcp_usage: none
---

# database-seeding

## Propósito

Esta skill define cómo poblar la base de datos con datos iniciales, catálogos maestros y fixtures de prueba de forma idempotente, trazable y reproducible.  
Su función es asegurar que todo entorno (dev, staging, producción) tenga los datos mínimos necesarios para funcionar, sin depender de inserciones manuales ni scripts ad-hoc.

Esta skill complementa `database-migrations` (cambios de esquema) y `database-sp` (lógica de negocio). Mientras las migraciones definen la estructura, esta skill define los datos que la habilitan.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo se insertan catálogos maestros de forma idempotente?
2. ¿Cómo se separan datos de producción vs datos de prueba?
3. ¿Cómo se maneja el seeding en multi-tenancy (datos compartidos vs datos por tenant)?
4. ¿Qué datos van en migraciones y qué datos van en seeding?
5. ¿Cómo se garantiza que el seeding es reproducible en cualquier entorno?

## Relación con otras skills

- `database-migrations` crea el esquema que esta skill popula con datos.
- `database-sp` define SPs que pueden depender de datos de catálogo insertados por seeding.
- `database-audit` define las columnas de auditoría que los scripts de seeding deben respetar.
- `integration-testing` consume los fixtures de prueba definidos por esta skill.
- `data-access` consume los catálogos insertados por seeding para validar handlers.

## Qué debe hacer el agente cuando esta skill está activa

1. Separar scripts de seeding por categoría (catálogos maestros, datos de referencia, fixtures de prueba).
2. Escribir cada script de seeding como operación idempotente (MERGE/UPSERT, nunca INSERT directo).
3. Incluir columnas de auditoría en toda inserción (RecordCreationUser, RecordCreationDate, RecordStatus).
4. Ejecutar seeding después de migraciones, nunca antes.
5. Documentar el orden de ejecución de scripts de seeding (respetar FKs).
6. Validar que los datos insertados son correctos con queries de verificación post-seeding.
7. Definir fixtures de prueba separados de datos de producción.
8. Registrar cada ejecución de seeding en una tabla de historial.

## Entradas esperadas

Esta skill asume que ya existe:
- esquema de base de datos creado por `database-migrations`;
- stored procedures que dependen de catálogos (`database-sp`);
- convenciones de naming y auditoría (`database-modeling`, `database-audit`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- catálogos maestros (tipos de documento, estados, roles, permisos);
- datos de referencia (países, monedas, idiomas, zonas horarias);
- configuraciones iniciales por tenant;
- fixtures de prueba para entornos de desarrollo y QA;
- scripts de limpieza para entornos de prueba.

La fase no incluye todavía:
- migraciones de datos entre sistemas legacy;
- datos de producción generados por usuarios;
- ETL desde fuentes externas.

## Principios que siempre debe respetar

- Los scripts de seeding DEBEN ser idempotentes: MERGE/UPSERT, nunca INSERT directo sin verificación.
- Los catálogos maestros DEBEN tener IDs fijos (no IDENTITY) para estabilidad entre entornos.
- Los datos de prueba y producción DEBEN estar en carpetas separadas.
- El seeding se ejecuta DESPUÉS de las migraciones, nunca antes.
- Toda inserción DEBE incluir columnas de auditoría (RecordCreationUser, RecordCreationDate, RecordStatus).
- Los scripts de seeding DEBEN respetar el orden de FKs (insertar padres antes que hijos).
- Los scripts de limpieza (dev/QA) DEBEN ser seguros: solo borrar si existe un WHERE explícito.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la convención de naming y estructura de carpetas de seeding;
- la estrategia de idempotencia (MERGE vs UPSERT vs IF NOT EXISTS);
- la separación de datos por entorno (dev/staging/production);
- los fixtures mínimos para pruebas;

Esta skill delega:
- los cambios de esquema a `database-migrations`;
- la lógica de negocio en SPs a `database-sp`;
- las columnas de auditoría a `database-audit`;
- la validación end-to-end de datos a `integration-testing`.

## Qué debe definir el diseño

### 1. Categorías de datos de seeding

Definir:
- **Catálogos maestros**: datos compartidos inmutables (tipos, estados, roles, permisos). IDs fijos.
- **Datos de referencia**: datos compartidos mutables raramente (países, monedas, idiomas). IDs fijos.
- **Configuración por tenant**: datos específicos del tenant (settings, features). IDs pueden ser IDENTITY.
- **Fixtures de prueba**: datos ficticios para dev/QA (usuarios de prueba, órdenes de prueba). IDs variables.
- **Datos de demo**: datos realistas para demos y training. IDs pueden ser IDENTITY.

### 2. Estructura de carpetas de seeding

```
/seeding/
├── catalogs/
│   ├── V001__seed_roles.sql
│   ├── V002__seed_permissions.sql
│   ├── V003__seed_document_types.sql
│   └── V004__seed_countries.sql
├── reference/
│   ├── V001__seed_currencies.sql
│   └── V002__seed_timezones.sql
├── tenant/
│   ├── V001__seed_tenant_settings.sql
│   └── V002__seed_tenant_features.sql
├── fixtures/
│   ├── dev/
│   │   ├── V001__seed_test_users.sql
│   │   └── V002__seed_test_orders.sql
│   └── qa/
│       └── V001__seed_qa_scenarios.sql
└── cleanup/
    ├── dev/
    │   └── truncate_test_data.sql
    └── qa/
        └── truncate_qa_data.sql
```

### 3. Patrón idempotente UPSERT (PostgreSQL)

```sql
-- ============================================================
-- Seed: Catálogo de Estados de Registro
-- Category: Catalog (immutable)
-- Order: 001 (must run after roles)
-- ============================================================

INSERT INTO {schema}.record_status (status_code, status_name, status_description,
    record_creation_user, record_creation_date, record_status)
VALUES
    ('A', 'Active', 'Record is active and visible', 'SEED', NOW(), 'A'),
    ('I', 'Inactive', 'Record is inactive and hidden', 'SEED', NOW(), 'A'),
    ('*', 'Deleted', 'Record is soft-deleted', 'SEED', NOW(), 'A')
ON CONFLICT (status_code) DO UPDATE SET
    status_name = EXCLUDED.status_name,
    status_description = EXCLUDED.status_description,
    record_edit_user = 'SEED',
    record_edit_date = NOW();
```

### 4. Patrón idempotente UPSERT (PostgreSQL)

```sql
-- Seed: Catálogo de Monedas
-- Category: Reference (rarely mutable)

INSERT INTO {schema}.currency (code, name, symbol, decimal_places,
    record_creation_user, record_creation_date, record_status)
VALUES
    ('USD', 'US Dollar', '$', 2, 'SEED', NOW(), 'A'),
    ('EUR', 'Euro', '\u20ac', 2, 'SEED', NOW(), 'A'),
    ('MXN', 'Mexican Peso', '$', 2, 'SEED', NOW(), 'A')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    symbol = EXCLUDED.symbol,
    decimal_places = EXCLUDED.decimal_places,
    record_edit_user = 'SEED',
    record_edit_date = NOW();
```

### 5. Estrategia multi-tenancy

Definir:
- **Shared catalogs**: se ejecutan una vez en la BD compartida (roles, permisos, estados).
- **Per-tenant data**: se ejecutan para cada tenant nuevo (settings, features, configuración).
- **Seed de tenant nuevo**: script template que recibe parámetros del tenant.
- **Orden de ejecución**: primero shared catalogs, luego per-tenant data.

### 6. Verificación post-seeding

Definir:
- queries de verificación para cada script de seeding (COUNT, EXISTS);
- tabla de historial de seeding (similar a MigrationJournal);
- logging de ejecución exitosa/fallida;
- validación de FKs después de seeding completo.

## Preguntas guía

### 1. Sobre catálogos maestros
- ¿Cuáles son los catálogos obligatorios para que la aplicación funcione?
- ¿Los IDs de catálogo son fijos (INT con valor conocido) o IDENTITY?
- ¿Los catálogos se pueden modificar en producción o son inmutables?

### 2. Sobre datos por entorno
- ¿Qué datos necesita el entorno de dev? ¿Y staging? ¿Y producción?
- ¿Los fixtures de prueba se limpian automáticamente o manualmente?
- ¿Cómo se asegura que los datos de prueba NO llegan a producción?

### 3. Sobre multi-tenancy
- ¿Los catálogos son compartidos o por tenant?
- ¿Cómo se ejecuta el seeding cuando se crea un nuevo tenant?
- ¿Los fixtures de prueba son por tenant o globales?

### 4. Sobre orden de ejecución
- ¿Se respeta el orden de FKs en los scripts de seeding?
- ¿Qué pasa si un script de seeding falla a la mitad?
- ¿Se puede re-ejecutar un script de seeding sin duplicar datos?

### 5. Sobre mantenimiento
- ¿Cómo se agregan nuevos valores a un catálogo existente?
- ¿Se versionan los scripts de seeding igual que las migraciones?
- ¿Quién aprueba los cambios en catálogos de producción?

## Salidas esperadas de esta skill

### A. Carpeta de seeding estructurada
- `/seeding/catalogs/` — catálogos maestros inmutables
- `/seeding/reference/` — datos de referencia
- `/seeding/tenant/` — configuración por tenant
- `/seeding/fixtures/dev/` — datos de prueba dev
- `/seeding/fixtures/qa/` — datos de prueba QA
- `/seeding/cleanup/` — scripts de limpieza

### B. Scripts de seeding idempotentes
- Cada script usa MERGE o UPSERT para ser re-ejecutable.
- Cada script incluye columnas de auditoría.
- Cada script tiene header con metadata (categoría, orden, descripción).

### C. Scripts de verificación
- Queries de COUNT o EXISTS para validar que los datos se insertaron.
- Script de verificación completa que corre después de todo el seeding.

### D. Tabla de historial de seeding (PostgreSQL)
```sql
CREATE TABLE {schema}.seeding_journal (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description VARCHAR(500) NOT NULL,
    rows_affected INT NULL,
    applied_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    applied_by VARCHAR(128) NOT NULL
);
```

### E. Consumidores de esta skill
- `integration-testing` usa los fixtures de prueba para levantar BD de test;
- `unit-testing` usa los fixtures para datos de referencia en mocks;
- `data-access` consume los catálogos insertados para construir handlers;
- `framework-qa-validation` valida que los datos de catálogo están completos en producción.

## Criterios de calidad

- Todos los scripts de seeding son idempotentes (MERGE/UPSERT).
- Los catálogos maestros tienen IDs fijos y estables.
- Los datos de prueba y producción están en carpetas separadas.
- El seeding respeta el orden de FKs.
- Toda inserción incluye columnas de auditoría.
- El seeding se ejecuta después de las migraciones.
- Existe tabla de historial de seeding.
- Los scripts de verificación post-seeding existen y son correctos.
- Los scripts de limpieza solo borran con WHERE explícito.

## Comportamiento esperado del agente

Cuando el usuario pida insertar datos manualmente, el agente debe proponer un script de seeding idempotente y explicar los riesgos de inserciones ad-hoc.  
Cuando el usuario pregunte por datos de prueba en producción, el agente debe rechazar la idea y proponer separación estricta de entornos.  
Cuando el usuario tenga conflicto de FKs en seeding, el agente debe verificar el orden de inserción y reordenar.  
Cuando el usuario cree un nuevo tenant, el agente debe generar el script de seeding de tenant a partir del template.

## Checklist final de la skill

- ¿Se definieron los catálogos maestros obligatorios?
- ¿Los scripts de seeding son idempotentes (MERGE/UPSERT)?
- ¿Los catálogos tienen IDs fijos?
- ¿Se separaron datos de producción y pruebas?
- ¿Se respeta el orden de FKs?
- ¿Se incluyeron columnas de auditoría en toda inserción?
- ¿Se creó la tabla de historial de seeding?
- ¿Existen scripts de verificación post-seeding?
- ¿Existen scripts de limpieza para entornos de prueba?
- ¿Se definió la estrategia de seeding para multi-tenancy?

