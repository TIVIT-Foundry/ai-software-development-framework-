#!/usr/bin/env python3
"""check-orphan-skills.py — Verify every FRAMEWORK skill is referenced.

Only skills declared in SKILLS-MANIFEST.md must be referenced by an agent,
framework doc, or root doc (AGENTS.md/README/QUICKSTART). Skills that exist in
the project but are NOT in the manifest are LOCAL skills of the project
(p. ej. dotnet-gateway, react-hooks) — they are reported as informational WARN,
never as a failure, so the sync does not break projects with local skills.
"""
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

# Framework skills = those declared in SKILLS-MANIFEST (tables + phase bundles)
manifest_file = FRAMEWORK_DIR / "SKILLS-MANIFEST.md"
manifest_skills = set()
if manifest_file.exists():
    mt = manifest_file.read_text(encoding="utf-8")
    manifest_skills = {m for m in re.findall(r"^\|\s*([a-z][a-z0-9-]*)\s*\|", mt, re.MULTILINE)} & skills

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

orphan = (manifest_skills or skills) - referenced
local_skills = (skills - manifest_skills) - referenced

if orphan:
    for s in sorted(orphan):
        print(f"FAIL: Framework skill '{s}' not referenced in any agent/framework/root doc")
    print(f"\n{len(orphan)} orphan framework skill(s) found")
    sys.exit(1)

for s in sorted(local_skills):
    print(f"WARN: Skill '{s}' is a LOCAL project skill (not in SKILLS-MANIFEST) — document it or add it to the manifest")

print(f"All {len(manifest_skills)} framework skills referenced ({len(local_skills)} local project skill(s) tolerated)")
