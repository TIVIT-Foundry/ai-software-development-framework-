---
name: database-sp
description: 'Stored procedure templates (List, Get, Create, Update, Delete, Search,
  Merge) and patterns. Trigger: When creating or modifying stored procedures or database
  functions.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - database
  enforcement: mandatory
  depends_on:
  - database-modeling
  - database-audit
  - database-security
  consumed_by:
  - data-access
  - api-first-backend
  agent_roles:
  - design-agent
  - delivery-agent
  validation_profile: skill-contract
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Include header with full metadata + CHANGE HISTORY | ALWAYS | Traceability |
| Use EXCEPTION block with error logging | ALWAYS | Error handling |
| Entity name MANDATORY in all function names | ALWAYS | `{schema}.{action}_{entity}` always |
| Use whitelist for dynamic sorting | ALWAYS | SQL injection prevention |
| Return created/updated record after mutation | ALWAYS | API consistency |
| Use dot notation for nested structures | ALWAYS | ORM/mapping compatibility |

## Function Types Decision
| Need | Function Type |
|------|---------|
| List with pagination | List |
| Get single record | Get |
| Insert new record | Create |
| Update existing record | Update |
| Soft delete | Delete |
| Advanced search w/o pagination | Search |
| Bulk sync (insert/update) | Merge |

## Standard Structure (PostgreSQL)
```sql
/* ============================================================
   FUNCTION: {schema}.{operation}_{entity}
   Description: ...
   Author: ...
   Version: 1.0
   CHANGE HISTORY:
   | Version | Date | Author | Change |
   ============================================================ */
CREATE OR REPLACE FUNCTION {schema}.{operation}_{entity}(
    p_param VARCHAR(100),
    p_page INT DEFAULT 1,
    p_page_size INT DEFAULT 20
)
RETURNS TABLE(
    error_code VARCHAR(20),
    field VARCHAR(100),
    message TEXT,
    -- result columns...
    total_count BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    c_status_draft INT := 1101;  -- c_ prefix for constants
    v_group_id INT;              -- v_ prefix for variables
BEGIN
    ---------------------------------------------------------------
    -- STEP 1: Validations
    ---------------------------------------------------------------
    -- STEP 2: Operation
    ---------------------------------------------------------------
    -- STEP 3: Return result
    ---------------------------------------------------------------
    RETURN QUERY
    SELECT NULL::VARCHAR, NULL::VARCHAR, NULL::TEXT, /* result columns */;
EXCEPTION
    WHEN OTHERS THEN
        INSERT INTO log.log_db (error_message, created_at)
        VALUES (SQLERRM, NOW());
        RETURN QUERY
        SELECT 'SYS_001'::VARCHAR, NULL::VARCHAR,
            'Internal error'::TEXT, /* nulls for result columns */;
END;
$$;
```

## CONSTANTS and VARIABLES
```sql
c_status_draft INT := 1101;  -- c_ prefix for constants
v_group_id INT;              -- v_ prefix for variables
```

## Nested Structure (Dot Notation)
```sql
st.master_table_id AS "status.master_table_id",
st.name AS "status.name",
st.value AS "status.value"
```

## Sorting Pattern (Whitelist with PL/pgSQL)
```sql
DECLARE
    v_allowed_columns TEXT[] := ARRAY['created_date', 'priority', 'name', 'record_creation_date'];
    v_valid_sort_order TEXT;
BEGIN
    IF NOT (p_sort_by = ANY(v_allowed_columns)) THEN
        p_sort_by := 'created_date';
    END IF;
    IF UPPER(p_sort_order) NOT IN ('ASC', 'DESC') THEN
        p_sort_order := 'DESC';
    END IF;

    -- Use dynamic SQL with EXECUTE ... USING for safe ORDER BY
    EXECUTE format(
        'SELECT ... ORDER BY %I %s, created_date DESC LIMIT $1 OFFSET $2',
        p_sort_by, p_sort_order
    ) USING p_page_size, (p_page - 1) * p_page_size;
END;
```

## Pagination — TotalCount in Single ResultSet (PostgreSQL)
```sql
SELECT t.{entity}_id, ..., COUNT(*) OVER() AS total_count
FROM {schema}.{entity} t
WHERE t.record_status = 'A'
ORDER BY ...
LIMIT p_page_size OFFSET (p_page - 1) * p_page_size;
```

