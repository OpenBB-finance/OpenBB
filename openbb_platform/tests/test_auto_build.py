"""Test the auto_build feature."""

import importlib
import sys
from unittest.mock import patch

import pytest

# pylint: disable=redefined-outer-name, unused-import, import-outside-toplevel


@pytest.fixture(autouse=True)
def setup_mocks():
    """Set up mocks for the test."""
    with patch("openbb._PackageBuilder.auto_build") as mock_auto_build:
        mock_auto_build.return_value = None
        yield mock_auto_build


@pytest.fixture
def openbb_module(setup_mocks):
    """Reload the openbb module."""
    if "openbb" in sys.modules:
        importlib.reload(sys.modules["openbb"])
    else:
        pass
    return setup_mocks


@pytest.mark.integration
def test_autobuild_called(openbb_module):
    """Test that auto_build is called upon importing openbb."""
    openbb_module.assert_called_once()
