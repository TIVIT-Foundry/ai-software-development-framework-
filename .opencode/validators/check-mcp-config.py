#!/usr/bin/env python3
"""check-mcp-config.py — Verify mcp-metadata.json and opencode.json MCP consistency."""
import json
import sys
from datetime import date
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = OPENCODE_DIR.parent
mcp_file = OPENCODE_DIR / "mcp-metadata.json"
opencode_file = ROOT_DIR / "opencode.json"
errors = []
warnings = []

# Load mcp-metadata.json
if not mcp_file.exists():
    print(f"FAIL: mcp-metadata.json not found", file=sys.stderr)
    sys.exit(1)
try:
    # utf-8-sig tolera el BOM que PowerShell agrega al escribir JSON
    mcp_data = json.loads(mcp_file.read_text(encoding="utf-8-sig"))
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON in mcp-metadata.json: {e}", file=sys.stderr)
    sys.exit(1)

# Load opencode.json
if not opencode_file.exists():
    # Un proyecto puede no haber configurado MCPs aun: no es un fallo del framework.
    print("WARN: opencode.json not found in project root — MCP config check skipped")
    sys.exit(0)
try:
    oc_data = json.loads(opencode_file.read_text(encoding="utf-8-sig"))
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON in opencode.json: {e}", file=sys.stderr)
    sys.exit(1)

mcp_servers = mcp_data.get("mcpServers", {})
oc_mcp = oc_data.get("mcp", {})

# Check 1: Every MCP in opencode.json should have metadata.
# WARN, not FAIL: los proyectos pueden tener MCPs propios legitimos sin
# documentar aun (p. ej. automation-safe reservado) — es deuda de
# gobernanza del proyecto, no un fallo de integridad del framework.
for name in oc_mcp:
    if name not in mcp_servers:
        warnings.append(
            f"MCP '{name}' in opencode.json has no metadata in mcp-metadata.json "
            f"— documentarlo en mcp-metadata.json o quitarlo del opencode.json"
        )

# Check 2: Every MCP in metadata should be in opencode.json
for name in mcp_servers:
    if name not in oc_mcp:
        warnings.append(f"MCP '{name}' in mcp-metadata.json but not in opencode.json")

# Check 3: No PLACEHOLDER commands — solo para MCPs HABILITADOS.
# Un MCP deshabilitado puede tener un comando placeholder pendiente de
# configuracion (config local del proyecto) sin romper el pipeline.
for name, cfg in oc_mcp.items():
    if not cfg.get("enabled", True):
        continue
    cmd = cfg.get("command", [])
    if isinstance(cmd, list) and any("PLACEHOLDER" in str(c) for c in cmd):
        errors.append(f"MCP '{name}' is enabled but has PLACEHOLDER command")

# Check 4: filesystem MCP should not reference deleted dirs
fs_cfg = oc_mcp.get("filesystem", {})
fs_cmd = fs_cfg.get("command", [])
if isinstance(fs_cmd, list):
    for arg in fs_cmd:
        if arg in ("examples", "docs"):
            warnings.append(f"filesystem MCP references '{arg}/' which may not exist")

# Check 5: enabled flag + governance dates for every MCP.
# Fechas vacías advierten SIEMPRE (habilitado o no): un servidor sin
# authorized_date/review_date es deuda de gobernanza pendiente de completar.
enabled_count = 0
for name, cfg in oc_mcp.items():
    enabled = cfg.get("enabled", True)
    if enabled:
        enabled_count += 1
    meta = mcp_servers.get(name, {})
    if meta.get("authorized_date") in (None, ""):
        warnings.append(
            f"MCP '{name}' has no authorized_date in mcp-metadata.json"
            f" — sin autorizar, pendiente de completar"
        )
    if meta.get("review_date") in (None, ""):
        warnings.append(
            f"MCP '{name}' has no review_date in mcp-metadata.json"
            f" — sin fecha de revisión, pendiente de completar"
        )

# Check 6: expired review_date for every MCP in metadata.
# Las fechas ISO-8601 (YYYY-MM-DD) comparan correctamente como strings.
today = date.today().isoformat()
for name, meta in mcp_servers.items():
    review_date = meta.get("review_date")
    if review_date and review_date < today:
        warnings.append(
            f"MCP '{name}' has review_date {review_date} in the past (today {today})"
            f" — governance review overdue"
        )

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print(f"Valid config with {len(oc_mcp)} MCP servers in opencode.json ({enabled_count} enabled), {len(mcp_servers)} in metadata")
