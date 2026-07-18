#!/usr/bin/env python3
"""check-content-quality.py — Basic quality checks on skill files."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
errors = []

for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        continue
    content = skill_md.read_text(encoding="utf-8")
    if len(content.strip()) < 50:
        errors.append(f"Skill '{skill_dir.name}': SKILL.md too short ({len(content.strip())} chars)")
    if "description:" not in content[:500]:
        errors.append(f"Skill '{skill_dir.name}': missing description in frontmatter")

if errors:
    for e in errors:
        print(f"WARN: {e}", file=sys.stderr)
    sys.exit(1)
print("Content quality checks passed")
