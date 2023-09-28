# IMPORTATION STANDARD

import os

import pandas as pd

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import PreferencesModel, copy_user
from openbb_terminal.stocks.fundamental_analysis import fa_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "openbb_terminal.stocks.fundamental_analysis.fa_controller."
            "FundamentalAnalysisController.switch"
        ),
        return_value=["quit"],
    )
    stock = pd.DataFrame()
    result_menu = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        suffix="",
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
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
        target="openbb_terminal.stocks.fundamental_analysis.fa_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.fa_controller.session.prompt",
        return_value="quit",
    )

    stock = pd.DataFrame()
    result_menu = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        suffix="",
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    # DISABLE AUTO-COMPLETION
    preferences = PreferencesModel(USE_PROMPT_TOOLKIT=True)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.fa_controller.session",
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
        target=(
            "openbb_terminal.stocks.fundamental_analysis.fa_controller."
            "FundamentalAnalysisController.switch"
        ),
        new=mock_switch,
    )

    stock = pd.DataFrame()
    result_menu = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        suffix="",
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    stock = pd.DataFrame()
    controller = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        suffix="",
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
        ("r", ["quit", "quit", "reset", "stocks", "fa"]),
    ],
)
def test_switch(an_input, expected_queue):
    stock = pd.DataFrame()
    controller = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        stock=stock,
        suffix="",
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    stock = pd.DataFrame()
    controller = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        suffix="",
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
            ["quit", "quit", "reset", "stocks", "fa"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "fa", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    stock = pd.DataFrame()
    controller = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        stock=stock,
        suffix="",
        queue=queue,
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_analysis",
            "eclect_us_view.display_analysis",
            ["--export=csv"],
            dict(symbol="TSLA", export="csv", sheet_name=None),
        ),
        (
            "call_mgmt",
            "business_insider_view.display_management",
            ["--export=csv"],
            dict(symbol="TSLA", export="csv", sheet_name=None),
        ),
        (
            "call_overview",
            "finviz_view.display_screen_data",
            ["--source=Finviz", "--export=csv"],
            dict(symbol="TSLA", export="csv", sheet_name=None),
        ),
        (
            "call_score",
            "fmp_view.valinvest_score",
            [],
            {"TSLA"},
        ),
        (
            "call_overview",
            "yahoo_finance_view.display_info",
            ["--source=YahooFinance"],
            {"TSLA"},
        ),
        (
            "call_shrs",
            "yahoo_finance_view.display_shareholders",
            [],
            {"TSLA"},
        ),
        (
            "call_dupont",
            "av_view.display_dupont",
            [],
            {"TSLA"},
        ),
        (
            "call_epsfc",
            "seeking_alpha_view.display_eps_estimates",
            [],
            {"TSLA"},
        ),
        (
            "call_revfc",
            "seeking_alpha_view.display_rev_estimates",
            [],
            {"TSLA"},
        ),
        (
            "call_earnings",
            "yahoo_finance_view.display_earnings",
            ["--source=YahooFinance"],
            {"TSLA"},
        ),
        (
            "call_overview",
            "av_view.display_overview",
            ["--source=AlphaVantage"],
            {"TSLA"},
        ),
        (
            "call_metrics",
            "av_view.display_key",
            ["--source=AlphaVantage"],
            {"TSLA"},
        ),
        (
            "call_metrics",
            "av_view.display_key",
            ["--source=AlphaVantage", "--export=xlsx"],
            dict(symbol="TSLA", export="xlsx", sheet_name=None),
        ),
        (
            "call_income",
            "av_view.display_income_statement",
            ["--source=AlphaVantage", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_income",
            "polygon_view.display_fundamentals",
            ["--source=Polygon", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                statement="income",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_income",
            "fmp_view.display_income_statement",
            ["--source=FinancialModelingPrep", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_income",
            "yahoo_finance_view.display_fundamentals",
            ["--source=YahooFinance", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                statement="financials",
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
                limit=5,
            ),
        ),
        (
            "call_balance",
            "av_view.display_balance_sheet",
            ["--source=AlphaVantage", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_balance",
            "polygon_view.display_fundamentals",
            ["--source=Polygon", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                statement="balance",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_balance",
            "fmp_view.display_balance_sheet",
            ["--source=FinancialModelingPrep", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_balance",
            "yahoo_finance_view.display_fundamentals",
            ["--source=YahooFinance", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                statement="balance-sheet",
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
                limit=5,
            ),
        ),
        (
            "call_cash",
            "av_view.display_cash_flow",
            ["--source=AlphaVantage", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_cash",
            "fmp_view.display_cash_flow",
            ["--source=FinancialModelingPrep", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_cash",
            "polygon_view.display_fundamentals",
            ["--source=Polygon", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                statement="cash",
                limit=5,
                quarterly=False,
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_cash",
            "yahoo_finance_view.display_fundamentals",
            ["--source=YahooFinance", "--export=csv", "--limit=5"],
            dict(
                symbol="TSLA",
                statement="cash-flow",
                ratios=False,
                plot=[],
                export="csv",
                sheet_name=None,
                limit=5,
            ),
        ),
        (
            "call_earnings",
            "av_view.display_earnings",
            ["--limit=5", "--quarter", "--export=csv"],
            dict(symbol="TSLA", limit=5, quarterly=True, export="csv", sheet_name=None),
        ),
        (
            "call_fraud",
            "av_view.display_fraud",
            ["--export=csv"],
            dict(
                symbol="TSLA",
                export="csv",
                sheet_name=None,
                detail=False,
            ),
        ),
        (
            "call_dcf",
            "dcf_view.CreateExcelFA",
            ["--audit"],
            {"TSLA", True},
        ),
        (
            "call_warnings",
            "marketwatch_view.display_sean_seah_warnings",
            ["--debug"],
            {"symbol": "TSLA", "debug": True},
        ),
        (
            "call_rating",
            "finviz_view.analyst",
            ["--source=Finviz"],
            {"symbol": "TSLA", "export": "", "sheet_name": None},
        ),
        (
            "call_rating",
            "finviz_view.analyst",
            ["--source=Finviz", "--export=csv"],
            {"symbol": "TSLA", "export": "csv", "sheet_name": None},
        ),
        (
            "call_rating",
            "finviz_view.analyst",
            ["--source=Finviz", "--export=json"],
            {"symbol": "TSLA", "export": "json", "sheet_name": None},
        ),
        (
            "call_rating",
            "finviz_view.analyst",
            ["--source=Finviz", "--export=xlsx"],
            {"symbol": "TSLA", "export": "xlsx", "sheet_name": None},
        ),
        (
            "call_pt",
            "business_insider_view.display_price_target_from_analysts",
            ["--limit=10"],
            {
                "symbol": "TSLA",
                "data": None,
                "start_date": "10/25/2021",
                "limit": 10,
                "raw": False,
                "export": "",
                "sheet_name": None,
            },
        ),
        (
            "call_est",
            "business_insider_view.display_estimates",
            [],
            {
                "symbol": "TSLA",
                "estimate": "annual_earnings",
                "export": "",
                "sheet_name": None,
            },
        ),
        (
            "call_rot",
            "finnhub_view.rating_over_time",
            ["--limit=10"],
            {
                "symbol": "TSLA",
                "limit": 10,
                "raw": False,
                "export": "",
                "sheet_name": None,
            },
        ),
        (
            "call_rating",
            "fmp_view.rating",
            ["--source=FinancialModelingPrep", "--limit=10"],
            {
                "symbol": "TSLA",
                "limit": 10,
                "export": "",
                "sheet_name": None,
            },
        ),
        (
            "call_sec",
            "nasdaq_view.sec_filings",
            ["--limit=10"],
            {
                "symbol": "TSLA",
                "limit": 10,
                "export": "",
                "sheet_name": None,
                "year": None,
                "form_group": None,
            },
        ),
        (
            "call_supplier",
            "csimarket_view.suppliers",
            [],
            {
                "symbol": "TSLA",
                "export": "",
                "sheet_name": None,
            },
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis." + mocked_func,
        new=mock,
    )
    fa = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=None,
        suffix="",
    )

    getattr(fa, tested_func)(other_args=other_args)

    if isinstance(called_with, dict):
        mock.assert_called_once_with(**called_with)
    elif isinstance(called_with, list):
        mock.assert_called_once_with(*called_with)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_analysis",
        "call_mgmt",
        "call_overview",
        "call_mktcap",
        "call_score",
        "call_shrs",
        "call_growth",
        "call_metrics",
        "call_income",
        "call_balance",
        "call_cash",
        "call_earnings",
        "call_fraud",
        "call_divs",
        "call_dcf",
        "call_dcfc",
        "call_splits",
        "call_warnings",
        "call_ratios",
        "call_dupont",
        "call_epsfc",
        "call_revfc",
        "call_pt",
        "call_est",
        "call_rot",
        "call_rating",
        "call_sec",
        "call_supplier",
        "call_customer",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.fa_controller"
        ".FundamentalAnalysisController.parse_known_args_and_warn",
        return_value=None,
    )
    stock = pd.DataFrame()
    controller = fa_controller.FundamentalAnalysisController(
        ticker="AAPL",
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        suffix="",
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "fa"]),
    ],
)
def test_custom_reset(expected, ticker):
    stock = pd.DataFrame()
    controller = fa_controller.FundamentalAnalysisController(
        ticker=None,
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        suffix="",
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
