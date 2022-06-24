# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.behavioural_analysis import ba_controller
from openbb_terminal import parent_classes

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
        target=ba_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
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
    mocker.patch.object(
        target=ba_controller.obbff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
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
            "call_watchlist",
            ["--limit=2"],
            "reddit_view.display_watchlist",
            [],
            dict(num=2),
        ),
        (
            "call_spac",
            ["--limit=2"],
            "reddit_view.display_spac",
            [],
            dict(limit=2),
        ),
        (
            "call_spac_c",
            ["--limit=5", "--popular"],
            "reddit_view.display_spac_community",
            [],
            dict(
                limit=5,
                popular=True,
            ),
        ),
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
                n_top=10,
                posts_to_look_at=5,
                subreddits="MOCK_SUB",
            ),
        ),
        (
            "call_bullbear",
            [],
            "stocktwits_view.display_bullbear",
            [],
            dict(
                ticker="MOCK_TICKER",
            ),
        ),
        (
            "call_messages",
            ["--limit=2"],
            "stocktwits_view.display_messages",
            [],
            dict(
                ticker="MOCK_TICKER",
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
            "call_infer",
            ["--limit=20"],
            "twitter_view.display_inference",
            [],
            dict(
                ticker="MOCK_TICKER",
                num=20,
            ),
        ),
        (
            "call_sentiment",
            ["--limit=20", "--days=2", "--compare", "--export=csv"],
            "twitter_view.display_sentiment",
            [],
            dict(
                ticker="MOCK_TICKER",
                n_tweets=20,
                n_days_past=2,
                compare=True,
                export="csv",
            ),
        ),
        (
            "call_mentions",
            ["--start=2020-12-01", "--export=csv"],
            "google_view.display_mentions",
            [],
            dict(
                ticker="MOCK_TICKER",
                start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
                export="csv",
            ),
        ),
        (
            "call_regions",
            ["--limit=5", "--export=csv"],
            "google_view.display_regions",
            [],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_queries",
            ["--limit=5", "--export=csv"],
            "google_view.display_queries",
            [],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_rise",
            ["--limit=5", "--export=csv"],
            "google_view.display_rise",
            [],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_headlines",
            ["--export=csv", "--raw"],
            "finbrain_view.display_sentiment_analysis",
            [],
            dict(
                ticker="MOCK_TICKER",
                raw=True,
                export="csv",
            ),
        ),
        (
            "call_hist",
            [
                "--start=2020-12-01",
                "--end=2020-12-07",
                "--export=csv",
                "--number=100",
                "--raw",
                "--limit=10",
            ],
            "sentimentinvestor_view.display_historical",
            [],
            dict(
                ticker="MOCK_TICKER",
                start=datetime(2020, 12, 1),
                end=datetime(2020, 12, 7),
                number=100,
                export="csv",
                raw=True,
                limit=10,
            ),
        ),
        (
            "call_trend",
            [
                "--start=2020-12-01",
                "--hour=9",
                "--export=csv",
                "--number=20",
            ],
            "sentimentinvestor_view.display_trending",
            [],
            dict(
                start=datetime(2020, 12, 1),
                hour=9,
                export="csv",
                number=20,
            ),
        ),
        (
            "call_popular",
            ["--num=1", "--limit=2", "--sub=MOCK_SUB"],
            "reddit_view.display_popular_tickers",
            [],
            dict(
                n_top=2,
                posts_to_look_at=1,
                subreddits="MOCK_SUB",
            ),
        ),
        (
            "call_getdd",
            ["--limit=1", "--days=2", "--all"],
            "reddit_view.display_due_diligence",
            [],
            dict(
                ticker="MOCK_TICKER",
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
        "call_watchlist",
        "call_spac",
        "call_spac_c",
        "call_wsb",
        "call_popular",
        "call_bullbear",
        "call_messages",
        "call_trending",
        "call_stalker",
        "call_infer",
        "call_sentiment",
        "call_mentions",
        "call_regions",
        "call_queries",
        "call_rise",
        "call_headlines",
        "call_snews",
        "call_hist",
        "call_trend",
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
        "call_hist",
        "call_headlines",
        "call_sentiment",
        "call_infer",
        "call_rise",
        "call_queries",
        "call_regions",
        "call_mentions",
        "call_messages",
        "call_bullbear",
        "call_getdd",
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
        "--source=yf",
    ]
    controller.call_load(other_args=other_args)
