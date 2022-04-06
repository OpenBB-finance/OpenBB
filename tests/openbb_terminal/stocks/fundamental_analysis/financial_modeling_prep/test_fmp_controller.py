# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep import (
    fmp_controller,
)

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "queue, expected",
    [
        (["profile", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller."
            "FinancialModelingPrepController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = fmp_controller.FinancialModelingPrepController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
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
        target=fmp_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.session.prompt",
        return_value="quit",
    )
    result_menu = fmp_controller.FinancialModelingPrepController(
        ticker="TSLA", start="10/25/2021", interval="1440min", queue=None
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
        target=fmp_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.session",
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
            "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller."
            "FinancialModelingPrepController.switch"
        ),
        new=mock_switch,
    )
    result_menu = fmp_controller.FinancialModelingPrepController(
        ticker="TSLA", start="10/25/2021", interval="1440min", queue=None
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
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
        ("r", ["quit", "quit", "quit", "reset", "stocks", "fa", "fmp"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = fmp_controller.FinancialModelingPrepController(
        ticker="",
        start="",
        interval="",
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
                "quit",
            ],
        ),
        ("call_exit", ["help"], ["quit", "quit", "quit", "quit", "help"]),
        ("call_home", [], ["quit", "quit", "quit"]),
        ("call_help", [], []),
        ("call_quit", [], ["quit"]),
        ("call_quit", ["help"], ["quit", "help"]),
        (
            "call_reset",
            [],
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "load MOCK_TICKER",
                "fa",
                "fmp",
            ],
        ),
        (
            "call_reset",
            ["help"],
            [
                "quit",
                "quit",
                "quit",
                "reset",
                "stocks",
                "load MOCK_TICKER",
                "fa",
                "fmp",
                "help",
            ],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = fmp_controller.FinancialModelingPrepController(
        ticker="MOCK_TICKER",
        start="",
        interval="",
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
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_dcf",
            "fmp_view.display_discounted_cash_flow",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_income",
            "fmp_view.display_income_statement",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_balance",
            "fmp_view.display_balance_sheet",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_cash",
            "fmp_view.display_cash_flow",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_metrics",
            "fmp_view.display_key_metrics",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_ratios",
            "fmp_view.display_financial_ratios",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
        (
            "call_growth",
            "fmp_view.display_financial_statement_growth",
            ["--export=csv", "--limit=5", "--quarter"],
            {"ticker": "TSLA", "number": 5, "quarterly": True, "export": "csv"},
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep."
        + mocked_func,
        new=mock,
    )
    controller = fmp_controller.FinancialModelingPrepController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
    )
    getattr(controller, tested_func)(other_args=other_args)

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
        "openbb_terminal.stocks.fundamental_analysis.financial_modeling_prep.fmp_controller.parse_known_args_and_warn",
        return_value=None,
    )
    controller = fmp_controller.FinancialModelingPrepController(
        ticker="AAPL",
        start="10/25/2021",
        interval="1440min",
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    getattr(fmp_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "fa", "fmp"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = fmp_controller.FinancialModelingPrepController(
        ticker=None,
        start="10/25/2021",
        interval="1440min",
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
