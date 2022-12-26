"""Coinbase Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import logging
from typing import List

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.brokers.coinbase_advanced import coinbase_advanced_view
from openbb_terminal.cryptocurrency.coinbase_advanced_helpers import (
    get_order_id_list,
    DateTimeAction,
)
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class CoinbaseAdvController(BaseController):
    """Coinbase Advanced Controller class"""

    CHOICES_COMMANDS = [
        "account",
        "orders",
        "market",
        "limitgtc",
        "limitgtd",
        "stopgtc",
        "stopgtd",
        "cancelorder",
    ]

    order_sortby = [
        "product_id",
        "side",
        "price",
        "size",
        "order_type",
        "created_time",
        "status",
    ]

    order_status = [
        "ALL",
        "OPEN",
        "FILLED",
        "CANCELLED",
        "EXPIRED, FAILED",
        "UNKNOWN_ORDER_STATUS",
    ]

    PATH = "/portfolio/bro/cbadv/"
    CHOICES_GENERATION = True

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("portfolio/bro/cbadv/")
        mt.add_info("accountmanagement")
        mt.add_cmd("account")
        mt.add_raw("\n")
        mt.add_info("manageorders")
        mt.add_cmd("orders")
        mt.add_cmd("market")
        mt.add_cmd("limitgtc")
        mt.add_cmd("limitgtd")
        mt.add_cmd("stopgtc")
        mt.add_cmd("stopgtd")
        console.print(text=mt.menu_text, menu="Portfolio - Brokers - Coinbase Advanced")

    @log_start_end(log=logger)
    def call_account(self, other_args):
        """Process account command"""
        parser = argparse.ArgumentParser(
            prog="account",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Coinbase Advanced",
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
            coinbase_advanced_view.display_account(
                currency=ns_parser.currency,
                export=ns_parser.export,
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
            help="Sort by given column. Default: created_time",
            default="created_time",
            choices=self.order_sortby,
        )
        parser.add_argument(
            "-o",
            "--order_status",
            dest="status",
            type=str,
            help="Order Status",
            default="ALL",
            choices=self.order_status,
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
            coinbase_advanced_view.display_orders(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=not ns_parser.reverse,
                export=ns_parser.export,
                status=ns_parser.status,
            )

    @log_start_end(log=logger)
    def call_market(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="market",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Place a Market value order with Coinbase Advanced",
        )
        parser.add_argument(
            "--dry_run",
            dest="dry_run",
            type=bool,
            help="Dry Run shows the payload to the Coinbase API. If set to True, it does not create the order",
            default=False,
            choices=[True, False],
        )
        parser.add_argument(
            "--product_id",
            dest="product_id",
            help="Valid coin pair COIN-COIN  COIN-USD",
            default="BTC-USD",
            type=str,
        )
        parser.add_argument(
            "--side",
            dest="side",
            type=str,
            help="BUY or SELL",
            default="",
            choices=["BUY", "SELL"],
        )
        parser.add_argument(
            "--quote_size",
            dest="quote_size",
            type=float,
            help="Amount of quote currency to spend on order. Required for market_market_ioc BUY orders.",
            default=0,
        )
        parser.add_argument(
            "-b",
            "--base_size",
            dest="base_size",
            type=float,
            help="Amount of base currency to spend on order. Required for SELL orders",
            default=0,
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_advanced_view.display_create_order(
                product_id=ns_parser.product_id,
                side=ns_parser.side,
                quote_size=ns_parser.quote_size,
                base_size=ns_parser.base_size,
                order_type="market_market_ioc",
                dry_run=ns_parser.dry_run,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_limitgtc(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="limitgtc",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Place a limit GTC order with Coinbase Advanced",
        )
        parser.add_argument(
            "--dry_run",
            dest="dry_run",
            type=bool,
            help="Dry Run shows the paylod to the Coinbase API. If set to True, it does not create the order",
            default=False,
            choices=[True, False],
        )
        parser.add_argument(
            "--product_id",
            dest="product_id",
            help="Valid coin pair COIN-COIN  COIN-USD",
            default="BTC-USD",
            type=str,
        )
        parser.add_argument(
            "--side",
            dest="side",
            type=str,
            help="BUY or SELL",
            default="",
            choices=["BUY", "SELL"],
        )
        parser.add_argument(
            "--limit_price",
            dest="limit_price",
            type=float,
            help="Ceiling price for which the order should get filled.",
            default=0,
        )
        parser.add_argument(
            "--base_size",
            dest="base_size",
            type=float,
            help="Amount of base currency to spend on order",
            default=0,
        )
        parser.add_argument(
            "--post_only",
            dest="post_only",
            type=bool,
            help="Post only limit order",
            default=True,
            choices=[True, False],
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_advanced_view.display_create_order(
                product_id=ns_parser.product_id,
                side=ns_parser.side,
                base_size=ns_parser.base_size,
                post_only=ns_parser.post_only,
                limit_price=ns_parser.limit_price,
                order_type="limit_limit_gtc",
                dry_run=ns_parser.dry_run,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_limitgtd(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="limitgtc",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Place a limit GTD order with Coinbase Advanced",
        )
        parser.add_argument(
            "--dry_run",
            dest="dry_run",
            type=bool,
            help="Dry Run shows the paylod to the Coinbase API. If set to True, it does not create the order",
            default=False,
            choices=[True, False],
        )
        parser.add_argument(
            "-p",
            "--product_id",
            dest="product_id",
            help="Valid coin pair COIN-COIN  COIN-USD",
            default="BTC-USD",
            type=str,
        )
        parser.add_argument(
            "-s",
            "--side",
            dest="side",
            type=str,
            help="BUY or SELL",
            default="",
            choices=["BUY", "SELL"],
        )
        parser.add_argument(
            "-l",
            "--limit_price",
            dest="limit_price",
            type=float,
            help="Ceiling price for which the order should get filled.",
            default=0,
        )
        parser.add_argument(
            "-b",
            "--base_size",
            dest="base_size",
            type=float,
            help="Amount of base currency to spend on order",
            default=0,
        )
        parser.add_argument(
            "--post_only",
            dest="post_only",
            type=bool,
            help="Post only limit order",
            default=True,
            choices=[True, False],
        )
        parser.add_argument(
            "-d",
            "--date_time",
            dest="end_time",
            type=str,
            action=DateTimeAction,
            help="Order valid until this Date-Time. Format 'DD/MM/YYYY_HH:MM_AM/PM'"
            " important: use single quotes and no spaces (_)",
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_advanced_view.display_create_order(
                product_id=ns_parser.product_id,
                side=ns_parser.side,
                base_size=ns_parser.base_size,
                post_only=ns_parser.post_only,
                limit_price=ns_parser.limit_price,
                end_time=ns_parser.end_time,
                order_type="limit_limit_gtd",
                dry_run=ns_parser.dry_run,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_stopgtd(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="stopgtd",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Place a Stop limit GTD order with Coinbase Advanced",
        )
        parser.add_argument(
            "--dry_run",
            dest="dry_run",
            type=bool,
            help="Dry Run shows the paylod to the Coinbase API. If set to True, it does not create the order",
            default=False,
            choices=[True, False],
        )
        parser.add_argument(
            "--product_id",
            dest="product_id",
            help="Valid coin pair COIN-COIN  COIN-USD",
            default="BTC-USD",
            type=str,
        )
        parser.add_argument(
            "--side",
            dest="side",
            type=str,
            help="BUY or SELL",
            default="",
            choices=["BUY", "SELL"],
        )
        parser.add_argument(
            "--limit_price",
            dest="limit_price",
            type=float,
            help="Ceiling price for which the order should get filled.",
            default=0,
        )
        parser.add_argument(
            "--stop_price",
            dest="stop_price",
            type=float,
            help="Price at which the order should trigger - if stop direction is Up, "
            "then the order will trigger when the last trade price goes above this,"
            " otherwise order will trigger when last trade price goes below this price.",
            default=0,
        )
        parser.add_argument(
            "--base_size",
            dest="base_size",
            type=float,
            help="Amount of base currency to spend on order",
            default=0,
        )
        parser.add_argument(
            "--stop_direction",
            dest="stop_direction",
            type=str,
            default="",
            choices=["STOP_DIRECTION_STOP_UP", "STOP_DIRECTION_STOP_DOWN"],
        )
        parser.add_argument(
            "--date_time",
            dest="end_time",
            type=str,
            action=DateTimeAction,
            help="Order valid until this Date-Time. Format 'DD/MM/YYYY_HH:MM_AM/PM' "
            "important: no spaces use underscore (_)",
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_advanced_view.display_create_order(
                product_id=ns_parser.product_id,
                side=ns_parser.side,
                base_size=ns_parser.base_size,
                limit_price=ns_parser.limit_price,
                end_time=ns_parser.end_time,
                stop_price=ns_parser.stop_price,
                stop_direction=ns_parser.stop_direction,
                order_type="stop_limit_stop_limit_gtd",
                dry_run=ns_parser.dry_run,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_stopgtc(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="stopgtd",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Place a Stop limit GTC order with Coinbase Advanced",
        )
        parser.add_argument(
            "--dry_run",
            dest="dry_run",
            type=bool,
            help="Dry Run shows the paylod to the Coinbase API. If set to True, it does not create the order",
            default=False,
            choices=[True, False],
        )
        parser.add_argument(
            "--product_id",
            dest="product_id",
            help="Valid coin pair COIN-COIN  COIN-USD",
            default="BTC-USD",
            type=str,
        )
        parser.add_argument(
            "--side",
            dest="side",
            type=str,
            help="BUY or SELL",
            default="",
            choices=["BUY", "SELL"],
        )
        parser.add_argument(
            "--limit_price",
            dest="limit_price",
            type=float,
            help="Ceiling price for which the order should get filled.",
            default=0,
        )
        parser.add_argument(
            "--stop_price",
            dest="stop_price",
            type=float,
            help="Price at which the order should trigger - if stop direction is Up,"
            " then the order will trigger when the last trade price goes above this,"
            " otherwise order will trigger when last trade price goes below this price.",
            default=0,
        )
        parser.add_argument(
            "--base_size",
            dest="base_size",
            type=float,
            help="Amount of base currency to spend on order",
            default=0,
        )
        parser.add_argument(
            "--stop_direction",
            dest="stop_direction",
            type=str,
            default="",
            choices=["STOP_DIRECTION_STOP_UP", "STOP_DIRECTION_STOP_DOWN"],
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_advanced_view.display_create_order(
                product_id=ns_parser.product_id,
                side=ns_parser.side,
                base_size=ns_parser.base_size,
                limit_price=ns_parser.limit_price,
                stop_price=ns_parser.stop_price,
                stop_direction=ns_parser.stop_direction,
                order_type="stop_limit_stop_limit_gtc",
                dry_run=ns_parser.dry_run,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_cancelorder(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="cancelorder",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Cancel order by id",
        )
        parser.add_argument(
            "--order_id",
            dest="order_id",
            help="Coinbase Advanced Order id",
            choices=get_order_id_list(status="OPEN"),
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_advanced_view.display_cancel_order(
                order_id=ns_parser.order_id,
                export=ns_parser.export,
            )
