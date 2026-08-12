#!/usr/bin/env python3
"""check-orphan-skills.py — Verify all skills are referenced by an agent,
framework doc, or root doc (AGENTS.md/README/QUICKSTART)."""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
AGENTS_DIR = OPENCODE_DIR / "agents"
FRAMEWORK_DIR = OPENCODE_DIR / "framework"
ROOT_DIR = OPENCODE_DIR.parent

# Collect all skill names
skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}

# Collect all reference content: agents + framework docs + root docs
content = ""
for agent_file in AGENTS_DIR.glob("*.md"):
    content += agent_file.read_text(encoding="utf-8")
for doc_file in FRAMEWORK_DIR.glob("*.md"):
    content += doc_file.read_text(encoding="utf-8")
for root_doc in ("AGENTS.md", "README.md", "QUICKSTART.md", "CLAUDE.md"):
    p = ROOT_DIR / root_doc
    if p.exists():
        content += p.read_text(encoding="utf-8")

referenced = set()
for skill in skills:
    if skill in content or skill.replace("-", "_") in content:
        referenced.add(skill)

orphan = skills - referenced
if orphan:
    for s in sorted(orphan):
        print(f"FAIL: Skill '{s}' not referenced in any agent/framework/root doc")
    print(f"\n{len(orphan)} orphan skill(s) found")
    sys.exit(1)
else:
    print(f"All {len(skills)} skills referenced")
