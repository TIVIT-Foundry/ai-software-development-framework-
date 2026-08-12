#!/usr/bin/env python3
"""check-skill-ids.py — Verify skill directories have valid names."""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
errors = []

for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    name = skill_dir.name
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        errors.append(f"Invalid skill name: '{name}' (must be lowercase, alphanumeric + hyphens)")
    if "--" in name:
        errors.append(f"Skill '{name}': double hyphens not allowed")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
count = len([d for d in SKILLS_DIR.iterdir() if d.is_dir()])
print(f"All {count} skill names valid")
