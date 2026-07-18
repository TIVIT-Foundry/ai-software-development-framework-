---
name: data-migration
description: "Data migration and ETL patterns for moving and transforming data between systems, versions, and environments. Covers big-bang vs incremental migration, data transformation, rollback of data, integrity verification, and cross-system data synchronization. Trigger: When migrating data between systems, transforming data for new schemas, or implementing ETL processes."
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - database
  enforcement: recommended
  depends_on:
  - database-migrations
  consumed_by:
  - data-access
  - integration-testing
  agent_roles:
  - delivery-agent
  validation_profile: skill-contract
  mcp_usage: none
---

# data-migration

## Propósito

Esta skill define cómo migrar datos entre sistemas, versiones y entornos de forma segura, trazable y reversible.  
A diferencia de `database-migrations` que maneja cambios de esquema (DDL), esta skill maneja la migración de los datos mismos (DML): transformaciones, ETL, sincronización entre sistemas y verificación de integridad.

Esta skill complementa `database-migrations` (cambios de esquema) y `database-seeding` (datos iniciales). Mientras esas manejan CREATE TABLE e INSERT de catálogos, esta skill maneja transformaciones de datos entre versiones y sistemas.

## Objetivo

Usa esta skill para responder estas preguntas:

1. ¿Cómo migrar datos entre versiones del esquema (ej. split de columna)?
2. ¿Cómo migrar datos entre sistemas (ej. legacy → nuevo)?
3. ¿Qué estrategia usar: big-bang, incremental o paralela?
4. ¿Cómo verificar la integridad de los datos migrados?
5. ¿Cómo hacer rollback de una migración de datos fallida?

## Relación con otras skills

- `database-migrations` maneja los cambios de esquema (DDL); esta skill maneja los datos (DML).
- `database-seeding` inserta datos iniciales; esta skill transforma datos existentes.
- `database-modeling` define el esquema destino; esta skill migra los datos al nuevo esquema.
- `integration-testing` valida que los datos migrados son correctos.

## Qué debe hacer el agente cuando esta skill está activa

1. Definir la estrategia de migración (big-bang, incremental, paralela).
2. Escribir scripts de transformación de datos idempotentes.
3. Implementar verificación de integridad antes y después de la migración.
4. Definir el procedimiento de rollback de datos.
5. Documentar las reglas de transformación (mapeo de campos).
6. Ejecutar la migración en entorno de staging antes de producción.
7. Verificar que el conteo de registros coincide entre origen y destino.
8. Documentar las diferencias aceptadas entre origen y destino.

## Entradas esperadas

Esta skill asume que ya existe:
- esquema destino creado (`database-migrations`);
- datos de origen disponibles para migración;
- reglas de transformación definidas (mapeo de campos).

Si falta esta base, la skill debe pedirla antes de concluir.

## Alcance de la fase

La fase sí incluye:
- estrategias de migración (big-bang, incremental, paralela);
- scripts de transformación de datos;
- verificación de integridad;
- rollback de datos;
- migración cross-system (legacy → nuevo);
- ETL patterns;

La fase no incluye todavía:
- cambios de esquema (cubiertos por `database-migrations`);
- datos iniciales de catálogo (cubiertos por `database-seeding`);
- replicación en tiempo real (cubierta por `real-time`).

## Principios que siempre debe respetar

- Los scripts de migración de datos DEBEN ser idempotentes.
- Los datos de origen NUNCA deben modificarse durante la migración (read-only).
- La migración DEBE incluir verificación de integridad (conteo, checksums, mapeo).
- El rollback de datos DEBE estar probado antes de la migración.
- Las reglas de transformación DEBEN estar documentadas en una tabla de mapeo.
- La migración DEBE probarse en staging antes de producción.
- Las diferencias aceptadas DEBEN documentarse explícitamente.

## Qué decide esta skill y qué delega

