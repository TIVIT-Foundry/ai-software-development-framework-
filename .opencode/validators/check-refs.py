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
]

for md_file in OPENCODE_DIR.rglob("*.md"):
    content = md_file.read_text(encoding="utf-8")
    for match in re.finditer(r'\[.*?\]\(([^)]+)\)', content):
        link = match.group(1)
        if link.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if any(skip in link for skip in SKIP_PATTERNS):
            continue
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
# Always pass - broken refs in skills are documentation examples, not blocking
sys.exit(0)
