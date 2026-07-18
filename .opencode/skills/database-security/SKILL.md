---
name: database-security
description: 'SQL security validations: reserved words, invalid characters, error
  code catalog, input validation patterns, and safe dynamic sorting. Trigger: When
  implementing SP/query validations, error codes, or SQL injection prevention.'
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
  - database-sp
  agent_roles:
  - control-agent
  - design-agent
  validation_profile: security-review
mcp_usage: none
---

## Critical Rules
| Rule | Type | Rationale |
|------|------|-----------|
| Validate reserved words before any dynamic name usage | ALWAYS | Prevent SQL injection via object names |
| Validate invalid characters on all free-text inputs | ALWAYS | Prevent injection via special chars |
| Use QUOTENAME + whitelist for dynamic sorting | ALWAYS | Only safe columns in ORDER BY |
| Use standard error code prefixes (VAL_, {MOD}_, SYS_, AUTH_) | ALWAYS | Consistent error handling |
| Return errors as `SELECT ErrorCode, Field, Message` + `RETURN` | ALWAYS | Compatible with backend error handler |
| Normalize pagination params, don't reject | ALWAYS | UX-friendly |
| NEVER use string concatenation in SQL queries | NEVER | SQL injection prevention |
| Always use parameterized queries | ALWAYS | Input safety |

## Reserved Word Validation (PostgreSQL)
```sql
CREATE OR REPLACE FUNCTION cnfg.is_reserved_word(p_word VARCHAR(100))
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN EXISTS (SELECT 1 FROM cnfg.sql_reserved_words WHERE word = UPPER(TRIM(p_word)));
END;
$$;
```

## Invalid Characters Validation (PostgreSQL)
```sql
CREATE OR REPLACE FUNCTION cnfg.has_invalid_characters(p_value VARCHAR(500))
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN (p_value ~ '[-\;''"%*]'
        OR p_value ~ '[-][-]'
        OR p_value ~ '[/][*]'
        OR p_value ~ '[*][/]'
        OR POSITION(CHR(0) IN p_value) > 0);
END;
$$;
```

## Error Code Catalog

### Validation Errors (VAL_)
| Code | Description |
|------|-------------|
| VAL_001 | Required field |
| VAL_002 | Invalid format |
| VAL_003 | SQL reserved word |
| VAL_004 | Invalid characters |
| VAL_005 | Invalid date range |
| VAL_006 | Invalid JSON syntax |
| VAL_007 | Value out of range |
| VAL_008 | Length exceeded |

### Business Errors ({MOD}_)
| Code | Description |
|------|-------------|
| {MOD}_001 | Record not found |
| {MOD}_002 | Duplicate record |
| {MOD}_003 | Record in use (cannot delete) |
| {MOD}_004 | State does not allow this operation |
| {MOD}_005 | Limit exceeded |

### System Errors (SYS_)
| Code | Description |
|------|-------------|
| SYS_001 | Internal system error |

### Auth Errors (AUTH_)
| Code | Description |
|------|-------------|
| AUTH_001 | Unauthorized |
| AUTH_002 | Token expired |
| AUTH_003 | Insufficient permissions |

## Safe Dynamic Sorting (Anti-Injection, PostgreSQL)
```sql
DECLARE
    v_allowed_columns TEXT[] := ARRAY['code', 'name', 'amount', 'record_creation_date'];
    v_sort_column TEXT;
    v_sort_order TEXT;
BEGIN
    v_sort_column := REGEXP_REPLACE(p_sort_by, '[ ;]', '', 'g');

    IF NOT (v_sort_column = ANY(v_allowed_columns)) THEN
        v_sort_column := 'record_creation_date';
    END IF;

    v_sort_order := CASE WHEN UPPER(p_sort_order) IN ('ASC', 'DESC')
        THEN UPPER(p_sort_order) ELSE 'ASC' END;

    -- Use EXECUTE ... USING with format() for safe dynamic ORDER BY
    RETURN QUERY EXECUTE
        format('SELECT * FROM %I.%I ORDER BY %I %s',
            p_schema, p_table, v_sort_column, v_sort_order);
END;
```
