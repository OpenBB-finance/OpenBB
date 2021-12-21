"""Behavioural Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union
from datetime import datetime, timedelta
import textwrap
from prompt_toolkit.completion import NestedCompleter
from colorama import Style
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    get_flair,
    parse_known_args_and_warn,
    check_int_range,
    valid_date,
    check_positive,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.common.behavioural_analysis import (
    google_view,
    reddit_view,
    stocktwits_view,
    finbrain_view,
    finnhub_view,
    twitter_view,
)
from gamestonk_terminal.stocks import stocks_helper

# pylint:disable=R0904,C0302


class BehaviouralAnalysisController:
    """Behavioural Analysis Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]
    CHOICES_COMMANDS = [
        "load",
        "watchlist",
        "spac",
        "spac_c",
        "wsb",
        "popular",
        "bullbear",
        "messages",
        "trending",
        "stalker",
        "infer",
        "sentiment",
        "mentions",
        "regions",
        "queries",
        "rise",
        "headlines",
        "stats",
        "metrics",
        "social",
        "historical",
        "emerging",
        "popular",
        "popularsi",
        "getdd",
    ]
    CHOICES += CHOICES_COMMANDS

    historical_sort = ["date", "value"]
    historical_direction = ["asc", "desc"]
    historical_metric = ["sentiment", "AHI", "RHI", "SGP"]

    def __init__(self, ticker: str, start: datetime, queue: List[str] = None):
        """Constructor"""
        self.ba_parser = argparse.ArgumentParser(add_help=False, prog="ba")
        self.ba_parser.add_argument(
            "cmd",
            choices=self.CHOICES + self.CHOICES_COMMANDS,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["historical"]["-s"] = {c: None for c in self.historical_sort}
            choices["historical"]["--sort"] = {c: None for c in self.historical_sort}
            choices["historical"]["-d"] = {c: None for c in self.historical_direction}
            choices["historical"]["--direction"] = {
                c: None for c in self.historical_direction
            }
            choices["historical"]["-m"] = {c: None for c in self.historical_metric}
            choices["historical"]["--metric"] = {
                c: None for c in self.historical_metric
            }
            choices["historical"] = {c: None for c in self.historical_metric}

            self.completer = NestedCompleter.from_nested_dict(choices)

        self.ticker = ticker
        self.start = start

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        dim = Style.DIM if not self.ticker else ""
        res = Style.RESET_ALL
        help_txt = f"""
    load           load a specific stock ticker for analysis

Ticker: {self.ticker.upper() or None}

Finbrain:{dim}
    headlines     sentiment from 15+ major news headlines {res}
Finnhub:{dim}
    stats         sentiment stats including comparison with sector{res}
Reddit:
    wsb           show what WSB gang is up to in subreddit wallstreetbets
    watchlist     show other users watchlist
    popular       show popular tickers
    spac_c        show other users spacs announcements from subreddit SPACs community
    spac          show other users spacs announcements from other subs{dim}
    getdd         gets due diligence from another user's post{res}
Stocktwits:{dim}
    bullbear      estimate quick sentiment from last 30 messages on board
    messages      output up to the 30 last messages on the board{res}
    trending      trending stocks
    stalker       stalk stocktwits user's last messages
Twitter:{dim}
    infer         infer about stock's sentiment from latest tweets
    sentiment     in-depth sentiment prediction from tweets over time{res}
Google:{dim}
    mentions      interest over time based on stock's mentions
    regions       regions that show highest interest in stock
    queries       top related queries with this stock
    rise          top rising related queries with stock{res}
SentimentInvestor:
    popularsi     show most popular stocks on social media right now
    emerging      show stocks that are being talked about more than usual{dim}
    metrics       core social sentiment metrics for this stock
    social        social media figures for stock popularity
    historical    plot the past week of data for a selected metric{res}
        """
        print(help_txt)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            print("")
            return None

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.ba_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        return self.queue

    def call_help(self, _):
        """Process help command"""
        self.print_help()
        return self.queue

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "quit"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "ba")
            self.queue.insert(0, "stocks")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "reset", "stocks", "ba"]

    @try_except
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be"
            " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            df_stock_candidate = stocks_helper.load(
                ns_parser.ticker,
                ns_parser.start,
            )
            if not df_stock_candidate.empty:
                self.start = ns_parser.start
                if "." in ns_parser.ticker:
                    self.ticker = ns_parser.ticker.upper().split(".")[0]
                else:
                    self.ticker = ns_parser.ticker.upper()
            else:
                print("Provide a valid ticker")

        return self.queue

    @try_except
    def call_watchlist(self, other_args: List[str]):
        """Process watchlist command"""
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
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of posts with watchlists retrieved.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            reddit_view.display_watchlist(num=ns_parser.limit)

        return self.queue

    @try_except
    def call_spac(self, other_args: List[str]):
        """Process spac command"""
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            reddit_view.display_spac(limit=ns_parser.n_limit)

        return self.queue

    @try_except
    def call_spac_c(self, other_args: List[str]):
        """Process spac_c command"""
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            reddit_view.display_spac_community(
                limit=ns_parser.n_limit, popular=ns_parser.b_popular
            )

        return self.queue

    @try_except
    def call_wsb(self, other_args: List[str]):
        """Process wsb command"""
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            reddit_view.display_wsb_community(
                limit=ns_parser.n_limit, new=ns_parser.b_new
            )

        return self.queue

    @try_except
    def call_popular(self, other_args: List[str]):
        """Process popular command"""
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
            default=50,
            help="number of posts retrieved per sub reddit.",
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            reddit_view.display_popular_tickers(
                n_top=ns_parser.limit,
                posts_to_look_at=ns_parser.num,
                subreddits=ns_parser.s_subreddit,
            )

        return self.queue

    @try_except
    def call_getdd(self, other_args: List[str]):
        """Process getdd command"""
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                reddit_view.display_due_diligence(
                    ticker=self.ticker,
                    limit=ns_parser.limit,
                    n_days=ns_parser.days,
                    show_all_flairs=ns_parser.all,
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_bullbear(self, other_args: List[str]):
        """Process bullbear command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bullbear",
            description="""
                Print bullbear sentiment based on last 30 messages on the board.
                Also prints the watchlist_count. [Source: Stocktwits]
            """,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                stocktwits_view.display_bullbear(ticker=self.ticker)
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_messages(self, other_args: List[str]):
        """Process messages command"""
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                stocktwits_view.display_messages(
                    ticker=self.ticker, limit=ns_parser.limit
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_trending(self, other_args: List[str]):
        """Process trending command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="trending",
            description="""Stocks trending. [Source: Stocktwits]""",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            stocktwits_view.display_trending()

        return self.queue

    @try_except
    def call_stalker(self, other_args: List[str]):
        """Process stalker command"""
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stocktwits_view.display_stalker(
                user=ns_parser.s_user, limit=ns_parser.limit
            )

        return self.queue

    @try_except
    def call_mentions(self, other_args: List[str]):
        """Process mentions command"""
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
            default=self.start,
            help="starting date (format YYYY-MM-DD) from when we are interested in stock's mentions.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                google_view.display_mentions(
                    ticker=self.ticker, start=ns_parser.start, export=ns_parser.export
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_regions(self, other_args: List[str]):
        """Process regions command"""
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                google_view.display_regions(
                    ticker=self.ticker, num=ns_parser.limit, export=ns_parser.export
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_queries(self, other_args: List[str]):
        """Process queries command"""
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                google_view.display_queries(
                    ticker=self.ticker, num=ns_parser.limit, export=ns_parser.export
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_rise(self, other_args: List[str]):
        """Process rise command"""
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                google_view.display_rise(
                    ticker=self.ticker, num=ns_parser.limit, export=ns_parser.export
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_infer(self, other_args: List[str]):
        """Process infer command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="infer",
            description="""
                Print quick sentiment inference from last tweets that contain the ticker.
                This model splits the text into character-level tokens and uses vader sentiment analysis.
                [Source: Twitter]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(10, 100),
            default=100,
            help="limit of latest tweets to infer from.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                twitter_view.display_inference(ticker=self.ticker, num=ns_parser.limit)
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_sentiment(self, other_args: List[str]):
        """Process sentiment command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sentiment",
            description="""
                Plot in-depth sentiment predicted from tweets from last days
                that contain pre-defined ticker. [Source: Twitter]
            """,
        )
        # in reality this argument could be 100, but after testing it takes too long
        # to compute which may not be acceptable
        # TODO: use https://github.com/twintproject/twint instead of twitter API
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(10, 62),
            default=15,
            help="limit of tweets to extract per hour.",
        )
        parser.add_argument(
            "-d",
            "--days",
            action="store",
            dest="n_days_past",
            type=check_int_range(1, 6),
            default=6,
            help="number of days in the past to extract tweets.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                twitter_view.display_sentiment(
                    ticker=self.ticker,
                    n_tweets=ns_parser.limit,
                    n_days_past=ns_parser.n_days_past,
                    export=ns_parser.export,
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_headlines(self, other_args: List[str]):
        """Process finbrain command"""
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                finbrain_view.display_sentiment_analysis(
                    ticker=self.ticker, export=ns_parser.export
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_stats(self, other_args: List[str]):
        """Process stats command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stats",
            description="""
                Sentiment stats which displays buzz, news score, articles last week, articles weekly average,
                bullish vs bearish percentages, sector average bullish percentage, and sector average news score.
                [Source: https://finnhub.io]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                finnhub_view.display_sentiment_stats(
                    ticker=self.ticker, export=ns_parser.export
                )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_metrics(self, other_args: List[str]):
        """Process metrics command"""
        command_description = f"""
        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.

        The {Style.BRIGHT}metrics{Style.RESET_ALL} command prints the following realtime metrics:

        {Style.BRIGHT}AHI (Absolute Hype Index){Style.RESET_ALL}
        ---
        AHI is a measure of how much people are talking about a stock on social media.
        It is calculated by dividing the total number of mentions for the chosen stock
        on a social network by the mean number of mentions any stock receives on that
        social medium.

        {Style.BRIGHT}RHI (Relative Hype Index){Style.RESET_ALL}
        ---
        RHI is a measure of whether people are talking about a stock more or less than
        usual, calculated by dividing the mean AHI for the past day by the mean AHI for
        for the past week for that stock.

        {Style.BRIGHT}Sentiment Score{Style.RESET_ALL}
        ---
        Sentiment score is the percentage of people talking positively about the stock.
        For each social network the number of positive posts/comments is divided by the
        total number of both positive and negative posts/comments.

        {Style.BRIGHT}SGP (Standard General Perception){Style.RESET_ALL}
        ---
        SGP is a measure of whether people are more or less positive about a stock than
        usual. It is calculated by averaging the past day of sentiment values and then
        dividing it by the average of the past week of sentiment values.
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="metrics",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(command_description),
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                print(
                    "Currently under maintenance by the new Sentiment Investor team.\n"
                )
                # sentimentinvestor_view.display_metrics(ticker=self.ticker)
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_social(self, other_args: List[str]):
        """Process social command"""
        command_description = f"""
        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.

        The {Style.BRIGHT}social{Style.RESET_ALL} command prints the raw data for a given stock, including the number
        of mentions it has received on social media in the last hour and the sentiment
        score of those comments.
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="social",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(command_description),
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                print(
                    "Currently under maintenance by the new Sentiment Investor team.\n"
                )
                # sentimentinvestor_view.display_social(ticker=self.ticker)
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        command_description = f"""
        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.

        The {Style.BRIGHT}historical{Style.RESET_ALL} command plots the past week of data for a selected metric, one of:

        {Style.BRIGHT}AHI (Absolute Hype Index){Style.RESET_ALL}
        ---
        AHI is a measure of how much people are talking about a stock on social media.
        It is calculated by dividing the total number of mentions for the chosen stock
        on a social network by the mean number of mentions any stock receives on that
        social medium.

        {Style.BRIGHT}RHI (Relative Hype Index){Style.RESET_ALL}
        ---
        RHI is a measure of whether people are talking about a stock more or less than
        usual, calculated by dividing the mean AHI for the past day by the mean AHI for
        for the past week for that stock.

        {Style.BRIGHT}Sentiment Score{Style.RESET_ALL}
        ---
        Sentiment score is the percentage of people talking positively about the stock.
        For each social network the number of positive posts/comments is divided by the
        total number of both positive and negative posts/comments.

        {Style.BRIGHT}SGP (Standard General Perception){Style.RESET_ALL}
        ---
        SGP is a measure of whether people are more or less positive about a stock than
        usual. It is calculated by averaging the past day of sentiment values and then
        dividing it by the average of the past week of sentiment values.
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="historical",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(command_description),
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            type=str,
            default="date",
            help="the parameter to sort output table by",
            dest="sort_param",
            choices=self.historical_sort,
        )
        parser.add_argument(
            "-d",
            "--direction",
            action="store",
            type=str,
            default="desc",
            help="the direction to sort the output table",
            dest="sort_dir",
            choices=self.historical_direction,
        )
        parser.add_argument(
            "-m",
            "--metric",
            type=str,
            action="store",
            default="sentiment",
            dest="metric",
            choices=self.historical_metric,
            help="the metric to plot",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-m")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                print(
                    "Currently under maintenance by the new Sentiment Investor team.\n"
                )
                # sentimentinvestor_view.display_historical(
                #    ticker=self.ticker,
                #    sort_param=ns_parser.sort_param,
                #    metric=ns_parser.metric,
                #    sort_dir=ns_parser.sort_dir,
                # )
            else:
                print("No ticker loaded. Please load using 'load <ticker>'\n")

        return self.queue

    @try_except
    def call_popularsi(self, other_args: List[str]):
        """Process popular command"""
        command_description = f"""
        The {Style.BRIGHT}popular{Style.RESET_ALL} command prints the stocks with highest Average Hype Index right now.

        {Style.BRIGHT}AHI (Absolute Hype Index){Style.RESET_ALL}
        ---
        AHI is a measure of how much people are talking about a stock on social media.
        It is calculated by dividing the total number of mentions for the chosen stock
        on a social network by the mean number of mentions any stock receives on that
        social medium.

        ===

        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="popularsi",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(command_description),
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=10,
            help="the maximum number of stocks to retrieve",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            print("Currently under maintenance by the new Sentiment Investor team.\n")
            # sentimentinvestor_view.display_top(metric="AHI", limit=ns_parser.limit)

        return self.queue

    @try_except
    def call_emerging(self, other_args: List[str]):
        """Process emerging command"""
        command_description = f"""
        The {Style.BRIGHT}emerging{Style.RESET_ALL} command prints the stocks with highest Relative Hype Index right now.

        {Style.BRIGHT}RHI (Relative Hype Index){Style.RESET_ALL}
        ---
        RHI is a measure of whether people are talking about a stock more or less than
        usual, calculated by dividing the mean AHI for the past day by the mean AHI for
        for the past week for that stock.

        ===

        {Style.BRIGHT}Sentiment Investor{Style.RESET_ALL} analyzes data from four major social media platforms to
        generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
        sentiment metrics powered by proprietary NLP models.
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="popular",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(command_description),
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=10,
            help="the maximum number of stocks to retrieve",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            print("Currently under maintenance by the new Sentiment Investor team.\n")
            # sentimentinvestor_view.display_top(metric="RHI", limit=ns_parser.limit)

        return self.queue


def menu(ticker: str, start: datetime, queue: List[str] = None):
    """Behavioural Analysis Menu"""
    ba_controller = BehaviouralAnalysisController(ticker, start, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if ba_controller.queue and len(ba_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if ba_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(ba_controller.queue) > 1:
                    return ba_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = ba_controller.queue[0]
            ba_controller.queue = ba_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in ba_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/ba/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                ba_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and ba_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/ba/ $ ",
                    completer=ba_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/ba/ $ ")

        try:
            # Process the input command
            ba_controller.queue = ba_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/ba menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                ba_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        ba_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                ba_controller.queue.insert(0, an_input)
            else:
                print("\n")
