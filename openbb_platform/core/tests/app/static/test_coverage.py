"""Test the coverage.py file."""
# pylint: disable=redefined-outer-name

import pytest
from openbb_core.app.static.coverage import Coverage


@pytest.fixture(scope="module")
def coverage():
    """Return coverage."""
    return Coverage()


def test_coverage_init(coverage):
    """Test coverage init."""
    assert coverage


def test_coverage_providers(coverage):
    """Test coverage providers."""
    provider_coverage = coverage.providers
    assert provider_coverage
    assert isinstance(provider_coverage, dict)


def test_coverage_commands(coverage):
    """Test coverage commands."""
    command_coverage = coverage.commands
    assert command_coverage
    assert isinstance(command_coverage, dict)
