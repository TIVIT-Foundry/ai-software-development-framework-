#!/usr/bin/env python3
"""check-secrets.py — Scan for accidentally committed secrets and hardcoded URLs."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PATTERNS = [
    r'(?i)(api[_-]?key|secret|password|token)\s*[=:]\s*["\'][A-Za-z0-9+/=]{20,}["\']',
    r'(?i)(AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID)\s*=\s*["\'][^"\']+["\']',
]
SKIP = {".git", "__pycache__", "node_modules", ".venv"}
warnings = []
url_warnings = []

# URLs should be environment-configured, not hardcoded — but this only applies
# to actual code/generated-code templates, never to .md docs (which legitimately
# show example URLs). Hosts below are conventionally safe placeholders/local dev.
URL_PATTERN = r'(?i)\b(url|endpoint|host|base_url|api_url)\s*[=:]\s*["\']https?://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|example\.(com|org))[^"\']+["\']'
URL_CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".j2"}

for f in ROOT.rglob("*"):
    if f.is_file() and f.suffix not in (".pyc", ".exe", ".dll", ".so", ".png", ".jpg"):
        rel_parts = set(f.relative_to(ROOT).parts)
        if rel_parts & SKIP:
            continue
        if f.stat().st_size > 1_000_000:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in PATTERNS:
            if re.search(pat, text):
                warnings.append(f"Possible secret in: {f.relative_to(ROOT)}")
        if f.suffix in URL_CODE_EXTS and re.search(URL_PATTERN, text):
            url_warnings.append(f"Possible hardcoded URL (should be env var): {f.relative_to(ROOT)}")

if warnings:
    for w in warnings:
        print(f"WARN: {w}")
    print(f"\n{len(warnings)} possible secret(s) found (review manually)")
else:
    print("No secrets found")

if url_warnings:
    for w in url_warnings:
        print(f"WARN: {w}")
    print(f"\n{len(url_warnings)} possible hardcoded URL(s) found (review manually)")
else:
    print("No hardcoded URLs found")

sys.exit(0)
