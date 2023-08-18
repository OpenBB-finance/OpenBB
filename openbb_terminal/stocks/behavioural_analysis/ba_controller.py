"""Behavioural Analysis Controller Module."""
__docformat__ = "numpy"

import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Optional

import yfinance as yf

from openbb_terminal.common.behavioural_analysis import (
    finbrain_view,
    google_view,
    reddit_view,
    stocktwits_view,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative,
    check_positive,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks.behavioural_analysis import (
    finnhub_view,
    news_sentiment_view,
)

# pylint:disable=R0904,C0302


logger = logging.getLogger(__name__)


class BehaviouralAnalysisController(StockBaseController):
    """Behavioural Analysis Controller class."""

    CHOICES_COMMANDS = [
        "load",
        "wsb",
        "popular",
        "getdd",
        "redditsent",
        "bullbear",
        "messages",
        "trending",
        "stalker",
        "mentions",
        "regions",
        "queries",
        "rise",
        "headlines",
        "snews",
        "interest",
        "ns",
    ]

    historical_sort = ["date", "value"]
    historical_direction = ["asc", "desc"]
    historical_metric = ["sentiment", "AHI", "RHI", "SGP"]
    reddit_sort = ["relevance", "hot", "top", "new", "comments"]
    reddit_time = ["hour", "day", "week", "month", "year", "all"]
    PATH = "/stocks/ba/"
    CHOICES_GENERATION = True

    def __init__(self, ticker: str, start: datetime, queue: Optional[List[str]] = None):
        """Construct a new instance."""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("stocks/ba/")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker.upper())
        mt.add_raw("\n")
        mt.add_cmd("headlines", self.ticker)
        mt.add_cmd("snews", self.ticker)
        mt.add_cmd("wsb")
        mt.add_cmd("popular")
        mt.add_cmd("getdd")
        mt.add_cmd("redditsent", self.ticker)
        mt.add_cmd("trending")
        mt.add_cmd("stalker")
        mt.add_cmd("bullbear", self.ticker)
        mt.add_cmd("messages", self.ticker)
        mt.add_cmd("mentions", self.ticker)
        mt.add_cmd("regions", self.ticker)
        mt.add_cmd("interest", self.ticker)
        mt.add_cmd("queries", self.ticker)
        mt.add_cmd("rise", self.ticker)
        mt.add_cmd("ns")
        console.print(text=mt.menu_text, menu="Stocks - Behavioural Analysis")

    def custom_reset(self):
        """Class specific component of reset command."""
        if self.ticker:
            return ["stocks", "ba", f"load {self.ticker}"]
        return []

    @log_start_end(log=logger)
    def call_snews(self, other_args: List[str]):
        """Process snews command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="snews",
            description="Display stock price and headlines sentiment using VADER model over time. [Source: Finnhub]",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            finnhub_view.display_stock_price_headlines_sentiment(
                symbol=self.ticker, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_wsb(self, other_args: List[str]):
        """Process wsb command."""
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
            "--new",
            action="store_true",
            default=False,
            dest="b_new",
            help="new flag, if true the posts retrieved are based on being more recent rather than their score.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            reddit_view.display_wsb_community(
                limit=ns_parser.n_limit, new=ns_parser.b_new
            )

    @log_start_end(log=logger)
    def call_popular(self, other_args: List[str]):
        """Process popular command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="popular",
            description="""Print latest popular tickers. [Source: Reddit]""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of top tickers to retrieve",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="number of posts retrieved per sub reddit.",
        )
        parser.add_argument(
            "-s",
            "--sub",
            action="store",
            dest="s_subreddit",
            type=str,
            help="""
                Subreddits to look for tickers, e.g. pennystocks,stocks.
                Default: pennystocks, RobinHoodPennyStocks, Daytrading, StockMarket, stocks, investing,
                wallstreetbets
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            reddit_view.display_popular_tickers(
                limit=ns_parser.limit,
                post_limit=ns_parser.num,
                subreddits=ns_parser.s_subreddit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_getdd(self, other_args: List[str]):
        """Process getdd command."""
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
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of posts to retrieve.",
        )
        parser.add_argument(
            "-d",
            "--days",
            action="store",
            dest="days",
            type=check_positive,
            default=3,
            help="number of prior days to look for.",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            default=False,
            help="""
                search through all flairs (apart from Yolo and Meme), otherwise we focus on
                specific flairs: DD, technical analysis, Catalyst, News, Advice, Chart""",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            reddit_view.display_due_diligence(
                limit=ns_parser.limit,
                n_days=ns_parser.days,
                show_all_flairs=ns_parser.all,
            )

    @log_start_end(log=logger)
    def call_redditsent(self, other_args: List[str]):
        """Process redditsent command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="redditsent",
            description="""
                Determine general Reddit sentiment about a ticker. [Source: Reddit]
            """,
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            dest="sort",
            choices=self.reddit_sort,
            default="relevance",
            help="search sorting type",
        )
        parser.add_argument(
            "-c",
            "--company",
            action="store",
            dest="company",
            default=None,
            help="explicit name of company to search for, will override ticker symbol",
        )
        parser.add_argument(
            "--subreddits",
            action="store",
            dest="subreddits",
            default="all",
            help="comma-separated list of subreddits to search",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            default=10,
            type=check_positive,
            help="how many posts to gather from each subreddit",
        )
        parser.add_argument(
            "-t",
            "--time",
            action="store",
            dest="time",
            default="week",
            choices=self.reddit_time,
            help="time period to get posts from -- all, year, month, week, or day; defaults to week",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            dest="full_search",
            default=False,
            help="enable comprehensive search",
        )
        parser.add_argument(
            "-g",
            "--graphic",
            action="store_true",
            dest="graphic",
            default=True,
            help="display graphic",
        )
        parser.add_argument(
            "-d",
            "--display",
            action="store_true",
            dest="display",
            default=False,
            help="Print table of sentiment values",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            ticker = ns_parser.company if ns_parser.company else self.ticker
            if self.ticker:
                reddit_view.display_redditsent(
                    symbol=ticker,
                    sortby=ns_parser.sort,
                    limit=ns_parser.limit,
                    graphic=ns_parser.graphic,
                    time_frame=ns_parser.time,
                    full_search=ns_parser.full_search,
                    subreddits=ns_parser.subreddits,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    display=ns_parser.display,
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    @log_start_end(log=logger)
    def call_bullbear(self, other_args: List[str]):
        """Process bullbear command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bullbear",
            description="""
                Print bullbear sentiment based on last 30 messages on the board.
                Also prints the watchlist_count. [Source: Stocktwits]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                stocktwits_view.display_bullbear(symbol=self.ticker)
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    @log_start_end(log=logger)
    def call_messages(self, other_args: List[str]):
        """Process messages command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="messages",
            description="""Print up to 30 of the last messages on the board. [Source: Stocktwits]""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=30,
            help="limit messages shown.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                stocktwits_view.display_messages(
                    symbol=self.ticker, limit=ns_parser.limit
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    @log_start_end(log=logger)
    def call_trending(self, other_args: List[str]):
        """Process trending command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="trending",
            description="""Stocks trending. [Source: Stocktwits]""",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            stocktwits_view.display_trending()

    @log_start_end(log=logger)
    def call_stalker(self, other_args: List[str]):
        """Process stalker command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stalker",
            description="""Print up to the last 30 messages of a user. [Source: Stocktwits]""",
        )
        parser.add_argument(
            "-u",
            "--user",
            action="store",
            dest="s_user",
            type=str,
            default="Newsfilter",
            help="username.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=30,
            help="limit messages shown.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stocktwits_view.display_stalker(
                user=ns_parser.s_user, limit=ns_parser.limit
            )

    @log_start_end(log=logger)
    def call_mentions(self, other_args: List[str]):
        """Process mentions command."""
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
            default=self.start if self.start != "" else "2000-01-01",
            help="starting date (format YYYY-MM-DD) from when we are interested in stock's mentions.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                google_view.display_mentions(
                    symbol=self.ticker,
                    start_date=ns_parser.start,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    @log_start_end(log=logger)
    def call_regions(self, other_args: List[str]):
        """Process regions command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="regions",
            description="""Plot bars of regions based on stock's interest. [Source: Google]""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of regions to plot that show highest interest.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                google_view.display_regions(
                    symbol=self.ticker, limit=ns_parser.limit, export=ns_parser.export
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    @log_start_end(log=logger)
    def call_interest(self, other_args: List[str]):
        """Process interest command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="interest",
            description="""
                Plot interest over time of words/sentences versus stock price. [Source: Google]
            """,
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            dest="start",
            default=(datetime.now() - timedelta(days=2 * 366)).strftime("%Y-%m-%d"),
            help="starting date (format YYYY-MM-DD) of interest",
        )
        parser.add_argument(
            "-w",
            "--words",
            help="Select multiple sentences/words separated by commas. E.g. COVID,WW3,NFT",
            dest="words",
            nargs="+",
            type=str,
            default=None,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-w")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                if ns_parser.words:
                    words = " ".join(ns_parser.words).split(",")
                    df_stock = yf.download(
                        self.ticker,
                        start=ns_parser.start.strftime("%Y-%m-%d"),
                        progress=False,
                    )

                    if not df_stock.empty:
                        google_view.display_correlation_interest(
                            symbol=self.ticker,
                            data=df_stock,
                            words=words,
                            export=ns_parser.export,
                            sheet_name=" ".join(ns_parser.sheet_name)
                            if ns_parser.sheet_name
                            else None,
                        )
                    else:
                        console.print(
                            "[red]Ticker provided doesn't exist, load another one.\n[/red]"
                        )
                else:
                    console.print("[red]Please provide a phrase for analysis.\n[/red]")
            else:
                console.print(
                    "[red]No ticker loaded. Please load using 'load <ticker>'.\n[/red]"
                )

    @log_start_end(log=logger)
    def call_queries(self, other_args: List[str]):
        """Process queries command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="queries",
            description="""Print top related queries with this stock's query. [Source: Google]""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of top related queries to print.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                google_view.display_queries(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    @log_start_end(log=logger)
    def call_rise(self, other_args: List[str]):
        """Process rise command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rise",
            description="""Print top rising related queries with this stock's query. [Source: Google]""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of top rising related queries to print.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                google_view.display_rise(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    @log_start_end(log=logger)
    def call_headlines(self, other_args: List[str]):
        """Process finbrain command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="headlines",
            description="""FinBrain collects the news headlines from 15+ major financial news
                        sources on a daily basis and analyzes them to generate sentiment scores
                        for more than 4500 US stocks.FinBrain Technologies develops deep learning
                        algorithms for financial analysis and prediction, which currently serves
                        traders from more than 150 countries all around the world.
                        [Source:  https://finbrain.tech]""",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            if self.ticker:
                finbrain_view.display_sentiment_analysis(
                    symbol=self.ticker, raw=ns_parser.raw, export=ns_parser.export
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    def call_ns(self, other_args: List[str]):
        """Process ns command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ns",
            description="Shows the News Sentiment articles data",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            type=str,
            default=None,
            help="Ticker to search for.",
        )
        parser.add_argument(
            "-s",
            "--start_date",
            dest="start_date",
            type=str,
            default=None,
            help="The starting date (format YYYY-MM-DD) to search news articles from",
        )
        parser.add_argument(
            "-e",
            "--end_date",
            dest="end_date",
            type=str,
            default=None,
            help="The end date (format YYYY-MM-DD) to search news articles upto",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=str,
            default=None,
            help="""Shows the news articles data on this day (format YYYY-MM-DD).
                    If you use this Argument start date and end date will be ignored
                """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_non_negative,
            help="Number of news articles to be displayed.",
        )
        parser.add_argument(
            "-o",
            "--offset",
            default=0,
            dest="offset",
            type=check_non_negative,
            help="offset indicates the starting position of news articles.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker

            news_sentiment_view.display_articles_data(
                ticker=self.ticker,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                date=ns_parser.date,
                limit=ns_parser.limit,
                offset=ns_parser.offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
