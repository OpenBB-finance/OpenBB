"""Reddit Model"""
__docformat__ = "numpy"
# pylint:disable=C0302

import logging
import warnings
from datetime import datetime, timedelta
from typing import List, Tuple

import finviz
import pandas as pd
import praw
from prawcore.exceptions import ResponseException
from psaw import PushshiftAPI
from requests import HTTPError
from sklearn.feature_extraction import _stop_words
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from openbb_terminal import config_terminal as cfg
from openbb_terminal.common.behavioural_analysis.reddit_helpers import find_tickers
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

l_sub_reddits = [
    "Superstonk",
    "pennystocks",
    "RobinHoodPennyStocks",
    "Daytrading",
    "StockMarket",
    "stocks",
    "investing",
    "wallstreetbets",
]


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_watchlists(
    limit: int = 5,
) -> Tuple[List[praw.models.reddit.submission.Submission], dict, int]:
    """Get reddit users watchlists [Source: reddit].

    Parameters
    ----------
    limit : int
        Number of posts to look through

    Returns
    -------
    Tuple[List[praw.models.reddit.submission.Submission], dict, int]
        List of reddit submissions,
        Dictionary of tickers and their count,
        Count of how many posts were analyzed.
    """
    d_watchlist_tickers: dict = {}
    l_watchlist_author = []
    subs = []

    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return [], {}, 0

    psaw_api = PushshiftAPI()
    submissions = psaw_api.search_submissions(
        subreddit=l_sub_reddits,
        q="WATCHLIST|Watchlist|watchlist",
        filter=["id"],
    )
    n_flair_posts_found = 0

    try:
        for sub in submissions:
            submission = praw_api.submission(id=sub.id)
            if (
                not submission.removed_by_category
                and submission.selftext
                and submission.link_flair_text not in ["Yolo", "Meme"]
                and submission.author.name not in l_watchlist_author
            ):
                l_tickers_found = find_tickers(submission)

                if l_tickers_found:
                    # Add another author's name to the parsed watchlists
                    l_watchlist_author.append(submission.author.name)

                    # Lookup stock tickers within a watchlist
                    for key in l_tickers_found:
                        if key in d_watchlist_tickers:
                            # Increment stock ticker found
                            d_watchlist_tickers[key] += 1
                        else:
                            # Initialize stock ticker found
                            d_watchlist_tickers[key] = 1

                    # Increment count of valid posts found
                    n_flair_posts_found += 1
                    subs.append(submission)
            if n_flair_posts_found > limit - 1:
                break

    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")

    return subs, d_watchlist_tickers, n_flair_posts_found


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_popular_tickers(
    limit: int = 10, post_limit: int = 50, subreddits: str = ""
) -> pd.DataFrame:
    """Get popular tickers from list of subreddits [Source: reddit].

    Parameters
    ----------
    limit : int
        Number of top tickers to get
    post_limit : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.

    Returns
    -------
    pd.DataFrame
        DataFrame of top tickers from supplied subreddits
    """
    sub_reddit_list = (
        (subreddits.split(",") if "," in subreddits else [subreddits])
        if subreddits
        else l_sub_reddits
    )
    d_watchlist_tickers: dict = {}
    l_watchlist_author = []

    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    psaw_api = PushshiftAPI()

    for s_sub_reddit in sub_reddit_list:
        console.print(
            f"Searching for latest tickers for {post_limit} '{s_sub_reddit}' posts"
        )
        warnings.filterwarnings(
            "ignore", message=".*Not all PushShift shards are active.*"
        )
        submissions = psaw_api.search_submissions(
            subreddit=s_sub_reddit,
            limit=post_limit,
            filter=["id"],
        )

        n_tickers = 0
        for submission in submissions:
            try:
                # Get more information about post using PRAW api
                submission = praw_api.submission(id=submission.id)

                # Ensure that the post hasn't been removed by moderator in the meanwhile,
                # that there is a description and it's not just an image, that the flair is
                # meaningful, and that we aren't re-considering same author's content
                if (
                    submission is not None
                    and not submission.removed_by_category
                    and (submission.selftext or submission.title)
                    and submission.author.name not in l_watchlist_author
                ):
                    l_tickers_found = find_tickers(submission)

                    if l_tickers_found:
                        n_tickers += len(l_tickers_found)

                        # Add another author's name to the parsed watchlists
                        l_watchlist_author.append(submission.author.name)

                        # Lookup stock tickers within a watchlist
                        for key in l_tickers_found:
                            if key in d_watchlist_tickers:
                                # Increment stock ticker found
                                d_watchlist_tickers[key] += 1
                            else:
                                # Initialize stock ticker found
                                d_watchlist_tickers[key] = 1

            except ResponseException as e:
                logger.exception("Invalid response: %s", str(e))

                if "received 401 HTTP response" in str(e):
                    console.print("[red]Invalid API Key[/red]\n")
                else:
                    console.print(f"[red]Invalid response: {str(e)}[/red]\n")

                return pd.DataFrame()

        console.print(f"  {n_tickers} potential tickers found.")
    lt_watchlist_sorted = sorted(
        d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
    )

    if lt_watchlist_sorted:
        n_top_stocks = 0
        # pylint: disable=redefined-outer-name
        popular_tickers = []
        for t_ticker in lt_watchlist_sorted:
            if n_top_stocks > limit:
                break
            try:
                # If try doesn't trigger exception, it means that this stock exists on finviz
                # thus we can print it.
                stock_info = finviz.get_stock(t_ticker[0])
                popular_tickers.append(
                    (
                        t_ticker[1],
                        t_ticker[0],
                        stock_info["Company"],
                        stock_info["Sector"],
                        stock_info["Price"],
                        stock_info["Change"],
                        stock_info["Perf Month"],
                        f"https://finviz.com/quote.ashx?t={t_ticker[0]}",
                    )
                )
                n_top_stocks += 1
            except HTTPError as e:
                if e.response.status_code != 404:
                    logger.exception("Unexpected exception from Finviz: %s", str(e))
                    console.print(f"Unexpected exception from Finviz: {e}")
            except Exception as e:
                logger.exception(str(e))
                console.print(e, "\n")
                return pd.DataFrame()

        popular_tickers_df = pd.DataFrame(
            popular_tickers,
            columns=[
                "Mentions",
                "Ticker",
                "Company",
                "Sector",
                "Price",
                "Change",
                "Perf Month",
                "URL",
            ],
        )
    return popular_tickers_df


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_spac_community(
    limit: int = 10, popular: bool = False
) -> Tuple[pd.DataFrame, dict]:
    """Get top tickers from r/SPACs [Source: reddit].

    Parameters
    ----------
    limit : int
        Number of posts to look at
    popular : bool
        Search by hot instead of new

    Returns
    -------
    Tuple[pd.DataFrame, dict]
        Dataframe of reddit submission,
        Dictionary of tickers and number of mentions.
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame(), {}

    d_watchlist_tickers: dict = {}
    l_watchlist_author = []

    if popular:
        submissions = praw_api.subreddit("SPACs").hot(limit=limit)
    else:
        submissions = praw_api.subreddit("SPACs").new(limit=limit)

    columns = [
        "Date",
        "Subreddit",
        "Flair",
        "Title",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
        "Link",
    ]
    subs = pd.DataFrame(columns=columns)

    try:
        for sub in submissions:
            if not sub:
                break

            # Get more information about post using PRAW api
            submission = praw_api.submission(id=sub.id)

            # Ensure that the post hasn't been removed  by moderator in the meanwhile,
            # that there is a description and it's not just an image, that the flair is
            # meaningful, and that we aren't re-considering same author's watchlist
            if (
                not submission.removed_by_category
                and submission.selftext
                and submission.link_flair_text not in ["Yolo", "Meme"]
                and submission.author.name not in l_watchlist_author
            ):
                l_tickers_found = find_tickers(submission)

                if l_tickers_found:
                    # Add another author's name to the parsed watchlists
                    l_watchlist_author.append(submission.author.name)
                    s_datetime = datetime.utcfromtimestamp(
                        submission.created_utc
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    s_link = f"https://old.reddit.com{submission.permalink}"
                    s_all_awards = "".join(
                        f"{award['count']} {award['name']}\n"
                        for award in submission.all_awardings
                    )

                    s_all_awards = s_all_awards[:-2]

                    data = [
                        s_datetime,
                        submission.subreddit,
                        submission.link_flair_text,
                        submission.title,
                        submission.score,
                        submission.num_comments,
                        f"{round(100 * submission.upvote_ratio)}%",
                        s_all_awards,
                        s_link,
                    ]
                    subs.loc[len(subs)] = data
                    # Lookup stock tickers within a watchlist
                    for key in l_tickers_found:
                        if key in d_watchlist_tickers:
                            # Increment stock ticker found
                            d_watchlist_tickers[key] += 1
                        else:
                            # Initialize stock ticker found
                            d_watchlist_tickers[key] = 1

    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")

    return subs, d_watchlist_tickers


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_spac(
    limit: int = 5,
) -> Tuple[pd.DataFrame, dict, int]:
    """Get posts containing SPAC from top subreddits [Source: reddit].

    Parameters
    ----------
    limit : int, optional
        Number of posts to get for each subreddit, by default 5

    Returns
    -------
    Tuple[pd.DataFrame, dict, int]
        Dataframe of reddit submission,
        Dictionary of tickers and counts,
        Number of posts found.
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame(), {}, 0

    d_watchlist_tickers: dict = {}
    l_watchlist_author = []
    columns = [
        "Date",
        "Subreddit",
        "Flair",
        "Title",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
        "Link",
    ]
    subs = pd.DataFrame(columns=columns)
    psaw_api = PushshiftAPI()
    submissions = psaw_api.search_submissions(
        subreddit=l_sub_reddits,
        q="SPAC|Spac|spac|Spacs|spacs",
        filter=["id"],
    )
    n_flair_posts_found = 0

    try:
        for submission in submissions:
            # Get more information about post using PRAW api
            submission = praw_api.submission(id=submission.id)

            # Ensure that the post hasn't been removed  by moderator in the meanwhile,
            # that there is a description and it's not just an image, that the flair is
            # meaningful, and that we aren't re-considering same author's watchlist
            if (
                not submission.removed_by_category
                and submission.selftext
                and submission.link_flair_text not in ["Yolo", "Meme"]
                and submission.author.name not in l_watchlist_author
            ):
                l_tickers_found = find_tickers(submission)

                s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                s_link = f"https://old.reddit.com{submission.permalink}"
                s_all_awards = "".join(
                    f"{award['count']} {award['name']}\n"
                    for award in submission.all_awardings
                )

                s_all_awards = s_all_awards[:-2]

                data = [
                    s_datetime,
                    submission.subreddit,
                    submission.link_flair_text,
                    submission.title,
                    submission.score,
                    submission.num_comments,
                    f"{round(100 * submission.upvote_ratio)}%",
                    s_all_awards,
                    s_link,
                ]
                subs.loc[len(subs)] = data

                if l_tickers_found:
                    # Add another author's name to the parsed watchlists
                    l_watchlist_author.append(submission.author.name)

                    # Lookup stock tickers within a watchlist
                    for key in l_tickers_found:
                        if key in d_watchlist_tickers:
                            # Increment stock ticker found
                            d_watchlist_tickers[key] += 1
                        else:
                            # Initialize stock ticker found
                            d_watchlist_tickers[key] = 1

                    # Increment count of valid posts found
                    n_flair_posts_found += 1

                # Check if number of wanted posts found has been reached
                if n_flair_posts_found > limit - 1:
                    break

    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")

    return subs, d_watchlist_tickers, n_flair_posts_found


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_wsb_community(limit: int = 10, new: bool = False) -> pd.DataFrame:
    """Get wsb posts [Source: reddit].

    Parameters
    ----------
    limit : int, optional
        Number of posts to get, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False

    Returns
    -------
    pd.DataFrame
        Dataframe of reddit submissions
    """
    # See https://github.com/praw-dev/praw/issues/1016 regarding praw arguments
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    if new:
        submissions = praw_api.subreddit("wallstreetbets").new(limit=limit)
    else:
        submissions = praw_api.subreddit("wallstreetbets").hot(limit=limit)

    columns = [
        "Date",
        "Subreddit",
        "Flair",
        "Title",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
        "Link",
    ]
    subs = pd.DataFrame(columns=columns)

    try:
        for submission in submissions:
            submission = praw_api.submission(id=submission.id)
            # Ensure that the post hasn't been removed  by moderator in the meanwhile,
            # that there is a description and it's not just an image, that the flair is
            # meaningful, and that we aren't re-considering same author's watchlist
            if not submission.removed_by_category:
                s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                s_link = f"https://old.reddit.com{submission.permalink}"
                s_all_awards = "".join(
                    f"{award['count']} {award['name']}\n"
                    for award in submission.all_awardings
                )

                s_all_awards = s_all_awards[:-2]

                data = [
                    s_datetime,
                    submission.subreddit,
                    submission.link_flair_text,
                    submission.title,
                    submission.score,
                    submission.num_comments,
                    f"{round(100 * submission.upvote_ratio)}%",
                    s_all_awards,
                    s_link,
                ]
                subs.loc[len(subs)] = data
    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")
    return subs


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_due_dilligence(
    symbol: str, limit: int = 5, n_days: int = 3, show_all_flairs: bool = False
) -> pd.DataFrame:
    """Gets due diligence posts from list of subreddits [Source: reddit].

    Parameters
    ----------
    symbol: str
        Stock ticker
    limit: int
        Number of posts to get
    n_days: int
        Number of days back to get posts
    show_all_flairs: bool
        Search through all flairs (apart from Yolo and Meme)

    Returns
    -------
    pd.DataFrame
        Dataframe of submissions
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    psaw_api = PushshiftAPI()

    n_ts_after = int((datetime.today() - timedelta(days=n_days)).timestamp())
    l_flair_text = [
        "DD",
        "technical analysis",
        "Catalyst",
        "News",
        "Advice",
        "Chart",
        "Charts and Setups",
        "Fundamental Analysis",
        "forex",
        "Trade Idea",
    ]
    l_sub_reddits_dd = [
        "pennystocks",
        "RobinHoodPennyStocks",
        "Daytrading",
        "StockMarket",
        "stocks",
        "investing",
        "wallstreetbets",
        "forex",
        "Forexstrategy",
    ]

    submissions = psaw_api.search_submissions(
        after=int(n_ts_after), subreddit=l_sub_reddits_dd, q=symbol, filter=["id"]
    )
    n_flair_posts_found = 0
    columns = [
        "Date",
        "Subreddit",
        "Flair",
        "Title",
        "Score",
        "# Comments",
        "Upvote %",
        "Awards",
        "Link",
    ]
    subs = pd.DataFrame(columns=columns)

    try:
        for submission in submissions:
            # Get more information about post using PRAW api
            submission = praw_api.submission(id=submission.id)

            # Ensure that the post hasn't been removed in the meanwhile
            # Either just filter out Yolo, and Meme flairs, or focus on DD, based on b_DD flag
            if (
                not submission.removed_by_category
                and submission.link_flair_text in l_flair_text,
                submission.link_flair_text not in ["Yolo", "Meme"],
            )[show_all_flairs]:
                s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                s_link = f"https://old.reddit.com{submission.permalink}"
                s_all_awards = "".join(
                    f"{award['count']} {award['name']}\n"
                    for award in submission.all_awardings
                )

                s_all_awards = s_all_awards[:-2]

                data = [
                    s_datetime,
                    submission.subreddit,
                    submission.link_flair_text,
                    submission.title,
                    submission.score,
                    submission.num_comments,
                    f"{round(100 * submission.upvote_ratio)}%",
                    s_all_awards,
                    s_link,
                ]
                subs.loc[len(subs)] = data
                # Increment count of valid posts found
                n_flair_posts_found += 1

            # Check if number of wanted posts found has been reached
            if n_flair_posts_found > limit - 1:
                break
    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))

        if "received 401 HTTP response" in str(e):
            console.print("[red]Invalid API Key[/red]\n")
        else:
            console.print(f"[red]Invalid response: {str(e)}[/red]\n")
    return subs


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_posts_about(
    symbol: str,
    limit: int = 100,
    sortby: str = "relevance",
    time_frame: str = "week",
    full_search: bool = True,
    subreddits: str = "all",
) -> Tuple[pd.DataFrame, list, float]:
    """Finds posts related to a specific search term in Reddit.

    Parameters
    ----------
    symbol: str
        Ticker symbol to search for
    limit: int
        Number of posts to get per subreddit
    sortby: str
        Search type (Possibilities: "relevance", "hot", "top", "new", or "comments")
    time_frame: str
        Relative time of post (Possibilities: "hour", "day", "week", "month", "year", "all")
    full_search: bool
        Enable comprehensive search for ticker
    subreddits: str
        Comma-separated list of subreddits

    Returns
    -------
    Tuple[pd.DataFrame, list, float]:
        Dataframe of submissions related to the search term,
        List of polarity scores,
        Average polarity score.
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
        check_for_updates=False,
        comment_kind="t1",
        message_kind="t4",
        redditor_kind="t2",
        submission_kind="t3",
        subreddit_kind="t5",
        trophy_kind="t6",
        oauth_url="https://oauth.reddit.com",
        reddit_url="https://www.reddit.com",
        short_url="https://redd.it",
        ratelimit_seconds=5,
        timeout=16,
    )
    try:
        praw_api.user.me()
    except (Exception, ResponseException):
        console.print("[red]Wrong Reddit API keys[/red]\n")
        return pd.DataFrame()

    subreddits_l = subreddits.split(",")
    posts = []
    post_ids = set()
    console.print("Searching through subreddits for posts.")
    for sub_str in tqdm(subreddits_l):
        try:
            subreddit = praw_api.subreddit(sub_str)
        except Exception:
            console.print("Invalid subreddit name {sub_str}, skipping")
            continue
        submissions = subreddit.search(
            query=symbol,
            limit=limit,
            sort=sortby,
            time_filter=time_frame,
        )
        for sub in submissions:
            if (
                sub.selftext
                and sub.title
                and not sub.removed_by_category
                and sub.id not in post_ids
            ):
                post_ids.add(sub.id)
                posts.append(sub)

    polarity_scores = []
    post_data = []
    console.print("Analyzing each post...")
    for p in tqdm(posts):
        texts = [p.title, p.selftext]
        if full_search:
            tlcs = get_comments(p)
            texts.extend(tlcs)
        preprocessed_text = clean_reddit_text(texts)
        sentiment = get_sentiment(preprocessed_text)
        polarity_scores.append(sentiment)
        post_data.append([p.title, sentiment])

    avg_polarity = sum(polarity_scores) / len(polarity_scores)

    columns = ["Title", "Polarity Score"]
    df = pd.DataFrame(post_data, columns=columns)

    return df, polarity_scores, avg_polarity


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_comments(
    post: praw.models.reddit.submission.Submission,
) -> List[praw.models.reddit.comment.Comment]:
    """Recursively gets comments from a post.

    Parameters
    ----------
    post: praw.models.reddit.submission.Submission
        Post to get comments from

    Returns
    -------
    list[praw.models.reddit.comment.Comment]
        List of all comments on the post
    """

    def get_more_comments(comments):
        sub_tlcs = []
        for comment in comments:
            if isinstance(comment, praw.models.reddit.comment.Comment):
                sub_tlcs.append(comment.body)
            else:
                sub_comments = get_more_comments(comment.comments())
                sub_tlcs.extend(sub_comments)
        return sub_tlcs

    if post.comments:
        return get_more_comments(post.comments)
    return []


