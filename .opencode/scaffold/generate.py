#!/usr/bin/env python3
"""
Scaffolding Generator for TIVIT Foundry Framework.

Parses an api-first-spec markdown document and generates:
- Backend: Python FastAPI + SQLAlchemy 2.0 OR Bun (TypeScript) + Elysia + postgres.js
- Frontend: React + Vite (function components, hooks) OR Angular (standalone components, signals)
- Database: PostgreSQL DDL + functions
- Tests: Playwright E2E

Usage:
    python generate.py <spec-file> [--output <output-dir>] [--backend python|bun] [--frontend react|angular] [--namespace <ns>] [--schema <schema>]
"""

import re
import os
import sys
import argparse
from string import Template
from pathlib import Path


# ─── Template loading ────────────────────────────────────────────────────────

TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_template(name):
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return Template(path.read_text())


# ─── Pluralization ───────────────────────────────────────────────────────────

def pluralize(word):
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if word.endswith("y") and len(word) > 2 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    return word + "s"


# ─── Name helpers ────────────────────────────────────────────────────────────

def camel(s):
    return s[0].lower() + s[1:] if s else s


def to_snake(name):
    result = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    result = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", result)
    return result.lower()


def to_camel(name):
    s = to_snake(name)
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def pascal_plural(name):
    return pluralize(name)[0].upper() + pluralize(name)[1:]


# ─── Spec parsing ────────────────────────────────────────────────────────────

def parse_spec(filepath):
    with open(filepath, "r") as f:
        content = f.read()

    module_name = extract_module_name(content)
    entities = extract_entities(content)
    endpoints = extract_endpoints(content)
    dtos = extract_dtos(content)

    return {
        "module": module_name,
        "entities": entities,
        "endpoints": endpoints,
        "dtos": dtos,
    }


def extract_module_name(content):
    match = re.search(r"^#\s+(?:Module[:\s]+)?(.+)$", content, re.MULTILINE)
    if not match:
        print("Warning: No module title found, using 'UnknownModule'")
        return "UnknownModule"
    name = match.group(1).strip()
    name = "".join(word.capitalize() for word in re.split(r"[\s_/-]+", name))
    return name


