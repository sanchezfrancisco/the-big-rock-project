from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"


def main() -> int:
    if not CHANGELOG_PATH.exists():
        print("ERROR: CHANGELOG.md not found.")
        return 1

    changed_files = _git_changed_files()
    relevant = [p for p in changed_files if _is_relevant_change(p)]
    if not relevant:
        print("No relevant file changes detected; changelog check skipped.")
        return 0

    changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
    if not _unreleased_has_items(changelog):
        print("ERROR: Relevant changes detected but [Unreleased] in CHANGELOG.md is empty.")
        print("Changed files:")
        for path in relevant:
            print(f"- {path}")
        return 1

    required_sections = _required_sections_for_changes(relevant)
    missing = _missing_required_sections(changelog, required_sections)
    if missing:
        print("ERROR: Unreleased changelog missing required sections with content:")
        for section in sorted(missing):
            print(f"- {section}")
        print("Changed files:")
        for path in relevant:
            print(f"- {path}")
        return 1

    print("Changelog check passed: Unreleased has content and required sections.")
    return 0


def _required_sections_for_changes(files: list[str]) -> set[str]:
    required: set[str] = set()
    for path in files:
        lower = path.lower()
        if any(
            lower.endswith(ext)
            for ext in (".py", ".js", ".ts", ".tsx", ".css", ".html", ".toml", ".yml", ".yaml")
        ):
            required.add("Changed")
        if lower.startswith("docs/") and lower.endswith(".md"):
            required.add("Changed")
        if "security" in lower or "auth" in lower or "secret" in lower:
            required.add("Security")
    if not required:
        required.add("Changed")
    return required


def _missing_required_sections(changelog: str, required: set[str]) -> set[str]:
    unreleased = _unreleased_block(changelog)
    missing: set[str] = set()
    for section in required:
        if not _section_has_meaningful_bullet(unreleased, section):
            missing.add(section)
    return missing


def _unreleased_block(changelog: str) -> str:
    block_match = re.search(
        r"## \[Unreleased\](.*?)(?:\n## \[|\Z)",
        changelog,
        flags=re.S,
    )
    return block_match.group(1) if block_match else ""


def _section_has_meaningful_bullet(block: str, section: str) -> bool:
    pattern = rf"### {re.escape(section)}(.*?)(?:\n### |\Z)"
    match = re.search(pattern, block, flags=re.S)
    if not match:
        return False
    lines = [line.strip() for line in match.group(1).splitlines()]
    bullets = [line for line in lines if line.startswith("-")]
    meaningful = [line for line in bullets if line not in {"-", "- "}]
    return len(meaningful) > 0


def _unreleased_has_items(changelog: str) -> bool:
    block = _unreleased_block(changelog)
    if not block:
        return False
    lines = [line.strip() for line in block.splitlines()]
    bullets = [line for line in lines if line.startswith("-")]
    meaningful = [line for line in bullets if line != "-" and line != "- "]
    return len(meaningful) > 0


def _git_changed_files() -> list[str]:
    base_ref = "origin/main"
    # Fallback to HEAD~1 if origin/main is unavailable in local/CI context.
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if files:
            return files
    except subprocess.CalledProcessError:
        pass

    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1...HEAD"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _is_relevant_change(path: str) -> bool:
    if path == "CHANGELOG.md":
        return False
    if path.startswith("docs/releases/"):
        return False
    return path.endswith(".py") or path.endswith(".md") or path.endswith(".toml") or path.endswith(".html") or path.endswith(".css") or path.endswith(".js")


if __name__ == "__main__":
    sys.exit(main())
