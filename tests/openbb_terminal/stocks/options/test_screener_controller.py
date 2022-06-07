# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options.screen import screener_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

PRICES = pd.DataFrame(data={"Price": [11.0, 12.0], "Chance": [0.2, 0.8]})


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.stocks.options.screen.screener_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ScreenerController.switch",
        return_value=["quit"],
    )
    result_menu = screener_controller.ScreenerController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.stocks.options.screen.screener_controller"

    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="openbb_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session",
    )
    mocker.patch(
        target="openbb_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=screener_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target=f"{path_controller}.session",
    )
    mocker.patch(
        target=f"{path_controller}.session.prompt",
        return_value="quit",
    )

    result_menu = screener_controller.ScreenerController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.stocks.options.screen.screener_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=screener_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target=f"{path_controller}.session",
        return_value=None,
    )

    # MOCK USER INPUT
    mocker.patch("builtins.input", return_value=mock_input)

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
        target=f"{path_controller}.ScreenerController.switch",
        new=mock_switch,
    )

    result_menu = screener_controller.ScreenerController(queue=None).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = screener_controller.ScreenerController(queue=None)
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        ("/help", ["home", "help"]),
        ("help/help", ["help", "help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "options",
                "screen",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = screener_controller.ScreenerController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = screener_controller.ScreenerController(queue=None)
    controller.call_cls([])

    assert controller.queue == []
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func, queue, expected_queue",
    [
        (
            "call_exit",
            [],
            ["quit", "quit", "quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "options",
                "screen",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "options",
                "screen",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = screener_controller.ScreenerController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_view",
            [
                "high_IV",
            ],
            "syncretism_view.view_available_presets",
            [],
            dict(),
        ),
        (
            "call_set",
            [
                "high_IV",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_scr",
            [
                "high_IV",
                "--limit=1",
            ],
            "syncretism_view.view_screener_output",
            [],
            dict(),
        ),
        (
            "call_ca",
            [],
            "ca_controller.ComparisonAnalysisController.menu",
            [],
            dict(),
        ),
        (
            "call_po",
            [],
            "po_controller.PortfolioOptimizationController.menu",
            [],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.stocks.options.screen.screener_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = screener_controller.ScreenerController(queue=None)
        controller.screen_tickers = ["PM"]
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = screener_controller.ScreenerController(queue=None)
        controller.screen_tickers = ["PM"]
        getattr(controller, tested_func)(other_args)
