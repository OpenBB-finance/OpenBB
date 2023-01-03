"""Gemini Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import logging
from typing import List
from dotenv import get_key, set_key

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.base_helpers import strtobool
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.brokers.gemini import gemini_view
from openbb_terminal.cryptocurrency.gemini_helpers import (
    GeminiFunctions,
)
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class GeminiController(BaseController):
    """Gemini Controller class"""

    CHOICES_COMMANDS = [
        "accounts",
        "sandbox",
        "dryrun",
        "setaccount",
        "createorder",
        "listorders",
        "cancelorders",
    ]

    order_sortby = [
        "order_id",
        "symbol",
        "exchange",
        "side",
        "price",
        "timestamnp",
        "type",
        "is_live",
        "is_cancelled",
    ]

    PATH = "/portfolio/bro/gemini/"
    CHOICES_GENERATION = True

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.sandbox = get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_SANDBOX") or "False"
        self.account = (
            get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_ACCOUNT") or "primary"
        )
        self.dryrun = get_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_DRYRUN") or "False"

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("portfolio/bro/gemini/")

        mt.add_param("_OperationsAccount", self.account)
        mt.add_raw("\n")

        mt.add_info("Account")
        mt.add_cmd("accounts")
        mt.add_raw("\n")
        mt.add_info("manageorders")
        mt.add_cmd("listorders")
        if strtobool(self.dryrun):
            mt.add_raw("\n")
            mt.add_param(
                "_dryrun",
                f"[bold]{'True' if strtobool(self.dryrun) else 'False'}[bold]",
            )
        mt.add_cmd("createorder")
        mt.add_cmd("cancelorders")
        mt.add_raw("\n")
        mt.add_info("Settings")
        mt.add_cmd("sandbox")
        mt.add_cmd("setaccount")
        mt.add_cmd("dry-run")

        console.print(
            text=mt.menu_text,
            menu=f"Portfolio - Brokers - Gemini{' - [red]Sandbox API[/red]' if strtobool(self.sandbox) else ''}",
        )

    @log_start_end(log=logger)
    def call_sandbox(self, other_args):
        """Process enable command"""
        parser = argparse.ArgumentParser(
            prog="sandbox",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Enable development mode: Sandbox",
        )
        parser.add_argument(
            "--enable",
            dest="sandbox",
            help="Enable work on Sandbox (for testing and dev)",
            choices=["True", "False"],
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.sandbox = ns_parser.sandbox
            set_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_SANDBOX", self.sandbox)

    @log_start_end(log=logger)
    def call_dryrun(self, other_args):
        """Process enable command"""
        parser = argparse.ArgumentParser(
            prog="dryrun",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Set order mode to dry-run",
        )
        parser.add_argument(
            "--enable",
            dest="dryrun",
            help="Enable dryrun mode (orders are not created, you will see the payload to the API)",
            choices=["True", "False"],
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.dryrun = ns_parser.dryrun
            set_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_DRYRUN", self.dryrun)

    @log_start_end(log=logger)
    def call_setaccount(self, other_args):
        """Process enable command"""
        parser = argparse.ArgumentParser(
            prog="setaccount",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Set account for order operations",
        )
        parser.add_argument(
            "--setaccount",
            dest="account",
            help="Set account for order operations",
            type=str,
            default=False,
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            valid_account = GeminiFunctions().check_account_validity(ns_parser.account)

            if valid_account != ns_parser.account:
                console.print(f"{ns_parser.account} is an invalid account\n")
                return
            self.account = ns_parser.account
            set_key(obbff.USER_ENV_FILE, "OPENBB_GEMINI_ACCOUNT", self.account)

    @log_start_end(log=logger)
    def call_accounts(self, other_args):
        """Process account command"""
        parser = argparse.ArgumentParser(
            prog="account",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Gemini Advanced",
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            gemini_view.display_accounts(
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_listorders(self, other_args):
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
            default="timestamp",
            choices=self.order_sortby,
        )
        parser.add_argument(
            "--status",
            dest="status",
            default="all",
            help=("Filter by status Live, Cancelled, all"),
            choices=["is_live", "is_cancelled", "all"],
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
            gemini_view.display_orders(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=not ns_parser.reverse,
                export=ns_parser.export,
                status=ns_parser.status,
            )

    @log_start_end(log=logger)
    def call_cancelorders(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="cancelorder",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Cancel order by id or all active orders",
        )
        parser.add_argument(
            "--order_id",
            dest="order_id",
            help="Gemini Order id",
        )
        parser.add_argument(
            "--all_active",
            dest="all_active",
            help="Cancel all active orders",
            choices=["True", "False"],
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            gemini_view.display_cancel_orders(
                order_id=ns_parser.order_id,
                all_active=ns_parser.all_active,
                account=self.account,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_createorder(self, other_args):
        """Process orders command"""
        parser = argparse.ArgumentParser(
            prog="create",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Create Gemini order",
        )
        parser.add_argument(
            "--symbol",
            dest="symbol",
            type=str,
            help="Gemini valid symbol",
        )
        parser.add_argument(
            "--amount",
            dest="amount",
            type=float,
            help="decimal amount to purchase",
        )
        parser.add_argument(
            "--price",
            dest="price",
            type=float,
            help="decimal amount to spend per unit",
        )
        parser.add_argument(
            "--side", dest="side", type=str, help="Trade side", choices=["buy", "sell"]
        )
        parser.add_argument(
            "--type",
            dest="type",
            type=str,
            default="exchange limit",
            help="The order type. 'exchange limit' for all order types except for stop-limit orders."
            " 'exchange stop limit' for stop-limit orders.",
            choices=["exchange_limit", "exchange_stop_limit"],
        )
        parser.add_argument(
            "--stop_price",
            dest="stop_price",
            type=float,
            help="Optional. The price to trigger a stop-limit order. Only available for stop-limit orders.",
        )
        parser.add_argument(
            "--options",
            dest="options",
            type=str,
            help="Please read: ORDER EXECUTION OPTIONS in https://docs.gemini.com/rest-api/#new-order",
            choices=["maker-or-cancel", "immediate-or-cancel", "fill-or-kill"],
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            gemini_view.display_create_order(
                symbol=ns_parser.symbol,
                side=ns_parser.side,
                amount=ns_parser.amount,
                price=ns_parser.price,
                order_type=ns_parser.type.replace("_", " "),
                stop_price=ns_parser.stop_price,
                options=ns_parser.options,
                account=self.account,
                export=ns_parser.export,
            )
