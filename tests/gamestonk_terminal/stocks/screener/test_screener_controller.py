# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.screener import screener_controller

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
    path_controller = "gamestonk_terminal.stocks.screener.screener_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ScreenerController.switch",
        return_value=["quit"],
    )
    result_menu = screener_controller.ScreenerController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.stocks.screener.screener_controller"

    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="gamestonk_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session",
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=screener_controller.gtff,
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
    path_controller = "gamestonk_terminal.stocks.screener.screener_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=screener_controller.gtff,
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
                "oversold",
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
                "oversold",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_historical",
            [
                "1",
                "--no-scale",
                "--start=2022-01-03",
                "--type=o",
                "--export=csv",
            ],
            "yahoofinance_view.historical",
            [
                "top_gainers",
                1,
                datetime.strptime("2022-01-03", "%Y-%m-%d"),
                "o",
                True,
                "csv",
            ],
            dict(),
        ),
        (
            "call_overview",
            [
                "1",
                "--ascend",
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
                sort="Ticker",
                export="csv",
            ),
        ),
        (
            "call_valuation",
            [
                "1",
                "--preset=top_gainers",
                "--ascend",
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
                sort="Ticker",
                export="csv",
            ),
        ),
        (
            "call_financial",
            [
                "1",
                "--preset=top_gainers",
                "--ascend",
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
                sort="Ticker",
                export="csv",
            ),
        ),
        (
            "call_ownership",
            [
                "1",
                "--preset=top_gainers",
                "--ascend",
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
                sort="Ticker",
                export="csv",
            ),
        ),
        (
            "call_performance",
            [
                "1",
                "--preset=top_gainers",
                "--ascend",
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
                sort="Ticker",
                export="csv",
            ),
        ),
        (
            "call_technical",
            [
                "1",
                "--preset=top_gainers",
                "--ascend",
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
                sort="Ticker",
                export="csv",
            ),
        ),
        (
            "call_po",
            [],
            "po_controller.PortfolioOptimization.menu",
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
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.stocks.screener.screener_controller"

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
        "call_po",
        "call_ca",
    ],
)
def test_call_func_no_ticker(func):
    controller = screener_controller.ScreenerController(queue=None)

    func_result = getattr(controller, func)(list())
    assert func_result is None
