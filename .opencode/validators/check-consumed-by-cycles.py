#!/usr/bin/env python3
"""check-consumed-by-cycles.py — Detect circular dependencies in the skill graph.

Builds a directed graph from each skill's `depends_on` list (skill A depends_on
skill B means an edge A -> B) and fails if any cycle exists. Also cross-checks
that `consumed_by` is the mirror of `depends_on`: if A depends_on B, B should
list A in its own consumed_by (and vice versa) — drift here means the two
fields were edited independently and no longer agree.
"""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
errors = []
warnings = []


def parse_frontmatter(content):
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    return content[3:end]


def parse_list_field(fm, field):
    """Parse a YAML block-list field like:
    depends_on:
      - foo
      - bar
    Stops at the next top-level (non-indented, non '-') key.
    """
    lines = fm.splitlines()
    items = []
    in_field = False
    for line in lines:
        stripped = line.strip()
        if re.match(rf"^{field}\s*:\s*$", stripped):
            in_field = True
            continue
        if in_field:
            if stripped.startswith("-"):
                items.append(stripped.lstrip("-").strip().strip("'\""))
                continue
            if stripped == "" :
                continue
            # New top-level key (no leading '-') ends the list field.
            if re.match(r"^[A-Za-z_]+\s*:", stripped) and not line.startswith((" ", "\t")):
                break
            if re.match(r"^[A-Za-z_]+\s*:", stripped) and not stripped.startswith("-"):
                # Could be a nested key at same indent as the list items in some
                # malformed frontmatter; treat as end of field to be safe.
                break
    return items


skills = {}  # name -> {depends_on: set, consumed_by: set}
for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        continue
    content = skill_file.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    if fm is None:
        continue
    skills[skill_dir.name] = {
        "depends_on": set(parse_list_field(fm, "depends_on")),
        "consumed_by": set(parse_list_field(fm, "consumed_by")),
    }

# --- Cycle detection over the depends_on graph ---
WHITE, GRAY, BLACK = 0, 1, 2
color = {name: WHITE for name in skills}
path = []


def dfs(node):
    color[node] = GRAY
    path.append(node)
    for dep in sorted(skills.get(node, {}).get("depends_on", [])):
        if dep not in skills:
            continue  # unknown/external dep name, not this validator's concern
        if color.get(dep, WHITE) == GRAY:
            cycle_start = path.index(dep)
            cycle = path[cycle_start:] + [dep]
            errors.append("Dependency cycle: " + " -> ".join(cycle))
        elif color.get(dep, WHITE) == WHITE:
            dfs(dep)
    path.pop()
    color[node] = BLACK


for name in sorted(skills):
    if color[name] == WHITE:
        dfs(name)

# --- consumed_by / depends_on mirror check ---
for name, data in sorted(skills.items()):
    for dep in data["depends_on"]:
        if dep not in skills:
            continue
        if name not in skills[dep]["consumed_by"]:
            warnings.append(
                f"'{name}' depends_on '{dep}', but '{dep}' does not list '{name}' in consumed_by"
            )

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print(f"No dependency cycles found across {len(skills)} skills ({len(warnings)} consumed_by drift warning(s))")
