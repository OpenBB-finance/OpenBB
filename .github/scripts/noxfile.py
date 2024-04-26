"""Nox sessions."""

from pathlib import Path

import nox

ROOT_DIR = Path(__file__).parent.parent.parent
PLATFORM_DIR = ROOT_DIR / "openbb_platform"
PLATFORM_TESTS = [
    str(PLATFORM_DIR / p) for p in ["tests", "core", "providers", "extensions"]
]


@nox.session(python=["3.9", "3.10", "3.11"])
def tests(session):
    """Run the test suite."""
    session.install("poetry", "toml")
    session.run(
        "python",
        str(PLATFORM_DIR / "dev_install.py"),
        "-e",
        "all",
        external=True,
    )
    session.install("pytest")
    session.install("pytest-cov")
    session.run(
        "pytest", *PLATFORM_TESTS, f"--cov={PLATFORM_DIR}", "-m", "not integration"
    )
