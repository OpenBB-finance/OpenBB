""" Government Controller Module """
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks.government import quiverquant_view

logger = logging.getLogger(__name__)


class GovController(StockBaseController):
    """Gov Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "lasttrades",
        "topbuys",
        "topsells",
        "lastcontracts",
        "qtrcontracts",
        "toplobbying",
        "gtrades",
        "contracts",
        "histcont",
        "lobbying",
    ]

    gov_type_choices = ["congress", "senate", "house"]
    analysis_choices = ["total", "upmom", "downmom"]
    PATH = "/stocks/gov/"
    CHOICES_GENERATION = True

    def __init__(
        self,
        ticker: str,
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/gov/", 80)
        mt.add_info("_explore")
        mt.add_cmd("lasttrades")
        mt.add_cmd("topbuys")
        mt.add_cmd("topsells")
        mt.add_cmd("lastcontracts")
        mt.add_cmd("qtrcontracts")
        mt.add_cmd("toplobbying")
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker or "")
        mt.add_raw("\n")
        mt.add_cmd("gtrades", self.ticker)
        mt.add_cmd("contracts", self.ticker)
        mt.add_cmd("histcont", self.ticker)
        mt.add_cmd("lobbying", self.ticker)
        console.print(text=mt.menu_text, menu="Stocks - Government")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "gov"]
        return []

    @log_start_end(log=logger)
    def call_lasttrades(self, other_args: List[str]):
        """Process lasttrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lasttrades",
            description="Last government trades. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_days",
            action="store",
            dest="past_transactions_days",
            type=check_positive,
            default=5,
            help="Past transaction days",
        )
        parser.add_argument(
            "-r",
            "--representative",
            action="store",
            dest="representative",
            type=str,
            default="",
            help="Representative",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            quiverquant_view.display_last_government(
                gov_type=ns_parser.gov,
                limit=ns_parser.past_transactions_days,
                representative=ns_parser.representative,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_topbuys(self, other_args: List[str]):
        """Process topbuys command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="topbuys",
            description="Top buys for government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_months",
            action="store",
            dest="past_transactions_months",
            type=check_positive,
            default=6,
            help="Past transaction months",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of top tickers to display",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_government_buys(
                gov_type=ns_parser.gov,
                past_transactions_months=ns_parser.past_transactions_months,
                limit=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_topsells(self, other_args: List[str]):
        """Process topsells command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="topsells",
            description="Top sells for government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_months",
            action="store",
            dest="past_transactions_months",
            type=check_positive,
            default=6,
            help="Past transaction months",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of top tickers to display",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_government_sells(
                gov_type=ns_parser.gov,
                past_transactions_months=ns_parser.past_transactions_months,
                limit=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_lastcontracts(self, other_args: List[str]):
        """Process lastcontracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lastcontracts",
            description="Last government contracts. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-p",
            "--past_transaction_days",
            action="store",
            dest="past_transaction_days",
            type=check_positive,
            default=2,
            help="Past transaction days",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=20,
            help="Limit of contracts to display",
        )
        parser.add_argument(
            "-s",
            "--sum",
            action="store_true",
            dest="sum",
            default=False,
            help="Flag to show total amount of contracts.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_last_contracts(
                past_transaction_days=ns_parser.past_transaction_days,
                limit=ns_parser.limit,
                sum_contracts=ns_parser.sum,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_qtrcontracts(self, other_args: List[str]):
        """Process qtrcontracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="qtrcontracts",
            description="Look at government contracts [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of tickers to get",
        )
        parser.add_argument(
            "-a",
            "--analysis",
            action="store",
            dest="analysis",
            choices=self.analysis_choices,
            type=str,
            default="total",
            help="""Analysis to look at contracts. 'Total' shows summed contracts.
            'Upmom' shows highest sloped contacts while 'downmom' shows highest decreasing slopes.""",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_qtr_contracts(
                analysis=ns_parser.analysis,
                limit=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_toplobbying(self, other_args: List[str]):
        """Process toplobbying command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="toplobbying",
            description="Top lobbying. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of stocks to display",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_top_lobbying(
                limit=ns_parser.limit, raw=ns_parser.raw, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_gtrades(self, other_args: List[str]):
        """Process gtrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gtrades",
            description="Government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_months",
            action="store",
            dest="past_transactions_months",
            type=check_positive,
            default=6,
            help="Past transaction months",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_government_trading(
                    symbol=self.ticker,
                    gov_type=ns_parser.gov,
                    past_transactions_months=ns_parser.past_transactions_months,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded. Use `load <ticker>` first.\n")

    @log_start_end(log=logger)
    def call_contracts(self, other_args: List[str]):
        """Process contracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="contracts",
            description="Contracts associated with ticker. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-p",
            "--past_transaction_days",
            action="store",
            dest="past_transaction_days",
            type=check_positive,
            default=10,
            help="Past transaction days",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_contracts(
                    symbol=self.ticker,
                    past_transaction_days=ns_parser.past_transaction_days,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded. Use `load <ticker>` first.\n")

    @log_start_end(log=logger)
    def call_histcont(self, other_args: List[str]):
        """Process histcont command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="histcont",
            description="Quarterly-contracts historical [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_hist_contracts(
                    symbol=self.ticker, raw=ns_parser.raw, export=ns_parser.export
                )
            else:
                console.print("No ticker loaded. Use `load <ticker>` first.\n")

    @log_start_end(log=logger)
    def call_lobbying(self, other_args: List[str]):
        """Process lobbying command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lobbying",
            description="Lobbying details [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of events to show",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_lobbying(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                )
            else:
                console.print("No ticker loaded. Use `load <ticker>` first.\n")
