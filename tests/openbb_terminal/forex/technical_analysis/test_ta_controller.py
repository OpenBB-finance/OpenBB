# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.forex.technical_analysis import ta_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

EMPTY_DF = pd.DataFrame()
MOCK_STOCK_DF = pd.read_csv(
    "tests/openbb_terminal/forex/technical_analysis/csv/test_ta_controller/data_df.csv",
    index_col=0,
)


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
    path_controller = "openbb_terminal.forex.technical_analysis.ta_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.TechnicalAnalysisController.switch",
        return_value=["quit"],
    )

    result_menu = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        source="yf",
        interval="MOCK_INTERVAL",
        data=MOCK_STOCK_DF,
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.forex.technical_analysis.ta_controller"

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

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=ta_controller.obbff,
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

    result_menu = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        source="yf",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        data=MOCK_STOCK_DF,
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.forex.technical_analysis.ta_controller"

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=ta_controller.obbff,
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
        target=f"{path_controller}.TechnicalAnalysisController.switch",
        new=mock_switch,
    )

    result_menu = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        source="yf",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        data=MOCK_STOCK_DF,
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "start",
    [
        datetime.strptime("2021-12-01", "%Y-%m-%d"),
    ],
)
def test_print_help(start):
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        source="yf",
        start=start,
        interval="MOCK_INTERVAL",
        data=MOCK_STOCK_DF,
        queue=None,
    )
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "an_input, expected_queue",
    [
        ("", []),
        (
            "/help",
            [
                "home",
                "help",
            ],
        ),
        ("help/help", ["help", "help"]),
        ("q", ["quit"]),
        ("h", []),
        (
            "r",
            [
                "quit",
                "quit",
                "reset",
                "forex",
                "from MOCK_FROM",
                "to MOCK_TO",
                "load",
                "ta",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_FROM/MOCK_TO",
        source="yf",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        data=MOCK_STOCK_DF,
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER/MOCK_TICKER",
        source="yf",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        data=MOCK_STOCK_DF,
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
                "forex",
                "from MOCK_FROM",
                "to MOCK_TO",
                "load",
                "ta",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "reset",
                "forex",
                "from MOCK_FROM",
                "to MOCK_TO",
                "load",
                "ta",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_FROM/MOCK_TO",
        source="yf",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        interval="MOCK_INTERVAL",
        data=MOCK_STOCK_DF,
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
            "call_ema",
            [
                "1,2",
                "--offset=2",
                "--export=csv",
            ],
            "overlap_view.view_ma",
            [],
            dict(),
        ),
        (
            "call_sma",
            [
                "1,2",
                "--offset=2",
                "--export=csv",
            ],
            "overlap_view.view_ma",
            [],
            dict(),
        ),
        (
            "call_zlma",
            [
                "1,2",
                "--offset=2",
                "--export=csv",
            ],
            "overlap_view.view_ma",
            [],
            dict(),
        ),
        (
            "call_cci",
            [
                "--length=1",
                "--scalar=2",
                "--export=csv",
            ],
            "momentum_view.display_cci",
            [],
            dict(),
        ),
        (
            "call_macd",
            [
                "--fast=1",
                "--slow=2",
                "--signal=3",
                "--export=csv",
            ],
            "momentum_view.display_macd",
            [],
            dict(),
        ),
        (
            "call_rsi",
            [
                "1",
                "--scalar=2",
                "--drift=3",
                "--export=csv",
            ],
            "momentum_view.display_rsi",
            [],
            dict(),
        ),
        (
            "call_stoch",
            [
                "--fastkperiod=1",
                "--slowdperiod=2",
                "--slowkperiod=3",
                "--export=csv",
            ],
            "momentum_view.display_stoch",
            [],
            dict(),
        ),
        (
            "call_fisher",
            [
                "1",
                "--export=csv",
            ],
            "momentum_view.display_fisher",
            [],
            dict(),
        ),
        (
            "call_cg",
            [
                "1",
                "--export=csv",
            ],
            "momentum_view.display_cg",
            [],
            dict(),
        ),
        (
            "call_adx",
            [
                "1",
                "--scalar=2",
                "--drift=3",
                "--export=csv",
            ],
            "trend_indicators_view.display_adx",
            [],
            dict(),
        ),
        (
            "call_aroon",
            [
                "1",
                "--scalar=2",
                "--export=csv",
            ],
            "trend_indicators_view.display_aroon",
            [],
            dict(),
        ),
        (
            "call_bbands",
            [
                "1",
                "--std=2",
                "--mamode=MOCK_MAMODE",
                "--export=csv",
            ],
            "volatility_view.display_bbands",
            [],
            dict(),
        ),
        (
            "call_donchian",
            [
                "--length_upper=1",
                "--length_lower=2",
                "--export=csv",
            ],
            "volatility_view.display_donchian",
            [],
            dict(),
        ),
        (
            "call_fib",
            [
                "1",
                "--start=2021-12-01",
                "--end=2021-12-02",
                "--export=csv",
            ],
            "custom_indicators_view.fibonacci_retracement",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.forex.technical_analysis.ta_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = ta_controller.TechnicalAnalysisController(
            ticker="MOCK_FROM/MOCK_TO",
            source="yf",
            start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
            interval="MOCK_INTERVAL",
            data=MOCK_STOCK_DF,
            queue=None,
        )
        # controller.screen_tickers = ["PM"]
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = ta_controller.TechnicalAnalysisController(
            ticker="MOCK_FROM/MOCK_TO",
            source="yf",
            start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
            interval="MOCK_INTERVAL",
            data=MOCK_STOCK_DF,
            queue=None,
        )
        # controller.screen_tickers = ["PM"]
        getattr(controller, tested_func)(other_args)
