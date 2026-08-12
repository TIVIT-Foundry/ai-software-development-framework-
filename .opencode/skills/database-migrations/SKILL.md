---
name: database-migrations
description: "Database schema versioning and migration patterns for PostgreSQL/Alembic. Covers script naming conventions, rollback strategies, ALTER TABLE patterns, multi-tenancy migrations, and idempotent scripts. Trigger: When creating or managing database schema migrations, versioning database changes, or applying rollback strategies."
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - database
  enforcement: mandatory
  depends_on:
  - database-modeling
  - database-sp
  consumed_by:
  - data-access
  - database-seeding
  - integration-testing
  agent_roles:
  - delivery-agent
  validation_profile: skill-contract
  mcp_usage: none
---

# database-migrations

## Propósito

Esta skill define cómo versionar, ejecutar y revertir cambios de esquema en la base de datos de forma segura, repetible y trazable.  
Su función es asegurar que toda modificación a tablas, columnas, índices, constraints y datos de catálogo sea manejada por scripts versionados, nunca por cambios manuales directos.

Esta skill complementa `database-modeling` (diseño de tablas) y `database-sp` (lógica de negocio). Mientras esas definen QUÉ estructura y lógica existen, esta skill define CÓMO esos cambios llegan a cada entorno de forma controlada.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo se versionan los cambios de esquema?
2. ¿Cómo se nombran y organizan los scripts de migración?
3. ¿Cómo se hace rollback de una migración sin perder datos?
4. ¿Cómo se manejan migraciones en multi-tenancy (shared DB vs schema-per-tenant)?
5. ¿Cómo se garantiza idempotencia en scripts de migración?

## Relación con otras skills

- `database-modeling` define la estructura de tablas que esta skill migra.
- `database-sp` define SPs que pueden depender de columnas creadas por migraciones.
- `database-seeding` consume la infraestructura de migración para insertar datos de catálogo.
- `data-access` consume el esquema resultante de las migraciones aplicadas.
- `database-audit` define las columnas de auditoría que toda tabla debe incluir y que las migraciones deben crear.

## Qué debe hacer el agente cuando esta skill está activa

1. Crear una carpeta de migraciones con convención de naming versionado.
2. Escribir cada cambio de esquema como un script migración independiente e idempotente.
3. Incluir scripts de rollback (down) para cada migración.
4. Verificar que las columnas de auditoría (RecordStatus, RecordCreationUser, etc.) estén en toda tabla nueva.
5. Documentar el orden de dependencia entre migraciones.
6. Probar que las migraciones son reversibles en un entorno de desarrollo antes de promover.
7. Validar que las migraciones respetan las convenciones de `database-modeling` (naming, schemas, tipos).
8. Generar un manifiesto de migración que liste versión, descripción y entorno.

## Entradas esperadas

Esta skill asume que ya existe:
- diseño de tablas validado (`database-modeling`);
- convenciones de naming y schemas (`database-modeling`);
- stored procedures que dependen del esquema (`database-sp`);
- columnas de auditoría definidas (`database-audit`).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- scripts de creación de esquemas (CREATE TABLE, ALTER TABLE, CREATE INDEX);
- scripts de alteración de columnas y constraints;
- scripts de rollback (DROP, ALTER reverso);
- migraciones de datos dentro del esquema (columnas calculadas, splits, merges);
- validación pre/post migración;
- manejo de migraciones en multi-tenancy.

La fase no incluye todavía:
- datos de prueba o catálogos maestros (`database-seeding`);
- lógica de negocio en SPs (`database-sp`);
- migración de datos entre sistemas legacy.

## Principios que siempre debe respetar

- Toda modificación de esquema DEBE ser un script versionado, nunca manual.
- Los scripts de migración DEBEN ser idempotentes (pueden ejecutarse más de una vez sin error).
- Cada migración DEBE tener un script de rollback correspondiente.
- Las migraciones NUNCA deben eliminar datos de producción sin backup previo explícito.
- Las columnas de auditoría DEBEN incluirse en toda tabla nueva desde la migración inicial.
- El orden de ejecución DEBE ser secuencial por número de versión.
- Las migraciones DEBEN ser probadas en dev antes de promover a staging/producción.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la convención de naming y estructura de carpetas de migraciones;
- la herramienta de migración (Alembic);
- la estrategia de rollback para cada tipo de cambio;
- la validación pre/post migración.

