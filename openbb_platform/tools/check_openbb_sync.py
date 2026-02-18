"""Validate sync policy between primary and mirror OpenBB trees.

Primary tree:
  - openbb_platform/...
Mirror tree:
  - OpenBB/openbb_platform/...
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        while chunk := fp.read(1024 * 64):
            digest.update(chunk)
    return digest.hexdigest()


def _contains_token(path: Path, token: str) -> bool:
    if not path.exists():
        return False
    return token in path.read_text(encoding="utf-8")


def _check_file_sync(primary: Path, mirror: Path) -> tuple[bool, str]:
    if not primary.exists():
        return False, f"missing primary file: {primary}"
    if not mirror.exists():
        return False, f"missing mirror file: {mirror}"
    if _sha256(primary) != _sha256(mirror):
        return False, f"content mismatch: {primary} != {mirror}"
    return True, f"sync ok: {primary.name}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check sync policy for OpenBB mirror tree.")
    parser.add_argument("--repo-root", default=".")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.repo_root).resolve()

    checks: list[tuple[bool, str]] = []
    checks.append(
        _check_file_sync(
            root / "openbb_platform" / "core" / "openbb" / "assets" / "reference.json",
            root / "OpenBB" / "openbb_platform" / "core" / "openbb" / "assets" / "reference.json",
        )
    )
    checks.append(
        _check_file_sync(
            root / "openbb_platform" / "core" / "openbb" / "package" / "__extensions__.py",
            root / "OpenBB" / "openbb_platform" / "core" / "openbb" / "package" / "__extensions__.py",
        )
    )

    primary_pyproject = root / "openbb_platform" / "pyproject.toml"
    mirror_pyproject = root / "OpenBB" / "openbb_platform" / "pyproject.toml"
    for token in (
        'openbb-quant-ml = { version = "^0.1.0", optional = true }',
        'quant_ml = ["openbb-quant-ml"]',
        '"openbb-quant-ml"',
    ):
        ok = _contains_token(primary_pyproject, token) and _contains_token(mirror_pyproject, token)
        checks.append((ok, f"token sync ({token})"))

    failures = [message for ok, message in checks if not ok]
    for ok, message in checks:
        status = "OK" if ok else "FAIL"
        print(f"{status} {message}")  # noqa: T201

    if failures:
        print("sync policy check failed")  # noqa: T201
        return 1

    print("sync policy check passed")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
