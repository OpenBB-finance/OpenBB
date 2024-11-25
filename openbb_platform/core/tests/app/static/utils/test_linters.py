"""Test linters.py file."""

# pylint: disable=redefined-outer-name

import pytest
from openbb_core.app.static.package_builder import (
    Linters,
)


@pytest.fixture(scope="module")
def tmp_package_dir(tmp_path_factory):
    """Return a temporary package directory."""
    return tmp_path_factory.mktemp("package")


@pytest.fixture(scope="module")
def linters(tmp_package_dir):
    """Return linters."""
    return Linters(tmp_package_dir)


def test_linters_init(linters):
    """Test linters init."""
    assert linters


def test_print_separator(linters):
    """Test print separator."""
    linters.print_separator(symbol="AAPL")


def test_run(linters):
    """Test run."""
    linters.run(linter="ruff")


def test_ruff(linters):
    """Test ruff."""
    linters.ruff()


def test_black(linters):
    """Test black."""
    linters.black()
