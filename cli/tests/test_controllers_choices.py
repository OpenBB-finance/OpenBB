"""Test the choices controller."""

from argparse import ArgumentParser
from unittest.mock import patch

import pytest
from openbb_cli.controllers.choices import (
    build_controller_choice_map,
)

# pylint: disable=redefined-outer-name, protected-access, unused-argument, unused-variable


class MockController:
    """Mock controller class for testing."""

    CHOICES_COMMANDS = ["test_command"]
    controller_choices = ["test_command", "help"]

    def call_test_command(self, args):
        """Mock function for test_command."""
        parser = ArgumentParser()
        parser.add_argument(
            "--example", choices=["option1", "option2"], help="Example argument."
        )
        return parser.parse_args(args)


@pytest.fixture
def mock_controller():
    """Mock controller fixture."""
    return MockController()


def test_build_command_choice_map(mock_controller):
    """Test the building of a command choice map."""
    with patch(
        "openbb_cli.controllers.choices._get_argument_parser"
    ) as mock_get_parser:
        parser = ArgumentParser()
        parser.add_argument(
            "--option", choices=["opt1", "opt2"], help="A choice option."
        )
        mock_get_parser.return_value = parser

        choice_map = build_controller_choice_map(controller=mock_controller)

        assert "test_command" in choice_map
        assert "--option" in choice_map["test_command"]
        assert "opt1" in choice_map["test_command"]["--option"]
        assert "opt2" in choice_map["test_command"]["--option"]
