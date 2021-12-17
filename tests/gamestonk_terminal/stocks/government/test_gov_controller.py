# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.government import gov_controller

# pylint: disable=E1101
# pylint: disable=W0603

pytest.skip(allow_module_level=True)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.government.gov_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.government.gov_controller.session.prompt",
        return_value="quit",
    )

    result_menu = gov_controller.menu(ticker="TSLA")

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
    mocker.patch("gamestonk_terminal.stocks.government.gov_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.government.gov_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.government.gov_controller.GovController.switch",
        new=mock_switch,
    )

    gov_controller.menu(ticker="TSLA")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    dd = gov_controller.GovController(ticker="")
    dd.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    dd = gov_controller.GovController(ticker="")
    result = dd.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    dd = gov_controller.GovController(ticker="")
    result = dd.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    dd = gov_controller.GovController(ticker="")
    result = dd.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    dd = gov_controller.GovController(ticker="")
    other_args = list()
    result = dd.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    dd = gov_controller.GovController(ticker="")
    other_args = list()
    result = dd.call_quit(other_args)

    assert result is True


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_contracts",
            "quiverquant_view.display_contracts",
            ["--past_transaction_days=5", "--raw"],
            dict(
                ticker="MOCK_TICKER",
                past_transaction_days=5,
                raw=True,
            ),
        ),
        (
            "call_gtrades",
            "quiverquant_view.display_government_trading",
            ["--past_transactions_months=5", "--govtype=congress", "--raw"],
            dict(
                ticker="MOCK_TICKER",
                gov_type="congress",
                past_transactions_months=5,
                raw=True,
            ),
        ),
        (
            "call_histcont",
            "quiverquant_view.display_hist_contracts",
            ["--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                export="csv",
            ),
        ),
        (
            "call_lastcontracts",
            "quiverquant_view.display_last_contracts",
            ["--past_transaction_days=2", "--num=5", "--sum", "--export=csv"],
            dict(
                past_transaction_days=2,
                num=5,
                sum_contracts=True,
                export="csv",
            ),
        ),
        (
            "call_lasttrades",
            "quiverquant_view.display_last_government",
            [
                "--govtype=congress",
                "--past_transactions_days=5",
                "--representative=MOCK_TEXT",
                "--export=csv",
            ],
            dict(
                gov_type="congress",
                past_days=5,
                representative="MOCK_TEXT",
                export="csv",
            ),
        ),
        (
            "call_lobbying",
            "quiverquant_view.display_lobbying",
            ["--num=5"],
            dict(
                ticker="MOCK_TICKER",
                num=5,
            ),
        ),
        (
            "call_qtrcontracts",
            "quiverquant_view.display_qtr_contracts",
            ["--num=5", "--analysis=total"],
            dict(
                analysis="total",
                num=5,
            ),
        ),
        (
            "call_topbuys",
            "quiverquant_view.display_government_buys",
            [
                "--govtype=congress",
                "--past_transactions_months=2",
                "--num=5",
                "--raw",
                "--export=csv",
            ],
            dict(
                gov_type="congress",
                past_transactions_months=2,
                num=5,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_toplobbying",
            "quiverquant_view.display_top_lobbying",
            ["--num=5", "--raw", "--export=csv"],
            dict(
                num=5,
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_topsells",
            "quiverquant_view.display_government_sells",
            [
                "--govtype=congress",
                "--past_transactions_months=2",
                "--num=5",
                "--raw",
                "--export=csv",
            ],
            dict(
                gov_type="congress",
                past_transactions_months=2,
                num=5,
                raw=True,
                export="csv",
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.government." + mocked_func,
        new=mock,
    )
    controller = gov_controller.GovController(ticker="MOCK_TICKER")
    getattr(controller, tested_func)(other_args=other_args)

    if isinstance(called_with, dict):
        mock.assert_called_once_with(**called_with)
    elif isinstance(called_with, list):
        mock.assert_called_once_with(**called_with)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_load",
        "call_contracts",
        "call_gtrades",
        "call_histcont",
        "call_lastcontracts",
        "call_lasttrades",
        "call_lobbying",
        "call_qtrcontracts",
        "call_topbuys",
        "call_toplobbying",
        "call_topsells",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.government.gov_controller.parse_known_args_and_warn",
        return_value=None,
    )
    controller = gov_controller.GovController(ticker="AAPL")

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    getattr(gov_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_move="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "expected, ticker",
    [(True, "MOCK_TYPE"), (False, None)],
)
def test_check_ticker(expected, ticker):
    controller = gov_controller.GovController(ticker=ticker)

    # pylint: disable=protected-access
    assert controller._check_ticker() == expected
