#!/usr/bin/env python3
"""check-dependencies.py — Verify framework dependencies are present."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
REQUIRED = [
    OPENCODE_DIR / "skills",
    OPENCODE_DIR / "agents",
    OPENCODE_DIR / "scaffold",
    OPENCODE_DIR / "mcp-metadata.json",
]
errors = []
for path in REQUIRED:
    if not path.exists():
        errors.append(f"Missing: {path.name}")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
print("All dependencies present")
