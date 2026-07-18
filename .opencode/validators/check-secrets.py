#!/usr/bin/env python3
"""check-secrets.py — Scan for accidentally committed secrets."""
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

if warnings:
    for w in warnings:
        print(f"WARN: {w}")
    print(f"\n{len(warnings)} possible secret(s) found (review manually)")
else:
    print("No secrets found")
sys.exit(0)