Esta skill sí decide:
- la estrategia de migración;
- los scripts de transformación;
- la verificación de integridad;
- el procedimiento de rollback;

Esta skill delega:
- los cambios de esquema a `database-migrations`;
- los datos iniciales de catálogo a `database-seeding`;
- la validación end-to-end a `integration-testing`.

## Qué debe definir el diseño

### 1. Estrategias de migración

| Estrategia | Descripción | Pros | Contras | Uso recomendado |
|------------|-------------|------|---------|-----------------|
| **Big-bang** | Migrar todo de una vez, pausar servicio | Simple, datos consistentes | Downtime largo, riesgo alto | Migraciones pequeñas (< 1h downtime) |
| **Incremental** | Migrar en lotes, mantener ambos sistemas | Sin downtime, rollback por lote | Complejo, datos en dos sistemas | **Por defecto**, migraciones grandes |
| **Paralela** | Escribir en ambos sistemas, leer del nuevo | Sin downtime, transición suave | Doble escritura, complejo | Migraciones críticas con SLA estricto |

### 2. Tabla de mapeo de campos

| Campo Origen | Tabla Origen | Campo Destino | Tabla Destino | Transformación | Notas |
|-------------|-------------|---------------|-------------|----------------|-------|
| `usr_name` | `Users` | `FullName` | `Customers` | Concat | `first_name + ' ' + last_name` |
| `usr_email` | `Users` | `Email` | `Customers` | Direct | Sin cambio |
| `usr_status` | `Users` | `Status` | `Customers` | Map | `A→Active, I→Inactive, *=Deleted` |
| `usr_created` | `Users` | `RecordCreationDate` | `Customers` | Cast | `datetime→datetimeoffset` |
| NULL | `Users` | `Phone` | `Customers` | Default | Default: empty string |

### 3. Script de transformación (PostgreSQL)

```sql
-- ============================================================
-- Data Migration: Users → Customers (v1 to v2)
-- Strategy: Incremental by batch
-- Batch size: 10000 records
-- ============================================================

-- Pre-verification
DO $$
DECLARE
    v_source_count INT;
    v_target_count INT;
    v_batch_size INT := 10000;
    v_rows_processed INT := 1;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM {schema}.migration_journal WHERE version = 'DATA-001') THEN
        -- Verify source data
        SELECT COUNT(*) INTO v_source_count FROM legacy.users WHERE usr_status IN ('A', 'I');
        SELECT COUNT(*) INTO v_target_count FROM {schema}.customers WHERE source_system = 'LegacyUsers';

        IF v_source_count <> v_target_count THEN
            RAISE NOTICE 'Migration DATA-001: Source count (%) <> Target count (%). Starting migration.',
                v_source_count, v_target_count;
        END IF;

        -- Migrate in batches
        WHILE v_rows_processed > 0 LOOP
            INSERT INTO {schema}.customers (
                full_name, email, phone, status,
                source_system, source_id,
                record_creation_user, record_creation_date, record_status
            )
            SELECT
                INITCAP(u.usr_first_name) || ' ' || INITCAP(u.usr_last_name),
                LOWER(u.usr_email),
                COALESCE(u.usr_phone, ''),
                CASE u.usr_status WHEN 'A' THEN 'Active' WHEN 'I' THEN 'Inactive' ELSE 'Deleted' END,
                'LegacyUsers',
                u.usr_id::VARCHAR(50),
                'MIGRATION',
                NOW(),
                'A'
            FROM legacy.users u
            WHERE u.usr_status IN ('A', 'I')
            AND NOT EXISTS (
                SELECT 1 FROM {schema}.customers c
                WHERE c.source_system = 'LegacyUsers' AND c.source_id = u.usr_id::VARCHAR(50)
            )
            LIMIT v_batch_size;

            GET DIAGNOSTICS v_rows_processed = ROW_COUNT;
            RAISE NOTICE 'Migrated % records.', v_rows_processed;
        END LOOP;

        -- Post-verification
        SELECT COUNT(*) INTO v_source_count FROM legacy.users WHERE usr_status IN ('A', 'I');
        SELECT COUNT(*) INTO v_target_count FROM {schema}.customers WHERE source_system = 'LegacyUsers';

        IF v_source_count <> v_target_count THEN
            RAISE EXCEPTION 'Migration DATA-001: Count mismatch! Source: %, Target: %',
                v_source_count, v_target_count;
        ELSE
            INSERT INTO {schema}.migration_journal (version, description, applied_on, applied_by)
            VALUES ('DATA-001', 'Users → Customers migration', NOW(), 'MIGRATION');
            RAISE NOTICE 'Migration DATA-001 completed successfully.';
        END IF;
    ELSE
        RAISE NOTICE 'Migration DATA-001 already applied. Skipping.';
    END IF;
END $$;
```

