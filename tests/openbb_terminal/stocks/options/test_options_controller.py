# IMPORTATION STANDARD
import os
from collections import namedtuple

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.options import options_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111
# pylint: disable=C0302

EXPIRY_DATES = [
    "2022-01-07",
    "2022-01-14",
    "2022-01-21",
    "2022-01-28",
    "2022-02-04",
    "2022-02-18",
    "2022-03-18",
    "2022-04-14",
    "2022-05-20",
    "2022-06-17",
    "2022-07-15",
    "2022-09-16",
    "2023-01-20",
    "2023-03-17",
    "2023-06-16",
    "2023-09-15",
    "2024-01-19",
]

CALLS = pd.DataFrame(
    data={
        "contractSymbol": ["TSLA211231C00200000", "TSLA211231C00250000"],
        "lastTradeDate": [
            pd.Timestamp("2021-12-29 15:01:33"),
            pd.Timestamp("2021-12-10 15:09:36"),
        ],
        "strike": [200.0, 250.0],
        "lastPrice": [878.02, 744.2],
        "bid": [884.5, 834.5],
        "ask": [887.0, 837.0],
        "change": [-11.849976, 0.0],
        "percentChange": [-1.3316524, 0.0],
        "volume": [30.0, 11.0],
        "openInterest": [36, 12],
        "impliedVolatility": [9.46875408203125, 8.238286101074216],
        "inTheMoney": [True, True],
        "contractSize": ["REGULAR", "REGULAR"],
        "currency": ["USD", "USD"],
    }
)

PUTS = pd.DataFrame(
    {
        "contractSymbol": ["TSLA211231P00200000", "TSLA211231P00250000"],
        "lastTradeDate": [
            pd.Timestamp("2021-12-29 20:42:48"),
            pd.Timestamp("2021-12-29 17:42:53"),
        ],
        "strike": [200.0, 250.0],
        "lastPrice": [0.01, 0.01],
        "bid": [0.0, 0.0],
        "ask": [0.01, 0.01],
        "change": [0.0, 0.0],
        "percentChange": [0.0, 0.0],
        "volume": [22.0, 1.0],
        "openInterest": [1892, 513],
        "impliedVolatility": [6.125002343749999, 5.375003281249999],
        "inTheMoney": [False, False],
        "contractSize": ["REGULAR", "REGULAR"],
        "currency": ["USD", "USD"],
    }
)

