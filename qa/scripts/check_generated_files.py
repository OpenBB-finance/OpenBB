"""Validate repo-managed generated file boundaries."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PACKAGE_DIR = "openbb_platform/core/openbb/package/"
APPROVED_GENERATED = {f"{PACKAGE_DIR}__init__.py"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _tracked_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    """Reject unexpected generated package wrappers."""
    repo_root = _repo_root()
    blocked = [
        path
        for path in _tracked_files(repo_root)
        if path.startswith(PACKAGE_DIR) and path not in APPROVED_GENERATED
    ]
    if not blocked:
        return 0

    print(
        "Error: attempting to commit generated files in "
        f"'{PACKAGE_DIR}'. Only __init__.py is allowed.",
        file=sys.stderr,
    )
    for path in blocked:
        print(path, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
