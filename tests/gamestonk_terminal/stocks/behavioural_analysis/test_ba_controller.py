# IMPORTATION STANDARD
import os
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.behavioural_analysis import ba_controller

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
        (["load", "help"], []),
        (["quit", "help"], ["help"]),
    ],
)
def test_menu_with_queue(expected, mocker, queue):
    mocker.patch(
        target=(
            "gamestonk_terminal.stocks.behavioural_analysis.ba_controller."
            "BehaviouralAnalysisController.switch"
        ),
        return_value=["quit"],
    )
    result_menu = ba_controller.menu(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        queue=queue,
    )

    assert result_menu == expected


@pytest.mark.vcr(record_mode="none")
def test_menu_without_queue_completion(mocker):
    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=ba_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=True,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.behavioural_analysis.ba_controller.session",
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.behavioural_analysis.ba_controller.session.prompt",
        return_value="quit",
    )

    result_menu = ba_controller.menu(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        queue=None,
    )

    assert result_menu == []


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "mock_input",
    ["help", "homee help", "home help", "mock"],
)
def test_menu_without_queue_sys_exit(mock_input, mocker):
    # DISABLE AUTO-COMPLETION
    mocker.patch.object(
        target=ba_controller.gtff,
        attribute="USE_PROMPT_TOOLKIT",
        new=False,
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.behavioural_analysis.ba_controller.session",
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
            "gamestonk_terminal.stocks.behavioural_analysis.ba_controller."
            "BehaviouralAnalysisController.switch"
        ),
        new=mock_switch,
    )

    result_menu = ba_controller.menu(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        queue=None,
    )

    assert result_menu == []


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
        ("/help", ["quit", "quit", "help"]),
        ("help/help", ["help"]),
        ("q", ["quit"]),
        ("h", []),
        ("r", ["quit", "quit", "reset", "stocks", "ba"]),
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
            ["quit", "quit", "reset", "stocks", "ba"],
        ),
        (
            "call_reset",
            ["help"],
            ["quit", "quit", "reset", "stocks", "ba", "help"],
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
    "tested_func, mocked_func, other_args, called_with",
    [
        (
            "call_watchlist",
            "reddit_view.display_watchlist",
            ["--limit=2"],
            dict(num=2),
        ),
        (
            "call_spac",
            "reddit_view.display_spac",
            ["--limit=2"],
            dict(limit=2),
        ),
        (
            "call_spac_c",
            "reddit_view.display_spac_community",
            ["--limit=5", "--popular"],
            dict(
                limit=5,
                popular=True,
            ),
        ),
        (
            "call_wsb",
            "reddit_view.display_wsb_community",
            ["--limit=5", "--new"],
            dict(
                limit=5,
                new=True,
            ),
        ),
        (
            "call_popular",
            "reddit_view.display_popular_tickers",
            ["--num=5", "--limit=10", "--sub=MOCK_SUB"],
            dict(
                n_top=10,
                posts_to_look_at=5,
                subreddits="MOCK_SUB",
            ),
        ),
        (
            "call_bullbear",
            "stocktwits_view.display_bullbear",
            list(),
            dict(
                ticker="MOCK_TICKER",
            ),
        ),
        (
            "call_messages",
            "stocktwits_view.display_messages",
            ["--limit=2"],
            dict(
                ticker="MOCK_TICKER",
                limit=2,
            ),
        ),
        (
            "call_trending",
            "stocktwits_view.display_trending",
            list(),
            dict(),
        ),
        (
            "call_stalker",
            "stocktwits_view.display_stalker",
            ["--user=MOCK_USER", "--limit=5"],
            dict(
                user="MOCK_USER",
                limit=5,
            ),
        ),
        (
            "call_infer",
            "twitter_view.display_inference",
            ["--limit=20"],
            dict(
                ticker="MOCK_TICKER",
                num=20,
            ),
        ),
        (
            "call_sentiment",
            "twitter_view.display_sentiment",
            ["--limit=20", "--days=2", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                n_tweets=20,
                n_days_past=2,
                export="csv",
            ),
        ),
        (
            "call_mentions",
            "google_view.display_mentions",
            ["--start=2020-12-01", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
                export="csv",
            ),
        ),
        (
            "call_regions",
            "google_view.display_regions",
            ["--limit=5", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_queries",
            "google_view.display_queries",
            ["--limit=5", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_rise",
            "google_view.display_rise",
            ["--limit=5", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_headlines",
            "finbrain_view.display_sentiment_analysis",
            ["--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                export="csv",
            ),
        ),
        (
            "call_stats",
            "finnhub_view.display_sentiment_stats",
            ["--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                export="csv",
            ),
        ),
        (
            "call_metrics",
            "sentimentinvestor_view.display_metrics",
            list(),
            None,
            # dict(
            #     ticker="MOCK_TICKER",
            # ),
        ),
        (
            "call_social",
            "sentimentinvestor_view.display_social",
            list(),
            None,
            # dict(
            #     ticker="MOCK_TICKER",
            # ),
        ),
        (
            "call_historical",
            "sentimentinvestor_view.display_historical",
            ["--sort=date", "--direction=desc", "--metric=sentiment"],
            None,
            # dict(
            #     ticker="MOCK_TICKER",
            #     sort_param="date",
            #     sort_dir="desc",
            #     metric="sentiment",
            # ),
        ),
        (
            "call_emerging",
            "sentimentinvestor_view.display_top",
            ["--limit=2"],
            None,
            # dict(
            #     metric="RHI",
            #     limit=2,
            # ),
        ),
        (
            "call_popular",
            "reddit_view.display_popular_tickers",
            ["--num=1", "--limit=2", "--sub=MOCK_SUB"],
            dict(
                n_top=2,
                posts_to_look_at=1,
                subreddits="MOCK_SUB",
            ),
        ),
        (
            "call_popularsi",
            "sentimentinvestor_view.display_top",
            ["--limit=2"],
            None,
            # dict(
            #     metric="AHI",
            #     limit=2,
            # ),
        ),
        (
            "call_getdd",
            "reddit_view.display_due_diligence",
            ["--limit=1", "--days=2", "--all"],
            dict(
                ticker="MOCK_TICKER",
                limit=1,
                n_days=2,
                show_all_flairs=True,
            ),
        ),
    ],
)
def test_call_func(tested_func, mocked_func, other_args, called_with, mocker):
    if called_with:
        mock = mocker.Mock()
        mocker.patch(
            "gamestonk_terminal.stocks.behavioural_analysis.ba_controller."
            + mocked_func,
            new=mock,
        )
        EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
        controller = ba_controller.BehaviouralAnalysisController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        )
        getattr(controller, tested_func)(other_args=other_args)

        if isinstance(called_with, dict):
            mock.assert_called_once_with(**called_with)
        elif isinstance(called_with, list):
            mock.assert_called_once_with(*called_with)
        else:
            mock.assert_called_once()
    else:
        EMPTY_DF.drop(EMPTY_DF.index, inplace=True)
        controller = ba_controller.BehaviouralAnalysisController(
            ticker="MOCK_TICKER",
            start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
        )
        getattr(controller, tested_func)(other_args=other_args)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_load",
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
        "call_stats",
        "call_metrics",
        "call_social",
        "call_historical",
        "call_emerging",
        "call_popular",
        "call_popularsi",
        "call_getdd",
    ],
)
def test_call_func_no_parser(func, mocker):
    mocker.patch(
        "gamestonk_terminal.stocks.behavioural_analysis.ba_controller.parse_known_args_and_warn",
        return_value=None,
    )
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="MOCK_TICKER",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    getattr(ba_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "func",
    [
        "call_historical",
        "call_social",
        "call_metrics",
        "call_stats",
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
        "gamestonk_terminal.stocks.behavioural_analysis.ba_controller.parse_known_args_and_warn",
        return_value=True,
    )
    controller = ba_controller.BehaviouralAnalysisController(
        ticker=None,
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )

    func_result = getattr(controller, func)(other_args=list())
    assert func_result is None
    assert controller.queue == []
    getattr(ba_controller, "parse_known_args_and_warn").assert_called_once()


@pytest.mark.vcr
def test_call_load(mocker):
    yf_download = ba_controller.stocks_helper.yf.download

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
    ]
    controller.call_load(other_args=other_args)
