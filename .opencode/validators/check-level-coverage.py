#!/usr/bin/env python3
"""check-level-coverage.py — Verify skill level coverage."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"

# Group skills by domain prefix
domains = {}
for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    parts = skill_dir.name.split("-", 1)
    domain = parts[0] if len(parts) > 1 else "root"
    domains.setdefault(domain, []).append(skill_dir.name)

print(f"Skill coverage by domain:")
for domain, skills in sorted(domains.items()):
    print(f"  {domain}: {len(skills)} skill(s)")
