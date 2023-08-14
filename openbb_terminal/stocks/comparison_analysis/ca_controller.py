"""Comparison Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
import random
from datetime import datetime, timedelta
from typing import List, Optional

import yfinance as yf

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative,
    check_positive,
    check_start_less_than_end,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console, get_ordered_list_sources
from openbb_terminal.stocks.comparison_analysis import (
    finbrain_view,
    finnhub_model,
    finviz_compare_model,
    finviz_compare_view,
    marketwatch_view,
    polygon_model,
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
        "get",
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
    choices_ohlca = ["o", "h", "l", "c", "a"]
    CHOICES_MENUS: List = list()
    PATH = "/stocks/ca/"
    CHOICES_GENERATION = True

    def __init__(
        self, similar: Optional[List[str]] = None, queue: Optional[List[str]] = None
    ):
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

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def call_exit(self, _) -> None:
        """Process exit terminal command from forecast menu."""
        self.save_class()
        for _ in range(self.PATH.count("/") + 1):
            self.queue.insert(0, "quit")

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/ca/", 80)
        mt.add_cmd("ticker")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker)
        mt.add_raw("\n")
        mt.add_cmd("tsne", self.ticker)
        mt.add_cmd("get", self.ticker)
        mt.add_raw("\n")
        mt.add_cmd("set")
        mt.add_cmd("add")
        mt.add_cmd("rmv")
        mt.add_raw("\n")
        mt.add_param("_similar", ", ".join(self.similar))
        mt.add_raw("\n")
        mt.add_cmd("historical", self.similar and len(self.similar) > 1)
        mt.add_cmd("hcorr", self.similar and len(self.similar) > 1)
        mt.add_cmd("volume", self.similar and len(self.similar) > 1)
        mt.add_cmd("income", self.similar and len(self.similar) > 1)
        mt.add_cmd("balance", self.similar and len(self.similar) > 1)
        mt.add_cmd("cashflow", self.similar and len(self.similar) > 1)
        mt.add_cmd("sentiment", self.similar and len(self.similar) > 1)
        mt.add_cmd("scorr", self.similar and len(self.similar) > 1)
        mt.add_cmd("overview", self.similar and len(self.similar) > 1)
        mt.add_cmd("valuation", self.similar and len(self.similar) > 1)
        mt.add_cmd("financial", self.similar and len(self.similar) > 1)
        mt.add_cmd("ownership", self.similar and len(self.similar) > 1)
        mt.add_cmd("performance", self.similar and len(self.similar) > 1)
        mt.add_cmd("technical", self.similar and len(self.similar) > 1)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
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
                    self.similar = []

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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                self.similar = yahoo_finance_view.display_sp500_comps_tsne(
                    self.ticker,
                    lr=ns_parser.lr,
                    no_plot=ns_parser.no_plot,
                    limit=ns_parser.limit,
                )

                self.similar = [self.ticker] + self.similar
                console.print(
                    f"[ML] Similar Companies: {', '.join(self.similar)}", "\n"
                )

            else:
                console.print(
                    "You need to 'set' a ticker to get similar companies from first! This is "
                    "for example done by running 'ticker gme'"
                )

    @log_start_end(log=logger)
    def call_get(self, other_args: List[str]):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="get",
            description="""Get similar companies from selected data source (default: Finviz) to compare with.""",
        )
        parser.add_argument(
            "-u",
            "--us_only",
            action="store_true",
            default=False,
            dest="us_only",
            help="Show only stocks from the US stock exchanges. Works only with Polygon",
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                if ns_parser.source == "Finviz":
                    compare_list = (
                        ["Sector", "Industry"]
                        if ns_parser.b_no_country
                        else ["Sector", "Industry", "Country"]
                    )

                    self.similar = finviz_compare_model.get_similar_companies(
                        self.ticker, compare_list
                    )
                    if self.similar is None:
                        return
                    self.user = "Finviz"

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
                        )
                elif ns_parser.source == "Polygon":
                    self.similar = polygon_model.get_similar_companies(
                        self.ticker, ns_parser.us_only
                    )
                    if self.similar is None:
                        return
                    self.user = "Polygon"

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
                elif ns_parser.source == "Finnhub":
                    self.similar = finnhub_model.get_similar_companies(self.ticker)

                    if self.similar:
                        self.user = "Finnhub"

                        if self.ticker.upper() in self.similar:
                            self.similar.remove(self.ticker.upper())

                        if len(self.similar) > ns_parser.limit:
                            random.shuffle(self.similar)
                            self.similar = sorted(self.similar[: ns_parser.limit])
                            console.print(
                                f"The limit of stocks to compare are {ns_parser.limit}."
                                " The subsample will occur randomly.\n",
                            )

                        self.similar = [self.ticker] + self.similar
                        console.print(
                            f"[{self.user}] Similar Companies: {', '.join(self.similar)}",
                            "\n",
                        )
                else:
                    console.print(
                        f"Use a valid data source: {', '.join(get_ordered_list_sources(f'{self.PATH}get'))}"
                    )
            else:
                console.print(
                    "You need to 'set' a ticker to get similar companies from first! This is "
                    "for example done by running 'ticker aapl'"
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                self.similar = list(set(ns_parser.l_similar + [self.ticker.upper()]))
            else:
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
            choices=self.choices_ohlca,
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
            help="The starting date (format YYYY-MM-DD) of the stocks",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=(datetime.now()).strftime("%Y-%m-%d"),
            dest="end",
            help="The end date (format YYYY-MM-DD) of the stocks",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                if check_start_less_than_end(ns_parser.start, ns_parser.end):
                    return
                yahoo_finance_view.display_historical(
                    similar=self.similar,
                    start_date=ns_parser.start.strftime("%Y-%m-%d"),
                    end_date=ns_parser.end.strftime("%Y-%m-%d"),
                    candle_type=ns_parser.type_candle,
                    normalize=ns_parser.normalize,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
            choices=self.choices_ohlca,
            default="a",  # in case it's adjusted close
            help="Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close, r-returns.",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=(datetime.now()).strftime("%Y-%m-%d"),
            dest="end",
            help="The end date (format YYYY-MM-DD) of the stocks",
        )
        parser.add_argument(
            "--display-full-matrix",
            action="store_true",
            help="Display all matrix values, rather than masking off half.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                if check_start_less_than_end(ns_parser.start, ns_parser.end):
                    return
                yahoo_finance_view.display_correlation(
                    similar=self.similar,
                    start_date=ns_parser.start.strftime("%Y-%m-%d"),
                    end_date=ns_parser.end.strftime("%Y-%m-%d"),
                    candle_type=ns_parser.type_candle,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    display_full_matrix=ns_parser.display_full_matrix,
                    raw=ns_parser.raw,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_income_comparison(
                symbols=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=(datetime.now()).strftime("%Y-%m-%d"),
            dest="end",
            help="The end date (format YYYY-MM-DD) of the stocks",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                if check_start_less_than_end(ns_parser.start, ns_parser.end):
                    return
                yahoo_finance_view.display_volume(
                    similar=self.similar,
                    start_date=ns_parser.start.strftime("%Y-%m-%d"),
                    end_date=ns_parser.end.strftime("%Y-%m-%d"),
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_balance_comparison(
                symbols=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
            help="Specify year/quarter of the cashflow statement to be retrieved. The format for year is YYYY and for "
            "quarter is DD-MMM-YYY (for example, 30-Sep-2021). Default is last year/quarter.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.display_cashflow_comparison(
                symbols=self.similar,
                timeframe=ns_parser.s_timeframe,
                quarter=ns_parser.b_quarter,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finbrain_view.display_sentiment_compare(
                    similar=self.similar,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finbrain_view.display_sentiment_correlation(
                    similar=self.similar,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="overview",
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="valuation",
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="financial",
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="ownership",
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="performance",
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.similar and len(self.similar) > 1:
                finviz_compare_view.screener(
                    similar=self.similar,
                    data_type="technical",
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print(
                    "Please make sure there are more than 1 similar tickers selected. \n"
                )
