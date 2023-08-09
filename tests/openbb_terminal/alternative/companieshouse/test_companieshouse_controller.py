"""Test the companieshouse controller."""
import os

import pytest

from openbb_terminal.alternative.companieshouse import companieshouse_controller
from openbb_terminal.core.session.current_user import PreferencesModel, copy_user


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = companieshouse_controller.CompaniesHouseController(queue=None)
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session",
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        target="openbb_terminal.alternative.companieshouse.companieshouse_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.alternative.companieshouse.companieshouse_controller.session.prompt",
        return_value="quit",
    )

    result_menu = companieshouse_controller.CompaniesHouseController().menu()

    assert result_menu == ["help"]


@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = (
        "openbb_terminal.alternative.companieshouse.companieshouse_controller"
    )

    # DISABLE AUTO-COMPLETION
    preferences = PreferencesModel(
        USE_PROMPT_TOOLKIT=False,
    )
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch(
        target=f"{path_controller}.session",
        return_value=None,
    )

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value=mock_input)

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.CompaniesHouseController.switch",
        return_value=["quit"],
    )

    # MOCK SWITCH
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return ["quit"]

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())

    mocker.patch(
        target=f"{path_controller}.CompaniesHouseController.switch",
        new=mock_switch,
    )

    result_menu = companieshouse_controller.CompaniesHouseController().menu()

    assert result_menu == ["help"]


@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["home", "help"]),
        ("help/help", ["help", "help"]),
        ("q", ["quit"]),
        ("h", []),
        ("home", ["quit", "quit"]),
        (
            "r",
            ["quit", "quit", "reset", "alternative", "companieshouse"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = companieshouse_controller.CompaniesHouseController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = companieshouse_controller.CompaniesHouseController(queue=None)
    controller.call_cls([])

    assert controller.queue == []

    os.system.assert_called_once_with("cls||clear")


@pytest.mark.parametrize(
    "func, queue, expected_queue",
    [
        (
            "call_exit",
            [],
            ["quit", "quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            ["quit", "quit", "reset", "alternative", "companieshouse"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "alternative", "companieshouse", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = companieshouse_controller.CompaniesHouseController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_quit():
    controller = companieshouse_controller.CompaniesHouseController(queue=None)
    controller.call_quit([])
    assert controller.queue == ["quit"]
