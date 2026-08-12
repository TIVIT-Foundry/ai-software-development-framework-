#!/usr/bin/env python3
"""check-duplicate-descriptions.py — Check for duplicate skill descriptions.

Compares FULL descriptions (multiline YAML folded), not just the first line.
Exact duplicates are FAIL; near-duplicates (>= 0.9 similarity) are WARN —
the meta-skill pairs are intentionally similar, but identical descriptions
mean a copy/paste error.
"""
import sys
from pathlib import Path

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
descriptions = {}
errors = []
warnings = []


def extract_frontmatter(content):
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    return content[3:end]


def normalized(desc):
    return " ".join(desc.split()).lower()


for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        continue
    content = skill_md.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)
    if fm is None:
        continue
    desc = None
    if HAVE_YAML:
        try:
            parsed = yaml.safe_load(fm)
            desc = parsed.get("description") if isinstance(parsed, dict) else None
        except Exception:
            desc = None
    if desc is None:
        # Fallback: capture the first `description:` line (single-line form).
        for line in fm.splitlines():
            if line.strip().startswith("description:"):
                desc = line.split(":", 1)[1].strip().strip("'\"")
                break
    if desc is None:
        continue
    descriptions[skill_dir.name] = desc

names = sorted(descriptions)
for i, name in enumerate(names):
    for other in names[i + 1:]:
        if normalized(descriptions[name]) == normalized(descriptions[other]):
            errors.append(f"Duplicate description: '{name}' identical to '{other}'")
        else:
            # Quick overlap check: share a long prefix or high token overlap.
            a = set(descriptions[name].split())
            b = set(descriptions[other].split())
            if a and b:
                jaccard = len(a & b) / len(a | b)
                if jaccard >= 0.9:
                    warnings.append(f"Near-duplicate description: '{name}' ~ '{other}' (similarity {jaccard:.2f})")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print(f"No duplicate descriptions found across {len(descriptions)} skills")
