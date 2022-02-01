# IMPORTATION STANDARD
import os

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import dd_controller

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
            "gamestonk_terminal.stocks.due_diligence.dd_controller."
            "DueDiligenceController.switch"
        ),
        return_value=["quit"],
    )
    stock = pd.DataFrame()
    result_menu = dd_controller.DueDiligenceController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=stock,
        queue=queue,
    ).menu()

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    # ENABLE AUTO-COMPLETION : HELPER_FUNCS.MENU
    mocker.patch(
        target="gamestonk_terminal.feature_flags.USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session",
    )
    mocker.patch(
        target="gamestonk_terminal.parent_classes.session.prompt",
        return_value="quit",
    )

    # DISABLE AUTO-COMPLETION : CONTROLLER.COMPLETER
    mocker.patch.object(
        target=dd_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.due_diligence.dd_controller.session",
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.due_diligence.dd_controller.session.prompt",
        return_value="quit",
    )

    stock = pd.DataFrame()
    result_menu = dd_controller.DueDiligenceController(
        ticker="TSLA", start="10/25/2021", interval="1440min", stock=stock, queue=None
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
        target=dd_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.due_diligence.dd_controller.session",
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
            "gamestonk_terminal.stocks.due_diligence.dd_controller."
            "DueDiligenceController.switch"
        ),
        new=mock_switch,
    )

    stock = pd.DataFrame()
    result_menu = dd_controller.DueDiligenceController(
        ticker="TSLA", start="10/25/2021", interval="1440min", stock=stock, queue=None
    ).menu()

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
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
        ("r", ["quit", "quit", "reset", "stocks", "dd"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = dd_controller.DueDiligenceController(
        ticker="",
        start="",
        interval="",
        stock=pd.DataFrame(),
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = dd_controller.DueDiligenceController(
        ticker="", start="", interval="", stock=pd.DataFrame()
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
            ["quit", "quit", "reset", "stocks", "dd"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "dd", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = dd_controller.DueDiligenceController(
        ticker="",
        start="",
        interval="",
        stock=pd.DataFrame(),
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
            ["--limit=10"],
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
            ["--limit=10"],
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
            ["--limit=10"],
            {
                "ticker": "TSLA",
                "num": 10,
                "export": "",
            },
        ),
        (
            "call_sec",
            "marketwatch_view.sec_filings",
            ["--limit=10"],
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
            ["--limit=10", "--show_ticker"],
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
    controller = dd_controller.DueDiligenceController(
        ticker="TSLA",
        start="10/25/2021",
        interval="1440min",
        stock=None,
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
    controller = dd_controller.DueDiligenceController(
        ticker="AAPL", start="10/25/2021", interval="1440min", stock=pd.DataFrame()
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    getattr(dd_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "ticker, expected",
    [
        (None, []),
        ("MOCK_TICKER", ["stocks", "load MOCK_TICKER", "dd"]),
    ],
)
def test_custom_reset(expected, ticker):
    controller = dd_controller.DueDiligenceController(
        ticker=None,
        start="10/25/2021",
        interval="1440min",
        stock=pd.DataFrame(),
    )
    controller.ticker = ticker

    result = controller.custom_reset()

    assert result == expected
