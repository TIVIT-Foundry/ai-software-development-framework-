#!/usr/bin/env python3
"""check-agent-roles.py — Validate frontmatter agent_roles against sources of truth.

Sources:
- SKILL-ROUTING.md (Routing por Fase: "Nxx: skill -> agente") — the EXECUTING
  agent is mandatory: if a skill has a level, its routing agent must be listed
  in agent_roles (FAIL otherwise).
- AGENT-MODEL.md (Owner/Consulta/Stack skills per agent) — complementary: agents
  that use or consult the skill.

Convention (see SKILL-TEMPLATE.md): agent_roles = routing agent (if any) UNION
AGENT-MODEL agents. Skills without any source are demand-driven (no level); a
WARN is emitted so a missing entry is visible, but it is not a failure.
"""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = OPENCODE_DIR.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
ROUTING = OPENCODE_DIR / "framework" / "SKILL-ROUTING.md"
AGENT_MODEL = OPENCODE_DIR / "framework" / "AGENT-MODEL.md"

VALID_AGENTS = {"orchestrator-agent", "design-agent", "control-agent", "delivery-agent"}
errors = []
warnings = []


def norm(agent):
    a = agent.strip().lower().replace("_", "-")
    if a == "orchestrator":
        return "orchestrator-agent"
    return a if a.endswith("-agent") else f"{a}-agent"


def parse_frontmatter(content):
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    return content[3:end]


def current_roles(fm):
    m = re.search(r"^  agent_roles:\r?\n((?:  - .+\r?\n?)+)", fm, re.MULTILINE)
    if not m:
        return set()
    return {norm(x.strip("- ").strip()) for x in m.group(1).splitlines() if x.strip()}


# --- Source 1: routing levels ---
routing_src = {}
routing_text = ROUTING.read_text(encoding="utf-8")
for m in re.finditer(r"\bN\d{1,2}:\s*([\w/-]+)\s*→\s*(\w+)", routing_text):
    entry, agent = m.group(1), norm(m.group(2))
    for alt in entry.split("/"):
        alt = alt.strip()
        if alt:
            routing_src.setdefault(alt, set()).add(agent)

# --- Source 2: AGENT-MODEL ---
model_src = {}
model_text = AGENT_MODEL.read_text(encoding="utf-8")
current_agent = None
for line in model_text.splitlines():
    m_agent = re.match(r"^###\s+(\w+)\s*\(", line)
    if m_agent:
        current_agent = norm(m_agent.group(1))
        continue
    m_row = re.match(r"^\|\s*\*\*(Owner skills|Consulta skills|Stack skills)\*\*\s*\|\s*(.*?)\s*\|", line)
    if m_row and current_agent and current_agent != "orchestrator-agent":
        cell = m_row.group(2)
        if cell.strip() == "Ninguna":
            continue
        for token in cell.split(","):
            token = token.strip().strip("`")
            if token and re.match(r"^[a-z][a-z0-9-]*$", token):
                model_src.setdefault(token, set()).add(current_agent)

skills = {}
for d in sorted(SKILLS_DIR.iterdir()):
    if not d.is_dir():
        continue
    f = d / "SKILL.md"
    if not f.exists():
        continue
    fm = parse_frontmatter(f.read_text(encoding="utf-8"))
    if fm is None:
        continue
    skills[d.name] = current_roles(fm)

no_source = 0
for name in sorted(skills):
    roles = skills[name]
    bad = roles - VALID_AGENTS
    if bad:
        errors.append(f"Skill '{name}' has invalid agent_roles: {sorted(bad)}")

    src = set()
    if name in routing_src:
        src |= routing_src[name]
    if name in model_src:
        src |= model_src[name]

    if name in routing_src:
        missing = routing_src[name] - roles
        if missing:
            errors.append(
                f"Skill '{name}' is routed to {sorted(missing)} (SKILL-ROUTING) "
                f"but agent_roles={sorted(roles)}"
            )

    if not src:
        no_source += 1
        warnings.append(f"Skill '{name}' has no routing level nor AGENT-MODEL entry — review manually")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print(f"agent_roles OK across {len(skills)} skills ({no_source} demand-driven without routing/model source)")
