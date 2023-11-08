# IMPORTATION STANDARD

import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal import parent_classes
from openbb_terminal.core.session.current_user import PreferencesModel, copy_user
from openbb_terminal.stocks.behavioural_analysis import ba_controller

# pylint: disable=E1101
# pylint: disable=W0603
# pylint: disable=E1111

EMPTY_DF = pd.DataFrame()


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
            "openbb_terminal.stocks.behavioural_analysis.ba_controller."
            "BehaviouralAnalysisController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
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
        target="openbb_terminal.stocks.behavioural_analysis.ba_controller.session",
    )
    mocker.patch(
        target="openbb_terminal.stocks.behavioural_analysis.ba_controller.session.prompt",
        return_value="quit",
    )

    result_menu = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
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
        target="openbb_terminal.stocks.behavioural_analysis.ba_controller.session",
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
            "openbb_terminal.stocks.behavioural_analysis.ba_controller."
            "BehaviouralAnalysisController.switch"
        ),
        new=mock_switch,
    )

    result_menu = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        queue=None,
    ).menu()

    assert result_menu == ["help"]


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
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
        ("r", ["quit", "quit", "reset", "stocks", "ba", "load TSLA"]),
    ],
)
def test_switch(an_input, expected_queue):
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        queue=None,
    )
    queue = controller.switch(an_input=an_input)

    assert queue == expected_queue


@pytest.mark.vcr(record_mode="none")
def test_call_cls(mocker):
    mocker.patch("os.system")
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
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
            ["quit", "quit", "reset", "stocks", "ba", "load TSLA"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "ba", "load TSLA", "help"],
        ),
    ],
)
def test_call_func_expect_queue(expected_queue, queue, func):
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        queue=queue,
    )
    result = getattr(controller, func)([])

    assert result is None
    assert controller.queue == expected_queue


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_wsb",
            ["--limit=5", "--new"],
            "reddit_view.display_wsb_community",
            [],
            dict(
                limit=5,
                new=True,
            ),
        ),
        (
            "call_popular",
            ["--num=5", "--limit=10", "--sub=MOCK_SUB"],
            "reddit_view.display_popular_tickers",
            [],
            dict(
                limit=10,
                post_limit=5,
                subreddits="MOCK_SUB",
                export="",
                sheet_name=None,
            ),
        ),
        (
            "call_bullbear",
            [],
            "stocktwits_view.display_bullbear",
            [],
            dict(
                symbol="MOCK_TICKER",
            ),
        ),
        (
            "call_messages",
            ["--limit=2"],
            "stocktwits_view.display_messages",
            [],
            dict(
                symbol="MOCK_TICKER",
                limit=2,
            ),
        ),
        (
            "call_trending",
            [],
            "stocktwits_view.display_trending",
            [],
            dict(),
        ),
        (
            "call_stalker",
            ["--user=MOCK_USER", "--limit=5"],
            "stocktwits_view.display_stalker",
            [],
            dict(
                user="MOCK_USER",
                limit=5,
            ),
        ),
        (
            "call_mentions",
            ["--start=2020-12-01", "--export=csv"],
            "google_view.display_mentions",
            [],
            dict(
                symbol="MOCK_TICKER",
                start_date=datetime.strptime("2020-12-01", "%Y-%m-%d"),
                export="csv",
                sheet_name=None,
            ),
        ),
        (
            "call_regions",
            ["--limit=5", "--export=csv"],
            "google_view.display_regions",
            [],
            dict(symbol="MOCK_TICKER", limit=5, export="csv"),
        ),
        (
            "call_queries",
            ["--limit=5", "--export=csv"],
            "google_view.display_queries",
            [],
            dict(symbol="MOCK_TICKER", limit=5, export="csv", sheet_name=None),
        ),
        (
            "call_rise",
            ["--limit=5", "--export=csv"],
            "google_view.display_rise",
            [],
            dict(symbol="MOCK_TICKER", limit=5, export="csv", sheet_name=None),
        ),
        (
            "call_headlines",
            ["--export=csv", "--raw"],
            "finbrain_view.display_sentiment_analysis",
            [],
            dict(symbol="MOCK_TICKER", raw=True, export="csv"),
        ),
        (
            "call_popular",
            ["--num=1", "--limit=2", "--sub=MOCK_SUB"],
            "reddit_view.display_popular_tickers",
            [],
            dict(
                limit=2, post_limit=1, subreddits="MOCK_SUB", export="", sheet_name=None
            ),
        ),
        (
            "call_getdd",
            ["--limit=1", "--days=2", "--all"],
            "reddit_view.display_due_diligence",
            [],
            dict(
                limit=1,
                n_days=2,
                show_all_flairs=True,
            ),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.stocks.behavioural_analysis.ba_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
        controller = ba_controller.BehaviouralAnalysisController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        )
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
        controller = ba_controller.BehaviouralAnalysisController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        )
        getattr(controller, tested_func)(other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_wsb",
        "call_popular",
        "call_bullbear",
        "call_messages",
        "call_trending",
        "call_stalker",
        "call_mentions",
        "call_regions",
        "call_queries",
        "call_rise",
        "call_headlines",
        "call_snews",
        "call_popular",
        "call_getdd",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.behavioural_analysis.ba_controller.BehaviouralAnalysisController"
        ".parse_known_args_and_warn",
        return_value=None,
    )
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    controller.parse_known_args_and_warn.assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_headlines",
        "call_rise",
        "call_queries",
        "call_regions",
        "call_mentions",
        "call_messages",
        "call_bullbear",
    ],
)
def test_call_func_no_ticker(func, mocker):
    mocker.patch(
        "openbb_terminal.stocks.behavioural_analysis.ba_controller"
        ".BehaviouralAnalysisController.parse_known_args_and_warn",
        return_value=True,
    )
    controller = ba_controller.BehaviouralAnalysisController(
        ticker=None,
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )

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
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )
    other_args = [
        "TSLA",
        "--start=2021-12-17",
        "--source=YahooFinance",
    ]
    controller.call_load(other_args=other_args)
