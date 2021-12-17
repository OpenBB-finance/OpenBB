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


empty_df = pd.DataFrame()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_menu_quick_exit(mocker):
    mocker.patch("builtins.input", return_value="quit")
    mocker.patch("gamestonk_terminal.stocks.behavioural_analysis.ba_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.behavioural_analysis.ba_controller.session.prompt",
        return_value="quit",
    )

    result_menu = ba_controller.menu(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
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
    mocker.patch("gamestonk_terminal.stocks.behavioural_analysis.ba_controller.session")
    mocker.patch(
        "gamestonk_terminal.stocks.behavioural_analysis.ba_controller.session.prompt",
        return_value="quit",
    )
    mocker.patch(
        "gamestonk_terminal.stocks.behavioural_analysis.ba_controller.BehaviouralAnalysisController.switch",
        new=mock_switch,
    )

    ba_controller.menu(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )
    controller.print_help()


@pytest.mark.vcr(record_mode="none")
def test_switch_empty():
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )
    result = controller.switch(an_input="")

    assert result is None


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_switch_help():
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )
    result = controller.switch(an_input="?")

    assert result is None


@pytest.mark.vcr(record_mode="none")
def test_switch_cls(mocker):
    mocker.patch("os.system")
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )
    result = controller.switch(an_input="cls")

    assert result is None
    os.system.assert_called_once_with("cls||clear")


@pytest.mark.vcr(record_mode="none")
def test_call_q():
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )
    other_args = list()
    result = controller.call_q(other_args)

    assert result is False


@pytest.mark.vcr(record_mode="none")
def test_call_quit():
    controller = ba_controller.BehaviouralAnalysisController(
        ticker="TSLA",
        start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
    )
    other_args = list()
    result = controller.call_quit(other_args)

    assert result is True


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
            ["--number=5", "--limit=10", "--sub=MOCK_SUB"],
            dict(
                n_top=5,
                posts_to_look_at=10,
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
            ["--num=20"],
            dict(
                ticker="MOCK_TICKER",
                num=20,
            ),
        ),
        (
            "call_sentiment",
            "twitter_view.display_sentiment",
            ["--num=20", "--days=2", "--export=csv"],
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
            ["--start=2020-12-02", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                start=datetime.strptime("2020-12-01", "%Y-%m-%d"),
                export="csv",
            ),
        ),
        (
            "call_regions",
            "google_view.display_regions",
            ["--num=5", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_queries",
            "google_view.display_queries",
            ["--num=5", "--export=csv"],
            dict(
                ticker="MOCK_TICKER",
                num=5,
                export="csv",
            ),
        ),
        (
            "call_rise",
            "google_view.display_rise",
            ["--num=5", "--export=csv"],
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
            dict(
                ticker="MOCK_TICKER",
            ),
        ),
        (
            "call_social",
            "sentimentinvestor_view.display_social",
            list(),
            dict(
                ticker="MOCK_TICKER",
            ),
        ),
        (
            "call_historical",
            "sentimentinvestor_view.display_historical",
            ["--sort=date", "--direction=desc", "--metric=sentiment"],
            dict(
                ticker="MOCK_TICKER",
                sort_param="date",
                sort_dir="desc",
                metric="sentiment",
            ),
        ),
        (
            "call_emerging",
            "sentimentinvestor_view.display_top",
            ["--limit=2"],
            dict(
                metric="RHI",
                limit=2,
            ),
        ),
        (
            "call_popular",
            "reddit_view.display_popular_tickers",
            ["--number=1", "--limit=2", "--sub=MOCK_SUB"],
            dict(
                n_top=1,
                posts_to_look_at=2,
                subreddits="MOCK_SUB",
            ),
        ),
        (
            "call_popularsi",
            "sentimentinvestor_view.display_top",
            ["--limit=2"],
            dict(
                metric="AHI",
                limit=2,
            ),
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
    mock = mocker.Mock()
    mocker.patch(
        "gamestonk_terminal.stocks.behavioural_analysis.ba_controller." + mocked_func,
        new=mock,
    )
    empty_df.drop(empty_df.index, inplace=True)
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
    getattr(ba_controller, "parse_known_args_and_warn").assert_called_once()