Esta skill delega:
- el diseño de tablas a `database-modeling`;
- las convenciones generales de BD a `database-modeling`;
- la inserción de datos de catálogo a `database-seeding`;
- la lógica de negocio en SPs a `database-sp`.

## Qué debe definir el diseño

### 1. Convención de naming de migraciones

Definir:
- formato de nombre de archivo (`{timestamp}_{description}.py` para Alembic);
- carpeta base (`/migrations/versions/`);
- separación entre migraciones de esquema (DDL) y migraciones de datos (DML);
- convención para migraciones de rollback (scripts `downgrade` en cada revisión).

### 2. Estructura de una migración

Definir:
- header con metadata (versión, autor, fecha, descripción, ticket);
- script UP (cambio forward);
- script DOWN (rollback);
- validación pre-ejecución (IF NOT EXISTS);
- validación post-ejecución (verificar que el cambio se aplicó).

### 3. Estrategia de rollback

Definir:
- rollback por migración individual;
- rollback a un punto específico (basetime);
- reglas para columnas con datos (NO eliminar columna con datos sin migrar primero);
- manejo de rollback en tablas con FK (orden de eliminación).

### 4. Multi-tenancy en migraciones

Definir:
- estrategia para shared DB (misma migración afecta a todos los tenants);
- estrategia para schema-per-tenant (ejecutar migración en cada schema);
- estrategia para DB-per-tenant (migración distribuida con verificación por tenant);
- orden de ejecución en entornos multi-tenant.

### 5. Validación y verificación

Definir:
- script de pre-verificación (verificar que la migración no se ha aplicado);
- script de post-verificación (verificar que el cambio existe);
- cómo manejar migraciones que fallan a la mitad;
- logging de migraciones aplicadas (tabla de historial).

### 6. ⚠️ Columnas computadas por la DB + ORM async (`onupdate=func.now()`)

