"""Ally Controller"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional

from openbb_terminal import feature_flags as obbff
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.brokers.ally import ally_view
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class AllyController(BaseController):
    """Ally Controller class"""

    CHOICES_COMMANDS = ["holdings", "history", "balances", "quote", "movers"]

    list_choices = [
        "toplosers",
        "toppctlosers",
        "topvolume",
        "topactive",
        "topgainers",
        "toppctgainers",
    ]
    list_exchanges = ["A", "N", "Q", "U", "V"]
    PATH = "/portfolio/bro/ally/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("portfolio/bro/ally/")
        mt.add_cmd("holdings")
        mt.add_cmd("history")
        mt.add_cmd("balances")
        mt.add_raw("\n")
        mt.add_info("_info_")
        mt.add_cmd("quote")
        mt.add_cmd("movers")
        console.print(text=mt.menu_text, menu="Portfolio - Brokers - Ally")

    @log_start_end(log=logger)
    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            prog="holdings",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Ally",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_holdings(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_history(self, other_args: List[str]):
        """Process history command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="history",
            description="""Account transaction history""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            default=15,
            type=int,
            help="Number of recent transactions to show",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_history(
                n_to_show=ns_parser.limit, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_balances(self, other_args: List[str]):
        """Process balances command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balances",
            description="""Account balance details""",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_balances(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_quote(self, other_args: List[str]):
        """Process balances command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="""Get stock quote""",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        parser.add_argument(
            "-t",
            "--ticker",
            help="Ticker to get quote for. Can be in form of 'tick1,tick2...'",
            type=str,
            dest="ticker",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            ally_view.display_stock_quote(ns_parser.ticker)

    @log_start_end(log=logger)
    def call_movers(self, other_args: List[str]):
        """Process movers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="movers",
            description="""Get stock movers""",
        )
        parser.add_argument(
            "-t",
            "--type",
            help="List to get movers of",
            choices=self.list_choices,
            default="topactive",
            dest="list_type",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            help="""Exchange to look at.  Can be
            A:American Stock Exchange.
            N:New York Stock Exchange.
            Q:NASDAQ
            U:NASDAQ Bulletin Board
            V:NASDAQ OTC Other""",
            choices=self.list_exchanges,
            default="N",
            dest="exchange",
        )
        parser.add_argument(
            "-l", "--limit", help="Number to show", type=int, default=15, dest="limit"
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_top_lists(
                list_type=ns_parser.list_type,
                exchange=ns_parser.exchange,
                num_to_show=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
