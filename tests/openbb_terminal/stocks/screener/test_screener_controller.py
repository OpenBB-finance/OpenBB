# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.screener import screener_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.stocks.screener.screener_controller"

    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
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

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch(
        target=f"{path_controller}.session",
    )
    mocker.patch(
        target=f"{path_controller}.session.prompt",
        return_value="quit",
    )

    result_menu = screener_controller.ScreenerController(queue=None).menu()

    assert result_menu == ["help"]


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
                "reset",
                "stocks",
                "scr",
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
            [
                "quit",
                "quit",
                "reset",
                "stocks",
                "scr",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "reset",
                "stocks",
                "scr",
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
                "oversold.ini",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_view",
            [],
            "",
            [],
            dict(),
        ),
        (
            "call_set",
            [
                "oversold.ini",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_set",
            [
                "short_squeeze_scan.ini",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_overview",
            [
                "1",
                "--reverse",
                "--sort=Ticker",
                "--export=csv",
            ],
            "finviz_view.screener",
            [],
            dict(
                loaded_preset="top_gainers",
                data_type="overview",
                limit=1,
                ascend=True,
                sortby="Ticker",
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_valuation",
            [
                "1",
                "--preset=top_gainers",
                "--reverse",
                "--sort=Ticker",
                "--export=csv",
            ],
            "finviz_view.screener",
            [],
            dict(
                loaded_preset="top_gainers",
                data_type="valuation",
                limit=1,
                ascend=True,
                sortby="Ticker",
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_financial",
            [
                "1",
                "--preset=top_gainers",
                "--reverse",
                "--sort=Ticker",
                "--export=csv",
            ],
            "finviz_view.screener",
            [],
            dict(
                loaded_preset="top_gainers",
                data_type="financial",
                limit=1,
                ascend=True,
                sortby="Ticker",
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_ownership",
            [
                "1",
                "--preset=top_gainers",
                "--reverse",
                "--sort=Ticker",
                "--export=csv",
            ],
            "finviz_view.screener",
            [],
            dict(
                loaded_preset="top_gainers",
                data_type="ownership",
                limit=1,
                ascend=True,
                sortby="Ticker",
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_performance",
            [
                "1",
                "--preset=top_gainers",
                "--reverse",
                "--sort=Ticker",
                "--export=csv",
            ],
            "finviz_view.screener",
            [],
            dict(
                loaded_preset="top_gainers",
                data_type="performance",
                limit=1,
                ascend=True,
                sortby="Ticker",
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_technical",
            [
                "1",
                "--preset=top_gainers",
                "--reverse",
                "--sort=Ticker",
                "--export=csv",
            ],
            "finviz_view.screener",
            [],
            dict(
                loaded_preset="top_gainers",
                data_type="technical",
                limit=1,
                ascend=True,
                sortby="Ticker",
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_ca",
            [],
            "ca_controller.ComparisonAnalysisController.menu",
            [],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.stocks.screener.screener_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = screener_controller.ScreenerController(queue=None)
        controller.screen_tickers = ["MOCK_TICKER_1", "MOCK_TICKER_2"]
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = screener_controller.ScreenerController(queue=None)
        controller.screen_tickers = ["MOCK_TICKER_1", "MOCK_TICKER_2"]
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_ca",
    ],
)
def test_call_func_no_ticker(func):
    controller = screener_controller.ScreenerController(queue=None)

    func_result = getattr(controller, func)(list())
    assert func_result is None
