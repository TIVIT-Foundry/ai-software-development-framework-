#!/usr/bin/env python3
"""check-duplicate-descriptions.py — Check for duplicate skill descriptions."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
descriptions = {}
errors = []

for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        continue
    content = skill_md.read_text(encoding="utf-8")
    for line in content.split("\n"):
        if line.strip().startswith("description:"):
            desc = line.split(":", 1)[1].strip().strip("'\"")
            if desc in descriptions.values():
                dup = [k for k, v in descriptions.items() if v == desc]
                errors.append(f"Duplicate description: '{skill_dir.name}' same as '{dup[0]}'")
            descriptions[skill_dir.name] = desc
            break

if errors:
    for e in errors:
        print(f"WARN: {e}", file=sys.stderr)
    sys.exit(1)
print(f"No duplicate descriptions found")
