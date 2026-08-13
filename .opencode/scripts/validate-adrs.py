#!/usr/bin/env python3
"""validate-adrs.py — Validate ADR files in docs/adr/.

Checks every file matching ADR-###-*.md:
  - Naming: ADR-###-kebab-title.md
  - Required headers (## Contexto / ## Decisión / ## Consecuencias)
  - Required fields in the first 10 lines: status, fecha, decidido_por (best-effort)

Usage:
    python .opencode/scripts/validate-adrs.py docs/adr/
Exit 0 = ok, 1 = violations found.
"""
import re
import sys
from pathlib import Path

REQUIRED_HEADERS = ["## Contexto", "## Decisión", "## Consecuencias"]
# Convencion del framework: **Estado:** / **Fecha:** en el encabezado del ADR.
REQUIRED_FIELDS = ["estado", "fecha"]


def validate_dir(adr_dir: Path) -> list[str]:
    errors = []
    files = sorted(adr_dir.glob("ADR-*.md")) if adr_dir.exists() else []
    if not files:
        errors.append(f"No ADR files found in {adr_dir}")
        return errors

    for f in files:
        if not re.match(r"^ADR-\d{3}-[a-z0-9-]+\.md$", f.name):
            errors.append(f"{f.name}: nombre invalido (esperado ADR-###-kebab-title.md)")
        content = f.read_text(encoding="utf-8")
        for header in REQUIRED_HEADERS:
            if header not in content:
                errors.append(f"{f.name}: falta encabezado '{header}'")
        head = content[:400].lower()
        for field in REQUIRED_FIELDS:
            if f"{field}:" not in head:
                errors.append(f"{f.name}: falta campo '{field}' en el frontmatter")
    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: validate-adrs.py <docs/adr>", file=sys.stderr)
        return 2
    errors = validate_dir(Path(sys.argv[1]))
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} violation(s)", file=sys.stderr)
        return 1
    print("ADR validation OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
