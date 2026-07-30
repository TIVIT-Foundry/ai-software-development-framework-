#!/usr/bin/env python3
"""check-bundle-consistency.py — Verify the phase bundles in SKILLS-MANIFEST.md
are consistent with the actual skill catalog.

Parses the "## Fases del Framework" table (columns: Fase | Niveles | Skills |
Confirmaciones) and checks that every skill name listed in the "Skills" column
of every bundle row actually exists as a skill directory. Entries containing a
wildcard (e.g. `database-*`) or a parenthetical note (e.g. `(skills de
implementación)`) are treated as intentional group references, not literal
skill names, and are skipped.
"""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
MANIFEST = OPENCODE_DIR / "framework" / "SKILLS-MANIFEST.md"
errors = []
warnings = []

skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}

if not MANIFEST.exists():
    print(f"FAIL: {MANIFEST} not found", file=sys.stderr)
    sys.exit(1)

content = MANIFEST.read_text(encoding="utf-8")

section_match = re.search(r"##\s*Fases del Framework(.*?)(?:\n##\s|\Z)", content, re.DOTALL)
if not section_match:
    print("FAIL: '## Fases del Framework' section not found in SKILLS-MANIFEST.md", file=sys.stderr)
    sys.exit(1)

section = section_match.group(1)
row_pattern = re.compile(r"^\|\s*(.+?)\s*\|\s*(N[\dN\-]+)\s*\|\s*(.+?)\s*\|\s*\d+\s*\|$", re.MULTILINE)

rows = row_pattern.findall(section)
if not rows:
    print("FAIL: No bundle rows parsed from 'Fases del Framework' table", file=sys.stderr)
    sys.exit(1)

total_refs = 0
for fase, niveles, skills_col in rows:
    for raw in skills_col.split(","):
        name = raw.strip().strip("`")
        if not name:
            continue
        if "*" in name or name.startswith("("):
            continue  # wildcard group (database-*) or parenthetical note, not a literal skill
        total_refs += 1
        if name not in skills:
            errors.append(f"Fase '{fase}' ({niveles}) references unknown skill '{name}'")

# Cross-check: every skill flagged `enforcement: mandatory` in the catalog tables
# (outside this section) should appear in at least one bundle row, so it's actually
# scheduled somewhere in the pipeline.
catalog_rows = re.findall(r"^\|\s*([a-z][a-z0-9\-]*)\s*\|.*?\|.*?\|\s*mandatory\s*\|", content, re.MULTILINE)
bundled_skills = set()
for _, _, skills_col in rows:
    for raw in skills_col.split(","):
        name = raw.strip().strip("`")
        if name and "*" not in name and not name.startswith("("):
            bundled_skills.add(name)

for skill_name in sorted(set(catalog_rows)):
    if skill_name in skills and skill_name not in bundled_skills:
        warnings.append(f"Mandatory skill '{skill_name}' is not scheduled in any Fase bundle")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print(f"Bundle consistency OK: {len(rows)} fases, {total_refs} skill references checked against {len(skills)} skills")
