"""Behavioural Analysis Controller Module"""
__docformat__ = "numpy"
# pylint:disable=too-many-lines

import argparse
import os
from typing import List
from datetime import datetime
from prompt_toolkit.completion import NestedCompleter
from colorama import Style
import pandas as pd
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_int_range,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.common.behavioural_analysis import (
    google_view,
    reddit_view,
    stocktwits_view,
    finbrain_view,
    finnhub_view,
    sentimentinvestor_view,
    twitter_view,
)
from gamestonk_terminal.stocks.stocks_helper import load


class BehaviouralAnalysisController:
    """Behavioural Analysis Controller class"""

    # Command choices
    CHOICES = ["?", "cls", "help", "q", "quit", "load"]
    CHOICES_COMMANDS = [
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
        "finbrain",
        "stats",
        "metrics",
        "social",
        "historical",
        "emerging",
        "popular",
        "popularsi",
        "getdd",
    ]

    def __init__(self, ticker: str, start: datetime):
        """Constructor"""
        self.ticker = ticker
        self.start = start
        self.ba_parser = argparse.ArgumentParser(add_help=False, prog="ba")
        self.ba_parser.add_argument(
            "cmd",
            choices=self.CHOICES + self.CHOICES_COMMANDS,
        )

    def print_help(self):
        dim = Style.DIM if not self.ticker else ""
        res = Style.RESET_ALL
        help_string = f"""
>>>Behavioural Analysis:<<<

What would you like to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

Ticker: {self.ticker.upper() or None}

Finbrain:{dim}
    finbrain      sentiment from 15+ major news headlines {res}
Finnhub:{dim}
    stats         sentiment stats including comparison with sector{res}
Reddit:
    wsb           show what WSB gang is up to in subreddit wallstreetbets
    watchlist     show other users watchlist
    popular       show popular tickers
    spac_c        show other users spacs announcements from subreddit SPACs community
    spac          show other users spacs announcements from other subs
    getdd         gets due diligence from another user's post
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
    emerging      show stocks that are being talked about more than usual
    metrics       core social sentiment metrics for this stock{dim}
    social        social media figures for stock popularity
    historical    plot the past week of data for a selected metric{res}
        """
        print(help_string)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """
        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.ba_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def _check_ticker(self):
        """Checks if ticker loaded"""
        if not self.ticker:
            print("No ticker loaded.  Please load using 'load <ticker>'\n")
            return False
        return True

    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker, _, _, _ = load(
            other_args, self.ticker, "", "1440min", pd.DataFrame()
        )
        if "." in self.ticker:
            self.ticker = self.ticker.split(".")[0]

    def call_watchlist(self, other_args: List[str]):
        """Process watchlist command"""
        reddit_view.watchlist(other_args)

    def call_spac(self, other_args: List[str]):
        """Process spac command"""
        reddit_view.spac(other_args)

    def call_spac_c(self, other_args: List[str]):
        """Process spac_c command"""
        reddit_view.spac_community(other_args)

    def call_wsb(self, other_args: List[str]):
        """Process wsb command"""
        reddit_view.wsb_community(other_args)

    def call_popular(self, other_args: List[str]):
        """Process popular command"""
        reddit_view.popular_tickers(other_args)

    def call_getdd(self, other_args: List[str]):
        """Process getdd command"""
        reddit_view.get_due_diligence(other_args, self.ticker)

    def call_bullbear(self, other_args: List[str]):
        """Process bullbear command"""
        stocktwits_view.bullbear(other_args, self.ticker)

    def call_messages(self, other_args: List[str]):
        """Process messages command"""
        stocktwits_view.messages(other_args, self.ticker)

    def call_trending(self, other_args: List[str]):
        """Process trending command"""
        stocktwits_view.trending(other_args)

    def call_stalker(self, other_args: List[str]):
        """Process stalker command"""
        stocktwits_view.stalker(other_args)

    def call_mentions(self, other_args: List[str]):
        """Process mentions command"""
        google_view.mentions(other_args, self.ticker, self.start)

    def call_regions(self, other_args: List[str]):
        """Process regions command"""
        google_view.regions(other_args, self.ticker)

    def call_queries(self, other_args: List[str]):
        """Process queries command"""
        google_view.queries(other_args, self.ticker)

    def call_rise(self, other_args: List[str]):
        """Process rise command"""
        google_view.rise(other_args, self.ticker)

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
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_int_range(10, 100),
            default=100,
            help="num of latest tweets to infer from.",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if self._check_ticker():
                twitter_view.display_inference(ticker=self.ticker, num=ns_parser.n_num)
        except Exception as e:
            print(e, "\n")

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
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_tweets",
            type=check_int_range(10, 62),
            default=15,
            help="number of tweets to extract per hour.",
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
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            if self._check_ticker():
                twitter_view.display_sentiment(
                    ticker=self.ticker,
                    n_tweets=ns_parser.n_tweets,
                    n_days_past=ns_parser.n_days_past,
                    export=ns_parser.export,
                )
        except Exception as e:
            print(e, "\n")

    def call_finbrain(self, other_args: List[str]):
        """Process finbrain command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="finbrain",
            description="""FinBrain collects the news headlines from 15+ major financial news
                        sources on a daily basis and analyzes them to generate sentiment scores
                        for more than 4500 US stocks.FinBrain Technologies develops deep learning
                        algorithms for financial analysis and prediction, which currently serves
                        traders from more than 150 countries all around the world.
                        [Source:  https://finbrain.tech]""",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            if self._check_ticker():
                finbrain_view.display_sentiment_analysis(
                    ticker=self.ticker, export=ns_parser.export
                )
        except Exception as e:
            print(e, "\n")

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if self._check_ticker():
                finnhub_view.display_sentiment_stats(
                    ticker=self.ticker, export=ns_parser.export
                )

        except Exception as e:
            print(e, "\n")

    def call_metrics(self, other_args: List[str]):
        """Process metrics command"""
        sentimentinvestor_view.metrics(self.ticker, other_args)

    def call_social(self, other_args: List[str]):
        """Process social command"""
        sentimentinvestor_view.socials(self.ticker, other_args)

    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        sentimentinvestor_view.historical(self.ticker, other_args)

    def call_popularsi(self, other_args: List[str]):
        """Process popular command"""
        sentimentinvestor_view.sort_sentiment("AHI", other_args, "popularsi")

    def call_emerging(self, other_args: List[str]):
        """Process emerging command"""
        sentimentinvestor_view.sort_sentiment("RHI", other_args, "emerging")


def menu(ticker: str, start: datetime):
    """Behavioural Analysis Menu"""

    ba_controller = BehaviouralAnalysisController(ticker, start)
    ba_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ba_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(ba)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(ba)> ")

        try:
            process_input = ba_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
