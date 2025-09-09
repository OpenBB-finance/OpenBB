"""Root configuration for pytest."""

# flake8: noqa: S101
# pylint: disable=unused-argument

import os
import shutil
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def cleanup_generated_files():
    """Clean up generated files and restore original state before and after test session."""
    reference_file = ROOT_DIR / "core" / "openbb" / "assets" / "reference.json"
    reference_backup = ROOT_DIR / "core" / "openbb" / "reference.json.original"

    def clean_and_restore():
        # 1. Remove all files in core/openbb/package except __init__.py
        package_dir = ROOT_DIR / "core" / "openbb" / "package"
        if package_dir.exists():
            for item in package_dir.iterdir():
                if item.name != "__init__.py":
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)

        # 2. Create backup before first cleanup if it doesn't exist
        if reference_file.exists() and not reference_backup.exists():
            shutil.copy2(reference_file, reference_backup)

        # 3. Restore from backup if it exists
        elif reference_backup.exists() and reference_file.exists():
            shutil.copy2(reference_backup, reference_file)
            reference_backup.unlink()

    # Clean before tests
    clean_and_restore()

    yield

    # Clean after tests
    clean_and_restore()


@pytest.mark.order(1)
def test_repository_state():
    """Ensure repository is in clean state before other tests."""
    # Check that core/openbb/package only contains __init__.py
    package_dir = ROOT_DIR / "core" / "openbb" / "package"
    if package_dir.exists():
        files = [f for f in package_dir.iterdir() if f.is_file()]
        assert (
            len(files) <= 1
        ), f"Package directory should only contain __init__.py, found: {[f.name for f in files]}"
        if files:
            assert (
                files[0].name == "__init__.py"
            ), f"Only __init__.py should exist, found: {files[0].name}"


def pytest_configure():
    """Set environment variables for testing."""
    os.environ["OPENBB_AUTO_BUILD"] = "true"


def pytest_collection_modifyitems(config, items):
    """Modify test collection to ensure cleanup-dependent tests run first."""
    # Find tests that should run early (checking clean state)
    early_tests: list = []
    other_tests: list = []

    for item in items:
        # Tests that check repository state should run first
        if (
            "repository_state" in item.name.lower()
            or "extension_map" in item.name.lower()
            or item.get_closest_marker("order")
        ):
            early_tests.append(item)
        else:
            other_tests.append(item)

    # Sort early tests by their order marker if present
    early_tests.sort(
        key=lambda x: (
            getattr(x.get_closest_marker("order"), "args", [999])[0]
            if x.get_closest_marker("order")
            else 999
        )
    )

    # Reorder: early tests first, then others
    items[:] = early_tests + other_tests
