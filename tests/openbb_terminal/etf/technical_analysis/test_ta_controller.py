# IMPORTATION STANDARD

import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.etf.technical_analysis import ta_controller

# pylint: disable=E1101,W0603,E1111

EMPTY_DF = pd.DataFrame()
MOCK_STOCK_DF = pd.read_csv(
    "tests/openbb_terminal/etf/technical_analysis/csv/test_ta_controller/stock_df.csv",
    index_col=0,
)
print(MOCK_STOCK_DF.columns)  # noqa: T201


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.etf.technical_analysis.ta_controller"

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.TechnicalAnalysisController.switch",
        return_value=["quit"],
    )

    result_menu = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        data=EMPTY_DF,
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.etf.technical_analysis.ta_controller"

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

    # DISABLE AUTO-COMPLETION
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

    result_menu = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        data=EMPTY_DF,
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.etf.technical_analysis.ta_controller"

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
        target=f"{path_controller}.TechnicalAnalysisController.switch",
        new=mock_switch,
    )

    result_menu = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        data=EMPTY_DF,
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "start",
    [
        datetime.strptime("2021-12-01", "%Y-%m-%d"),
        None,
    ],
)
def test_print_help(start):
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=start,
        data=EMPTY_DF,
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
                "etf",
                "load MOCK_TICKER",
                "ta",
            ],
        ),
    ],
)
def test_switch(an_input, expected_queue):
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        data=MOCK_STOCK_DF,
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        data=EMPTY_DF,
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
                "etf",
                "load MOCK_TICKER",
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
                "etf",
                "load MOCK_TICKER",
                "ta",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, queue):
    controller = ta_controller.TechnicalAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        data=EMPTY_DF,
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
            dict(
                ma_type="EMA",
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                window=[1, 2],
                offset=2,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                ma_type="SMA",
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                window=[1, 2],
                offset=2,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_wma",
            [
                "1,2",
                "--offset=2",
                "--export=csv",
            ],
            "overlap_view.view_ma",
            [],
            dict(
                ma_type="WMA",
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                window=[1, 2],
                offset=2,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_hma",
            [
                "1,2",
                "--offset=2",
                "--export=csv",
            ],
            "overlap_view.view_ma",
            [],
            dict(
                ma_type="HMA",
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                window=[1, 2],
                offset=2,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                ma_type="ZLMA",
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                window=[1, 2],
                offset=2,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                window=1,
                scalar=2,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                n_fast=1,
                n_slow=2,
                n_signal=3,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                window=1,
                scalar=2,
                drift=3,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                fastkperiod=1,
                slowdperiod=2,
                slowkperiod=3,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_fisher",
            [
                "1",
                "--export=csv",
            ],
            "momentum_view.display_fisher",
            [],
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                window=1,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_cg",
            [
                "1",
                "--export=csv",
            ],
            "momentum_view.display_cg",
            [],
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF["Adj Close"],
                window=1,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                window=1,
                scalar=2,
                drift=3,
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                window=1,
                scalar=2,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_bbands",
            [
                "1",
                "--std=2",
                "--mamode=ema",
                "--export=csv",
            ],
            "volatility_view.display_bbands",
            [],
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                window=1,
                n_std=2,
                mamode="ema",
                export="csv",
                sheet_name=None,
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                upper_length=1,
                lower_length=2,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_kc",
            [
                "1",
                "--scalar=2",
                "--mamode=sma",
                "--offset=3",
                "--export=csv",
            ],
            "volatility_view.view_kc",
            [],
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                window=1,
                scalar=2,
                mamode="sma",
                offset=3,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_ad",
            [
                "--open",
                "--export=csv",
            ],
            "volume_view.display_ad",
            [],
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                use_open=True,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_adosc",
            [
                "--open",
                "--fast=1",
                "--slow=2",
                "--export=csv",
            ],
            "volume_view.display_adosc",
            [],
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                use_open=True,
                fast=1,
                slow=2,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_obv",
            [
                "--export=csv",
            ],
            "volume_view.display_obv",
            [],
            dict(
                symbol="MOCK_TICKER", data=MOCK_STOCK_DF, export="csv", sheet_name=None
            ),
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
            dict(
                symbol="MOCK_TICKER",
                data=MOCK_STOCK_DF,
                limit=1,
                start_date=datetime.strptime("2021-12-01", "%Y-%m-%d"),
                end_date=datetime.strptime("2021-12-02", "%Y-%m-%d"),
                export="csv",
                sheet_name=None,
            ),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.etf.technical_analysis.ta_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = ta_controller.TechnicalAnalysisController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
            data=MOCK_STOCK_DF,
            queue=None,
        )
        controller.screen_tickers = ["PM"]
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = ta_controller.TechnicalAnalysisController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
            data=EMPTY_DF,
            queue=None,
        )
        controller.screen_tickers = ["PM"]
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["etf", "load MOCK_TICKER", "ta"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = ta_controller.TechnicalAnalysisController(
        ticker=None,
        start=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        data=EMPTY_DF,
        queue=None,
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
