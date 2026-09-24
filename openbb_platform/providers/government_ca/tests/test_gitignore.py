"""Government of Canada .gitignore smoke tests."""

from pathlib import Path

ASSETS_ENTRY = "openbb_platform/providers/government_ca/openbb_government_ca/assets/*"


def _package_root() -> Path:
    """Return the government_ca package directory."""
    import openbb_government_ca

    return Path(openbb_government_ca.__file__).parent.parent


def _repo_root() -> Path:
    """Return the repository root that holds the shared .gitignore."""
    return _package_root().parents[2]


def test_assets_entry_is_unique():
    """The root .gitignore ignores the assets path with exactly one entry."""
    gitignore = (_repo_root() / ".gitignore").read_text(encoding="utf-8")
    entries = [line.strip() for line in gitignore.splitlines()]

    assert entries.count(ASSETS_ENTRY) == 1


def test_no_per_package_gitignore():
    """No hand-authored per-package .gitignore exists under the package directory."""
    package_dir = _package_root()

    # Tool caches and build outputs drop their own .gitignore; only
    # hand-authored ones count.
    tool_cache_dirs = {
        ".pytest_cache",
        ".ruff_cache",
        ".hypothesis",
        "__pycache__",
        ".mypy_cache",
        ".venv",
        "dist",
    }
    authored = [
        path
        for path in package_dir.rglob(".gitignore")
        if tool_cache_dirs.isdisjoint(path.parts)
    ]

    assert not authored
