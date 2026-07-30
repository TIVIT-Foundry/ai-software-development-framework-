#!/usr/bin/env python3
"""check-version-bumps.py — Verify that changed skills bump their `version:` field.

Per CONTRIBUTING.md: "Changing an existing skill: bump `version` in frontmatter
if the contract (inputs/outputs/dependencies) changes." This compares each
SKILL.md's working-tree content against the version last committed to git; if
the body changed but `version:` did not move, that's a contract change without
a version bump.

Skills with no git history yet (newly added, not committed) are skipped —
there is nothing to diff against.
"""
import re
import subprocess
import sys
from pathlib import Path

OPENCODE_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = OPENCODE_DIR / "skills"
ROOT_DIR = OPENCODE_DIR.parent
errors = []
warnings = []


def run_git(args):
    result = subprocess.run(
        ["git", *args], cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.returncode, result.stdout


def get_version(content):
    m = re.search(r"^version:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip().strip("'\"") if m else None


rc, _ = run_git(["rev-parse", "--is-inside-work-tree"])
if rc != 0:
    print("Not a git repository — skipping version-bump check")
    sys.exit(0)

rc, head_rev = run_git(["rev-parse", "HEAD"])
if rc != 0:
    print("No commits yet — skipping version-bump check")
    sys.exit(0)

checked = 0
for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        continue

    rel_path = skill_file.relative_to(ROOT_DIR).as_posix()

    # Skip skills not yet tracked in git (new, uncommitted skill directories).
    rc, tracked = run_git(["ls-files", "--error-unmatch", rel_path])
    if rc != 0:
        continue

    rc, head_content = run_git(["show", f"HEAD:{rel_path}"])
    if rc != 0:
        continue  # couldn't read committed version, skip

    working_content = skill_file.read_text(encoding="utf-8")
    if working_content == head_content:
        continue  # unchanged

    checked += 1
    head_version = get_version(head_content)
    working_version = get_version(working_content)

    # Ignore whitespace-only / version-line-only diffs from counting as "changed".
    def strip_version_line(text):
        return re.sub(r"^version:\s*.+$", "version:", text, flags=re.MULTILINE)

    if strip_version_line(head_content) == strip_version_line(working_content):
        continue  # only the version line itself changed (or nothing else did)

    if head_version is not None and working_version is not None and head_version == working_version:
        warnings.append(
            f"'{skill_dir.name}' SKILL.md content changed vs. last commit but version stayed at {working_version}"
        )

if warnings:
    for w in warnings:
        print(f"WARN: {w}")

print(f"Version-bump check: {checked} changed skill(s) reviewed, {len(warnings)} missing a version bump")
