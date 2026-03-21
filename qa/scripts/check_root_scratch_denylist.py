"""Reject staged root-level scratch artifacts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DENYLIST = {
    "macro_regime.json",
    "tmp_api_test.ps1",
    "tmp_backtest_payload.json",
    "test_growth.py",
    "test_growth2.py",
    "test_growth_out.txt",
    "test_yf.py",
    "test_yf_params.py",
    "yf_test_out.txt",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _staged_tracked_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return [
        path.decode("utf-8", "surrogateescape")
        for path in result.stdout.split(b"\x00")
        if path
    ]


def main() -> int:
    """Reject staged root scratch files while ignoring local untracked files."""
    repo_root = _repo_root()
    blocked = [path for path in _staged_tracked_files(repo_root) if path in DENYLIST]
    if not blocked:
        return 0

    print(
        "Error: root scratch files must stay local-only and should not be committed.",
        file=sys.stderr,
    )
    for path in blocked:
        print(path, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
