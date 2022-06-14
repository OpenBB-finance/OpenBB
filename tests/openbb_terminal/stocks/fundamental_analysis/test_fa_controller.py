# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import fa_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["load", "help"], []),
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
    result_menu = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        suffix="",
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
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
        target=fa_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.fa_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.fa_controller.session.prompt",
        return_value="quit",
    )

    result_menu = fa_controller.FundamentalAnalysisController(
        ticker="TSLA", start="10/25/2021", interval="1440min", suffix="", queue=None
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=fa_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
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

    result_menu = fa_controller.FundamentalAnalysisController(
        ticker="TSLA", start="10/25/2021", interval="1440min", suffix="", queue=None
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
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
    controller = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = fa_controller.FundamentalAnalysisController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
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
    controller = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
        queue=queue,
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_analysis",
            "eclect_us_view.display_analysis",
            [],
            {"TSLA"},
        ),
        (
            "call_mgmt",
            "business_insider_view.display_management",
            ["--export=csv"],
            {"ticker": "TSLA", "export": "csv"},
        ),
        (
            "call_data",
            "finviz_view.display_screen_data",
            [],
            {"TSLA"},
        ),
        (
            "call_score",
            "financial_modeling_prep.fmp_view.valinvest_score",
            [],
            {"TSLA"},
        ),
        (
            "call_info",
            "yahoo_finance_view.display_info",
            [],
            {"TSLA"},
        ),
        (
            "call_shrs",
            "yahoo_finance_view.display_shareholders",
            [],
            {"TSLA"},
        ),
        (
            "call_sust",
            "yahoo_finance_view.display_sustainability",
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
            "call_cal",
            "yahoo_finance_view.display_calendar_earnings",
            [],
            {"TSLA"},
        ),
        (
            "call_hq",
            "yahoo_finance_view.open_headquarters_map",
            [],
            {"TSLA"},
        ),
        (
            "call_web",
            "yahoo_finance_view.open_web",
            [],
            {"TSLA"},
        ),
        (
            "call_overview",
            "av_view.display_overview",
            [],
            {"TSLA"},
        ),
        (
            "call_key",
            "av_view.display_key",
            [],
            {"TSLA"},
        ),
        (
            "call_income",
            "av_view.display_income_statement",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "limit": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_balance",
            "av_view.display_balance_sheet",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "limit": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_cash",
            "av_view.display_cash_flow",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "limit": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_earnings",
            "av_view.display_earnings",
            ["--limit=5", "--quarter", "--export=csv"],
            {"ticker": "TSLA", "limit": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_fraud",
            "fa_controller.av_view.display_fraud",
            [],
            {"TSLA"},
        ),
        (
            "call_dcf",
            "dcf_view.CreateExcelFA",
            ["--audit"],
            {"TSLA", True},
        ),
        (
            "call_warnings",
            "market_watch_view.display_sean_seah_warnings",
            ["--debug"],
            {"ticker": "TSLA", "debug": True},
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
        "call_data",
        "call_score",
        "call_info",
        "call_shrs",
        "call_sust",
        "call_cal",
        "call_web",
        "call_hq",
        "call_overview",
        "call_key",
        "call_income",
        "call_balance",
        "call_cash",
        "call_earnings",
        "call_fraud",
        "call_dcf",
        "call_warnings",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.fa_controller"
        ".FundamentalAnalysisController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = fa_controller.FundamentalAnalysisController(
        ticker="AAPL",
        start="10/25/2021",
        interval="1440min",
        suffix="",
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_call_fmp(mocker):
    mocker.patch(
        (
            "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep."
            "fmp_controller.FinancialModelingPrepController.menu"
        ),
        return_value=["quit"],
    )

    controller = fa_controller.FundamentalAnalysisController(
        ticker="AAPL",
        start="10/25/2021",
        interval="1440min",
        suffix="",
    )

    mocker.patch.object(controller, "print_help", autospec=True)
    controller.call_fmp(list())
    assert controller.queue == ["quit"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "fa"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = fa_controller.FundamentalAnalysisController(
        ticker=None,
        start="10/25/2021",
        interval="1440min",
        suffix="",
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
