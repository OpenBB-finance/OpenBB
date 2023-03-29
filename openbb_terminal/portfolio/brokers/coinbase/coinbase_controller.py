"""Coinbase Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import logging
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED, check_positive
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.brokers.coinbase import coinbase_view
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class CoinbaseController(BaseController):
    """Coinbase Controller class"""

    CHOICES_COMMANDS = ["account", "history", "orders", "deposits"]

    order_sortby = [
        "product_id",
        "side",
        "price",
        "size",
        "type",
        "created_at",
        "status",
    ]
    deposit_sort = [
        "created_at",
        "amount",
    ]
    deposit_type = ["internal_deposit", "deposit"]
    PATH = "/portfolio/bro/cb/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("portfolio/bro/cb/")
        mt.add_cmd("account")
        mt.add_cmd("history")
        mt.add_cmd("deposits")
        mt.add_cmd("orders")
        console.print(text=mt.menu_text, menu="Portfolio - Brokers - Coinbase")

    @log_start_end(log=logger)
    def call_account(self, other_args):
        """Process account command"""
        parser = argparse.ArgumentParser(
            prog="account",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Coinbase",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Flag to display all your account",
            dest="all",
            default=False,
        )
        parser.add_argument(
            "-c",
            "--currency",
            default="USD",
            type=str,
            dest="currency",
            help="Currency to display value in.",
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_view.display_account(
                currency=ns_parser.currency,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_history(self, other_args):
        """Process account command"""
        parser = argparse.ArgumentParser(
            prog="history",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display account history",
        )
        parser.add_argument(
            "-a",
            "--acc",
            dest="account",
            help="Symbol of coin of account or id",
            type=str,
            default="BTC",
            required=False,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            help="Limit parameter.",
            default=20,
            type=check_positive,
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_view.display_history(
                ns_parser.account,
                ns_parser.export,
                ns_parser.sheet_name,
                ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_orders(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="orders",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="List your current open orders",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            help="Limit parameter.",
            default=20,
            type=check_positive,
        )
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: created_at",
            default="created_at",
            choices=self.order_sortby,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_view.display_orders(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=not ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_deposits(self, other_args):
        """Process deposits command"""
        parser = argparse.ArgumentParser(
            prog="deposits",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display a list of deposits for your account.",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            type=str,
            help="Deposit type. Either: internal_deposits (transfer between portfolios) or deposit",
            default="deposit",
            choices=self.deposit_type,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            help="Limit parameter.",
            default=20,
            type=check_positive,
        )
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: created_at",
            default="created_at",
            choices=self.deposit_sort,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinbase_view.display_deposits(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                deposit_type=ns_parser.type,
                descend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
