"""Test the BasePlatformController."""

from unittest.mock import MagicMock, patch

import pytest
from openbb_cli.controllers.base_platform_controller import PlatformController, Session

# pylint: disable=redefined-outer-name, protected-access, unused-argument, unused-variable


@pytest.fixture
def mock_session():
    """Mock session fixture."""
    with patch(
        "openbb_cli.controllers.base_platform_controller.session",
        MagicMock(spec=Session),
    ) as mock:
        yield mock


def test_initialization_with_valid_params(mock_session):
    """Test the initialization of the BasePlatformController."""
    translators = {"dummy_translator": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )
    assert controller._name == "test"
    assert controller.translators == translators


def test_initialization_without_required_params():
    """Test the initialization of the BasePlatformController without required params."""
    with pytest.raises(ValueError):
        PlatformController(name="test", parent_path=["parent"])


def test_command_generation(mock_session):
    """Test the command generation method."""
    translator = MagicMock()
    translators = {"test_command": translator}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    # Check if command function is correctly linked
    assert "test_command" in controller.translators


def test_print_help(mock_session):
    """Test the print help method."""
    translators = {"test_command": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    with patch(
        "openbb_cli.controllers.base_platform_controller.MenuText"
    ) as mock_menu_text:
        controller.print_help()
        mock_menu_text.assert_called_once_with("/parent/test/")


def test_sub_controller_generation(mock_session):
    """Test the sub controller generation method."""
    translators = {"test_menu_item": MagicMock()}
    controller = PlatformController(
        name="test", parent_path=["parent"], translators=translators
    )

    assert "test_menu_item" in controller.translators
