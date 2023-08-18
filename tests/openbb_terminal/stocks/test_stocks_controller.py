# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks import stocks_controller
from tests.test_helpers import no_dfs

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

DF_STOCK = pd.DataFrame.from_dict(
    data={
        pd.Timestamp("2020-11-30 00:00:00"): {
            "Open": 75.69999694824219,
            "High": 76.08999633789062,
            "Low": 75.41999816894531,
            "Close": 75.75,
            "Adj Close": 71.90919494628906,
            "Volume": 5539100,
            "date_id": 1,
            "OC_High": 75.75,
            "OC_Low": 75.69999694824219,
        },
        pd.Timestamp("2020-12-01 00:00:00"): {
            "Open": 76.0199966430664,
            "High": 77.12999725341797,
            "Low": 75.69000244140625,
            "Close": 77.02999877929688,
            "Adj Close": 73.1242904663086,
            "Volume": 6791700,
            "date_id": 2,
            "OC_High": 77.02999877929688,
            "OC_Low": 76.0199966430664,
        },
    },
    orient="index",
)
EMPTY_DF = pd.DataFrame()


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.stocks.stocks_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.StocksController.switch",
        return_value=["quit"],
    )
    result_menu = stocks_controller.StocksController(queue=queue).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.stocks.stocks_controller"

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

    result_menu = stocks_controller.StocksController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.stocks.stocks_controller"

    # DISABLE AUTO-COMPLETION
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
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
        target=f"{path_controller}.StocksController.switch",
        new=mock_switch,
    )

    result_menu = stocks_controller.StocksController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = stocks_controller.StocksController(queue=None)
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
                "reset",
                "stocks",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = stocks_controller.StocksController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = stocks_controller.StocksController(queue=None)
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
            ["quit", "quit"],
        ),
        ("call_exit", ["help"], ["quit", "quit", "help"]),
        ("call_home", [], ["quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "reset",
                "stocks",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "reset",
                "stocks",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = stocks_controller.StocksController(queue=queue)
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_search",
            [
                "--query=microsoft",
                "--limit=1",
                "--export=csv",
            ],
            "stocks_helper.search",
            [],
            dict(
                query="microsoft",
                country="",
                sector="",
                industry_group="",
                industry="",
                all_exchanges=False,
                exchange_country="",
                exchange="",
            ),
        ),
        (
            "call_quote",
            [],
            "stocks_view.display_quote",
            [],
            dict(),
        ),
        (
            "call_tob",
            ["--ticker=AAPL"],
            "cboe_view.display_top_of_book",
            [],
            dict(),
        ),
        (
            "call_candle",
            [
                "--plotly",
                "--sort=Open",
                "--reverse",
                "--raw",
                "--limit=1",
                "--trend",
                "--ma=2",
            ],
            "qa_view.display_raw",
            [],
            dict(
                data=EMPTY_DF,
                sortby="Open",
                ascend=False,
                limit=1,
            ),
        ),
        (
            "call_candle",
            [
                "--plotly",
                "--sort=Open",
                "--reverse",
                "--limit=1",
                "--trend",
                "--ma=20,30",
            ],
            "stocks_helper.display_candle",
            [],
            dict(
                symbol="MOCK_TICKER",
                data=EMPTY_DF,
                use_matplotlib=False,
                intraday=False,
                add_trend=True,
                ma=[20, 30],
                yscale="linear",
            ),
        ),
        (
            "call_disc",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_dps",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_scr",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_ins",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_gov",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_options",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_res",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_ca",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_fa",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_bt",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_ta",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_ba",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
        (
            "call_qa",
            [],
            "StocksController.load_class",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.stocks.stocks_controller"

    # MOCK EXPORT_DATA
    mocker.patch(target=f"{path_controller}.export_data")

    # MOCK PROCESS_CANDLE
    mocker.patch(
        target=f"{path_controller}.stocks_helper.process_candle", return_value=EMPTY_DF
    )

    # MOCK TICKER + INFO
    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = stocks_controller.StocksController(queue=None)
        controller.stock = EMPTY_DF
        controller.ticker = "MOCK_TICKER"
        controller.interval = "1440min"

        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs and no_dfs(called_args, called_kwargs):
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = stocks_controller.StocksController(queue=None)
        controller.stock = EMPTY_DF
        controller.ticker = "MOCK_TICKER"
        controller.interval = "1440min"

        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_search",
        "call_candle",
    ],
)
def test_call_func_no_parser(func, mocker):
    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        "openbb_terminal.stocks.stocks_controller.StocksController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = stocks_controller.StocksController(queue=None)

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    ["call_res"],
)
def test_call_func_no_ticker(func, mocker):
    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        "openbb_terminal.stocks.stocks_controller.StocksController.parse_known_args_and_warn",
        return_value=True,
    )

    controller = stocks_controller.StocksController(queue=None)

    func_result = getattr(controller, func)([])
    assert func_result is None
    assert controller.queue == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = stocks_controller.StocksController(queue=None)
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected


@pytest.mark.vcr
def test_call_load(mocker):
    # FORCE SINGLE THREADING
    yf_download = stocks_controller.stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    controller = stocks_controller.StocksController(queue=None)
    other_args = [
        "TSLA",
        "--start=2021-12-17",
        "--end=2021-12-18",
    ]
    controller.call_load(other_args=other_args)
