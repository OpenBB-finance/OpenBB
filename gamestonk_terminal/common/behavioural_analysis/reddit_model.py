"""Reddit Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import finviz
import pandas as pd
import praw
from prawcore.exceptions import ResponseException
from psaw import PushshiftAPI
from requests import HTTPError

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.common.behavioural_analysis.reddit_helpers import find_tickers
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

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

# pylint:disable=inconsistent-return-statements


@log_start_end(log=logger)
def get_watchlists(
    n_to_get: int,
) -> Tuple[List[praw.models.reddit.submission.Submission], Dict, int]:
    """Get reddit users watchlists [Source: reddit]

    Parameters
    ----------
    n_to_get : int
        Number of posts to look through

    Returns
    -------
    List[praw.models.reddit.submission.Submission]:
        List of reddit submissions
    Dict:
        Dictionary of tickers and counts
    int
        Count of how many posts were analyzed
    """
    d_watchlist_tickers: Dict = {}
    l_watchlist_author = []
    subs = []

    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
    )
    psaw_api = PushshiftAPI()
    submissions = psaw_api.search_submissions(
        subreddit=l_sub_reddits,
        q="WATCHLIST|Watchlist|watchlist",
        filter=["id"],
    )
    n_flair_posts_found = 0
    for sub in submissions:
        submission = praw_api.submission(id=sub.id)
        if submission:
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
            if n_flair_posts_found > n_to_get - 1:
                break
        else:
            logger.error("Invalid submission")
            console.print("[red]Invalid submission[/red]\n")
    return subs, d_watchlist_tickers, n_flair_posts_found


@log_start_end(log=logger)
def get_popular_tickers(
    n_top: int, posts_to_look_at: int, subreddits: str = ""
) -> pd.DataFrame:
    """Get popular tickers from list of subreddits [Source: reddit]

    Parameters
    ----------
    n_top : int
        Number of top tickers to get
    posts_to_look_at : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.

    Returns
    -------
    pd.DataFrame
        DataFrame of top tickers from supplied subreddits
    """
    if subreddits:
        sub_reddit_list = subreddits.split(",") if "," in subreddits else [subreddits]
    else:
        sub_reddit_list = l_sub_reddits
    d_watchlist_tickers: Dict = {}
    l_watchlist_author = []

    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
    )

    psaw_api = PushshiftAPI()
    for s_sub_reddit in sub_reddit_list:
        console.print(
            f"Search for latest tickers for {posts_to_look_at} '{s_sub_reddit}' posts"
        )
        submissions = psaw_api.search_submissions(
            subreddit=s_sub_reddit,
            limit=posts_to_look_at,
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
                    not submission.removed_by_category
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

            except ResponseException:
                logger.exception(
                    "Received a response from Reddit with an authorization error. Check your token."
                )
                console.print(
                    "Received a response from Reddit with an authorization error. Check your token.\n"
                )
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
            if n_top_stocks > n_top:
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
                return

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
def get_spac_community(
    limit: int, popular: bool
) -> Tuple[List[praw.models.reddit.submission.Submission], Dict]:
    """Get top tickers from r/SPACs [Source: reddit]

    Parameters
    ----------
    limit : int
        Number of posts to look at
    popular : bool
        Search by hot instead of new

    Returns
    -------
    List[praw.models.reddit.submission.Submission]:
        List of reddit submission
    Dict:
        Dictionary of tickers and number of mentions
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
    )

    d_watchlist_tickers: Dict = {}
    l_watchlist_author = []

    if popular:
        submissions = praw_api.subreddit("SPACs").hot(limit=limit)
    else:
        submissions = praw_api.subreddit("SPACs").new(limit=limit)

    subs = []
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
                subs.append(submission)
                # Lookup stock tickers within a watchlist
                for key in l_tickers_found:
                    if key in d_watchlist_tickers:
                        # Increment stock ticker found
                        d_watchlist_tickers[key] += 1
                    else:
                        # Initialize stock ticker found
                        d_watchlist_tickers[key] = 1
    return subs, d_watchlist_tickers


