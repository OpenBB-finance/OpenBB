# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import fa_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

pytest.skip(allow_module_level=True)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.fundamental_analysis.fa_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.fa_controller.session.prompt",
        return_value="quit",
    )

    result_menu = fa_controller.menu(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        suffix="",
    )

    assert result_menu


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_system_exit(mocker):
    class SystemExitSideEffect:
        def __init__(self):
            self.first_call = True

        def __call__(self, *args, **kwargs):
            if self.first_call:
                self.first_call = False
                raise SystemExit()
            return True

    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.fundamental_analysis.fa_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.fa_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.fa_controller.FundamentalAnalysisController.switch",
        new=mock_switch,
    )

    fa_controller.menu(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        suffix="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    dd = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
    )
    dd.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    dd = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
    )
    result = dd.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    dd = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
    )
    result = dd.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    dd = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
    )
    result = dd.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    dd = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
    )
    other_args = list()
    result = dd.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    dd = fa_controller.FundamentalAnalysisController(
        ticker="",
        start="",
        interval="",
        suffix="",
    )
    other_args = list()
    result = dd.call_quit(other_args)

    assert result is True


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
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_balance",
            "av_view.display_balance_sheet",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_cash",
            "av_view.display_cash_flow",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_earnings",
            "av_view.display_earnings",
            ["--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True},
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
        "gamestonk_terminal.stocks.fundamental_analysis." + mocked_func,
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
        "gamestonk_terminal.stocks.fundamental_analysis.fa_controller.parse_known_args_and_warn",
        return_value=None,
    )
    fa = fa_controller.FundamentalAnalysisController(
        ticker="AAPL",
        start="10/25/2021",
        interval="1440min",
        suffix="",
    )

    func_result = getattr(fa, func)(other_args=list())
    assert func_result is None
    getattr(fa_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_key_metrics_explained_no_parser(mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.fa_controller.parse_known_args_and_warn",
        return_value=None,
    )

    fa_controller.key_metrics_explained(other_args=list())
    getattr(fa_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "expected, mock_menu",
    [(None, False), (True, True)],
)
def test_call_fmp(expected, mock_menu, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.menu",
        return_value=mock_menu,
    )

    fa = fa_controller.FundamentalAnalysisController(
        ticker="AAPL",
        start="10/25/2021",
        interval="1440min",
        suffix="",
    )

    mocker.patch.object(fa, "print_help", autospec=True)
    assert fa.call_fmp(list()) is expected
