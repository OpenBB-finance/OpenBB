"""Resolve the canonical Python interpreter for this repository."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def resolve_python(repo_root: Path) -> Path:
    """Return the preferred Python interpreter for a repository."""
    candidates = (
        repo_root / ".venv" / "Scripts" / "python.exe",
        repo_root / ".venv" / "bin" / "python",
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    system_python = shutil.which("python")
    if system_python:
        return Path(system_python).resolve()

    raise FileNotFoundError(
        f"Could not resolve a Python interpreter for repository root: {repo_root}"
    )


def main(argv: list[str]) -> int:
    """Print the resolved Python interpreter path."""
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    try:
        print(resolve_python(repo_root))
        return 0
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
