"""Reddit View"""
__docformat__ = "numpy"
import argparse
import os
import warnings
from typing import List, Dict
from datetime import datetime, timedelta
from prettytable import PrettyTable
from tabulate import tabulate
from prawcore.exceptions import ResponseException
from psaw import PushshiftAPI
import praw
import finviz
from gamestonk_terminal.helper_funcs import (
    check_positive,
    export_data,
    parse_known_args_and_warn,
)
from gamestonk_terminal import config_terminal as cfg

from gamestonk_terminal.common.behavioural_analysis import reddit_model
from gamestonk_terminal import feature_flags as gtff

# pylint:disable=assignment-from-no-return
# pylint:disable=not-an-iterable
# pylint:disable=inconsistent-return-statements


def find_tickers(a):
    a += 1


def print_and_record_reddit_post(submissions_dict, submission):
    # Refactor data
    s_datetime = datetime.utcfromtimestamp(submission.created_utc).strftime(
        "%d/%m/%Y %H:%M:%S"
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


def display_spac_community(limit: int = 20, popular: bool = True):
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


def display_spac(other_args: List[str]):
    """Look at posts containing 'spac' in top communities

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="spac",
        description="""Show other users SPACs announcement. [Source: Reddit]""",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_limit",
        type=check_positive,
        default=5,
        help="limit of posts with SPACs retrieved.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        praw_api = praw.Reddit(
            client_id=cfg.API_REDDIT_CLIENT_ID,
            client_secret=cfg.API_REDDIT_CLIENT_SECRET,
            username=cfg.API_REDDIT_USERNAME,
            user_agent=cfg.API_REDDIT_USER_AGENT,
            password=cfg.API_REDDIT_PASSWORD,
        )

        d_submission: Dict = {}
        d_watchlist_tickers: Dict = {}
        l_watchlist_links = []
        l_watchlist_author = []

        # n_ts_after = int(
        #    (datetime.today() - timedelta(days=ns_parser.n_days)).timestamp()
        # )
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

        warnings.filterwarnings("ignore")  # To avoid printing the warning
        psaw_api = PushshiftAPI()
        submissions = psaw_api.search_submissions(
            # after=n_ts_after,
            subreddit=l_sub_reddits,
            q="SPAC|Spac|spac|Spacs|spacs",
            filter=["id"],
        )
        n_flair_posts_found = 0
        while True:
            try:
                submission = next(submissions, None)
                if submission:
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

                            l_watchlist_links.append(
                                f"https://old.reddit.com{submission.permalink}"
                            )

                            print_and_record_reddit_post(d_submission, submission)

                            # Increment count of valid posts found
                            n_flair_posts_found += 1

                    # Check if number of wanted posts found has been reached
                    if n_flair_posts_found > ns_parser.n_limit - 1:
                        break

                # Check if search_submissions didn't get anymore posts
                else:
                    break
            except ResponseException:
                print(
                    "Received a response from Reddit with an authorization error. check your token.\n"
                )
                return

        if n_flair_posts_found:
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

    except Exception as e:
        print(e, "\n")


def wsb_community(other_args: List[str]):
    """Print what WSB gang are up to in subreddit wallstreetbets. [Source: Reddit]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="wsb",
        description="""Print what WSB gang are up to in subreddit wallstreetbets. [Source: Reddit]""",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_limit",
        type=check_positive,
        default=10,
        help="limit of posts to print.",
    )
    parser.add_argument(
        "-n",
        "--new",
        action="store_true",
        default=False,
        dest="b_new",
        help="new flag, if true the posts retrieved are based on being more recent rather than their score.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        praw_api = praw.Reddit(
            client_id=cfg.API_REDDIT_CLIENT_ID,
            client_secret=cfg.API_REDDIT_CLIENT_SECRET,
            username=cfg.API_REDDIT_USERNAME,
            user_agent=cfg.API_REDDIT_USER_AGENT,
            password=cfg.API_REDDIT_PASSWORD,
        )

        d_submission: Dict = {}
        l_watchlist_links = []

        # psaw_api = PushshiftAPI()

        if ns_parser.b_new:
            submissions = praw_api.subreddit("wallstreetbets").new(
                limit=ns_parser.n_limit
            )
        else:
            submissions = praw_api.subreddit("wallstreetbets").hot(
                limit=ns_parser.n_limit
            )
        while True:
            try:
                submission = next(submissions, None)
                if submission:
                    # Get more information about post using PRAW api
                    submission = praw_api.submission(id=submission.id)

                    # Ensure that the post hasn't been removed  by moderator in the meanwhile,
                    # that there is a description and it's not just an image, that the flair is
                    # meaningful, and that we aren't re-considering same author's watchlist
                    if not submission.removed_by_category:

                        l_watchlist_links.append(
                            f"https://old.reddit.com{submission.permalink}"
                        )

                        print_and_record_reddit_post(d_submission, submission)

                # Check if search_submissions didn't get anymore posts
                else:
                    break
            except ResponseException:
                print(
                    "Received a response from Reddit with an authorization error. check your token.\n"
                )
                return
    except Exception as e:
        print(e, "\n")


