# IMPORTATION STANDARD

import os

# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal import parent_classes

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.government import gov_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


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
        (["load", "help"], ["help"]),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "openbb_terminal.stocks.government.gov_controller." "GovController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = gov_controller.GovController(
        ticker="TSLA",
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
        target="openbb_terminal.stocks.government.gov_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.government.gov_controller.session.prompt",
        return_value="quit",
    )

    result_menu = gov_controller.GovController(
        ticker="TSLA",
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
        target="openbb_terminal.stocks.government.gov_controller.session",
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
            "openbb_terminal.stocks.government.gov_controller." "GovController.switch"
        ),
        new=mock_switch,
    )

    result_menu = gov_controller.GovController(
        ticker="TSLA",
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = gov_controller.GovController(
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
        ("r", ["quit", "quit", "reset", "stocks", "gov"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = gov_controller.GovController(
        ticker="",
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = gov_controller.GovController(
        ticker="",
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
            ["quit", "quit", "reset", "stocks", "gov"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "gov", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = gov_controller.GovController(
        ticker="",
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
            "call_contracts",
            "quiverquant_view.display_contracts",
            ["--past_transaction_days=5", "--raw", "--export=csv"],
            dict(
                symbol="MOCK_TICKER",
                past_transaction_days=5,
                raw=True,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_gtrades",
            "quiverquant_view.display_government_trading",
            [
                "--past_transactions_months=5",
                "--govtype=congress",
                "--raw",
                "--export=csv",
            ],
            dict(
                symbol="MOCK_TICKER",
                gov_type="congress",
                past_transactions_months=5,
                raw=True,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_histcont",
            "quiverquant_view.display_hist_contracts",
            ["--raw", "--export=csv"],
            dict(
                symbol="MOCK_TICKER",
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_lastcontracts",
            "quiverquant_view.display_last_contracts",
            ["--past_transaction_days=2", "--limit=5", "--sum", "--export=csv"],
            dict(
                past_transaction_days=2,
                limit=5,
                sum_contracts=True,
                export="csv",
                sheet_name=None,
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
                limit=5,
                representative="MOCK_TEXT",
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_lobbying",
            "quiverquant_view.display_lobbying",
            ["--limit=5"],
            dict(
                symbol="MOCK_TICKER",
                limit=5,
            ),
        ),
        (
            "call_qtrcontracts",
            "quiverquant_view.display_qtr_contracts",
            ["--limit=5", "--analysis=total", "--raw", "--export=csv"],
            dict(analysis="total", limit=5, raw=True, export="csv", sheet_name=None),
        ),
        (
            "call_topbuys",
            "quiverquant_view.display_government_buys",
            [
                "--govtype=congress",
                "--past_transactions_months=2",
                "--limit=5",
                "--raw",
                "--export=csv",
            ],
            dict(
                gov_type="congress",
                past_transactions_months=2,
                limit=5,
                raw=True,
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_toplobbying",
            "quiverquant_view.display_top_lobbying",
            ["--limit=5", "--raw", "--export=csv"],
            dict(
                limit=5,
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
                "--limit=5",
                "--raw",
                "--export=csv",
            ],
            dict(
                gov_type="congress",
                past_transactions_months=2,
                limit=5,
                raw=True,
                export="csv",
                sheet_name=None,
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "openbb_terminal.stocks.government." + mocked_func,
        new=mock,
    )
    controller = gov_controller.GovController(ticker="MOCK_TICKER")
    getattr(controller, tested_func)(other_args=other_args)

    if isinstance(called_with, (dict, list)):
        mock.assert_called_once_with(**called_with)
    else:
        mock.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
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
        "openbb_terminal.stocks.government.gov_controller.GovController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = gov_controller.GovController(ticker="AAPL")

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_gtrades",
        "call_contracts",
        "call_histcont",
        "call_lobbying",
    ],
)
def test_call_func_no_ticker(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.government.gov_controller.GovController.parse_known_args_and_warn",
        return_value=True,
    )
    controller = gov_controller.GovController(ticker=None)

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr
def test_call_load(mocker):
    yf_download = parent_classes.stocks_helper.yf.download

    def mock_yf_download(*args, **kwargs):
        kwargs["threads"] = False
        return yf_download(*args, **kwargs)

    mocker.patch("yfinance.download", side_effect=mock_yf_download)
    controller = gov_controller.GovController(
        ticker="TSLA",
    )
    other_args = [
        "TSLA",
        "--start=2021-12-17",
        "--source=YahooFinance",
    ]
    controller.call_load(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "gov"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = gov_controller.GovController(ticker=None)
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
