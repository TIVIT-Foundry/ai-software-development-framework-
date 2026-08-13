#!/usr/bin/env python3
"""check-content-quality.py — Basic quality checks on skill files."""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
errors = []
warnings = []

for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        continue
    content = skill_md.read_text(encoding="utf-8")
    if len(content.strip()) < 50:
        errors.append(f"Skill '{skill_dir.name}': SKILL.md too short ({len(content.strip())} chars)")
    if not re.search(r"^description\s*:\s*", content[:500], re.MULTILINE):
        errors.append(f"Skill '{skill_dir.name}': missing description in frontmatter")

    # Reference packs (>800 lines) must open with a table of contents so the
    # agent can read selectively instead of consuming the whole file.
    if len(content.splitlines()) > 800:
        head = content[:2000].lower()
        if "table of contents" not in head and "tabla de contenidos" not in head:
            warnings.append(
                f"Skill '{skill_dir.name}' is a reference pack (>800 lines) without a "
                f"table of contents — add '## Tabla de contenidos' right after the frontmatter"
            )

if errors:
    for e in errors:
        print(f"WARN: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print("Content quality checks passed")
