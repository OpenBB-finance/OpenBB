"""Behavioural Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime, timedelta
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console

from gamestonk_terminal.parent_classes import StockController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    check_int_range,
    valid_date,
    valid_hour,
    check_positive,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.common.behavioural_analysis import (
    google_view,
    reddit_view,
    stocktwits_view,
    finbrain_view,
    finnhub_view,
    twitter_view,
    sentimentinvestor_view,
)

# pylint:disable=R0904,C0302


class BehaviouralAnalysisController(StockController):
    """Behavioural Analysis Controller class"""

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
        "popular",
        "getdd",
        "hist",
        "trend",
    ]

    historical_sort = ["date", "value"]
    historical_direction = ["asc", "desc"]
    historical_metric = ["sentiment", "AHI", "RHI", "SGP"]
    PATH = "/stocks/ba/"

    def __init__(self, ticker: str, start: datetime, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        has_ticker_start = "" if self.ticker else "[unvl]"
        has_ticker_end = "" if self.ticker else "[/unvl]"
        help_text = f"""[cmds]
    load           load a specific stock ticker for analysis

[param]Ticker: [/param]{self.ticker.upper() or None}
{has_ticker_start}
[src][Finbrain][/src]
    headlines     sentiment from 15+ major news headlines
[src][Finnhub][/src]
    stats         sentiment stats including comparison with sector{has_ticker_end}
[src][Reddit][/src]
    wsb           show what WSB gang is up to in subreddit wallstreetbets
    watchlist     show other users watchlist
    popular       show popular tickers
    spac_c        show other users spacs announcements from subreddit SPACs community
    spac          show other users spacs announcements from other subs{has_ticker_start}
    getdd         gets due diligence from another user's post{has_ticker_end}
[src][Stocktwits][/src]
    trending      trending stocks
    stalker       stalk stocktwits user's last messages{has_ticker_start}
    bullbear      estimate quick sentiment from last 30 messages on board
    messages      output up to the 30 last messages on the board
[src][Twitter][/src]
    infer         infer about stock's sentiment from latest tweets
    sentiment     in-depth sentiment prediction from tweets over time
[src][Google][/src]
    mentions      interest over time based on stock's mentions
    regions       regions that show highest interest in stock
    queries       top related queries with this stock
    rise          top rising related queries with stock{has_ticker_end}
[src][SentimentInvestor][/src]
    trend         most talked about tickers within the last hour{has_ticker_start}
    hist          plot historical RHI and AHI data by hour{has_ticker_end}[/cmds]

        """
        console.print(text=help_text, menu="Stocks - Behavioural Analysis")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

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
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    def call_hist(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hist",
            description="Plot historical sentiment data of RHI and AHI by hour",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
            dest="start",
            required="--end" in other_args,
            help="The starting date (format YYYY-MM-DD) of the stock. Default: 7 days ago",
        )

        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.utcnow().strftime("%Y-%m-%d"),
            dest="end",
            required="--start" in other_args,
            help="The ending date (format YYYY-MM-DD) of the stock. Default: today",
        )
        parser.add_argument(
            "-n",
            "--number",
            default=100,
            type=check_positive,
            dest="number",
            help="Number of results returned from Sentiment Investor. Default: 100",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True, limit=10
        )

        if ns_parser:
            if self.ticker:
                sentimentinvestor_view.display_historical(
                    ticker=self.ticker,
                    start=ns_parser.start,
                    end=ns_parser.end,
                    number=ns_parser.number,
                    export=ns_parser.export,
                    raw=ns_parser.raw,
                    limit=ns_parser.limit,
                )
            else:
                console.print("No ticker loaded. Please load using 'load <ticker>'\n")

    def call_trend(self, other_args: List[str]):
        """Process trend command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="trend",
            description="Show most talked about tickers within the last one hour",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=datetime.utcnow().strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD). Default: Today",
        )

        parser.add_argument(
            "-hr",
            "--hour",
            type=valid_hour,
            default=0,
            dest="hour",
            help="Hour of the day in the 24-hour notation. Example: 14",
        )

        parser.add_argument(
            "-n",
            "--number",
            default=10,
            type=check_positive,
            dest="number",
            help="Number of results returned from Sentiment Investor. Default: 10",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )

        if ns_parser:
            sentimentinvestor_view.display_trending(
                start=ns_parser.start,
                hour=ns_parser.hour,
                export=ns_parser.export,
                number=ns_parser.number,
            )
