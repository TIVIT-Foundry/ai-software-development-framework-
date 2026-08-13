---
name: database-audit
description: 'Audit columns, logging tables, and error capture for PostgreSQL.
  Covers soft delete (RecordStatus), Log tables (log_db, audit_http), and error
  logging stored procedures. Trigger: When creating tables with audit columns,
  implementing error logging, or HTTP auditing.'
version: 1.0
metadata:
  phase:
  - construction
  layer:
  - database
  enforcement: mandatory
  depends_on:
  - database-modeling
  consumed_by:
  - database-modeling
  - database-sp
  agent_roles:
  - control-agent
  - delivery-agent
  - design-agent
  validation_profile: architecture-consistency
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| ALL transactional tables MUST have 5 audit columns | ALWAYS | Consistent tracking |
| RecordStatus MUST have a CHECK constraint | ALWAYS | Prevents invalid values |
| Use timezone-aware timestamps | ALWAYS | Consistent across timezones |
| Soft delete sets RecordStatus = '*', NEVER physical DELETE | ALWAYS | Audit trail preservation |
| ALWAYS filter `RecordStatus = 'A'` in JOINs | ALWAYS | Prevent stale data leaks |
| Error capture in every CATCH block | ALWAYS | Centralized error logging |

## Soft Delete Pattern
```sql
-- PostgreSQL
UPDATE {schema}.{table}
SET record_status = '*',
    record_edit_user = p_record_edit_user,
    record_edit_date = NOW()
WHERE {table}_id = p_id;
```

## User Parameters in DB Operations
| Operation | Required Parameter |
|-----------|--------------------|
| CREATE | `p_record_creation_user VARCHAR(50)` |
| UPDATE | `p_record_edit_user VARCHAR(50)` |
| DELETE (soft) | `p_record_edit_user VARCHAR(50)` |

## Log Tables

### log.log_db (PostgreSQL — DB error log)
```sql
log_db_id SERIAL PRIMARY KEY,
error_number INT,
error_severity INT,
error_state INT,
error_procedure VARCHAR(150),
error_line INT,
error_message VARCHAR(500),
create_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

### log.audit_http (HTTP request audit)
```sql
audit_http_id SERIAL PRIMARY KEY,
http_status_code INT,
path VARCHAR(500),
method VARCHAR(10),
request_body TEXT,
response_body TEXT,
correlation_id VARCHAR(50),
ip_address VARCHAR(50),
duration VARCHAR(20),
create_date TIMESTAMPTZ NOT NULL DEFAULT NOW()
```

## Error Logging Function Pattern (PostgreSQL)
```sql
CREATE OR REPLACE FUNCTION log.get_error_info()
RETURNS TABLE(
    error_code VARCHAR(20),
    field VARCHAR(100),
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_error_message TEXT := SQLERRM;
    v_log_id INT;
BEGIN
    INSERT INTO log.log_db (error_message, create_date)
    VALUES (v_error_message, NOW())
    RETURNING log_db_id INTO v_log_id;

    RETURN QUERY
    SELECT 'SYS_001'::VARCHAR, NULL::VARCHAR,
        'Internal error [Ref:' || v_log_id || ']'::TEXT;
END;
$$;
```

## Usage in Functions
```sql
BEGIN
    -- function logic...
EXCEPTION WHEN OTHERS THEN
    INSERT INTO log.log_db (error_message, create_date)
    VALUES (SQLERRM, NOW());
    RAISE;
END;
```
