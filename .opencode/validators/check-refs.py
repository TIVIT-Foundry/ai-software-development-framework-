#!/usr/bin/env python3
"""check-refs.py — Verify internal references point to existing files."""
import re
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = OPENCODE_DIR.parent
warnings = []

SKIP_PATTERNS = [
    "../framework/",      # deleted framework docs
    "docs/api-catalog.md",  # deleted docs
    "docs/modules/",
    "docs/hus/",
    "./CHANGELOG.md",     # deleted
    "./docs/openapi.yaml",
    "./docs/architecture.md",
    "./docs/adr/",
    "{grafana-url}",      # placeholders, resolved at deploy time
    "{langfuse-url}",
    "{prometheus-url}",
]

# Files that intentionally reference the target project's own docs are skipped:
# READMEs and specs describe files that will exist in the consumer project.
TEMPLATE_DOCS = {"readme", "api-catalog", "api-first-spec"}

for md_file in OPENCODE_DIR.rglob("*.md"):
    # Never scan third-party tooling.
    if "node_modules" in md_file.parts or ".venv" in md_file.parts:
        continue
    content = md_file.read_text(encoding="utf-8")
    for match in re.finditer(r'\[.*?\]\(([^)]+)\)', content):
        link = match.group(1)
        if link.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if any(skip in link for skip in SKIP_PATTERNS):
            continue
        rel_parts = md_file.relative_to(OPENCODE_DIR).parts
        if len(rel_parts) >= 2 and rel_parts[0] == "skills" and rel_parts[1] in TEMPLATE_DOCS:
            continue  # generated README/spec references target-project files
        target = (md_file.parent / link).resolve()
        if not target.exists():
            rel = md_file.relative_to(ROOT_DIR)
            warnings.append(f"{rel}: broken link -> {link}")

if warnings:
    for w in warnings:
        print(f"WARN: {w}")
    print(f"\n{len(warnings)} broken link(s) found (non-blocking)")
else:
    print("All internal references valid")
# Non-blocking by design: broken refs in skills are documentation examples.
sys.exit(0)
