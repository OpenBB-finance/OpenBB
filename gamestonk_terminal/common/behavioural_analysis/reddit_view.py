"""Reddit View"""
__docformat__ = "numpy"

import os
import warnings
from datetime import datetime
from typing import Dict

import finviz
import praw
from prettytable import PrettyTable
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.behavioural_analysis import reddit_model
from gamestonk_terminal.helper_funcs import export_data


def print_and_record_reddit_post(
    submissions_dict: Dict, submission: praw.models.reddit.submission.Submission
):
    """Prints reddit submission

    Parameters
    ----------
    submissions_dict : Dict
        Dictionary for storing reddit post information
    submission : praw.models.reddit.submission.Submission
        Submission to show
    """
    # Refactor data
    s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    s_link = f"https://old.reddit.com{submission.permalink}"
    s_all_awards = "".join(
        f"{award['count']} {award['name']}\n" for award in submission.all_awardings
    )

    s_all_awards = s_all_awards[:-2]
    # Create dictionary with data to construct dataframe allows to save data
    submissions_dict[submission.id] = {
        "created_utc": s_datetime,
        "subreddit": submission.subreddit,
        "link_flair_text": submission.link_flair_text,
        "title": submission.title,
        "score": submission.score,
        "link": s_link,
        "num_comments": submission.num_comments,
        "upvote_ratio": submission.upvote_ratio,
        "awards": s_all_awards,
    }
    # Print post data collected so far
    print(f"{s_datetime} - {submission.title}")
    print(f"{s_link}")
    t_post = PrettyTable(
        ["Subreddit", "Flair", "Score", "# Comments", "Upvote %", "Awards"]
    )
    t_post.add_row(
        [
            submission.subreddit,
            submission.link_flair_text,
            submission.score,
            submission.num_comments,
            f"{round(100 * submission.upvote_ratio)}%",
            s_all_awards,
        ]
    )
    print(t_post)
    print("\n")


def display_watchlist(num: int):
    """Print other users watchlist. [Source: Reddit]

    Parameters
    ----------
    num: int
        Maximum number of submissions to look at
    """
    subs, d_watchlist_tickers, n_flair_posts_found = reddit_model.get_watchlists(num)
    for sub in subs:
        print_and_record_reddit_post({}, sub)
    if n_flair_posts_found > 0:
        lt_watchlist_sorted = sorted(
            d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
        )
        s_watchlist_tickers = ""
        n_tickers = 0
        for t_ticker in lt_watchlist_sorted:
            try:
                # If try doesn't trigger exception, it means that this stock exists on finviz
                # thus we can print it.
                finviz.get_stock(t_ticker[0])
                if int(t_ticker[1]) > 1:
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                n_tickers += 1
            except Exception:
                # print(e, "\n")
                pass
        if n_tickers:
            print(
                "The following stock tickers have been mentioned more than once across the previous watchlists:"
            )
            print(s_watchlist_tickers[:-2] + "\n")

    print("")


def display_popular_tickers(
    n_top: int = 10, posts_to_look_at: int = 50, subreddits: str = "", export: str = ""
):
    """Print latest popular tickers. [Source: Reddit]

    Parameters
    ----------
    n_top : int
        Number of top tickers to get
    posts_to_look_at : int
        How many posts to analyze in each subreddit
    subreddits : str, optional
        String of comma separated subreddits.
    export : str
        Format to export dataframe
    """
    popular_tickers_df = reddit_model.get_popular_tickers(
        n_top, posts_to_look_at, subreddits
    )
    if not popular_tickers_df.empty:
        print(f"\nThe following TOP {n_top} tickers have been mentioned:")
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    popular_tickers_df,
                    headers=popular_tickers_df.columns,
                    tablefmt="fancy_grid",
                    showindex=False,
                )
            )
        else:
            print(popular_tickers_df.to_string())
    else:
        print("No tickers found")

    print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "popular",
        popular_tickers_df,
    )


def display_spac_community(limit: int = 10, popular: bool = False):
    """Look at tickers mentioned in r/SPACs [Source: Reddit]

    Parameters
    ----------
    limit: int
        Number of posts to look through
    popular: bool
        Search by popular instead of new
    """
    subs, d_watchlist_tickers = reddit_model.get_spac_community(limit, popular)
    for sub in subs:
        print_and_record_reddit_post({}, sub)

    if d_watchlist_tickers:
        lt_watchlist_sorted = sorted(
            d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
        )
        s_watchlist_tickers = ""
        n_tickers = 0
        for t_ticker in lt_watchlist_sorted:
            try:
                # If try doesn't trigger exception, it means that this stock exists on finviz
                # thus we can print it.
                finviz.get_stock(t_ticker[0])
                if int(t_ticker[1]) > 1:
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                n_tickers += 1
            except Exception:
                # print(e, "\n")
                pass

        if n_tickers:
            print(
                "The following stock tickers have been mentioned more than once across the previous SPACs:"
            )
            print(s_watchlist_tickers[:-2])
    print("")


def display_spac(limit: int = 5):
    """Look at posts containing 'spac' in top communities

    Parameters
    ----------
    limit: int
        Number of posts to get from each subreddit
    """
    warnings.filterwarnings("ignore")  # To avoid printing the warning
    subs, d_watchlist_tickers, n_flair_posts_found = reddit_model.get_spac(limit)
    for sub in subs:
        print_and_record_reddit_post({}, sub)

    if n_flair_posts_found > 0:
        lt_watchlist_sorted = sorted(
            d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
        )
        s_watchlist_tickers = ""
        n_tickers = 0
        for t_ticker in lt_watchlist_sorted:
            try:
                # If try doesn't trigger exception, it means that this stock exists on finviz
                # thus we can print it.
                finviz.get_stock(t_ticker[0])
                if int(t_ticker[1]) > 1:
                    s_watchlist_tickers += f"{t_ticker[1]} {t_ticker[0]}, "
                n_tickers += 1
            except Exception:
                pass
        if n_tickers:
            print(
                "The following stock tickers have been mentioned more than once across the previous SPACs:"
            )
            print(s_watchlist_tickers[:-2])
    print("")


def display_wsb_community(limit: int = 10, new: bool = False):
    """Show WSB posts

    Parameters
    ----------
    limit : int, optional
        Number of posts to look at, by default 10
    new : bool, optional
        Flag to sort by new instead of hot, by default False
    """
    subs = reddit_model.get_wsb_community(limit, new)

    for sub in subs:
        print_and_record_reddit_post({}, sub)


def display_due_diligence(
    ticker: str, limit: int = 10, n_days: int = 3, show_all_flairs: bool = False
):
    """Display Reddit due diligence data for a given ticker

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
    """
    subs = reddit_model.get_due_dilligence(ticker, limit, n_days, show_all_flairs)
    for sub in subs:
        print_and_record_reddit_post({}, sub)
    if not subs:
        print(f"No DD posts found for {ticker}\n")
