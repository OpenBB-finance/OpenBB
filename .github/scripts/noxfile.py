"""Nox sessions."""

from pathlib import Path

import nox

ROOT_DIR = Path(__file__).parent.parent.parent
PLATFORM_DIR = ROOT_DIR / "openbb_platform"
PLATFORM_TESTS = [
    str(PLATFORM_DIR / p) for p in ["tests", "core", "providers", "extensions"]
]
CLI_DIR = ROOT_DIR / "cli"
CLI_TESTS = CLI_DIR / "tests"


@nox.session(python=["3.9", "3.10", "3.11"])
def unit_test_platform(session):
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
        "pytest",
        Path(
            ROOT_DIR, "openbb_platform/extensions/tests/test_integration_tests_api.py"
        ),
        # f"--cov={PLATFORM_DIR}",
        "-m",
        "not integration",
        "-s",
        "-k",
        "test_api_interface_integration_test_params",
    )
    # session.run(
    #     "pytest",
    #     "",
    #     f"--cov={PLATFORM_DIR}",
    #     "-m",
    #     "not integration",
    #     "-s",
    # )


@nox.session(python=["3.9", "3.10", "3.11"])
def unit_test_cli(session):
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
    session.run("pytest", CLI_TESTS, f"--cov={CLI_DIR}")