@log_start_end(log=logger)
def get_spac(
    limit: int = 5,
) -> Tuple[List[praw.models.reddit.submission.Submission], Dict, int]:
    """Get posts containing SPAC from top subreddits [Source: reddit]

    Parameters
    ----------
    limit : int, optional
        Number of posts to get for each subreddit, by default 5

    Returns
    -------
    List[praw.models.reddit.submission.Submission] :
        List of reddit submissions
    Dict :
        Dictionary of tickers and counts
    int :
        Number of posts found.
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
    )

    d_watchlist_tickers: Dict = {}
    l_watchlist_author = []
    subs = []
    psaw_api = PushshiftAPI()
    submissions = psaw_api.search_submissions(
        subreddit=l_sub_reddits,
        q="SPAC|Spac|spac|Spacs|spacs",
        filter=["id"],
    )
    n_flair_posts_found = 0
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
            subs.append(submission)
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

    return subs, d_watchlist_tickers, n_flair_posts_found


@log_start_end(log=logger)
def get_wsb_community(
    limit: int = 10, new: bool = False
) -> List[praw.models.reddit.submission.Submission]:
    """Get wsb posts [Source: reddit]

    Parameters
    ----------
    limit : int, optional
        Number of posts to get, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False

    Returns
    -------
    List[praw.models.reddit.submission.Submission]
        List of reddit submissions
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
    )

    if new:
        submissions = praw_api.subreddit("wallstreetbets").new(limit=limit)
    else:
        submissions = praw_api.subreddit("wallstreetbets").hot(limit=limit)

    subs = []
    try:
        for submission in submissions:
            submission = praw_api.submission(id=submission.id)
            # Ensure that the post hasn't been removed  by moderator in the meanwhile,
            # that there is a description and it's not just an image, that the flair is
            # meaningful, and that we aren't re-considering same author's watchlist
            if not submission.removed_by_category:
                subs.append(submission)
    except ResponseException as e:
        logger.exception("Invalid response: %s", str(e))
        console.print("[red]Invalid response[/red]\n")
    return subs


@log_start_end(log=logger)
def get_due_dilligence(
    ticker: str, limit: int = 5, n_days: int = 3, show_all_flairs: bool = False
) -> List[praw.models.reddit.submission.Submission]:
    """Gets due dilligence posts from list of subreddits [Source: reddit]

    Parameters
    ----------
    ticker: str
        Stock ticker
    limit: int
        Number of posts to get
    n_days: int
        Number of days back to get posts
    show_all_flairs: bool
        Search through all flairs (apart from Yolo and Meme)

    Returns
    -------
    List[praw.models.reddit.submission.Submission]
        List of submissions
    """
    praw_api = praw.Reddit(
        client_id=cfg.API_REDDIT_CLIENT_ID,
        client_secret=cfg.API_REDDIT_CLIENT_SECRET,
        username=cfg.API_REDDIT_USERNAME,
        user_agent=cfg.API_REDDIT_USER_AGENT,
        password=cfg.API_REDDIT_PASSWORD,
    )

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
        after=int(n_ts_after), subreddit=l_sub_reddits_dd, q=ticker, filter=["id"]
    )
    n_flair_posts_found = 0
    subs = []
    for submission in submissions:
        # Get more information about post using PRAW api
        submission = praw_api.submission(id=submission.id)

        # Ensure that the post hasn't been removed in the meanwhile
        if not submission.removed_by_category:

            # Either just filter out Yolo, and Meme flairs, or focus on DD, based on b_DD flag
            if (
                submission.link_flair_text in l_flair_text,
                submission.link_flair_text not in ["Yolo", "Meme"],
            )[show_all_flairs]:

                subs.append(submission)
                # Increment count of valid posts found
                n_flair_posts_found += 1

        # Check if number of wanted posts found has been reached
        if n_flair_posts_found > limit - 1:
            break

    return subs
