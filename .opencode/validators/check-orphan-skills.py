#!/usr/bin/env python3
"""check-orphan-skills.py — Verify all skills are referenced by at least one agent."""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
AGENTS_DIR = OPENCODE_DIR / "agents"

# Collect all skill names
skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}

# Collect all agent content
agent_content = ""
for agent_file in AGENTS_DIR.glob("*.md"):
    agent_content += agent_file.read_text(encoding="utf-8")

referenced = set()
for skill in skills:
    if skill in agent_content or skill.replace("-", "_") in agent_content:
        referenced.add(skill)

orphan = skills - referenced
if orphan:
    for s in sorted(orphan):
        print(f"WARN: Skill '{s}' not referenced in any agent")
    print(f"\n{len(orphan)} orphan skill(s) found")
else:
    print(f"All {len(skills)} skills referenced")
