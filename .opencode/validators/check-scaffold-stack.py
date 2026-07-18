#!/usr/bin/env python3
"""check-scaffold-stack.py — Verify scaffold templates are aligned with framework stack (Angular + Python/Bun)."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SCAFFOLD_DIR = OPENCODE_DIR / "scaffold"
TEMPLATES_DIR = SCAFFOLD_DIR / "templates"
errors = []
warnings = []

OBSOLETE_TEMPLATES = [
    "component.tsx.j2",
    "hook.ts.j2",
    "endpoint.cs.j2",
    "handler.cs.j2",
    "component.module.css.j2",
    "form.module.css.j2",
    "page.module.css.j2",
]

OBSOLETE_PATTERNS = ["@tanstack/react-query", "react-hook", "Microsoft.AspNetCore", "using Dapper"]

if not TEMPLATES_DIR.exists():
    errors.append(f"Scaffold templates directory not found: {TEMPLATES_DIR}")
else:
    for tpl in OBSOLETE_TEMPLATES:
        if (TEMPLATES_DIR / tpl).exists():
            errors.append(f"Obsolete template still present: {tpl}")
    for tpl_file in TEMPLATES_DIR.glob("*.j2"):
        content = tpl_file.read_text(encoding="utf-8", errors="ignore")
        for pattern in OBSOLETE_PATTERNS:
            if pattern in content:
                errors.append(f"Template '{tpl_file.name}' contains obsolete pattern: {pattern}")

readme = SCAFFOLD_DIR / "README.md"
if readme.exists():
    readme_content = readme.read_text(encoding="utf-8")
    if "React" in readme_content and "Angular" not in readme_content:
        errors.append("scaffold/README.md mentions React but not Angular")
    if "C#" in readme_content or ".cs" in readme_content:
        warnings.append("scaffold/README.md mentions C#/.cs")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print("Scaffold templates aligned with framework stack (Angular + Python/Bun)")