Si una columna usa `DEFAULT NOW()` / `ON UPDATE` computado por la DB (p. ej.
`updated_at TIMESTAMPTZ DEFAULT NOW()`) y el proyecto usa SQLAlchemy 2.0 async,
el modelo debe declarar la columna de forma coherente con el patrón de acceso
(`server_default` / `onupdate=func.now()`) y los endpoints que mutan la entidad
deben hacer `await session.refresh(entity)` post-flush antes de serializar el DTO.
Sin eso, acceder al atributo expired dispara `MissingGreenlet` (HTTP 500).
Ver la advertencia completa en `database-modeling` ("SQLAlchemy async + columnas
computadas por la DB") y el patrón de refresh en `data-access`.

## Preguntas guía

### 1. Sobre versionamiento
- ¿Qué formato de versión se usa (secuencial, timestamp, hash)?
- ¿Cómo se gestionan los conflictos cuando dos desarrolladores crean migraciones simultáneamente?

### 2. Sobre rollback
- ¿Cada migración tiene script de rollback o solo las críticas?
- ¿Cómo se maneja el rollback de una migración que ya se aplicó en producción?
- ¿Hay migraciones irreversibles (destructivas)? ¿Cómo se documentan?

### 3. Sobre multi-tenancy
- ¿Las migraciones se ejecutan en todos los tenants en paralelo o secuencialmente?
- ¿Qué pasa si un tenant falla durante la migración?
- ¿Cómo se versionan las migraciones por tenant?

### 4.Sobre CI/CD
- ¿Las migraciones se ejecutan automáticamente en el pipeline o manualmente?
- ¿Hay gates antes de ejecutar migraciones en producción?
- ¿Cómo se notifica al equipo si una migración falla?

### 5. Sobre datos
- ¿Las migraciones de esquema (DDL) y las migraciones de datos (DML) están separadas?
- ¿Los datos de catálogo van en migraciones o en seeding?
- ¿Cómo se manejan ALTER TABLE en tablas con millones de registros?

## Salidas esperadas de esta skill

### A. Carpeta de migraciones estructurada
- `/migrations/versions/a1b2c3d4e5f6_create_initial_schema.py`
- `/migrations/versions/b2c3d4e5f6g7_add_user_email_column.py`

### B. Plantilla de migración (PostgreSQL)
```sql
-- ============================================================
-- Migration: V{NNN}__{description}
-- Author: {author}
-- Date: {date}
-- Ticket: {ticket}
-- ============================================================

-- Pre-verification
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM {schema}.migration_journal WHERE version = '{NNN}') THEN
        RAISE NOTICE 'Migration V{NNN} already applied. Skipping.';
        RETURN;
    END IF;
END $$;

-- UP script
-- {description del cambio}

-- Post-verification
-- {verificar que el cambio se aplicó correctamente}

-- Record migration
INSERT INTO {schema}.migration_journal (version, description, applied_on, applied_by)
VALUES ('{NNN}', '{description}', NOW(), current_user);
```

### C. Plantilla de rollback (PostgreSQL)
```sql
-- ============================================================
-- Rollback: U{NNN}__{description}
-- Reverts: V{NNN}__{description}
-- ============================================================

-- Pre-verification
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM {schema}.migration_journal WHERE version = '{NNN}') THEN
        RAISE NOTICE 'Migration V{NNN} not applied. Nothing to rollback.';
        RETURN;
    END IF;
END $$;

-- DOWN script
-- {rollback del cambio}

-- Remove migration record
DELETE FROM {schema}.migration_journal WHERE version = '{NNN}';
```

### E. Tabla de historial de migraciones (PostgreSQL)
```sql
CREATE TABLE {schema}.migration_journal (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    description VARCHAR(500) NOT NULL,
    applied_on TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    applied_by VARCHAR(128) NOT NULL,
    execution_time_ms INT NULL,
    checksum VARCHAR(64) NULL
);

CREATE UNIQUE INDEX ux_{schema}_migration_journal_version
    ON {schema}.migration_journal (version);
```

### F. Consumidores de esta skill
- `database-seeding` consume la infraestructura de migración para insertar datos después de que el esquema está listo;
- `data-access` consume el esquema resultante para construir handlers;
- `integration-testing` usa migraciones para levantar la BD de prueba;
- `framework-operations-evolution` usa el historial de migraciones para trazabilidad en producción.

## Criterios de calidad

- Toda migración tiene script UP y DOWN correspondiente.
- Las migraciones son idempotentes: ejecutarlas más de una vez no produce error.
- Las columnas de auditoría están en toda tabla nueva desde la migración inicial.
- El naming sigue la convención definida (`V{NNN}__descripcion.sql`).
- Las migraciones destructivas (DROP COLUMN, DROP TABLE) están explícitamente documentadas y requieren aprobación.
- El orden de ejecución está garantizado por número de versión secuencial.
- Las migraciones se prueban en dev antes de promover a staging/producción.
- La tabla de historial de migraciones existe y registra cada ejecución.

## Comportamiento esperado del agente

Cuando el usuario pida crear una migración directamente sin versionado, el agente debe proponer el formato versionado y explicar los riesgos de cambios manuales.  
Cuando el usuario pida eliminar una columna con datos, el agente debe advertir sobre pérdida de datos y proponer migración previa de datos.  
Cuando el usuario tenga conflicto entre migraciones simultáneas, el agente debe sugerir la estrategia de resolución (rebase, merge manual).  
Cuando el usuario trabaje en multi-tenancy, el agente debe preguntar por la estrategia de tenant y aplicar las migraciones accordingly.

## Checklist final de la skill

- ¿Se definió la herramienta de migración (Alembic)?
- ¿Se creó la carpeta de migraciones con convención de naming?
- ¿Cada migración tiene script UP y DOWN?
- ¿Las migraciones son idempotentes?
- ¿Se creó la tabla de historial de migraciones?
- ¿Las columnas de auditoría están en toda tabla nueva?
- ¿Se documentaron las migraciones destructivas?
- ¿Se validó el orden de dependencia entre migraciones?
- ¿Se probó el rollback en un entorno de desarrollo?
- ¿Se registró el artefacto de migración para consumo de skills posteriores?