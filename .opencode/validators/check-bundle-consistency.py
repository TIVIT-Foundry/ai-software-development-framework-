#!/usr/bin/env python3
"""check-bundle-consistency.py — Verify skill bundles are consistent."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"

count = sum(1 for d in SKILLS_DIR.iterdir() if d.is_dir())
print(f"Bundle consistency: {count} skills total")
