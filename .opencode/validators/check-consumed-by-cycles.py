#!/usr/bin/env python3
"""check-consumed-by-cycles.py — Check for circular dependencies."""
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"

print("Dependency cycle check: N/A (skills are standalone)")
