# IMPORTATION STANDARD

import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import PreferencesModel, copy_user
from openbb_terminal.stocks.discovery import disc_controller

# pylint: disable=E1101,W0603,E1111


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
            "openbb_terminal.stocks.discovery.disc_controller."
            "DiscoveryController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = disc_controller.DiscoveryController(
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
        target="openbb_terminal.stocks.discovery.disc_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.discovery.disc_controller.session.prompt",
        return_value="quit",
    )

    result_menu = disc_controller.DiscoveryController(queue=None).menu()

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
        target="openbb_terminal.stocks.discovery.disc_controller.session",
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
            "openbb_terminal.stocks.discovery.disc_controller."
            "DiscoveryController.switch"
        ),
        new=mock_switch,
    )

    result_menu = disc_controller.DiscoveryController(queue=None).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = disc_controller.DiscoveryController()
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
        ("r", ["quit", "quit", "reset", "stocks", "disc"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = disc_controller.DiscoveryController(queue=None)
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = disc_controller.DiscoveryController()
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
            ["quit", "quit", "reset", "stocks", "disc"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "disc", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = disc_controller.DiscoveryController(
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
            "call_active",
            "yahoofinance_view.display_active",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_arkord",
            "ark_view.ark_orders_view",
            ["--limit=5", "--sortby=date", "--fund=ARKK", "--export=csv"],
            {
                "limit": 5,
                "sortby": "date",
                "ascend": False,
                "buys_only": False,
                "sells_only": False,
                "fund": "ARKK",
                "export": "csv",
                "sheet_name": None,
            },
        ),
        (
            "call_asc",
            "yahoofinance_view.display_asc",
            [
                "--limit=5",
                "--export=csv",
            ],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_fipo",
            "finnhub_view.future_ipo",
            ["--days=5", "--limit=20", "--export=csv"],
            {
                "num_days_ahead": 5,
                "end_date": None,
                "limit": 20,
                "export": "csv",
                "sheet_name": None,
            },
        ),
        (
            "call_gainers",
            "yahoofinance_view.display_gainers",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_gtech",
            "yahoofinance_view.display_gtech",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_hotpenny",
            "shortinterest_view.hot_penny_stocks",
            ["--limit=5", "--export=csv", "--source=YahooFinance"],
            {
                "limit": 5,
                "export": "csv",
                "sheet_name": None,
                "source": "YahooFinance",
            },
        ),
        (
            "call_losers",
            "yahoofinance_view.display_losers",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_lowfloat",
            "shortinterest_view.low_float",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_pipo",
            "finnhub_view.past_ipo",
            ["--days=5", "--limit=20", "--export=csv"],
            {
                "num_days_behind": 5,
                "start_date": None,
                "limit": 20,
                "export": "csv",
                "sheet_name": None,
            },
        ),
        (
            "call_rtat",
            "nasdaq_view.display_top_retail",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv"},
        ),
        (
            "call_trending",
            "seeking_alpha_view.news",
            [
                "--id=123",
                "--limit=5",
                "--export=csv",
            ],
            {
                "article_id": 123,
                "limit": 5,
                "export": "csv",
                "sheet_name": None,
            },
        ),
        (
            "call_ugs",
            "yahoofinance_view.display_ugs",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_ulc",
            "yahoofinance_view.display_ulc",
            ["--limit=5", "--export=csv"],
            {"limit": 5, "export": "csv", "sheet_name": None},
        ),
        (
            "call_upcoming",
            "seeking_alpha_view.upcoming_earning_release_dates",
            ["--start=2023-03-22", "--limit=5", "--export=csv"],
            {
                "limit": 5,
                "start_date": datetime(2023, 3, 22),
                "export": "csv",
                "sheet_name": None,
            },
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    mock = mocker.Mock()
    mocker.patch(
        "openbb_terminal.stocks.discovery." + mocked_func,
        new=mock,
    )
    controller = disc_controller.DiscoveryController()
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
        "call_active",
        "call_arkord",
        "call_asc",
        "call_fipo",
        "call_gainers",
        "call_gtech",
        "call_hotpenny",
        "call_losers",
        "call_lowfloat",
        "call_pipo",
        "call_rtat",
        "call_trending",
        "call_ugs",
        "call_ulc",
        "call_upcoming",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.discovery.disc_controller.DiscoveryController.parse_known_args_and_warn",
        return_value=None,
    )
    controller = disc_controller.DiscoveryController()

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()
