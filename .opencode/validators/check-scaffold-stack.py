#!/usr/bin/env python3
"""check-scaffold-stack.py — Verify scaffold templates + frontend skills are consistent
for a dual-frontend framework (React default, Angular as an explicit alternative — see
ADR-005). Unlike a "single stack enforced" check, this validates that BOTH stacks are
complete and internally consistent, and that they don't cross-contaminate each other's
templates. It still blocks genuinely obsolete/removed stacks (C#/.NET, Dapper)."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SCAFFOLD_DIR = OPENCODE_DIR / "scaffold"
TEMPLATES_DIR = SCAFFOLD_DIR / "templates"
ANGULAR_TEMPLATES_DIR = TEMPLATES_DIR / "angular"
SKILLS_DIR = OPENCODE_DIR / "skills"
errors = []
warnings = []

# Genuinely removed/obsolete stacks — these have no ADR reinstating them.
OBSOLETE_PATTERNS = [
    "endpoint.cs.j2",
    "handler.cs.j2",
]
OBSOLETE_CODE_PATTERNS = [
    "Microsoft.AspNetCore",
    "using Dapper",
]

# React templates expected directly under templates/ (default frontend).
REACT_TEMPLATES = [
    "model.ts.j2",
    "api.ts.j2",
    "component.tsx.j2",
    "table.component.tsx.j2",
    "form.component.tsx.j2",
    "page.component.tsx.j2",
    "index.ts.j2",
]

# Angular templates expected under templates/angular/ (explicit alternative frontend,
# kept in its own subdirectory so filenames don't collide with the React ones — the
# same mechanism used to keep the Python and Bun backend templates apart by filename).
ANGULAR_TEMPLATES = [
    "service.ts.j2",
    "component.ts.j2",
    "component.html.j2",
    "table.component.ts.j2",
    "table.component.html.j2",
    "form.component.ts.j2",
    "form.component.html.j2",
    "page.component.ts.j2",
    "page.component.html.j2",
    "index.ts.j2",
]

if not TEMPLATES_DIR.exists():
    errors.append(f"Scaffold templates directory not found: {TEMPLATES_DIR}")
else:
    # 1) Obsolete stacks must not reappear.
    for tpl in OBSOLETE_PATTERNS:
        if (TEMPLATES_DIR / tpl).exists():
            errors.append(f"Obsolete template still present: {tpl}")
    for tpl_file in TEMPLATES_DIR.rglob("*.j2"):
        content = tpl_file.read_text(encoding="utf-8", errors="ignore")
        for pattern in OBSOLETE_CODE_PATTERNS:
            if pattern in content:
                rel = tpl_file.relative_to(TEMPLATES_DIR)
                errors.append(f"Template '{rel}' contains obsolete pattern: {pattern}")

    # 2) React stack completeness — templates/*.j2 (top level).
    for tpl in REACT_TEMPLATES:
        if not (TEMPLATES_DIR / tpl).exists():
            errors.append(f"Missing React template: templates/{tpl}")

    # 3) Angular stack completeness — templates/angular/*.j2.
    if not ANGULAR_TEMPLATES_DIR.exists():
        errors.append(
            f"Angular templates directory not found: {ANGULAR_TEMPLATES_DIR} "
            "(the 'angular' skill exists — its scaffold templates must too, see ADR-005)"
        )
    else:
        for tpl in ANGULAR_TEMPLATES:
            if not (ANGULAR_TEMPLATES_DIR / tpl).exists():
                errors.append(f"Missing Angular template: templates/angular/{tpl}")

    # 4) No cross-contamination: top-level (non-angular) templates must not import
    #    Angular APIs, and templates/angular/*.j2 must not use JSX-only syntax.
    if TEMPLATES_DIR.exists():
        for tpl_file in TEMPLATES_DIR.glob("*.j2"):
            content = tpl_file.read_text(encoding="utf-8", errors="ignore")
            for marker in ("@angular/core", "@angular/common", "@angular/forms", "@angular/router", "NgModule"):
                if marker in content:
                    errors.append(
                        f"React/top-level template '{tpl_file.name}' contains Angular-specific pattern: {marker}"
                    )
    if ANGULAR_TEMPLATES_DIR.exists():
        for tpl_file in ANGULAR_TEMPLATES_DIR.glob("*.j2"):
            content = tpl_file.read_text(encoding="utf-8", errors="ignore")
            if "className=" in content:
                errors.append(f"Angular template '{tpl_file.name}' contains JSX-only syntax: className=")

# 5) Frontend skills: if the 'angular' skill exists, angular-services/angular-upgrade
#    and their templates/ should too (paired with react/react-services/react-upgrade),
#    and vice versa — a lopsided pair is a sign of a partial migration.
FRONTEND_PAIRS = [
    ("react", "angular"),
    ("react-services", "angular-services"),
]
for react_name, angular_name in FRONTEND_PAIRS:
    react_dir = SKILLS_DIR / react_name
    angular_dir = SKILLS_DIR / angular_name
    react_exists = (react_dir / "SKILL.md").exists()
    angular_exists = (angular_dir / "SKILL.md").exists()
    if react_exists and not angular_exists:
        warnings.append(f"Skill '{react_name}' exists but its Angular counterpart '{angular_name}' does not")
    if angular_exists and not react_exists:
        warnings.append(f"Skill '{angular_name}' exists but its React counterpart '{react_name}' does not")
    if react_exists and angular_exists:
        react_tpl = (react_dir / "templates").exists()
        angular_tpl = (angular_dir / "templates").exists()
        if react_tpl != angular_tpl:
            errors.append(
                f"'{react_name}' and '{angular_name}' are inconsistent: "
                f"templates/ present={react_tpl} vs {angular_tpl}"
            )

readme = SCAFFOLD_DIR / "README.md"
if readme.exists():
    readme_content = readme.read_text(encoding="utf-8")
    if "React" not in readme_content:
        errors.append("scaffold/README.md does not mention React")
    if "Angular" not in readme_content:
        errors.append("scaffold/README.md does not mention Angular (both frontends must be documented, see ADR-005)")
    if "--frontend" not in readme_content:
        errors.append("scaffold/README.md does not document the --frontend flag")
    if "C#" in readme_content or ".cs" in readme_content:
        warnings.append("scaffold/README.md mentions C#/.cs")

if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    sys.exit(1)

for w in warnings:
    print(f"WARN: {w}")

print("Scaffold templates aligned with framework stack (React + Angular + Python/Bun)")
