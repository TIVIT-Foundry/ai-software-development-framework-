#!/usr/bin/env python3
"""check-spec-drift.py — Verify alignment between API specs and implemented code.

Part of the Spec-Driven Development (SDD) / Spec Kit workflow (converge phase).
Checks for two kinds of drift:
  1. Spec-to-Code: Endpoints declared in docs/api-first/*.md missing from backend implementation.
  2. Code-to-Spec: Endpoints implemented in backend (FastAPI / Bun) missing from specs.

Exit codes:
  0 = Sin drift o sin módulos implementados aún (graceful pass)
  1 = Drift detectado (endpoints faltantes o no especificados)
"""
import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
API_DOCS_DIR = ROOT_DIR / "docs" / "api-first"
SRC_DIR = ROOT_DIR / "src"

HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}


def normalize_path(path: str) -> str:
    """Normalize route path for comparison: /api/v1/users/{id} -> /api/v1/users/:id."""
    path = path.strip()
    if not path.startswith("/"):
        path = "/" + path
    # Convert {param} or <param> to :param
    path = re.sub(r"\{([a-zA-Z0-9_]+)\}", r":\1", path)
    path = re.sub(r"<([a-zA-Z0-9_]+)>", r":\1", path)
    # Strip trailing slash unless root
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return path.lower()


def extract_spec_endpoints(api_dir: Path) -> dict[tuple[str, str], str]:
    """Extract (method, path) -> spec_file from Markdown tables."""
    endpoints = {}
    if not api_dir.exists():
        return endpoints

    for spec_file in api_dir.glob("*.md"):
        if spec_file.name.lower() == "readme.md":
            continue
        try:
            content = spec_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Match table rows like: | GET | /api/v1/users | ... |
        # or: | POST | /users | ... |
        for line in content.splitlines():
            row = [c.strip() for c in line.split("|")]
            if len(row) >= 3:
                method_cand = row[1].upper()
                path_cand = row[2]
                if method_cand in HTTP_METHODS and path_cand.startswith("/"):
                    norm_p = normalize_path(path_cand)
                    key = (method_cand, norm_p)
                    endpoints[key] = spec_file.name
    return endpoints


def extract_code_endpoints(src_dir: Path) -> dict[tuple[str, str], str]:
    """Extract (method, path) -> source_file from Python FastAPI and TypeScript Bun routes."""
    endpoints = {}
    if not src_dir.exists():
        return endpoints

    # 1. Python FastAPI routes (@router.get, @app.post, etc.)
    for py_file in src_dir.glob("**/*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Find router prefix if any
        router_prefix = ""
        prefix_m = re.search(r'APIRouter\([^)]*prefix=["\']([^"\']+)["\']', content)
        if prefix_m:
            router_prefix = prefix_m.group(1).rstrip("/")

        # Find decorators: @router.get("/path"), @app.post("/path", ...)
        matches = re.finditer(
            r'@(?:router|app)\.(get|post|put|delete|patch|head|options)\(\s*["\']([^"\']+)["\']',
            content,
            re.IGNORECASE,
        )
        for m in matches:
            method = m.group(1).upper()
            route_path = m.group(2)
            full_path = router_prefix + ("/" if not route_path.startswith("/") else "") + route_path
            norm_p = normalize_path(full_path)
            key = (method, norm_p)
            endpoints[key] = str(py_file.relative_to(ROOT_DIR))

    # 2. Bun Elysia / Express / Hono routes (.get("/path", ...), .post("/path", ...))
    for ts_file in src_dir.glob("**/*.ts"):
        if "node_modules" in ts_file.parts or ".test." in ts_file.name or ".spec." in ts_file.name:
            continue
        try:
            content = ts_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        matches = re.finditer(
            r'\.(get|post|put|delete|patch|head|options)\(\s*["\']([^"\']+)["\']',
            content,
            re.IGNORECASE,
        )
        for m in matches:
            method = m.group(1).upper()
            route_path = m.group(2)
            norm_p = normalize_path(route_path)
            key = (method, norm_p)
            endpoints[key] = str(ts_file.relative_to(ROOT_DIR))

    return endpoints


def main():
    parser = argparse.ArgumentParser(description="Check drift between API specs and codebase.")
    parser.add_argument("--strict", action="store_true", help="Fail if any drift is found")
    args = parser.parse_args()

    spec_endpoints = extract_spec_endpoints(API_DOCS_DIR)
    code_endpoints = extract_code_endpoints(SRC_DIR)

    if not spec_endpoints and not code_endpoints:
        print("Spec drift check: 0 specs y 0 rutas en código (repo limpio / pre-scaffold)")
        sys.exit(0)

    if not spec_endpoints and code_endpoints:
        print(f"WARN: Existen {len(code_endpoints)} rutas en código pero ninguna spec en docs/api-first/", file=sys.stderr)
        if args.strict:
            sys.exit(1)
        sys.exit(0)

    if spec_endpoints and not code_endpoints:
        print(f"INFO: {len(spec_endpoints)} endpoints especificados, código aún no generado (Fase D/E pendiente)")
        sys.exit(0)

    # Check for mismatches
    missing_in_code = []
    for ep, spec_file in spec_endpoints.items():
        if ep not in code_endpoints:
            # Check with /api or without /api prefix flexibility
            alt_ep1 = (ep[0], "/api" + ep[1])
            alt_ep2 = (ep[0], ep[1].replace("/api", "", 1)) if ep[1].startswith("/api") else None
            if alt_ep1 not in code_endpoints and (alt_ep2 is None or alt_ep2 not in code_endpoints):
                missing_in_code.append((ep, spec_file))

    untracked_in_spec = []
    for ep, code_file in code_endpoints.items():
        if ep not in spec_endpoints:
            alt_ep1 = (ep[0], "/api" + ep[1])
            alt_ep2 = (ep[0], ep[1].replace("/api", "", 1)) if ep[1].startswith("/api") else None
            if alt_ep1 not in spec_endpoints and (alt_ep2 is None or alt_ep2 not in spec_endpoints):
                untracked_in_spec.append((ep, code_file))

    if not missing_in_code and not untracked_in_spec:
        print(f"OK: Spec drift check: {len(spec_endpoints)} endpoints perfectamente alineados spec <-> código")
        sys.exit(0)

    print("--- Spec Drift Report ---", file=sys.stderr)
    if missing_in_code:
        print(f"Endpoints en spec sin implementar en código ({len(missing_in_code)}):", file=sys.stderr)
        for (method, path), spec in missing_in_code:
            print(f"  [MISSING] {method} {path} (en {spec})", file=sys.stderr)

    if untracked_in_spec:
        print(f"Endpoints en código no documentados en spec ({len(untracked_in_spec)}):", file=sys.stderr)
        for (method, path), src in untracked_in_spec:
            print(f"  [UNDOCUMENTED] {method} {path} (en {src})", file=sys.stderr)

    if args.strict or missing_in_code:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
