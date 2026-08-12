#!/usr/bin/env python3
"""check-level-coverage.py — Verify every N-level in SKILL-ROUTING maps to an
existing skill, and every level N0..N49 has an entry."""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
ROUTING = OPENCODE_DIR / "framework" / "SKILL-ROUTING.md"

skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}

routing_text = ROUTING.read_text(encoding="utf-8")

# Parse "Nxx: skill-name" entries from the phase listings.
level_entries = re.findall(r"\bN(\d{1,2}):\s*([\w/-]+)", routing_text)
levels_by_num = {}
for num, skill in level_entries:
    num = int(num)
    levels_by_num.setdefault(num, []).append(skill)

errors = []

# 1. Every level N0..N49 must exist in the routing.
for level in range(0, 50):
    if level not in levels_by_num:
        errors.append(f"Routing missing level N{level}")

# 2. Every routed skill must exist in the catalog.
#    Entries like "react/angular" are alternatives — each part must exist.
for level, routed_skills in sorted(levels_by_num.items()):
    for entry in routed_skills:
        for alt in entry.split("/"):
            alt = alt.strip()
            if alt and alt not in skills:
                errors.append(f"Routing N{level} references unknown skill '{alt}'")

# 3. Report coverage by phase (informational).
print("Skill coverage by phase:")
for level in sorted(levels_by_num):
    print(f"  N{level}: {', '.join(levels_by_num[level])}")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)
print(f"All levels N0-N49 covered, all routed skills exist ({len(level_entries)} entries)")
