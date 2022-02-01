# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.research import res_controller

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
    path_controller = "gamestonk_terminal.stocks.research.res_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.ResearchController.switch",
        return_value=["quit"],
    )
    result_menu = res_controller.ResearchController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "gamestonk_terminal.stocks.research.res_controller"

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
        target=res_controller.gtff,
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

    result_menu = res_controller.ResearchController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "gamestonk_terminal.stocks.research.res_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=res_controller.gtff,
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
        target=f"{path_controller}.ResearchController.switch",
        new=mock_switch,
    )

    result_menu = res_controller.ResearchController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = res_controller.ResearchController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=None,
    )
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
                "load MOCK_TICKER",
                "res",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = res_controller.ResearchController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")

    controller = res_controller.ResearchController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=None,
    )
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
                "load MOCK_TICKER",
                "res",
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
                "load MOCK_TICKER",
                "res",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = res_controller.ResearchController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=queue,
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_macroaxis",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_yahoo",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_finviz",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_marketwatch",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_fool",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_businessinsider",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_fmp",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_fidelity",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_tradingview",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_marketchameleon",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_stockrow",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_barchart",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_grufity",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_fintel",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_zacks",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_macrotrends",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_newsfilter",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
        (
            "call_stockanalysis",
            [],
            "webbrowser.open",
            [],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "gamestonk_terminal.stocks.research.res_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = res_controller.ResearchController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
            interval="MOCK_INTERVAL",
            queue=None,
        )
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = res_controller.ResearchController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
            interval="MOCK_INTERVAL",
            queue=None,
        )
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "res"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = res_controller.ResearchController(
        ticker=None,
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        queue=None,
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
