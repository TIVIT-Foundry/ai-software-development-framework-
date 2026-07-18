#!/usr/bin/env python3
"""check-version-bumps.py — Verify opencode.json is present and valid."""
import json
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = OPENCODE_DIR.parent
opencode_json = ROOT_DIR / "opencode.json"

if not opencode_json.exists():
    print("WARN: opencode.json not found at root", file=sys.stderr)
    sys.exit(1)

try:
    data = json.loads(opencode_json.read_text(encoding="utf-8"))
    print(f"opencode.json valid (version: {data.get('version', 'unknown')})")
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)
