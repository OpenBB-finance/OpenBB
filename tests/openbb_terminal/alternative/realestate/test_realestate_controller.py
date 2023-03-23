"""Test the realestate controller."""
import os

import pytest

from openbb_terminal.alternative.realestate import realestate_controller
from openbb_terminal.core.session.current_user import PreferencesModel, copy_user


@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.alternative.realestate.realestate_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.RealEstateController.switch",
        return_value=["quit"],
    )

    result_menu = realestate_controller.RealEstateController(queue=queue).menu()

    assert result_menu == expected


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
        target="openbb_terminal.alternative.realestate.realestate_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.alternative.realestate.realestate_controller.session.prompt",
        return_value="quit",
    )

    result_menu = realestate_controller.RealEstateController().menu()

    assert result_menu == ["help"]


@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.alternative.realestate.realestate_controller"

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
        target=f"{path_controller}.RealEstateController.switch",
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
        target=f"{path_controller}.RealEstateController.switch",
        new=mock_switch,
    )

    result_menu = realestate_controller.RealEstateController().menu()

    assert result_menu == ["help"]


@pytest.mark.record_verify_screen
def test_print_help():
    controller = realestate_controller.RealEstateController(queue=None)
    controller.print_help()


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
            ["quit", "quit", "reset", "alternative", "realestate"],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = realestate_controller.RealEstateController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.record_verify_screen
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = realestate_controller.RealEstateController(queue=None)
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
            ["quit", "quit", "reset", "alternative", "realestate"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "alternative", "realestate", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = realestate_controller.RealEstateController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.record_verify_screen
def test_quit():
    controller = realestate_controller.RealEstateController(queue=None)
    controller.call_quit([])
    assert controller.queue == ["quit"]


def test_call_sales():
    controller = realestate_controller.RealEstateController(queue=None)
    table = controller.call_sales([])

    assert controller.queue == []
    assert table is None


def test_call_townsales():
    controller = realestate_controller.RealEstateController(queue=None)
    table = controller.call_townsales([])

    assert controller.queue == []
    assert table is None


def test_call_regionstats():
    controller = realestate_controller.RealEstateController(queue=None)
    table = controller.call_regionstats([])

    assert controller.queue == []
    assert table is None
