"""Test the CLI controller."""

from unittest.mock import MagicMock, mock_open, patch

import pytest
from openbb_cli.controllers.cli_controller import (
    CLIController,
    handle_job_cmds,
    parse_and_split_input,
    run_cli,
)

# pylint: disable=redefined-outer-name, unused-argument


def test_parse_and_split_input_custom_filters():
    """Test the parse_and_split_input function with custom filters."""
    input_cmd = "query -q AAPL/P"
    result = parse_and_split_input(
        input_cmd, custom_filters=[r"((\ -q |\ --question|\ ).*?(/))"]
    )
    assert (
        "AAPL/P" not in result
    ), "Should filter out terms that look like a sorting parameter"


@patch("openbb_cli.controllers.cli_controller.CLIController.print_help")
def test_cli_controller_print_help(mock_print_help):
    """Test the CLIController print_help method."""
    controller = CLIController()
    controller.print_help()
    mock_print_help.assert_called_once()


@pytest.mark.parametrize(
    "controller_input, expected_output",
    [
        ("settings", True),
        ("random_command", False),
    ],
)
def test_CLIController_has_command(controller_input, expected_output):
    """Test the CLIController has_command method."""
    controller = CLIController()
    assert hasattr(controller, f"call_{controller_input}") == expected_output


def test_handle_job_cmds_with_export_path():
    """Test the handle_job_cmds function with an export path."""
    jobs_cmds = ["export /path/to/export some_command"]
    result = handle_job_cmds(jobs_cmds)
    expected = "some_command"
    assert expected in result[0]  # type: ignore


@patch("openbb_cli.controllers.cli_controller.CLIController.switch", return_value=[])
@patch("openbb_cli.controllers.cli_controller.print_goodbye")
def test_run_cli_quit_command(mock_print_goodbye, mock_switch):
    """Test the run_cli function with the quit command."""
    run_cli(["quit"], test_mode=True)
    mock_print_goodbye.assert_called_once()


@patch(
    "openbb_cli.controllers.cli_controller.parse_openbb_script",
    return_value=("mocked", ""),
)
@patch(
    "openbb_cli.controllers.cli_controller.CLIController.update_runtime_choices",
)
@patch("builtins.open", new_callable=mock_open, read_data="print('Hello World')")
@patch("requests.get")
def test_execute_openbb_routine_with_mocked_requests(
    mock_get, mock_file, mock_update, mock_parse
):
    """Test the call_exe function with mocked requests."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"script": "print('Hello World')"}
    mock_get.return_value = response
    controller = CLIController()
    controller.call_exe(
        ["--url", "https://my.openbb.co/u/test/routine/test.openbb"]
    )
    mock_get.assert_called_with(
        "https://my.openbb.co/u/test/routine/test.openbb?raw=true", timeout=10
    )
