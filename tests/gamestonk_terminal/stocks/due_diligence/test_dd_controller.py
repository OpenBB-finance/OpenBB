# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import dd_controller

# pylint: disable=E1101
# pylint: disable=W0603


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.due_diligence.dd_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.due_diligence.dd_controller.session.prompt",
        return_value="quit",
    )

    stock = pd.DataFrame()
    result_menu = dd_controller.menu(
        ticker="TSLA", start="10/25/2021", interval="1440min", stock=stock
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
    mocker.patch("gamestonk_terminal.stocks.due_diligence.dd_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.due_diligence.dd_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.due_diligence.dd_controller.DueDiligenceController.switch",
        new=mock_switch,
    )

    stock = pd.DataFrame()
    dd_controller.menu(
        ticker="TSLA", start="10/25/2021", interval="1440min", stock=stock
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    dd = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
    )
    dd.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    dd = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
    )
    result = dd.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    dd = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
    )
    result = dd.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    dd = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
    )
    result = dd.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    dd = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
    )
    other_args = list()
    result = dd.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    dd = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
    )
    other_args = list()
    result = dd.call_quit(other_args)

    assert result is True


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_analyst",
            "finviz_view.analyst",
            [],
            {"ticker": "TSLA", "export": ""},
        ),
        (
            "call_analyst",
            "finviz_view.analyst",
            ["--export=csv"],
            {"ticker": "TSLA", "export": "csv"},
        ),
        (
            "call_analyst",
            "finviz_view.analyst",
            ["--export=json"],
            {"ticker": "TSLA", "export": "json"},
        ),
        (
            "call_analyst",
            "finviz_view.analyst",
            ["--export=xlsx"],
            {"ticker": "TSLA", "export": "xlsx"},
        ),
        (
            "call_pt",
            "business_insider_view.price_target_from_analysts",
            ["--num=10"],
            {
                "ticker": "TSLA",
                "start": "10/25/2021",
                "interval": "1440min",
                "stock": None,
                "num": 10,
                "raw": False,
                "export": "",
            },
        ),
        (
            "call_est",
            "business_insider_view.estimates",
            [],
            {
                "ticker": "TSLA",
                "export": "",
            },
        ),
        (
            "call_rot",
            "finnhub_view.rating_over_time",
            ["--num=10"],
            {
                "ticker": "TSLA",
                "num": 10,
                "raw": False,
                "export": "",
            },
        ),
        (
            "call_rating",
            "fmp_view.rating",
            ["--num=10"],
            {
                "ticker": "TSLA",
                "num": 10,
                "export": "",
            },
        ),
        (
            "call_sec",
            "marketwatch_view.sec_filings",
            ["--num=10"],
            {
                "ticker": "TSLA",
                "num": 10,
                "export": "",
            },
        ),
        (
            "call_supplier",
            "csimarket_view.suppliers",
            [],
            {
                "ticker": "TSLA",
                "export": "",
            },
        ),
        (
            "call_arktrades",
            "ark_view.display_ark_trades",
            ["--num=10", "--show_ticker"],
            {
                "ticker": "TSLA",
                "num": 10,
                "export": "",
                "show_ticker": True,
            },
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.due_diligence.dd_controller." + mocked_func,
        new=mock,
    )
    dd = dd_controller.DueDiligenceController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=None,
    )
    getattr(dd, tested_func)(other_args=other_args)

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
        "call_analyst",
        "call_pt",
        "call_est",
        "call_rot",
        "call_rating",
        "call_sec",
        "call_supplier",
        "call_customer",
        "call_arktrades",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.due_diligence.dd_controller.parse_known_args_and_warn",
        return_value=None,
    )
    dd = dd_controller.DueDiligenceController(
        ticker="AAPL", start="10/25/2021", interval="1440min", stock=pd.DataFrame()
    )

    func_result = getattr(dd, func)(other_args=list())
    assert func_result is None
    getattr(dd_controller, "parse_known_args_and_warn").assert_called_once()