def get_due_diligence(other_args: List[str], ticker: str):
    """Display Reddit due diligence data for a given ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-l", "5"]
    ticker : str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="getdd",
        description="""
            Print top stock's due diligence from other users. [Source: Reddit]
        """,
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_limit",
        type=check_positive,
        default=5,
        help="limit of posts to retrieve.",
    )
    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days",
        type=check_positive,
        default=3,
        help="number of prior days to look for.",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="b_all",
        default=False,
        help="""
            search through all flairs (apart from Yolo and Meme), otherwise we focus on
            specific flairs: DD, technical analysis, Catalyst, News, Advice, Chart
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        praw_api = praw.Reddit(
            client_id=cfg.API_REDDIT_CLIENT_ID,
            client_secret=cfg.API_REDDIT_CLIENT_SECRET,
            username=cfg.API_REDDIT_USERNAME,
            user_agent=cfg.API_REDDIT_USER_AGENT,
            password=cfg.API_REDDIT_PASSWORD,
        )

        psaw_api = PushshiftAPI()

        n_ts_after = int(
            (datetime.today() - timedelta(days=ns_parser.n_days)).timestamp()
        )
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
        l_sub_reddits = [
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
            after=int(n_ts_after), subreddit=l_sub_reddits, q=ticker, filter=["id"]
        )
        d_submission = {}  # type: ignore
        n_flair_posts_found = 0
        while True:
            submission = next(submissions, None)
            if submission:
                # Get more information about post using PRAW api
                submission = praw_api.submission(id=submission.id)

                # Ensure that the post hasn't been removed in the meanwhile
                if not submission.removed_by_category:

                    # Either just filter out Yolo, and Meme flairs, or focus on DD, based on b_DD flag
                    if (
                        submission.link_flair_text in l_flair_text,
                        submission.link_flair_text not in ["Yolo", "Meme"],
                    )[ns_parser.b_all]:

                        print_and_record_reddit_post(d_submission, submission)

                        # If needed, submission.comments could give us the top comments

                        # Increment count of valid posts found
                        n_flair_posts_found += 1

                # Check if number of wanted posts found has been reached
                if n_flair_posts_found > ns_parser.n_limit - 1:
                    break

            # Check if search_submissions didn't get anymore posts
            else:
                break

        print(
            f"{('No more posts with specified requirements found.', '')[n_flair_posts_found > ns_parser.n_limit-1]}",
            "\n",
        )
        # Create df with found data. Useful for saving all info in excel file.
        # df_submissions = pd.DataFrame.from_dict(
        #   d_submission, orient='index', columns=list(d_submission[next(iter(d_submission.keys()))].keys())
        # )
        # df_submissions.sort_values(by=['created_utc'], inplace=True, ascending=True)

    except Exception as e:
        print(e)
        print("")