@log_start_end(log=logger)
def clean_reddit_text(docs: List[str]) -> List[str]:
    """Tokenizes and cleans a list of documents for sentiment analysis.

    Parameters
    ----------
    docs: list[str]
        A list of documents to prepare for sentiment analysis

    Returns
    -------
    list[str]
        List of cleaned and prepared docs
    """
    stopwords = _stop_words.ENGLISH_STOP_WORDS
    clean_docs = []
    docs = [doc.lower().strip() for doc in docs]

    for doc in docs:
        clean_doc = []
        tokens = doc.split()
        for tok in tokens:
            clean_tok = [c for c in tok if c.isalpha()]
            tok = "".join(clean_tok)
            if tok not in stopwords:
                clean_doc.append(tok)
        clean_docs.append(" ".join(clean_doc))
    return clean_docs


@log_start_end(log=logger)
@check_api_key(
    [
        "API_REDDIT_CLIENT_ID",
        "API_REDDIT_CLIENT_SECRET",
        "API_REDDIT_USERNAME",
        "API_REDDIT_USER_AGENT",
        "API_REDDIT_PASSWORD",
    ]
)
def get_sentiment(post_data: List[str]) -> float:
    """Find the sentiment of a post and related comments.

    Parameters
    ----------
    post_data: list[str]
        A post and its comments in string form

    Returns
    -------
    float
        A number in the range [-1, 1] representing sentiment
    """
    analyzer = SentimentIntensityAnalyzer()
    post_data_l = " ".join(post_data)
    sentiment = analyzer.polarity_scores(post_data_l)
    score = sentiment["pos"] - sentiment["neg"]
    return (score - 0.06) * 8