Options = namedtuple("Options", ["calls", "puts"])
CHAIN = Options(calls=CALLS, puts=PUTS)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    path_controller = "openbb_terminal.stocks.options.options_controller"

    # MOCK OPTION_EXPIRATIONS + CHAIN
    mocker.patch(
        target=f"{path_controller}.yfinance_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.tradier_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_option_chain",
        return_value=CHAIN,
    )

    # MOCK SWITCH
    mocker.patch(
        target=f"{path_controller}.OptionsController.switch",
        return_value=["quit"],
    )
    result_menu = options_controller.OptionsController(
        ticker="TSLA",
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    path_controller = "openbb_terminal.stocks.options.options_controller"

    # MOCK OPTION_EXPIRATIONS + CHAIN
    mocker.patch(
        target=f"{path_controller}.yfinance_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.tradier_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_option_chain",
        return_value=CHAIN,
    )

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
        target=options_controller.obbff,
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

    controller = options_controller.OptionsController(ticker="MOCK_TICKER")
    controller.call_exp(other_args=["--date=2022-01-07"])
    mocker.patch(
        target=f"{path_controller}.OptionsController",
        return_value=controller,
    )
    result_menu = options_controller.OptionsController(
        ticker="MOCK_TICKER",
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    path_controller = "openbb_terminal.stocks.options.options_controller"

    # MOCK OPTION_EXPIRATIONS + CHAIN
    mocker.patch(
        target=f"{path_controller}.yfinance_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.tradier_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_option_chain",
        return_value=CHAIN,
    )

    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=options_controller.obbff,
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
        target=f"{path_controller}.OptionsController.switch",
        new=mock_switch,
    )

    result_menu = options_controller.OptionsController(
        ticker="MOCK_TICKER",
        queue=None,
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = options_controller.OptionsController(
        ticker="",
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
        ("r", ["quit", "quit", "reset", "stocks", "options"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = options_controller.OptionsController(
        ticker="",
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = options_controller.OptionsController(
        ticker="",
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
            [
                "quit",
                "quit",
                "quit",
            ],
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
                "options",
                "exp -d 2022-01-07",
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
                "options",
                "exp -d 2022-01-07",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, func, mocker, queue):
    path_controller = "openbb_terminal.stocks.options.options_controller"

    # MOCK OPTION_EXPIRATIONS + CHAIN
    mocker.patch(
        target=f"{path_controller}.yfinance_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.tradier_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_option_chain",
        return_value=CHAIN,
    )

    controller = options_controller.OptionsController(
        ticker="MOCK_TICKER",
        queue=queue,
    )
    controller.call_exp(other_args=["--date=2022-01-07"])
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


# @pytest.mark.skip
@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_calc",
            [
                "--put",
                "--sell",
                "--strike=1",
                "--premium=2",
                "--min=3",
                "--max=4",
            ],
            "calculator_view.view_calculator",
            [],
            dict(
                strike=1.0,
                premium=2.0,
                put=True,
                sell=True,
                x_min=3.0,
                x_max=4.0,
            ),
        ),
        (
            "call_calc",
            [
                "--put",
                "--sell",
                "--strike=1",
                "--premium=2",
            ],
            "calculator_view.view_calculator",
            [],
            dict(
                strike=1.0,
                premium=2.0,
                put=True,
                sell=True,
            ),
        ),
        (
            "call_unu",
            [
                "1",
                "--sortby=Vol",
                "--ascending",
                "--puts_only",
                "--calls_only",
                "--export=csv",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_unu",
            [
                "1",
                "--sortby=Vol",
                "--ascending",
                "--puts_only",
                # "--calls_only",
                "--export=csv",
            ],
            "fdscanner_view.display_options",
            [],
            dict(
                num=1,
                sort_column=["Vol"],
                export="csv",
                ascending=True,
                calls_only=False,
                puts_only=True,
            ),
        ),
        (
            "call_pcr",
            ["10", "--start=2021-12-01", "--export=csv"],
            "alphaquery_view.display_put_call_ratio",
            [],
            dict(
                ticker="MOCK_TICKER",
                window="10",
                start_date="2021-12-01",
                export="csv",
            ),
        ),
        (
            "call_info",
            ["--export=csv"],
            "barchart_view.print_options_data",
            [],
            dict(
                ticker="MOCK_TICKER",
                export="csv",
            ),
        ),
        (
            # PUT
            "call_grhist",
            [
                "200",
                "--put",
                "--greek=theta",
                "--chain=MOCK_CHAIN_ID",
                "--raw",
                "--limit=2",
                "--export=csv",
            ],
            "syncretism_view.view_historical_greeks",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                strike=200.0,
                greek="theta",
                chain_id="MOCK_CHAIN_ID",
                put=True,
                raw=True,
                n_show="2",
                export="csv",
            ),
        ),
        (
            # CALL
            "call_grhist",
            [
                "200",
                # "--put",
                "--greek=theta",
                "--chain=MOCK_CHAIN_ID",
                "--raw",
                "--limit=2",
                "--export=csv",
            ],
            "syncretism_view.view_historical_greeks",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                strike=200.0,
                greek="theta",
                chain_id="MOCK_CHAIN_ID",
                put=False,
                raw=True,
                n_show="2",
                export="csv",
            ),
        ),
        (
            # DISPLAYS : "No correct strike input\n"
            "call_grhist",
            [
                "1",
                # "--put",
                "--greek=theta",
                "--chain=MOCK_CHAIN_ID",
                "--raw",
                "--limit=2",
                "--export=csv",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_load",
            ["MOCK_TICKER"],
            "",
            [],
            dict(),
        ),
        (
            # CHART EXCHANGE
            "call_hist",
            [
                "200",
                "--put",
                "--chain=MOCK_CHAIN_ID",
                "--raw",
                "--source=ce",
                "--limit=2",
                "--export=csv",
            ],
            "chartexchange_view.display_raw",
            [
                "MOCK_TICKER",
                "2022-01-07",
                False,
                200.0,
                2,
                "csv",
            ],
            dict(),
        ),
        (
            # TRADIER
            "call_hist",
            [
                "200",
                "--put",
                "--chain=MOCK_CHAIN_ID",
                "--raw",
                "--source=td",
                "--limit=2",
                "--export=csv",
            ],
            "tradier_view.display_historical",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                strike=200.0,
                put=True,
                export="csv",
                raw=True,
                chain_id="MOCK_CHAIN_ID",
            ),
        ),
        (
            # DISPLAYS : "No correct strike input\n"
            "call_hist",
            [
                "1",
                "--put",
                "--chain=MOCK_CHAIN_ID",
                "--raw",
                "--source=ce",
                "--limit=2",
                "--export=csv",
            ],
            "",
            [],
            dict(),
        ),
        (
            "call_chains",
            [
                "--calls",
                "--puts",
                "--min=1",
                "--max=2",
                "--display=volume",
                "--export=csv",
            ],
            "tradier_view.display_chains",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                to_display=["volume"],
                min_sp=1.0,
                max_sp=2.0,
                calls_only=True,
                puts_only=True,
                export="csv",
            ),
        ),
        (
            # SOURCE: YFINANCE
            "call_vol",
            [
                "--min=1",
                "--max=2",
                "--calls",
                "--puts",
                "--source=yf",
                "--export=csv",
            ],
            "yfinance_view.plot_vol",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                min_sp=1.0,
                max_sp=2.0,
                calls_only=True,
                puts_only=True,
                export="csv",
            ),
        ),
        (
            # SOURCE: TRADIER
            "call_vol",
            [
                "--min=1",
                "--max=2",
                "--calls",
                "--puts",
                "--source=tr",
                "--export=csv",
            ],
            "tradier_view.plot_vol",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                min_sp=1.0,
                max_sp=2.0,
                calls_only=True,
                puts_only=True,
                export="csv",
            ),
        ),
        (
            # SOURCE: YFINANCE
            "call_voi",
            [
                "--minv=1",
                "--min=2",
                "--max=3",
                "--source=yf",
                "--export=csv",
            ],
            "yfinance_view.plot_volume_open_interest",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                min_sp=2.0,
                max_sp=3.0,
                min_vol=1.0,
                export="csv",
            ),
        ),
        (
            # SOURCE: TRADIER
            "call_voi",
            [
                "--minv=1",
                "--min=2",
                "--max=3",
                "--source=tr",
                "--export=csv",
            ],
            "tradier_view.plot_volume_open_interest",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                min_sp=2.0,
                max_sp=3.0,
                min_vol=1.0,
                export="csv",
            ),
        ),
        (
            # SOURCE: YFINANCE
            "call_oi",
            [
                "--min=1",
                "--max=2",
                "--calls",
                "--puts",
                "--source=yf",
                "--export=csv",
            ],
            "yfinance_view.plot_oi",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                min_sp=1.0,
                max_sp=2.0,
                calls_only=True,
                puts_only=True,
                export="csv",
            ),
        ),
        (
            # SOURCE: TRADIER
            "call_oi",
            [
                "--min=1",
                "--max=2",
                "--calls",
                "--puts",
                "--source=tr",
                "--export=csv",
            ],
            "tradier_view.plot_oi",
            [],
            dict(
                ticker="MOCK_TICKER",
                expiry="2022-01-07",
                min_sp=1.0,
                max_sp=2.0,
                calls_only=True,
                puts_only=True,
                export="csv",
            ),
        ),
        (
            "call_plot",
            [
                "--put",
                "--x_axis=c",
                "--y_axis=v",
                "--custom=smile",
                "--export=jpg",
            ],
            "yfinance_view.plot_plot",
            [
                "MOCK_TICKER",
                "2022-01-07",
                True,
                "c",
                "v",
                "smile",
                "jpg",
            ],
            dict(),
        ),
        (
            "call_parity",
            [
                "--put",
                "--ask",
                "--min=1",
                "--max=2",
                "--export=csv",
            ],
            "yfinance_view.show_parity",
            [
                "MOCK_TICKER",
                "2022-01-07",
                True,
                True,
                1,
                2,
                "csv",
            ],
            dict(),
        ),
        (
            "call_binom",
            [
                "1",
                "--put",
                "--european",
                "--xlsx",
                "--plot",
                "--volatility=2",
                "--export=csv",
            ],
            "yfinance_view.show_binom",
            [
                "MOCK_TICKER",
                "2022-01-07",
                1.0,
                True,
                True,
                True,
                True,
                2.0,
            ],
            dict(),
        ),
        (
            "call_payoff",
            [],
            "payoff_controller.PayoffController",
            [
                "MOCK_TICKER",
                "2022-01-07",
                [],
            ],
            dict(),
        ),
        (
            "call_pricing",
            [],
            "pricing_controller.PricingController",
            [],
            dict(),
        ),
        (
            "call_screen",
            [],
            "screener_controller.ScreenerController",
            [],
            dict(),
        ),
    ],
)
def test_call_func_test(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.stocks.options.options_controller"

    # MOCK TRADIER_TOKEN
    mocker.patch.object(
        target=options_controller,
        attribute="TRADIER_TOKEN",
        new="MOCK_TRADIER_TOKEN",
    )

    # MOCK OPTION_EXPIRATIONS + CHAIN
    mocker.patch(
        target=f"{path_controller}.yfinance_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.tradier_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_option_chain",
        return_value=CHAIN,
    )

    if mocked_func:
        mock = mocker.MagicMock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = options_controller.OptionsController(ticker="MOCK_TICKER")
        controller.call_exp(["--date=2022-01-07"])
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = options_controller.OptionsController(ticker="MOCK_TICKER")
        controller.call_exp(["--date=2022-01-07"])
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_info",
        "call_pcr",
        "call_exp",
        "call_vol",
        "call_voi",
        "call_oi",
        "call_hist",
        "call_chains",
        "call_grhist",
        "call_plot",
        "call_parity",
        "call_binom",
        "call_payoff",
        "call_pricing",
    ],
)
def test_call_func_no_ticker(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.options.options_controller.parse_known_args_and_warn",
        return_value=True,
    )
    controller = options_controller.OptionsController(ticker=None)

    func_result = getattr(controller, func)(list())
    assert func_result is None
    assert controller.queue == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_grhist",
        "call_hist",
        "call_chains",
        "call_voi",
        "call_oi",
        "call_vol",
        "call_plot",
        "call_parity",
        "call_binom",
        "call_payoff",
        "call_pricing",
    ],
)
def test_call_func_no_selected_date(func, mocker):
    path_controller = "openbb_terminal.stocks.options.options_controller"

    # MOCK OPTION_EXPIRATIONS + CHAIN
    mocker.patch(
        target=f"{path_controller}.yfinance_model.option_expirations",
        return_value=[],
    )
    mocker.patch(
        target=f"{path_controller}.tradier_model.option_expirations",
        return_value=[],
    )
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_option_chain",
        return_value=None,
    )

    # MOCK PARSE_KNOWN_ARGS_AND_WARN
    mocker.patch(
        "openbb_terminal.stocks.options.options_controller.parse_known_args_and_warn",
        return_value=True,
    )

    controller = options_controller.OptionsController(ticker="MOCK_TICKER")

    func_result = getattr(controller, func)(list())
    assert func_result is None
    assert controller.selected_date == ""


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "other_args",
    [
        ["TSLA"],
        ["TSLA", "--source=yf"],
    ],
)
def test_call_load(mocker, other_args):
    path_controller = "openbb_terminal.stocks.options.options_controller"

    # MOCK OPTION_EXPIRATIONS + CHAIN
    mocker.patch(
        target=f"{path_controller}.yfinance_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.tradier_model.option_expirations",
        return_value=EXPIRY_DATES,
    )
    mocker.patch(
        target=f"{path_controller}.yfinance_model.get_option_chain",
        return_value=CHAIN,
    )

    controller = options_controller.OptionsController(ticker=None)
    old_expiry_dates = controller.expiry_dates
    controller.call_load(other_args=other_args)
    assert old_expiry_dates != controller.expiry_dates


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "options"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = options_controller.OptionsController(ticker=None)
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
