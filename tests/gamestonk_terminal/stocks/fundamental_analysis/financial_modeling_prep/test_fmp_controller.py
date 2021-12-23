# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_controller,
)

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

pytest.skip(allow_module_level=True)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.session"
    )
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.session.prompt",
        return_value="quit",
    )

    result_menu = fmp_controller.menu(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
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

    financial_modeling_prep = (
        "gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep"
    )
    mock_switch = mocker.Mock(side_effect=SystemExitSideEffect())
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch(financial_modeling_prep + ".fmp_controller.session")
    mocker.patch(
        financial_modeling_prep + ".fmp_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        financial_modeling_prep
        + ".fmp_controller.FinancialModelingPrepController.switch",
        new=mock_switch,
    )

    fmp_controller.menu(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    fmp = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
    )
    fmp.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    fmp = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
    )
    result = fmp.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    fmp = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
    )
    result = fmp.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    fmp = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
    )
    result = fmp.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    fmp = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
    )
    other_args = list()
    result = fmp.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    fmp = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
    )
    other_args = list()
    result = fmp.call_quit(other_args)

    assert result is True


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_profile",
            "fmp_view.display_profile",
            [],
            {"TSLA"},
        ),
        (
            "call_quote",
            "fmp_view.display_quote",
            [],
            {"TSLA"},
        ),
        (
            "call_enterprise",
            "fmp_view.display_enterprise",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_dcf",
            "fmp_view.display_discounted_cash_flow",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_income",
            "fmp_view.display_income_statement",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_balance",
            "fmp_view.display_balance_sheet",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_cash",
            "fmp_view.display_cash_flow",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_metrics",
            "fmp_view.display_key_metrics",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_ratios",
            "fmp_view.display_financial_ratios",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_growth",
            "fmp_view.display_financial_statement_growth",
            ["--export=csv", "--num=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep."
        + mocked_func,
        new=mock,
    )
    fa = fmp_controller.FinancialModelingPrepController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
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
        "call_profile",
        "call_quote",
        "call_enterprise",
        "call_dcf",
        "call_income",
        "call_balance",
        "call_cash",
        "call_metrics",
        "call_ratios",
        "call_growth",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.parse_known_args_and_warn",
        return_value=None,
    )
    fa = fmp_controller.FinancialModelingPrepController(
        ticker="AAPL",
        start="10/25/2021",
        interval="1440min",
    )

    func_result = getattr(fa, func)(other_args=list())
    assert func_result is None
    getattr(fmp_controller, "parse_known_args_and_warn").assert_called_once()
