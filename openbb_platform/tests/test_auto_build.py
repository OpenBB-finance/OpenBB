"""Test the auto_build feature."""

import importlib
import sys
from unittest.mock import patch

import pytest

# pylint: disable=redefined-outer-name, unused-import, import-outside-toplevel
#


@pytest.fixture(autouse=True)
def setup_mocks():
    with patch(
        "openbb_core.app.static.package_builder.PackageBuilder.auto_build"
    ) as mock_auto_build:
        mock_auto_build.return_value = None
        yield mock_auto_build


@pytest.fixture
def openbb_module(setup_mocks):
    if "openbb" in sys.modules:
        importlib.reload(sys.modules["openbb"])
    else:
        pass
    return setup_mocks


def test_autobuild_called(openbb_module):
    """
    Test that auto_build is called upon importing openbb.
    """
    openbb_module.assert_called_once()
