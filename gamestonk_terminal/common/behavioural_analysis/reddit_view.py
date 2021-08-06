import argparse
import warnings
from typing import List, Dict
import pandas as pd
from prawcore.exceptions import ResponseException
from requests import HTTPError
from psaw import PushshiftAPI
import praw
import finviz
from gamestonk_terminal.helper_funcs import check_positive, parse_known_args_and_warn
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import (
    print_and_record_reddit_post,
    find_tickers,
)


def watchlist(other_args: List[str]):
    """Print other users watchlist. [Source: Reddit]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="watchlist",
        description="""Print other users watchlist. [Source: Reddit]""",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_limit",
        type=check_positive,
        default=5,
        help="limit of posts with watchlists retrieved.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

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

        d_submission: Dict = {}
        d_watchlist_tickers: Dict = {}
        l_watchlist_links = list()
        l_watchlist_author = list()

        praw_api = praw.Reddit(
            client_id=cfg.API_REDDIT_CLIENT_ID,
            client_secret=cfg.API_REDDIT_CLIENT_SECRET,
            username=cfg.API_REDDIT_USERNAME,
            user_agent=cfg.API_REDDIT_USER_AGENT,
            password=cfg.API_REDDIT_PASSWORD,
        )

        # dt_last_time_market_close = get_last_time_market_was_open(
        #    datetime.now() - timedelta(hours=24)
        # )
        # n_ts_after = int(dt_last_time_market_close.timestamp())
        psaw_api = PushshiftAPI()
        submissions = psaw_api.search_submissions(
            # after=n_ts_after,
            subreddit=l_sub_reddits,
            q="WATCHLIST|Watchlist|watchlist",
            filter=["id"],
        )

        n_flair_posts_found = 0
        while True:
            try:
                submission = next(submissions, None)

                # Check if search_submissions didn't get anymore posts
                if not submission:
                    break

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
                    "The following stock tickers have been mentioned more than once across the previous watchlists:"
                )
                print(s_watchlist_tickers[:-2] + "\n")
        print("")

    except Exception as e:
        print(e, "\n")
        print("")


def popular_tickers(other_args: List[str]):
    """Print latest popular tickers. [Source: Reddit]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="popular",
        description="""Print latest popular tickers. [Source: Reddit]""",
    )
    parser.add_argument(
        "-n",
        "--number",
        action="store",
        dest="n_top",
        type=check_positive,
        default=10,
        help="display top N tickers",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_limit",
        type=check_positive,
        default=50,
        help="limit of posts retrieved per sub reddit.",
    )
    parser.add_argument(
        "-s",
        "--sub",
        action="store",
        dest="s_subreddit",
        type=str,
        help="""
            subreddits to look for tickers, e.g. pennystocks,stocks.
            Default: pennystocks, RobinHoodPennyStocks, Daytrading, StockMarket, stocks, investing,
            wallstreetbets
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # n_ts_after = int(
        #    (datetime.today() - timedelta(days=ns_parser.n_days)).timestamp()
        # )

        if ns_parser.s_subreddit:
            if "," in ns_parser.s_subreddit:
                l_sub_reddits = ns_parser.s_subreddit.split(",")
            else:
                l_sub_reddits = [ns_parser.s_subreddit]
        else:
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

        # d_submission = {}
        d_watchlist_tickers: Dict = {}
        # l_watchlist_links = list()
        l_watchlist_author = list()

        praw_api = praw.Reddit(
            client_id=cfg.API_REDDIT_CLIENT_ID,
            client_secret=cfg.API_REDDIT_CLIENT_SECRET,
            username=cfg.API_REDDIT_USERNAME,
            user_agent=cfg.API_REDDIT_USER_AGENT,
            password=cfg.API_REDDIT_PASSWORD,
        )

        psaw_api = PushshiftAPI()

        for s_sub_reddit in l_sub_reddits:
            print(
                f"Search for latest tickers under {ns_parser.n_limit} '{s_sub_reddit}' posts"
            )
            submissions = psaw_api.search_submissions(
                # after=int(n_ts_after),
                subreddit=s_sub_reddit,
                limit=ns_parser.n_limit,
                filter=["id"],
            )

            n_tickers = 0
            while True:
                try:
                    submission = next(submissions, None)
                    if submission:
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

                    # Check if search_submissions didn't get anymore posts
                    else:
                        break
                except ResponseException:
                    print(
                        "Received a response from Reddit with an authorization error. check your token.\n"
                    )
                    return

            print(f"  {n_tickers} potential tickers found.")

        lt_watchlist_sorted = sorted(
            d_watchlist_tickers.items(), key=lambda item: item[1], reverse=True
        )

        if lt_watchlist_sorted:
            n_top_stocks = 0
            # pylint: disable=redefined-outer-name
            popular_tickers = []
            for t_ticker in lt_watchlist_sorted:
                if n_top_stocks > ns_parser.n_top:
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
                        print(f"Unexpected exception from Finviz: {e}")
                except Exception as e:
                    print(e, "\n")
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

            print(f"\nThe following TOP {ns_parser.n_top} tickers have been mentioned:")

            print(popular_tickers_df, "\n")
        else:
            print("No tickers found")

        print("")

    except ResponseException:
        print(
            "Received a response from Reddit with an authorization error. check your token.\n"
        )
        return

    except Exception as e:
        print(e, "\n")


def spac_community(other_args: List[str]):
    """Print other users SPACs announcement under subreddit 'SPACs' [Source: Reddit]

    Parameters
    ----------
    other_args: List[str]
        Arguments for argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="spac_c",
        description="""Print other users SPACs announcement under subreddit 'SPACs'. [Source: Reddit]""",
    )
    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="n_limit",
        type=check_positive,
        default=10,
        help="limit of posts with SPACs retrieved",
    )
    parser.add_argument(
        "-p",
        "--popular",
        action="store_true",
        default=False,
        dest="b_popular",
        help="popular flag, if true the posts retrieved are based on score rather than time",
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
        l_watchlist_links = list()
        l_watchlist_author = list()

        # psaw_api = PushshiftAPI()

        if ns_parser.b_popular:
            submissions = praw_api.subreddit("SPACs").hot(limit=ns_parser.n_limit)
        else:
            submissions = praw_api.subreddit("SPACs").new(limit=ns_parser.n_limit)

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

                # Check if search_submissions didn't get anymore posts
                else:
                    break
            except ResponseException:
                print(
                    "Received a response from Reddit with an authorization error. check your token.\n"
                )
                return

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

    except Exception as e:
        print(e, "\n")


def spac(other_args: List[str]):
    """Show other users SPACs announcement [Source: Reddit]

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
        l_watchlist_links = list()
        l_watchlist_author = list()

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
        l_watchlist_links = list()

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
