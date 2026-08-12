#!/usr/bin/env python3
"""check-skill-contract.py — Verify each skill has required files and valid frontmatter."""
import re
import sys
from pathlib import Path

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
REQUIRED_FILES = ["SKILL.md"]
REQUIRED_FM_FIELDS = ["name", "description", "version"]
REQUIRED_METADATA_FIELDS = ["phase", "layer", "enforcement", "depends_on", "consumed_by", "agent_roles"]
errors = []
warnings = []


def extract_frontmatter(content):
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    return content[3:end]


def check_unescaped_apostrophes(fm, skill_name):
    """Detect YAML single-quoted scalars with unescaped apostrophes (e.g. project's).

    Per the YAML spec, inside a single-quoted scalar every apostrophe must be
    doubled (''). An unescaped ' terminates the scalar early and the trailing
    text on the same line makes the whole frontmatter unparseable — opencode
    silently drops such skills from its catalog.
    """
    lines = fm.split("\n")
    fields = {}
    cur = None
    for line in lines:
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            cur = m.group(1)
            fields[cur] = m.group(2)
        elif cur:
            fields[cur] += "\n" + line

    for name, val in fields.items():
        if not val.startswith("'"):
            continue
        # Walk the single-quoted scalar honoring '' escapes.
        j = 1
        closed = False
        while j < len(val):
            c = val[j]
            if c == "'":
                if j + 1 < len(val) and val[j + 1] == "'":
                    j += 2
                    continue
                closed = True
                break
            j += 1
        if not closed:
            errors.append(
                f"Skill '{skill_name}' frontmatter field '{name}': single-quoted scalar never closed"
            )
            continue
        rest = val[j + 1:].split("\n")[0]
        if rest.strip():
            errors.append(
                f"Skill '{skill_name}' frontmatter field '{name}': unescaped apostrophe "
                f"(text after closing quote: '{rest.strip()[:50]}') — escape it as '' "
                f"or switch the value to double quotes"
            )


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
    fm = extract_frontmatter(content)
    if fm is None:
        errors.append(f"Skill '{skill_name}' has no valid frontmatter")
        continue

    if HAVE_YAML:
        # Strict validation with a real YAML parser (catches unescaped
        # apostrophes, bad indentation, broken scalars, ...).
        try:
            parsed = yaml.safe_load(fm)
        except Exception as exc:
            errors.append(
                f"Skill '{skill_name}' frontmatter is invalid YAML: {str(exc).splitlines()[0]}"
            )
            continue
        if not isinstance(parsed, dict):
            errors.append(f"Skill '{skill_name}' frontmatter does not parse to a mapping")
            continue
        for field in REQUIRED_FM_FIELDS:
            if field not in parsed:
                errors.append(f"Skill '{skill_name}' frontmatter missing '{field}'")
        metadata = parsed.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        for field in REQUIRED_METADATA_FIELDS:
            if field not in metadata:
                warnings.append(f"Skill '{skill_name}' metadata missing '{field}'")
    else:
        # Fallback without PyYAML: substring checks + apostrophe detector.
        for field in REQUIRED_FM_FIELDS:
            if f"{field}:" not in fm:
                errors.append(f"Skill '{skill_name}' frontmatter missing '{field}'")
        for field in REQUIRED_METADATA_FIELDS:
            if f"{field}:" not in fm:
                warnings.append(f"Skill '{skill_name}' metadata missing '{field}'")
        check_unescaped_apostrophes(fm, skill_name)

    # Checks that work regardless of parser.
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

if not HAVE_YAML:
    warnings.append(
        "PyYAML not installed — frontmatter validated with the fallback parser; "
        "run setup-venv.ps1 to enable strict YAML validation"
    )

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

skill_count = len([d for d in SKILLS_DIR.iterdir() if d.is_dir()])
print(f"All {skill_count} skills have required files and valid frontmatter")
