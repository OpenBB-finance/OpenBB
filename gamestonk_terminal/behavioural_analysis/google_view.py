import argparse
from typing import List
from datetime import datetime
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
from gamestonk_terminal.helper_funcs import (
    check_positive,
    valid_date,
    parse_known_args_and_warn,
)


def mentions(other_args: List[str], ticker: str, start: datetime):
    """Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker
    start : str
        Start date
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="mentions",
        description="""
            Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]
        """,
    )
    parser.add_argument(
        "-s",
        "--start",
        type=valid_date,
        dest="start",
        default=start,
        help="starting date (format YYYY-MM-DD) from when we are interested in stock's mentions.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[ticker])
        df_interest = pytrend.interest_over_time()

        plt.title(f"Interest over time on {ticker}")
        if ns_parser.start:
            df_interest = df_interest[ns_parser.start :]
            plt.bar(df_interest.index, df_interest[ticker], width=2)
            plt.bar(
                df_interest.index[-1],
                df_interest[ticker].values[-1],
                color="tab:orange",
                width=2,
            )
        else:
            plt.bar(df_interest.index, df_interest[ticker], width=1)
            plt.bar(
                df_interest.index[-1],
                df_interest[ticker].values[-1],
                color="tab:orange",
                width=1,
            )

        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.ylabel("Interest [%]")
        plt.xlabel("Time")
        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def regions(other_args: List[str], ticker: str):
    """Plot bars of regions based on stock's interest. [Source: Google]

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="regions",
        description="""Plot bars of regions based on stock's interest. [Source: Google]""",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of regions to plot that show highest interest.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[ticker])
        df_interest_region = pytrend.interest_by_region()
        df_interest_region = df_interest_region.sort_values(
            [ticker], ascending=False
        ).head(ns_parser.n_num)

        plt.figure(figsize=(25, 5))
        plt.title(f"Top's regions interest on {ticker}")
        plt.bar(df_interest_region.index, df_interest_region[ticker], width=0.8)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.ylabel("Interest [%]")
        plt.xlabel("Region")
        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")


def queries(other_args: List[str], ticker: str):
    """Print top related queries with this stock's query. [Source: Google]

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="queries",
        description="""Print top related queries with this stock's query. [Source: Google]""",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of top related queries to print.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[ticker])
        df_related_queries = pytrend.related_queries()
        df_related_queries = df_related_queries[ticker]["top"].head(ns_parser.n_num)
        df_related_queries["value"] = df_related_queries["value"].apply(
            lambda x: str(x) + "%"
        )
        print(f"Top {ticker}'s related queries")
        print(df_related_queries.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def rise(other_args: List[str], ticker: str):
    """Print top rising related queries with this stock's query. [Source: Google]

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="rise",
        description="""Print top rising related queries with this stock's query. [Source: Google]""",
    )
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of top rising related queries to print.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[ticker])
        df_related_queries = pytrend.related_queries()
        df_related_queries = df_related_queries[ticker]["rising"].head(ns_parser.n_num)
        print(f"Top rising {ticker}'s related queries")
        print(df_related_queries.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")
