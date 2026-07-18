#!/usr/bin/env python3
"""check-skill-contract.py — Verify each skill has required files and valid frontmatter."""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
REQUIRED_FILES = ["SKILL.md"]
REQUIRED_FM_FIELDS = ["name", "description", "version"]
REQUIRED_METADATA_FIELDS = ["phase", "layer", "enforcement", "depends_on", "consumed_by", "agent_roles"]
errors = []
warnings = []

def parse_frontmatter(content):
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    return content[3:end]

for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_name = skill_dir.name
    for req in REQUIRED_FILES:
        if not (skill_dir / req).exists():
            errors.append(f"Skill '{skill_name}' missing {req}")
            continue
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        continue
    content = skill_file.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    if fm is None:
        errors.append(f"Skill '{skill_name}' has no valid frontmatter")
        continue
    for field in REQUIRED_FM_FIELDS:
        if f"{field}:" not in fm:
            errors.append(f"Skill '{skill_name}' frontmatter missing '{field}'")
    for field in REQUIRED_METADATA_FIELDS:
        if f"{field}:" not in fm:
            warnings.append(f"Skill '{skill_name}' metadata missing '{field}'")
    name_match = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    if name_match:
        fm_name = name_match.group(1).strip().strip("'\"")
        if fm_name != skill_name:
            errors.append(f"Skill '{skill_name}' frontmatter name '{fm_name}' != folder name")
    desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE | re.DOTALL)
    if desc_match:
        desc = desc_match.group(1)
        if "Trigger:" not in desc and "trigger:" not in desc:
            warnings.append(f"Skill '{skill_name}' description missing 'Trigger:' clause")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print(f"All {len(list(SKILLS_DIR.iterdir()))} skills have required files and valid frontmatter")
