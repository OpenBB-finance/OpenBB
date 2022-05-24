"""Comparison Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
import random
from datetime import datetime, timedelta
from typing import List

import yfinance as yf
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal.decorators import check_api_key
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative,
    check_positive,
    parse_known_args_and_warn,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.portfolio_optimization import po_controller
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.stocks.comparison_analysis import (
    finbrain_view,
    finnhub_model,
    finviz_compare_model,
    finviz_compare_view,
    marketwatch_view,
    polygon_model,
    yahoo_finance_model,
    yahoo_finance_view,
)

# pylint: disable=E1121,C0302,R0904

# TODO: HELP WANTED! This controller still has some view functionality that should be
#       refactored in order to implement an API wrapper. Use the discovery controller
#       as an example.


logger = logging.getLogger(__name__)


class ComparisonAnalysisController(BaseController):
    """Comparison Analysis Controller class"""

    CHOICES_COMMANDS = [
        "ticker",
        "getpoly",
        "getfinnhub",
        "getfinviz",
        "set",
        "add",
        "rmv",
        "historical",
        "hcorr",
        "volume",
        "income",
        "balance",
        "cashflow",
        "sentiment",
        "scorr",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
        "tsne",
    ]
    CHOICES_MENUS = [
        "po",
    ]
    PATH = "/stocks/ca/"

    def __init__(self, similar: List[str] = None, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ""
        self.user = ""

        if similar:
            self.similar = similar
            if len(similar) == 1:
                self.ticker = self.similar[0].upper()
        else:
            self.similar = []

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/ca/", 80)
        mt.add_cmd("ticker")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker)
        mt.add_raw("\n")
        mt.add_cmd("tsne", "", self.ticker)
        mt.add_cmd("getpoly", "Polygon", self.ticker)
        mt.add_cmd("getfinnhub", "Finnhub", self.ticker)
        mt.add_cmd("getfinviz", "Finviz", self.ticker)
        mt.add_raw("\n")
        mt.add_cmd("set")
        mt.add_cmd("add")
        mt.add_cmd("rmv")
        mt.add_raw("\n")
        mt.add_param("_similar", ", ".join(self.similar))
        mt.add_raw("\n")
        mt.add_cmd(
            "historical", "Yahoo Finance", self.similar and len(self.similar) > 1
        )
        mt.add_cmd("hcorr", "Yahoo Finance", self.similar and len(self.similar) > 1)
        mt.add_cmd("volume", "Yahoo Finance", self.similar and len(self.similar) > 1)
        mt.add_cmd("income", "Market Watch", self.similar and len(self.similar) > 1)
        mt.add_cmd("balance", "Market Watch", self.similar and len(self.similar) > 1)
        mt.add_cmd("cashflow", "Market Watch", self.similar and len(self.similar) > 1)
        mt.add_cmd("sentiment", "FinBrain", self.similar and len(self.similar) > 1)
        mt.add_cmd("scorr", "FinBrain", self.similar and len(self.similar) > 1)
        mt.add_cmd("overview", "Finviz", self.similar and len(self.similar) > 1)
        mt.add_cmd("valuation", "Finviz", self.similar and len(self.similar) > 1)
        mt.add_cmd("financial", "Finviz", self.similar and len(self.similar) > 1)
        mt.add_cmd("ownership", "Finviz", self.similar and len(self.similar) > 1)
        mt.add_cmd("performance", "Finviz", self.similar and len(self.similar) > 1)
        mt.add_cmd("technical", "Finviz", self.similar and len(self.similar) > 1)
        mt.add_raw("\n")
        mt.add_menu("po", self.similar and len(self.similar) > 1)
        console.print(text=mt.menu_text, menu="Stocks - Comparison Analysis")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.similar:
            return ["stocks", "ca", f"set {','.join(self.similar)}"]
        return []

    # TODO: Figure out if this function is actually needed here
    @log_start_end(log=logger)
    def call_ticker(self, other_args: List[str]):
        """Process ticker command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ticker",
            description="""Set ticker to extract similar from""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            type=str,
            required="-h" not in other_args,
            help="Ticker get similar tickers from",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if "," in ns_parser.ticker:
                console.print("Only one ticker must be selected!")
            else:
                stock_data = yf.download(
                    ns_parser.ticker,
                    progress=False,
                )
                if stock_data.empty:
                    console.print(
                        f"The ticker '{ns_parser.ticker}' provided does not exist!"
                    )
                else:
                    self.ticker = ns_parser.ticker.upper()
            console.print()

    @log_start_end(log=logger)
    def call_tsne(self, other_args: List[str]):
        """Process tsne command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tsne",
            description="""Get similar companies to compare with using sklearn TSNE.""",
        )
        parser.add_argument(
            "-r",
            "--learnrate",
            default=200,
            dest="lr",
            type=check_non_negative,
            help="TSNE Learning rate.  Typical values are between 50 and 200",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve. The subsample will occur randomly.",
        )
        parser.add_argument(
            "-p", "--no_plot", action="store_true", default=False, dest="no_plot"
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                self.similar = yahoo_finance_model.get_sp500_comps_tsne(
                    self.ticker,
                    lr=ns_parser.lr,
                    no_plot=ns_parser.no_plot,
                    num_tickers=ns_parser.limit,
                )

                self.similar = [self.ticker] + self.similar
                console.print(
                    f"[ML] Similar Companies: {', '.join(self.similar)}", "\n"
                )

            else:
                console.print(
                    "You need to 'set' a ticker to get similar companies from first!"
                )

    @log_start_end(log=logger)
    def call_getfinviz(self, other_args: List[str]):
        """Process getfinviz command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getfinviz",
            description="""Get similar companies from finviz to compare with.""",
        )
        parser.add_argument(
            "-n",
            "--nocountry",
            action="store_true",
            default=False,
            dest="b_no_country",
            help="Similar stocks from finviz using only Industry and Sector.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                if ns_parser.b_no_country:
                    compare_list = ["Sector", "Industry"]
                else:
                    compare_list = ["Sector", "Industry", "Country"]

                self.similar, self.user = finviz_compare_model.get_similar_companies(
                    self.ticker, compare_list
                )

                if self.ticker.upper() in self.similar:
                    self.similar.remove(self.ticker.upper())

                if len(self.similar) > ns_parser.limit:
                    random.shuffle(self.similar)
                    self.similar = sorted(self.similar[: ns_parser.limit])
                    console.print(
                        f"The limit of stocks to compare are {ns_parser.limit}. The subsample will occur randomly.\n",
                    )

                if self.similar:
                    self.similar = [self.ticker] + self.similar

                    console.print(
                        f"[{self.user}] Similar Companies: {', '.join(self.similar)}",
                        "\n",
                    )
            else:
                console.print(
                    "You need to 'set' a ticker to get similar companies from first!"
                )

    @log_start_end(log=logger)
    @check_api_key(["API_POLYGON_KEY"])
    def call_getpoly(self, other_args: List[str]):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getpoly",
            description="""Get similar companies from polygon to compare with.""",
        )
        parser.add_argument(
            "-u",
            "--us_only",
            action="store_true",
            default=False,
            dest="us_only",
            help="Show only stocks from the US stock exchanges",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if self.ticker:
                self.similar, self.user = polygon_model.get_similar_companies(
                    self.ticker, ns_parser.us_only
                )

                if self.ticker.upper() in self.similar:
                    self.similar.remove(self.ticker.upper())

                if len(self.similar) > ns_parser.limit:
                    random.shuffle(self.similar)
                    self.similar = sorted(self.similar[: ns_parser.limit])
                    console.print(
                        f"The limit of stocks to compare are {ns_parser.limit}. The subsample will occur randomly.\n",
                    )

                if self.similar:
                    self.similar = [self.ticker] + self.similar
                    console.print(
                        f"[{self.user}] Similar Companies: {', '.join(self.similar)}",
                        "\n",
                    )

            else:
                console.print(
                    "You need to 'set' a ticker to get similar companies from first!"
                )

    @log_start_end(log=logger)
    @check_api_key(["API_FINNHUB_KEY"])
    def call_getfinnhub(self, other_args: List[str]):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="getfinnhub",
            description="""Get similar companies from finnhub to compare with.""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            type=check_positive,
            help="Limit of stocks to retrieve.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                self.similar, self.user = finnhub_model.get_similar_companies(
                    self.ticker
                )

                if self.ticker.upper() in self.similar:
                    self.similar.remove(self.ticker.upper())

                if len(self.similar) > ns_parser.limit:
                    random.shuffle(self.similar)
                    self.similar = sorted(self.similar[: ns_parser.limit])
                    console.print(
                        f"The limit of stocks to compare are {ns_parser.limit}. The subsample will occur randomly.\n",
                    )

                if self.similar:

                    self.similar = [self.ticker] + self.similar
                    console.print(
                        f"[{self.user}] Similar Companies: {', '.join(self.similar)}",
                        "\n",
                    )

            else:
                console.print(
                    "You need to 'set' a ticker to get similar companies from first!"
                )

    @log_start_end(log=logger)
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="""Add similar tickers to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="Tickers to add to similar list",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.similar:
                self.similar = list(set(self.similar + ns_parser.l_similar))
            else:
                self.similar = ns_parser.l_similar
            self.user = "Custom"

            console.print(
                f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n"
            )

    @log_start_end(log=logger)
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rmv",
            description="""Remove similar tickers to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="Tickers to remove from similar list",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.l_similar:
                for symbol in ns_parser.l_similar:
                    if symbol in self.similar:
                        self.similar.remove(symbol)
                    else:
                        console.print(
                            f"Ticker {symbol} does not exist in similar list to be removed"
                        )

                console.print(
                    f"[{self.user}] Similar Companies: {', '.join(self.similar)}"
                )

            else:
                self.similar = []

            console.print()
            self.user = "Custom"

    @log_start_end(log=logger)
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="set",
            description="""Select similar companies to compare with.""",
        )
        parser.add_argument(
            "-s",
            "--similar",
            dest="l_similar",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="similar companies to compare with.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.similar = list(set(ns_parser.l_similar))
            self.user = "Custom"
            console.print(
                f"[{self.user}] Similar Companies: {', '.join(self.similar)}", "\n"
            )

    @log_start_end(log=logger)
    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="historical",
            description="""Historical price comparison between similar companies.""",
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="type_candle",
            type=str,
            choices=["o", "h", "l", "c", "a"],
            default="a",  # in case it's adjusted close
            help="Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close.",
        )
        parser.add_argument(
            "-n",
            "--normalize",
            action="store_true",
            dest="normalize",
            default=False,
            help="Flag to normalize all prices on same 0-1 scale",
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                yahoo_finance_view.display_historical(
                    similar_tickers=self.similar,
                    start=ns_parser.start.strftime("%Y-%m-%d"),
                    candle_type=ns_parser.type_candle,
                    normalize=ns_parser.normalize,
                    export=ns_parser.export,
                )

            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_hcorr(self, other_args: List[str]):
        """Process historical correlation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hcorr",
            description=""" Correlation heatmap based on historical price comparison between similar
            companies.
            """,
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="type_candle",
            type=str,
            choices=["o", "h", "l", "c", "a"],
            default="a",  # in case it's adjusted close
            help="Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close.",
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                yahoo_finance_view.display_correlation(
                    similar_tickers=self.similar,
                    start=ns_parser.start.strftime("%Y-%m-%d"),
                    candle_type=ns_parser.type_candle,
                    export=ns_parser.export,
                )
            else:
                console.print("Please make sure there are similar tickers selected. \n")

    @log_start_end(log=logger)
    def call_income(self, other_args: List[str]):
        """Process income command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="income",
            description="""
                Prints either yearly or quarterly income statement the company, and compares
                it against similar companies.
            """,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter financial data flag.",
        )
        parser.add_argument(
            "-t",
            "--timeframe",
            dest="s_timeframe",
            type=str,
            default=None,
            help="Specify yearly/quarterly timeframe. Default is last.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_income_comparison(
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

    @log_start_end(log=logger)
    def call_volume(self, other_args: List[str]):
        """Process volume command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="volume",
            description="""Historical volume comparison between similar companies.
            """,
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
            other_args.insert(0, "-s")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                yahoo_finance_view.display_volume(
                    similar_tickers=self.similar,
                    start=ns_parser.start.strftime("%Y-%m-%d"),
                    export=ns_parser.export,
                )

            else:
                console.print("Please make sure there are similar tickers selected. \n")

    @log_start_end(log=logger)
    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balance",
            description="""
                Prints either yearly or quarterly balance statement the company, and compares
                it against similar companies.
            """,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter financial data flag.",
        )
        parser.add_argument(
            "-t",
            "--timeframe",
            dest="s_timeframe",
            type=str,
            default=None,
            help="Specify yearly/quarterly timeframe. Default is last.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_balance_comparison(
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

    @log_start_end(log=logger)
    def call_cashflow(self, other_args: List[str]):
        """Process cashflow command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cashflow",
            description="""
                Prints either yearly or quarterly cashflow statement the company, and compares
                it against similar companies.
            """,
        )
        parser.add_argument(
            "-q",
            "--quarter",
            action="store_true",
            default=False,
            dest="b_quarter",
            help="Quarter financial data flag.",
        )
        parser.add_argument(
            "-t",
            "--timeframe",
            dest="s_timeframe",
            type=str,
            default=None,
            help="Specify yearly/quarterly timeframe. Default is last.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_cashflow_comparison(
                similar=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
            )

    @log_start_end(log=logger)
    def call_sentiment(self, other_args: List[str]):
        """Process sentiment command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sentiment_compare",
            description="""
                FinBrain's sentiment comparison across similar tickers.
            """,
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            default=False,
            help="Display raw sentiment data",
            dest="raw",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finbrain_view.display_sentiment_compare(
                    similar=self.similar,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_scorr(self, other_args: List[str]):
        """Process sentiment correlation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sentiment_compare",
            description="""
                FinBrain's sentiment correlation across similar tickers.
            """,
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            default=False,
            help="Display raw sentiment data",
            dest="raw",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finbrain_view.display_sentiment_correlation(
                    similar=self.similar,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                console.print("Please make sure there are similar tickers selected. \n")

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="overview",
                    export=ns_parser.export,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="valuation",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="valuation",
                    export=ns_parser.export,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_financial(self, other_args: List[str]):
        """Process financial command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="financial",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="financial",
                    export=ns_parser.export,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_ownership(self, other_args: List[str]):
        """Process ownership command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ownership",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="ownership",
                    export=ns_parser.export,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="performance",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="performance",
                    export=ns_parser.export,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_technical(self, other_args: List[str]):
        """Process technical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="technical",
            description="""
                Prints screener data of similar companies. [Source: Finviz]
            """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="technical",
                    export=ns_parser.export,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )

    @log_start_end(log=logger)
    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        if self.similar and len(self.similar) > 1:
            self.queue = po_controller.PortfolioOptimizationController(
                self.similar, self.queue
            ).menu(custom_path_menu_above="/portfolio/")
        else:
            console.print(
                "Please make sure there are more than 1 similar tickers selected. \n"
            )