## Search Pattern
```sql
v_search_pattern TEXT := NULL;
IF p_search_filter IS NOT NULL AND TRIM(p_search_filter) <> '' THEN
    v_search_pattern := '%' || TRIM(p_search_filter) || '%';
END IF;
-- Use in WHERE: AND (v_search_pattern IS NULL OR column_a ILIKE v_search_pattern OR column_b ILIKE v_search_pattern)
```

## JSON Parameters Pattern (PostgreSQL)
```sql
p_cases_json JSONB DEFAULT NULL;

INSERT INTO {schema}.{table} (col1, col2)
SELECT (rec->>'col1')::INT, (rec->>'col2')::INT
FROM jsonb_array_elements(p_cases_json) AS rec;
```

## Error Handling — Two Mechanisms
1. **Business/Validation errors** → `RETURN QUERY SELECT ErrorCode, Field, Message, ...; RETURN;` (not RAISE)
2. **System/SQL errors** → `EXCEPTION WHEN OTHERS THEN INSERT INTO log.log_db ... END;`

## Authorization Pattern
```sql
IF v_has_permission = FALSE THEN
    RETURN QUERY
    SELECT 'AUTH_001'::VARCHAR, 'user_id'::VARCHAR, 'Unauthorized'::TEXT, NULL::BIGINT;
    RETURN;
END IF;
```

## File Organization
```
database/{schema}/functions/
├── {schema}.create_{entity}.sql
├── {schema}.get_{entity}.sql
├── {schema}.list_{entity}.sql
├── {schema}.update_{entity}.sql
└── {schema}.delete_{entity}.sql
```

## Checklist
- [ ] Header with CHANGE HISTORY table
- [ ] Parameters with `p_` prefix / OUT params
- [ ] Variables with `v_` / `c_` prefix
- [ ] EXCEPTION block with error logging
- [ ] Safe sorting (whitelist pattern with EXECUTE ... USING)
- [ ] Business errors via RETURN QUERY SELECT (not RAISE)
- [ ] Return created/updated record after mutations
- [ ] Dot notation for nested structures
- [ ] TotalCount via `COUNT(*) OVER()` in same ResultSet

## Alternativas a Stored Procedures: ORM (Python/SQLAlchemy)

### Decisión: ¿CUÁNDO usar funciones PL/pgSQL vs ORM?

| Criterio | PL/pgSQL Functions | SQLAlchemy ORM |
|---|---|---|
| Lógica de negocio compleja en BD | Ideal | No óptimo |
| Reportes y agregaciones pesadas | Ideal | Puede ser lento |
| CRUD simple sobre una tabla | Over-engineering | Ideal |
| Cambios frecuentes de esquema | Requiere actualizar función | Migración automática |
| Control fino de performance SQL | Ideal | Depende del ORM |
| Testing unitario del backend | Difícil (mock funciones) | Fácil (mock repos) |

### Patrón Python (stack de referencia del framework)

```python
# CRUD simple: SQLAlchemy ORM
async def list_productos(session: AsyncSession, page: int, size: int):
    result = await session.execute(
        select(Producto)
        .where(Producto.activo == True)
        .order_by(Producto.nombre)
        .offset((page - 1) * size)
        .limit(size)
    )
    return result.scalars().all()

# Consultas complejas: text() con función PL/pgSQL
async def get_reporte_ventas(session: AsyncSession, desde: date, hasta: date):
    result = await session.execute(
        text("SELECT * FROM sp_reporte_ventas_por_periodo(:desde, :hasta)"),
        {"desde": desde, "hasta": hasta}
    )
    return result.fetchall()
```

### Regla de decisión

1. **CRUD simple** (1 tabla, operaciones estándar): Usar ORM. No crear función PL/pgSQL para esto.
2. **Consultas con joins y filtros**: ORM con includes/relations si la complejidad es baja. Función PL/pgSQL si la query tiene 3+ joins o agregaciones.
3. **Reportes y aggregation pipelines**: Función PL/pgSQL o SQL directo. NUNCA a través de ORM.
4. **Lógica de negocio en BD** (validaciones complejas, cálculos): Función PL/pgSQL. Nunca en ORM.
5. **Operaciones batch** (masivas): Función PL/pgSQL con bulk operations o SQL directo.

### Patrón híbrido recomendado

Para proyectos del framework:
- **Data Access Layer** (skill `data-access`): Usar ORM para CRUD, SQLAlchemy raw SQL para funciones PL/pgSQL.
- **Funciones PL/pgSQL para**: reporting, lógica compleja en BD, operaciones batch, validaciones multi-tabla.
- **ORM para**: CRUD simple, consultas con relaciones simples, paginación estándar.
