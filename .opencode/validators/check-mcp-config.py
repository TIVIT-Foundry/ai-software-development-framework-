#!/usr/bin/env python3
"""check-mcp-config.py — Verify mcp-metadata.json and opencode.json MCP consistency."""
import json
import sys
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
    mcp_data = json.loads(mcp_file.read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON in mcp-metadata.json: {e}", file=sys.stderr)
    sys.exit(1)

# Load opencode.json
if not opencode_file.exists():
    print(f"FAIL: opencode.json not found", file=sys.stderr)
    sys.exit(1)
try:
    oc_data = json.loads(opencode_file.read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON in opencode.json: {e}", file=sys.stderr)
    sys.exit(1)

mcp_servers = mcp_data.get("mcpServers", {})
oc_mcp = oc_data.get("mcp", {})

# Check 1: Every MCP in opencode.json must have metadata
for name in oc_mcp:
    if name not in mcp_servers:
        errors.append(f"MCP '{name}' in opencode.json has no metadata in mcp-metadata.json")

# Check 2: Every MCP in metadata should be in opencode.json
for name in mcp_servers:
    if name not in oc_mcp:
        warnings.append(f"MCP '{name}' in mcp-metadata.json but not in opencode.json")

# Check 3: No PLACEHOLDER commands
for name, cfg in oc_mcp.items():
    cmd = cfg.get("command", [])
    if isinstance(cmd, list) and any("PLACEHOLDER" in str(c) for c in cmd):
        errors.append(f"MCP '{name}' has PLACEHOLDER command")

# Check 4: filesystem MCP should not reference deleted dirs
fs_cfg = oc_mcp.get("filesystem", {})
fs_cmd = fs_cfg.get("command", [])
if isinstance(fs_cmd, list):
    for arg in fs_cmd:
        if arg in ("examples", "docs"):
            warnings.append(f"filesystem MCP references '{arg}/' which may not exist")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print(f"Valid config with {len(oc_mcp)} MCP servers in opencode.json, {len(mcp_servers)} in metadata")