### 4. Script de verificación de integridad

```sql
-- ============================================================
-- Integrity Verification: DATA-001
-- ============================================================

-- 1. Count verification
SELECT 'Count Verification' AS check_name,
    (SELECT COUNT(*) FROM legacy.users WHERE usr_status IN ('A', 'I')) AS source_count,
    (SELECT COUNT(*) FROM {schema}.customers WHERE source_system = 'LegacyUsers') AS target_count,
    CASE
        WHEN (SELECT COUNT(*) FROM legacy.users WHERE usr_status IN ('A', 'I'))
           = (SELECT COUNT(*) FROM {schema}.customers WHERE source_system = 'LegacyUsers')
        THEN 'PASS' ELSE 'FAIL'
    END AS result;

-- 2. Null check (fields that should NOT be null)
SELECT 'Null Check' AS check_name,
    COUNT(*) AS null_records
FROM {schema}.customers
WHERE source_system = 'LegacyUsers'
AND (full_name IS NULL OR email IS NULL OR status IS NULL);

-- 3. Transformation verification (sample records)
SELECT
    u.usr_first_name || ' ' || u.usr_last_name AS source_name,
    c.full_name AS target_name,
    u.usr_email AS source_email,
    c.email AS target_email,
    u.usr_status AS source_status,
    c.status AS target_status
FROM legacy.users u
JOIN {schema}.customers c ON c.source_system = 'LegacyUsers'
    AND c.source_id = u.usr_id::VARCHAR(50)
ORDER BY u.usr_id
LIMIT 100;
```

### 5. Rollback de datos

```sql
-- ============================================================
-- Rollback: DATA-001 (Users → Customers)
-- ============================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM {schema}.migration_journal WHERE version = 'DATA-001') THEN
        -- Delete migrated records
        DELETE FROM {schema}.customers
        WHERE source_system = 'LegacyUsers';

        -- Remove migration record
        DELETE FROM {schema}.migration_journal WHERE version = 'DATA-001';

        RAISE NOTICE 'Rollback DATA-001 completed.';
    ELSE
        RAISE NOTICE 'Migration DATA-001 not applied. Nothing to rollback.';
    END IF;
END $$;
```

### 6. Migración incremental por batch

```
/migrations/data/
├── DATA-001__users_to_customers.sql      -- Migración de usuarios
├── DATA-002__orders_to_orders_v2.sql     -- Migración de pedidos
├── DATA-003__products_to_catalog.sql     -- Migración de productos
├── rollback/
│   ├── UDATA-001__users_to_customers.sql
│   ├── UDATA-002__orders_to_orders_v2.sql
│   └── UDATA-003__products_to_catalog.sql
└── verification/
    ├── VDATA-001__verify_customers.sql
    ├── VDATA-002__verify_orders_v2.sql
    └── VDATA-003__verify_catalog.sql
```

### 7. ETL patterns

