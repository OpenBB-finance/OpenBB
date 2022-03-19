""" Due Diligence Controller """
__docformat__ = "numpy"

import argparse
import logging
from typing import List

from pandas.core.frame import DataFrame
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import StockBaseController
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.stocks.due_diligence import (
    ark_view,
    business_insider_view,
    csimarket_view,
    finnhub_view,
    finviz_view,
    fmp_view,
    marketwatch_view,
)

logger = logging.getLogger(__name__)


class DueDiligenceController(StockBaseController):
    """Due Diligence Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "sec",
        "rating",
        "pt",
        "rot",
        "est",
        "analyst",
        "supplier",
        "customer",
        "arktrades",
    ]
    PATH = "/stocks/dd/"

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"]["-i"] = {c: {} for c in stocks_helper.INTERVALS}
            choices["load"]["-s"] = {c: {} for c in stocks_helper.SOURCES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
[param]Ticker: [/param]{self.ticker}[cmds]

[src][Finviz][/src]
    analyst       analyst prices and ratings of the company
[src][FMP][/src]
    rating        rating over time (daily)
[src][Finnhub][/src]
    rot           number of analysts ratings over time (monthly)
[src][Business Insider][/src]
    pt            price targets over time
    est           quarter and year analysts earnings estimates
[src][Market Watch][/src]
    sec           SEC filings
[src][Csimarket][/src]
    supplier      list of suppliers
    customer      list of customers
[src][Cathiesark.com][/src]
    arktrades     get ARK trades for ticker[/cmds]
        """
        console.print(text=help_text, menu="Stocks - Due Diligence")

    def custom_reset(self) -> List[str]:
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "dd"]
        return []

    @log_start_end(log=logger)
    def call_analyst(self, other_args: List[str]):
        """Process analyst command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="analyst",
            description="""
                Print analyst prices and ratings of the company. The following fields are expected:
                date, analyst, category, price from, price to, and rating. [Source: Finviz]
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.analyst(ticker=self.ticker, export=ns_parser.export)

    @log_start_end(log=logger)
    def call_pt(self, other_args: List[str]):
        """Process pt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pt",
            description="""Prints price target from analysts. [Source: Business Insider]""",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of latest price targets from analysts to print.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            business_insider_view.price_target_from_analysts(
                ticker=self.ticker,
                start=self.start,
                interval=self.interval,
                stock=self.stock,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_est(self, other_args: List[str]):
        """Process est command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="est",
            description="""Yearly estimates and quarter earnings/revenues. [Source: Business Insider]""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            business_insider_view.estimates(
                ticker=self.ticker,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_rot(self, other_args: List[str]):
        """Process rot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rot",
            description="""
                Rating over time (monthly). [Source: Finnhub]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of last months",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            finnhub_view.rating_over_time(
                ticker=self.ticker,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_rating(self, other_args: List[str]):
        """Process rating command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rating",
            description="""
                Based on specific ratios, prints information whether the company
                is a (strong) buy, neutral or a (strong) sell. The following fields are expected:
                P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of last days to display ratings",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.rating(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_sec(self, other_args: List[str]):
        """Process sec command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="sec",
            description="""
                Prints SEC filings of the company. The following fields are expected: Filing Date,
                Document Date, Type, Category, Amended, and Link. [Source: Market Watch]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="number of latest SEC filings.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.sec_filings(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_supplier(self, other_args: List[str]):
        """Process supplier command"""
        parser = argparse.ArgumentParser(
            prog="supplier",
            add_help=False,
            description="List of suppliers from ticker provided. [Source: CSIMarket]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            csimarket_view.suppliers(
                ticker=self.ticker,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_customer(self, other_args: List[str]):
        """Process customer command"""
        parser = argparse.ArgumentParser(
            prog="customer",
            add_help=False,
            description="List of customers from ticker provided. [Source: CSIMarket]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            csimarket_view.customers(
                ticker=self.ticker,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_arktrades(self, other_args):
        """Process arktrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="arktrades",
            description="""
                Get trades for ticker across all ARK funds.
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Limit of rows to show",
            dest="limit",
            default=10,
            type=check_positive,
        )
        parser.add_argument(
            "-s",
            "--show_ticker",
            action="store_true",
            default=False,
            help="Flag to show ticker in table",
            dest="show_ticker",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ark_view.display_ark_trades(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
                show_ticker=ns_parser.show_ticker,
            )