def extract_entities(content):
    entities = []
    section = re.search(
        r"##\s*(?:Entity|ERD|Database|Tables|Model).*?\n(.+?)(?=\n##\s|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not section:
        return entities

    body = section.group(1)
    lines = body.split("\n")
    current_entity = None
    fields = []
    header_mode = True

    for line in lines:
        ent_match = re.match(r"^###\s+(.+)$", line)
        if ent_match:
            if current_entity and fields:
                entities.append({"name": current_entity, "fields": fields})
            current_entity = ent_match.group(1).strip()
            fields = []
            header_mode = True
            continue

        if not current_entity:
            continue

        if not line.strip().startswith("|"):
            if not header_mode:
                if current_entity and fields:
                    entities.append({"name": current_entity, "fields": fields})
                current_entity = None
                fields = []
                header_mode = True
            continue

        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 2:
            continue

        if header_mode:
            if all(p.strip("-: ") == "" for p in parts):
                header_mode = False
            continue

        field_name = parts[0].strip("`* ")
        field_type = parts[1].strip("`* ") if len(parts) > 1 else "string"
        field_desc = parts[2].strip() if len(parts) > 2 else ""
        fields.append({"name": field_name, "type": field_type, "desc": field_desc})

    if current_entity and fields:
        entities.append({"name": current_entity, "fields": fields})

    if not entities:
        first_table = extract_first_table(body)
        if first_table:
            entities.append({"name": "Entity", "fields": first_table})

    return entities


def extract_first_table(body):
    lines = body.strip().split("\n")
    in_table = False
    fields = []
    for line in lines:
        if line.strip().startswith("|") and line.strip().endswith("|"):
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                if not in_table:
                    in_table = True
                    continue
                if all(p.strip("-: ") == "" for p in parts):
                    continue
                field_name = parts[0].strip("`* ")
                field_type = parts[1].strip("`* ")
                fields.append({"name": field_name, "type": field_type, "desc": parts[2].strip() if len(parts) > 2 else ""})
        elif in_table and fields:
            break
    return fields if fields else None


def extract_endpoints(content):
    section = re.search(
        r"##\s*(?:Endpoint|API|Routes).*?\n(.+?)(?=\n##\s|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not section:
        return []

    body = section.group(1)
    endpoints = []
    lines = body.strip().split("\n")
    in_header = True

    for line in lines:
        if not line.strip().startswith("|"):
            in_header = False
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        parts = [p for p in parts if p]
        if len(parts) < 2:
            continue
        if in_header:
            if all(p.strip("-: ") == "" for p in parts):
                in_header = False
            continue
        method = parts[0].strip().upper()
        path = parts[1].strip()
        desc = parts[2].strip() if len(parts) > 2 else ""
        endpoints.append({"method": method, "path": path, "desc": desc})

    return endpoints


def extract_dtos(content):
    dtos = {}
    section = re.search(
        r"##\s*(?:DTO|Request|Response|Types).*?\n(.+?)(?=\n##\s|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not section:
        return dtos

    body = section.group(1)
    lines = body.split("\n")
    current_dto = None
    fields = []
    header_mode = True

    for line in lines:
        dto_match = re.match(r"^###\s+(.+)$", line)
        if dto_match:
            if current_dto and fields:
                dtos[current_dto] = fields
            current_dto = dto_match.group(1).strip()
            fields = []
            header_mode = True
            continue

        if not current_dto:
            continue

        if not line.strip().startswith("|"):
            if not header_mode:
                if current_dto and fields:
                    dtos[current_dto] = fields
                current_dto = None
                fields = []
                header_mode = True
            continue

        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        parts = [p for p in parts if p]
        if len(parts) < 2:
            continue

        if header_mode:
            if all(p.strip("-: ") == "" for p in parts):
                header_mode = False
            continue

        field_name = parts[0].strip("`* ")
        field_type = parts[1].strip("`* ")
        field_required = parts[2].strip() if len(parts) > 2 else "Yes"
        fields.append({"name": field_name, "type": field_type, "required": field_required})

    if current_dto and fields:
        dtos[current_dto] = fields

    return dtos


# ─── Type mapping helpers ────────────────────────────────────────────────────

SYSTEM_FIELD_NAMES = {
    "id", "created_at", "created_date", "createdat", "createddate",
    "created_by", "created_user", "createdby", "createduser",
    "updated_at", "updated_date", "updatedat", "updateddate",
    "updated_by", "updated_user", "updatedby", "updateduser",
    "record_status", "recordstatus", "is_deleted", "isdeleted",
}


def is_system_field(name):
    return name.lower().replace(" ", "_").replace("-", "_") in SYSTEM_FIELD_NAMES


def normalize_spec_type(t):
    return t.strip("`").rstrip("?").lower().replace(" ", "_").replace("-", "_")


def py_type(t):
    """Map spec type to Python type annotation."""
    base = normalize_spec_type(t)
    mapping = {
        "int": "int", "integer": "int",
        "string": "str", "str": "str", "text": "str",
        "bool": "bool", "boolean": "bool",
        "datetime": "datetime", "date": "datetime",
        "decimal": "float", "float": "float", "double": "float",
        "guid": "UUID", "uuid": "UUID",
        "enum": "str",
    }
    py = mapping.get(base, "str")
    nullable = t.strip("`").endswith("?")
    if nullable:
        py += " | None"
    return py


def sa_column_type(t):
    """Map spec type to SQLAlchemy column type."""
    base = normalize_spec_type(t)
    mapping = {
        "int": "Integer", "integer": "Integer",
        "string": "String(255)", "str": "String(255)",
        "text": "Text",
        "bool": "Boolean", "boolean": "Boolean",
        "datetime": "DateTime(timezone=True)", "date": "DateTime(timezone=True)",
        "decimal": "Numeric(18,2)", "float": "Numeric(18,6)", "double": "Numeric(18,6)",
        "guid": "UUID", "uuid": "UUID",
        "enum": "String(50)",
    }
    return mapping.get(base, "String(255)")


def pg_type(t):
    """Map spec type to PostgreSQL column type."""
    base = normalize_spec_type(t)
    mapping = {
        "int": "INTEGER", "integer": "INTEGER",
        "string": "VARCHAR(255)", "str": "VARCHAR(255)",
        "text": "TEXT",
        "bool": "BOOLEAN", "boolean": "BOOLEAN",
        "datetime": "TIMESTAMPTZ", "date": "TIMESTAMPTZ",
        "decimal": "NUMERIC(18,2)", "float": "NUMERIC(18,6)", "double": "NUMERIC(18,6)",
        "guid": "UUID", "uuid": "UUID",
        "enum": "VARCHAR(50)",
    }
    return mapping.get(base, "VARCHAR(255)")


def ts_type(t):
    """Map spec type to TypeScript type."""
    base = normalize_spec_type(t)
    mapping = {
        "int": "number", "integer": "number",
        "string": "string", "str": "string", "text": "string",
        "bool": "boolean", "boolean": "boolean",
        "datetime": "string", "date": "string",
        "decimal": "number", "float": "number", "double": "number",
        "guid": "string", "uuid": "string",
        "enum": "string",
    }
    result = mapping.get(base, "string")
    nullable = t.strip("`").endswith("?")
    if nullable:
        result += " | null"
    return result


def bun_zod_type(t):
    """Map spec type to Zod builder expression."""
    base = normalize_spec_type(t)
    mapping = {
        "int": "z.number().int()", "integer": "z.number().int()",
        "string": "z.string().max(255)", "str": "z.string().max(255)", "text": "z.string().max(1000)",
        "bool": "z.boolean()", "boolean": "z.boolean()",
        "datetime": "z.string().datetime()", "date": "z.string().datetime()",
        "decimal": "z.number()", "float": "z.number()", "double": "z.number()",
        "guid": "z.string().uuid()", "uuid": "z.string().uuid()",
        "enum": "z.string()",
    }
    zod = mapping.get(base, "z.string()")
    nullable = t.strip("`").endswith("?")
    if nullable:
        zod += ".optional().nullable()"
    return zod


# ─── Field generation helpers ────────────────────────────────────────────────

def field_snake(field):
    return to_snake(field["name"])


def field_camel(field):
    return to_camel(field["name"])


def py_model_field(field):
    """Generate SQLAlchemy mapped_column declaration line."""
    sn = field_snake(field)
    pt = py_type(field["type"])
    ct = sa_column_type(field["type"])
    nullable = field["type"].strip("`").endswith("?")
    parts = [f'    {sn}: Mapped[{pt}] = mapped_column({ct}']
    if nullable:
        parts.append(", nullable=True")
    if sn == "id":
        parts.append(", primary_key=True")
    parts.append(")")
    return "".join(parts)


def py_pydantic_field(field):
    """Generate Pydantic field declaration for create/update models."""
    sn = field_snake(field)
    pt = py_type(field["type"])
    nullable = field["type"].strip("`").endswith("?")
    if nullable:
        return f"    {sn}: {pt} = Field(None)"
    return f"    {sn}: {pt} = Field(...)"


def py_response_field(field):
    """Generate Pydantic field declaration for response model."""
    sn = field_snake(field)
    pt = py_type(field["type"])
    return f"    {sn}: {pt}"


def ts_field_decl(field):
    """Generate TypeScript interface field declaration."""
    cn = field_camel(field)
    tt = ts_type(field["type"])
    return f"  {cn}: {tt};"


def bun_zod_field(field):
    """Generate Zod field declaration."""
    cn = field_camel(field)
    zod = bun_zod_type(field["type"])
    return f"  {cn}: {zod},"


def bun_zod_field_optional(field):
    """Generate Zod field declaration where all fields are optional."""
    cn = field_camel(field)
    zod = bun_zod_type(field["type"])
    if ".optional()" not in zod:
        zod += ".optional()"
    return f"  {cn}: {zod},"


def pg_column_def(field):
    """Generate PostgreSQL column definition for CREATE TABLE."""
    sn = field_snake(field)
    pgt = pg_type(field["type"])
    nullable = field["type"].strip("`").endswith("?")
    null_clause = "" if nullable else " NOT NULL"
    return f"    {sn} {pgt}{null_clause},"


def pg_select_col(field):
    """Generate SELECT column reference with alias."""
    sn = field_snake(field)
    return f"        t.{sn},"


def pg_fn_param(field):
    """Generate PL/pgSQL function parameter declaration."""
    sn = field_snake(field)
    pgt = pg_type(field["type"])
    nullable = field["type"].strip("`").endswith("?")
    default = " DEFAULT NULL" if nullable else ""
    return f"    p_{sn} {pgt}{default}"


def pg_insert_col(field):
    """Generate INSERT column name."""
    return f"        {field_snake(field)}"


def pg_insert_value(field, index):
    """Generate INSERT value placeholder."""
    return f"        p_{field_snake(field)}"


def pg_update_set(field):
    """Generate SET clause for UPDATE."""
    sn = field_snake(field)
    return f"        {sn} = p_{sn}"


# ─── React (JSX) helpers ─────────────────────────────────────────────────────

def jsx_table_headers(fields):
    lines = []
    for f in fields:
        cn = field_camel(f)
        label = f["name"].replace("_", " ").title()
        lines.append(f"              <th onClick={{() => handleSort('{cn}')}}>{label}</th>")
    return "\n".join(lines)


def jsx_table_cells(fields):
    lines = []
    for f in fields:
        cn = field_camel(f)
        lines.append(f"                <td>{{item.{cn}}}</td>")
    return "\n".join(lines)


def jsx_form_fields(fields):
    lines = []
    for f in fields:
        cn = field_camel(f)
        label = re.sub(r"([A-Z])", r" \1", f["name"]).strip().title()
        base = normalize_spec_type(f["type"])
        if base in ("int", "integer"):
            input_type = "number"
        elif base in ("datetime", "date"):
            input_type = "datetime-local"
        elif base in ("bool", "boolean"):
            input_type = "checkbox"
        else:
            input_type = "text"
        nullable = f["type"].strip("`").endswith("?")
        required = "" if nullable else " required"
        if input_type == "checkbox":
            value_expr = (
                f"checked={{Boolean(values.{cn})}} "
                f"onChange={{(e) => setValues((v) => ({{ ...v, {cn}: e.target.checked }}))}}"
            )
        else:
            value_expr = (
                f"value={{values.{cn} ?? ''}} "
                f"onChange={{(e) => setValues((v) => ({{ ...v, {cn}: e.target.value }}))}}"
            )
        lines.append(
            f'      <div className="field">\n'
            f'        <label htmlFor="{cn}">{label}</label>\n'
            f'        <input id="{cn}" type="{input_type}" {value_expr}{required} />\n'
            f"      </div>"
        )
    return "\n".join(lines)


# ─── Angular helpers ──────────────────────────────────────────────────────────

def ng_table_headers(fields):
    lines = []
    for f in fields:
        cn = field_camel(f)
        label = f["name"].replace("_", " ").title()
        lines.append(f'          <th (click)="onSort(\'{cn}\')">{label}</th>')
    return "\n".join(lines)


def ng_table_cells(fields):
    lines = []
    for f in fields:
        cn = field_camel(f)
        lines.append(f'            <td>{{{{ item.{cn} }}}}</td>')
    return "\n".join(lines)


def ng_form_controls(fields):
    lines = []
    for f in fields:
        sn = field_snake(f)
        cn = field_camel(f)
        validators = []
        nullable = f["type"].strip("`").endswith("?")
        if not nullable:
            validators.append("Validators.required")
        max_match = re.search(r"(\d+)\s*(?:chars|characters|max)", f.get("desc", ""), re.IGNORECASE)
        if max_match:
            validators.append(f"Validators.maxLength({max_match.group(1)})")
        validators_str = ", ".join(validators) if validators else "[]"
        lines.append(f"      {sn}: [values?.{cn} ?? null, {validators_str}],")
    return "\n".join(lines)


def ng_form_fields(fields):
    lines = []
    for f in fields:
        sn = field_snake(f)
        label = re.sub(r"([A-Z])", r" \1", f["name"]).strip().title()
        base = normalize_spec_type(f["type"])
        if base in ("int", "integer"):
            input_type = "number"
        elif base in ("datetime", "date"):
            input_type = "datetime-local"
        elif base in ("bool", "boolean"):
            input_type = "checkbox"
        else:
            input_type = "text"
        lines.append(
            f'  <div class="field">\n    <label for="{sn}">{label}</label>\n    '
            f'<input id="{sn}" formControlName="{sn}" type="{input_type}" />\n  </div>'
        )
    return "\n".join(lines)


# ─── Bun helpers ─────────────────────────────────────────────────────────────

def bun_insert_cols_csv(fields):
    return ", ".join(field_snake(f) for f in fields)


def bun_insert_values_csv(fields):
    return ", ".join(f"${{data.{field_camel(f)}}}" for f in fields)


def bun_update_set_csv(fields):
    return ", ".join(f"{field_snake(f)} = ${{data.{field_camel(f)}}}" for f in fields)


def has_field_like(fields, *keywords):
    """Return True if any field name contains all keywords (case-insensitive)."""
    for f in fields:
        name_lower = f["name"].lower()
        if all(kw in name_lower for kw in keywords):
            return True
    return False


def generate_bun_service(entity, ctx):
    """Generate the Bun service file programmatically because SQL varies per entity."""
    entity_name = ctx["ENTITY"]
    entity_camel = ctx["entity"]
    entities_pascal = ctx["ENTITIES"]
    business_fields = [f for f in entity["fields"] if not is_system_field(f["name"])]
    insert_cols = bun_insert_cols_csv(business_fields)
    insert_values = bun_insert_values_csv(business_fields)
    update_set = bun_update_set_csv(business_fields)

    return f"""import {{ sql }} from './{entity_camel}.db';
import type {{
  {entity_name}Create,
  {entity_name}Update,
  {entity_name}QueryParams,
}} from './{entity_camel}.dto';

export async function list{entities_pascal}(params: {entity_name}QueryParams) {{
  const {{
    page = 1,
    pageSize = 20,
    sortBy = 'created_at',
    sortOrder = 'DESC',
    searchFilter,
  }} = params;
  const offset = (page - 1) * pageSize;

  const searchClause = searchFilter
    ? sql`AND (CAST(id AS TEXT) ILIKE ${{`%${{searchFilter}}%`}} OR title ILIKE ${{`%${{searchFilter}}%`}})`
    : sql``;

  const items = await sql`
    SELECT *
    FROM ${{sql.unsafe('{ctx["SCHEMA"]}')}}.${{sql.unsafe('{ctx["TABLE"]}')}}
    WHERE record_status = 'A'
    ${{searchClause}}
    ORDER BY ${{sql.unsafe(sortBy)}} ${{sql.unsafe(sortOrder)}}
    LIMIT ${{pageSize}}
    OFFSET ${{offset}}
  `;

  const [{{ count }}] = await sql`
    SELECT COUNT(*) AS count
    FROM ${{sql.unsafe('{ctx["SCHEMA"]}')}}.${{sql.unsafe('{ctx["TABLE"]}')}}
    WHERE record_status = 'A'
    ${{searchClause}}
  `;

  return {{
    items,
    total: Number(count),
    page,
    pageSize,
  }};
}}

export async function get{entity_name}(id: number) {{
  const [item] = await sql`
    SELECT * FROM ${{sql.unsafe('{ctx["SCHEMA"]}')}}.${{sql.unsafe('{ctx["TABLE"]}')}}
    WHERE id = ${{id}} AND record_status = 'A'
  `;
  return item ?? null;
}}

export async function create{entity_name}(data: {entity_name}Create) {{
  const [item] = await sql`
    INSERT INTO ${{sql.unsafe('{ctx["SCHEMA"]}')}}.${{sql.unsafe('{ctx["TABLE"]}')}} (
      {insert_cols},
      created_by
    ) VALUES (
      {insert_values},
      1
    )
    RETURNING *
  `;
  return item;
}}

export async function update{entity_name}(id: number, data: {entity_name}Update) {{
  const [item] = await sql`
    UPDATE ${{sql.unsafe('{ctx["SCHEMA"]}')}}.${{sql.unsafe('{ctx["TABLE"]}')}}
    SET
      {update_set},
      updated_at = NOW(),
      updated_by = 1
    WHERE id = ${{id}} AND record_status = 'A'
    RETURNING *
  `;
  return item ?? null;
}}

export async function delete{entity_name}(id: number) {{
  const result = await sql`
    UPDATE ${{sql.unsafe('{ctx["SCHEMA"]}')}}.${{sql.unsafe('{ctx["TABLE"]}')}}
    SET record_status = 'I', updated_at = NOW(), updated_by = 1
    WHERE id = ${{id}} AND record_status = 'A'
  `;
  return result.count > 0;
}}
"""


# ─── Substitution context ────────────────────────────────────────────────────

def build_context(spec, entity):
    entities_plural = pluralize(entity["name"])
    entity_name = entity["name"]
    module = spec["module"]
    module_camel = camel(module)
    entity_camel = camel(entity_name)
    entities_lower = entities_plural.lower()
    table_name = entities_lower
    schema = spec.get("schema", "public")

    all_fields = entity["fields"]
    business_fields = [f for f in all_fields if not is_system_field(f["name"])]

    # ── Python / SQLAlchemy ──
    py_all_lines = []
    for f in all_fields:
        py_all_lines.append(py_model_field(f))
    existing_snakes = {field_snake(f) for f in all_fields}
    if "id" not in existing_snakes:
        py_all_lines.insert(
            0,
            "    id: Mapped[int] = mapped_column(Integer, primary_key=True)"
        )
    if "created_at" not in existing_snakes:
        py_all_lines.append(
            "    created_at: Mapped[datetime] = mapped_column("
            "DateTime(timezone=True), server_default=func.now())"
        )
    if "created_by" not in existing_snakes:
        py_all_lines.append(
            "    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)"
        )
    if "updated_at" not in existing_snakes:
        py_all_lines.append(
            "    updated_at: Mapped[datetime | None] = mapped_column("
            "DateTime(timezone=True), nullable=True, onupdate=func.now())"
        )
    if "updated_by" not in existing_snakes:
        py_all_lines.append(
            "    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)"
        )
    if "record_status" not in existing_snakes:
        py_all_lines.append(
            "    record_status: Mapped[str] = mapped_column("
            "String(1), default='A', server_default='A')"
        )

    py_create_lines = [py_pydantic_field(f) for f in business_fields]

    py_update_lines = []
    for f in business_fields:
        sn = field_snake(f)
        pt = py_type(f["type"])
        optional_pt = pt if pt.endswith("| None") else f"{pt} | None"
        py_update_lines.append(f"    {sn}: {optional_pt} = Field(None)")

    py_response_lines = []
    for f in all_fields:
        py_response_lines.append(py_response_field(f))
    if "id" not in existing_snakes:
        py_response_lines.insert(0, "    id: int")
    if "created_at" not in existing_snakes:
        py_response_lines.append("    created_at: datetime")
    if "created_by" not in existing_snakes:
        py_response_lines.append("    created_by: int | None")
    if "updated_at" not in existing_snakes:
        py_response_lines.append("    updated_at: datetime | None")
    if "updated_by" not in existing_snakes:
        py_response_lines.append("    updated_by: int | None")
    if "record_status" not in existing_snakes:
        py_response_lines.append("    record_status: str")

    # ── TypeScript / React ──
    ts_lines = []
    for f in all_fields:
        ts_lines.append(ts_field_decl(f))
    if "id" not in existing_snakes:
        ts_lines.insert(0, "  id: number;")
    if "created_at" not in existing_snakes:
        ts_lines.append("  createdAt: string;")
    if "created_by" not in existing_snakes:
        ts_lines.append("  createdBy: number | null;")
    if "updated_at" not in existing_snakes:
        ts_lines.append("  updatedAt: string | null;")
    if "updated_by" not in existing_snakes:
        ts_lines.append("  updatedBy: number | null;")
    if "record_status" not in existing_snakes:
        ts_lines.append("  recordStatus: string;")

    ts_create_lines = [ts_field_decl(f) for f in business_fields]
    ts_update_lines = [ts_field_decl(f) for f in business_fields]

    # ── PostgreSQL ──
    # Table DDL + SELECTs include every spec field so the schema matches the model.
    pg_col_lines = []
    if "id" not in existing_snakes:
        pg_col_lines.append("    id SERIAL NOT NULL,")
    pg_col_lines.extend(pg_column_def(f) for f in all_fields)

    pg_select_lines = []
    if "id" not in existing_snakes:
        pg_select_lines.append("        t.id,")
    pg_select_lines.extend(pg_select_col(f) for f in all_fields)

    # CRUD params only operate on business fields (no audit/system fields).
    fn_params_create_lines = [pg_fn_param(f) for f in business_fields]
    fn_params_create_lines.append("    p_current_user_id INTEGER")

    fn_params_update_lines = [pg_fn_param(f) for f in business_fields]
    fn_params_update_lines.append("    p_current_user_id INTEGER")

    insert_cols = [pg_insert_col(f) for f in business_fields]
    insert_values = [pg_insert_value(f, i) for i, f in enumerate(business_fields, 1)]
    update_set_lines = [pg_update_set(f) for f in business_fields]

    field_csv = ", ".join(field_snake(f) for f in business_fields)

    # ── React (JSX) extra ──
    table_headers = jsx_table_headers(business_fields)
    table_cells = jsx_table_cells(business_fields)
    form_fields = jsx_form_fields(business_fields)

    # ── Angular extra ──
    ng_table_headers_val = ng_table_headers(business_fields)
    ng_table_cells_val = ng_table_cells(business_fields)
    ng_form_controls_val = ng_form_controls(business_fields)
    ng_form_fields_val = ng_form_fields(business_fields)

    # ── Bun extra ──
    bun_create_lines = [bun_zod_field(f) for f in business_fields]
    bun_update_lines = [bun_zod_field_optional(f) for f in business_fields]

    ctx = {
        "MODULE": module,
        "MODULE_CAMEL": module_camel,
        "ENTITY": entity_name,
        "ENTITIES": pascal_plural(entity_name),
        "entity": entity_camel,
        "entities": entities_lower,
        "SCHEMA": schema,
        "TABLE": table_name,
        "NAMESPACE": spec.get("namespace", f"app.{module_camel}"),

        # Python
        "PY_ALL_FIELDS": "\n".join(py_all_lines),
        "PY_CREATE_FIELDS": "\n".join(py_create_lines),
        "PY_UPDATE_FIELDS": "\n".join(py_update_lines),
        "PY_RESPONSE_FIELDS": "\n".join(py_response_lines),

        # TypeScript
        "TS_FIELDS": f"export interface {entity_name}ListItem {{\n" + "\n".join(ts_lines) + "\n}",
        "TS_CREATE_FIELDS": "\n".join(ts_create_lines),
        "TS_UPDATE_FIELDS": "\n".join(ts_update_lines),

        # PostgreSQL DDL
        "SQL_COLUMNS": "\n".join(pg_col_lines),
        "SQL_SELECT_COLS": "\n".join(pg_select_lines),
        "SQL_COLUMNS_RETURN": "\n".join(
            (["    id INTEGER,"] if "id" not in existing_snakes else [])
            + [f"    {field_snake(f)} {pg_type(f['type'])}," for f in all_fields]
        ),
        "SQL_INSERT_COLS": "\n".join(insert_cols),
        "SQL_VALUES_PLACEHOLDERS": "\n".join(insert_values),
        "SQL_UPDATE_SET": "\n".join(update_set_lines),

        # PL/pgSQL function params
        "FN_PARAMS_CREATE": ",\n".join(fn_params_create_lines),
        "FN_PARAMS_UPDATE": ",\n".join(fn_params_update_lines),

        # React
        "TABLE_HEADERS": table_headers,
        "TABLE_CELLS": table_cells,
        "FORM_FIELDS": form_fields,

        # Angular (used when --frontend angular; merged over the React keys above
        # at render time — see generate())
        "NG_TABLE_HEADERS": ng_table_headers_val,
        "NG_TABLE_CELLS": ng_table_cells_val,
        "NG_FORM_CONTROLS": ng_form_controls_val,
        "NG_FORM_FIELDS": ng_form_fields_val,

        # Bun
        "BUN_CREATE_FIELDS": "\n".join(bun_create_lines),
        "BUN_UPDATE_FIELDS": "\n".join(bun_update_lines),

        # Misc
        "ENTITY_FIELDS_CSV": field_csv,
    }
    return ctx


# ─── File generation ─────────────────────────────────────────────────────────

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  Created: {path}")


_generated_init = False
_generated_database = False


def generate(spec, output_dir, backend="python", frontend="react"):
    global _generated_init, _generated_database

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _generated_init = False
    _generated_database = False

    for entity in spec["entities"]:
        ctx = build_context(spec, entity)
        entity_name = ctx["ENTITY"]
        entity_camel = ctx["entity"]
        entities_lower = ctx["entities"]
        module_lower = ctx["MODULE_CAMEL"]

        # ── Backend ──
        backend_dir = output / "backend"

        if backend == "python":
            # __init__.py (once)
            if not _generated_init:
                write_file(backend_dir / "__init__.py", "")
                _generated_init = True

            # database.py (once)
            if not _generated_database:
                write_file(
                    backend_dir / "database.py",
                    load_template("database.py.j2").safe_substitute(ctx),
                )
                _generated_database = True

            write_file(
                backend_dir / f"{entity_camel}_router.py",
                load_template("router.py.j2").safe_substitute(ctx),
            )
            write_file(
                backend_dir / f"{entity_camel}_service.py",
                load_template("service.py.j2").safe_substitute(ctx),
            )
            write_file(
                backend_dir / f"{entity_camel}_schemas.py",
                load_template("schemas.py.j2").safe_substitute(ctx),
            )
        elif backend == "bun":
            write_file(
                backend_dir / f"{entity_camel}.route.ts",
                load_template("route.ts.j2").safe_substitute(ctx),
            )
            write_file(
                backend_dir / f"{entity_camel}.service.ts",
                generate_bun_service(entity, ctx),
            )
            write_file(
                backend_dir / f"{entity_camel}.dto.ts",
                load_template("dto.ts.j2").safe_substitute(ctx),
            )
            write_file(
                backend_dir / f"{entity_camel}.db.ts",
                load_template("db.ts.j2").safe_substitute(ctx),
            )
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        # ── Frontend (React + Vite, or Angular — per --frontend) ──
        frontend_dir = output / "frontend"
        write_file(
            frontend_dir / f"{entity_camel}.model.ts",
            load_template("model.ts.j2").safe_substitute(ctx),
        )

        if frontend == "react":
            write_file(
                frontend_dir / f"{entity_camel}.api.ts",
                load_template("api.ts.j2").safe_substitute(ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-list.tsx",
                load_template("component.tsx.j2").safe_substitute(ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-table.tsx",
                load_template("table.component.tsx.j2").safe_substitute(ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-form.tsx",
                load_template("form.component.tsx.j2").safe_substitute(ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-page.tsx",
                load_template("page.component.tsx.j2").safe_substitute(ctx),
            )
            write_file(
                frontend_dir / "index.ts",
                load_template("index.ts.j2").safe_substitute(ctx),
            )
        elif frontend == "angular":
            # Angular templates reuse the TABLE_HEADERS/TABLE_CELLS/FORM_FIELDS
            # placeholder names but with Angular-flavored markup (NG_* in ctx),
            # plus FORM_CONTROLS for reactive forms — not used by React.
            ng_ctx = dict(ctx)
            ng_ctx["TABLE_HEADERS"] = ctx["NG_TABLE_HEADERS"]
            ng_ctx["TABLE_CELLS"] = ctx["NG_TABLE_CELLS"]
            ng_ctx["FORM_FIELDS"] = ctx["NG_FORM_FIELDS"]
            ng_ctx["FORM_CONTROLS"] = ctx["NG_FORM_CONTROLS"]

            write_file(
                frontend_dir / f"{entity_camel}.service.ts",
                load_template("angular/service.ts.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-list.component.ts",
                load_template("angular/component.ts.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-list.component.html",
                load_template("angular/component.html.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-table.component.ts",
                load_template("angular/table.component.ts.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-table.component.html",
                load_template("angular/table.component.html.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-form.component.ts",
                load_template("angular/form.component.ts.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-form.component.html",
                load_template("angular/form.component.html.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-page.component.ts",
                load_template("angular/page.component.ts.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / f"{entity_camel}-page.component.html",
                load_template("angular/page.component.html.j2").safe_substitute(ng_ctx),
            )
            write_file(
                frontend_dir / "index.ts",
                load_template("angular/index.ts.j2").safe_substitute(ng_ctx),
            )
        else:
            raise ValueError(f"Unsupported frontend: {frontend}")

        # ── Database (PostgreSQL) ──
        db_dir = output / "database"
        write_file(
            db_dir / f"001_create_{entities_lower}.sql",
            load_template("sql_create.sql.j2").safe_substitute(ctx),
        )
        write_file(
            db_dir / f"002_fn_{entities_lower}_crud.sql",
            load_template("sql_fn.sql.j2").safe_substitute(ctx),
        )

        # ── Tests (Playwright) ──
        tests_dir = output / "tests"
        write_file(
            tests_dir / f"{module_lower}.spec.ts",
            load_template("test.spec.ts.j2").safe_substitute(ctx),
        )


# ─── CLI entry point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate project scaffolding from api-first-spec")
    parser.add_argument("spec", help="Path to the spec markdown file")
    parser.add_argument("--output", "-o", default="./output", help="Output directory")
    parser.add_argument("--backend", "-b", choices=["python", "bun"], default="python", help="Backend stack")
    parser.add_argument("--frontend", "-f", choices=["react", "angular"], default="react", help="Frontend stack")
    parser.add_argument("--namespace", "-n", default=None, help="Python package namespace override")
    parser.add_argument("--schema", "-s", default="public", help="Database schema name (PostgreSQL)")
    args = parser.parse_args()

    if not os.path.exists(args.spec):
        print(f"Error: Spec file not found: {args.spec}")
        sys.exit(1)

    print(f"Parsing spec: {args.spec}")
    spec = parse_spec(args.spec)
    spec["namespace"] = args.namespace or f"app.{spec['module'].lower()}"
    spec["schema"] = args.schema

    print(f"Module: {spec['module']}")
    print(f"Entities: {[e['name'] for e in spec['entities']]}")
    print(f"Endpoints: {len(spec['endpoints'])}")
    print(f"Backend: {args.backend}")
    print(f"Frontend: {args.frontend}")
    print(f"\nGenerating scaffolding in: {args.output}")

    generate(spec, args.output, backend=args.backend, frontend=args.frontend)

    print(f"\nDone. Output: {args.output}")
    print(f"  Backend:  {args.output}/backend/")
    print(f"  Frontend: {args.output}/frontend/")
    print(f"  Database: {args.output}/database/")
    print(f"  Tests:    {args.output}/tests/")


if __name__ == "__main__":
    main()