| Pattern | Uso | Ejemplo |
|---------|-----|---------|
| **Extract-Transform-Load** | Migración con transformación compleja | Legacy → Nuevo sistema |
| **Extract-Load-Transform** | Cargar datos crudos, transformar en destino | Big data, data warehouse |
| **Change Data Capture** | Sincronización incremental en tiempo real | Replicación continua |
| **Snapshot** | Migración completa de un punto en el tiempo | Big-bang migration |

## Preguntas guía

### 1. Sobre estrategia
- ¿Se migra todo de una vez (big-bang) o en lotes (incremental)?
- ¿Se requiere downtime durante la migración?
- ¿Los dos sistemas coexisten durante la transición?

### 2. Sobre transformación
- ¿Qué campos cambian de nombre o tipo?
- ¿Hay campos que se concatenan o dividen?
- ¿Hay valores que se mapean (ej. estados 'A' → 'Active')?
- ¿Hay datos que se pierden en la transformación?

### 3. Sobre integridad
- ¿Cómo se verifica que todos los registros se migraron?
- ¿Se hace checksum de campos críticos?
- ¿Se verifica la consistencia referencial (FKs)?

### 4. Sobre rollback
- ¿Se puede hacer rollback de la migración de datos?
- ¿El rollback borra los datos migrados?
- ¿Se preservan los datos de origen después de la migración?

### 5. Sobre cross-system
- ¿Se necesita sincronización en tiempo real entre sistemas?
- ¿Los sistemas coexisten temporalmente?
- ¿Cómo se manejan los cambios en ambos sistemas durante la transición?

## Salidas esperadas de esta skill

### A. Tabla de mapeo de campos
- Documento con campo origen → campo destino → transformación.

### B. Scripts de migración de datos
- Scripts idempotentes en `/migrations/data/`.
- Un script por migración de datos.
- Cada script con verificación pre y post.

### C. Scripts de verificación de integridad
- Verificación de conteo.
- Verificación de checksum.
- Verificación de nulls.
- Verificación de muestreo.

### D. Scripts de rollback
- Rollback de cada migración de datos.
- Rollback idempotente.

### E. Consumidores de esta skill
- `database-migrations` provée el esquema que esta skill pobla;
- `database-seeding` provée datos de catálogo complementarios;
- `integration-testing` valida que los datos migrados son correctos;
- `framework-operations-evolution` define el proceso de migración en producción.

## Criterios de calidad

- Los scripts de migración son idempotentes (pueden ejecutarse más de una vez).
- Los datos de origen NO se modifican durante la migración.
- La verificación de integridad incluye conteo, checksums y muestreo.
- El rollback está probado antes de la migración.
- Las reglas de transformación están documentadas en tabla de mapeo.
- La migración se prueba en staging antes de producción.
- Las diferencias aceptadas están documentadas explícitamente.

## Comportamiento esperado del agente

Cuando el usuario quiera modificar datos de origen durante la migración, el agente debe rechazar y exigir que los datos de origen sean read-only durante la migración.  
Cuando el usuario quiera hacer una migración big-bang sin downtime, el agente debe advertir que big-bang implica downtime y proponer migración incremental.  
Cuando el usuario no tenga tabla de mapeo, el agente debe proponer una tabla de mapeo con campo origen, campo destino y transformación.  
Cuando el usuario no pruebe el rollback de datos, el agente debe insistir en probarlo antes de la migración a producción.

## Checklist final de la skill

- ¿Se definió la estrategia de migración (big-bang, incremental, paralela)?
- ¿Se creó la tabla de mapeo de campos?
- ¿Los scripts de migración son idempotentes?
- ¿Se incluye verificación de integridad (conteo, checksum)?
- ¿El rollback está probado?
- ¿La migración se probó en staging?
- ¿Los datos de origen son read-only durante la migración?
- ¿Las diferencias aceptadas están documentadas?
- ¿Los scripts están separados por migración (DATA-001, DATA-002)?
- ¿Se documentaron las reglas de transformación?