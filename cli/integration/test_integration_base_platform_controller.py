"""Test the base platform controller."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from openbb_cli.controllers.base_platform_controller import (
    PlatformController,
    Session,
)

# pylint: disable=protected-access, unused-variable, redefined-outer-name


@pytest.fixture
def platform_controller():
    """Return a platform controller."""
    session = Session()  # noqa: F841
    translators = {"test_command": MagicMock(), "test_menu": MagicMock()}  # noqa: F841
    translators["test_command"]._parser = Mock(
        _actions=[Mock(dest="data", choices=[], type=str, nargs=None)]
    )
    translators["test_command"].execute_func = Mock(return_value=Mock())
    translators["test_menu"]._parser = Mock(
        _actions=[Mock(dest="data", choices=[], type=str, nargs=None)]
    )
    translators["test_menu"].execute_func = Mock(return_value=Mock())

    controller = PlatformController(
        name="test", parent_path=["platform"], translators=translators
    )
    return controller


@pytest.mark.integration
def test_platform_controller_initialization(platform_controller):
    """Test the initialization of the platform controller."""
    expected_path = "/platform/test/"
    assert (
        expected_path == platform_controller.PATH
    ), "Controller path was not set correctly"


@pytest.mark.integration
def test_command_generation(platform_controller):
    """Test the generation of commands."""
    command_name = "test_command"
    mock_execute_func = Mock(return_value=(Mock(), None))
    platform_controller.translators[command_name].execute_func = mock_execute_func

    platform_controller._generate_command_call(
        name=command_name, translator=platform_controller.translators[command_name]
    )
    command_method_name = f"call_{command_name}"
    assert hasattr(
        platform_controller, command_method_name
    ), "Command method was not created"


@patch(
    "openbb_cli.controllers.base_platform_controller.PlatformController._link_obbject_to_data_processing_commands"
)
@patch(
    "openbb_cli.controllers.base_platform_controller.PlatformController._generate_commands"
)
@patch(
    "openbb_cli.controllers.base_platform_controller.PlatformController._generate_sub_controllers"
)
@pytest.mark.integration
def test_platform_controller_calls(
    mock_sub_controllers, mock_commands, mock_link_commands
):
    """Test the calls of the platform controller."""
    translators = {"test_command": Mock()}
    translators["test_command"].parser = Mock()
    translators["test_command"].execute_func = Mock()
    _ = PlatformController(
        name="test", parent_path=["platform"], translators=translators
    )
    mock_sub_controllers.assert_called_once()
    mock_commands.assert_called_once()
    mock_link_commands.assert_called_once()
