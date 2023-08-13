# IMPORTATION STANDARD
import argparse
import datetime
import logging
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user

# IMPORTATION INTERNAL
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED, valid_date
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.brokers.degiro.degiro_view import DegiroView

logger = logging.getLogger(__name__)


class DegiroController(BaseController):
    """Degiro Controller class"""

    CHOICES_COMMANDS = [
        "cancel",
        "companynews",
        "create",
        "hold",
        "lastnews",
        "login",
        "logout",
        "lookup",
        "pending",
        "topnews",
        "update",
        "paexport",
    ]
    PATH = "/portfolio/bro/degiro/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.__degiro_view = DegiroView()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            zero_to_hundred: dict = {str(c): {} for c in range(0, 100)}

            choices["login"] = {
                "--one-time-password": None,
                "-otp": "--one-time-password",
            }
            choices["lookup"] = {
                "--limit": None,
                "-l": "--limit",
                "--offset": zero_to_hundred,
                "-o": "--offset",
            }
            choices["create"] = {
                "--action": {c: {} for c in DegiroView.ORDER_ACTION},
                "-a": "--action",
                "--product": None,
                "-prod": "--product",
                "--symbol": None,
                "-sym": "--symbol",
                "--price": None,
                "-p": "--price",
                "--size": None,
                "-s": "--size",
                "--up-to": None,
                "-up": "--up-to",
                "--duration": {c: {} for c in DegiroView.ORDER_DURATION},
                "-d": "--duration",
                "--type": {c: {} for c in DegiroView.ORDER_TYPE},
                "-t": "--type",
            }
            choices["update"] = {
                "--price": None,
                "-p": "--price",
            }
            choices["lastnews"] = {
                "--limit": None,
                "-l": "--limit",
            }
            choices["paexport"] = {
                "--start": None,
                "-s": "--start",
                "--end": None,
                "-e": "--end",
                "--currency": None,
                "-c": "--currency",
            }

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        DegiroView.help_display()

    @log_start_end(log=logger)
    def call_cancel(self, other_args: List[str]):
        """Cancel an order using the `id`."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="cancel",
        )
        parser.add_argument(
            "id",
            help="Order's id.",
            type=str,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.cancel(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_companynews(self, other_args: List[str]):
        """Display news related to a company using its ISIN."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="companynews",
        )
        parser.add_argument(
            "-s",
            "--symbol",
            type=str,
            help="ISIN code of the company.",
            required="-h" not in other_args,
            action="store",
            dest="symbol",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            default=10,
            help="Number of news to display.",
            required=False,
            action="store",
            dest="limit",
        )
        parser.add_argument(
            "-o",
            "--offset",
            type=int,
            default=0,
            help="Offset of news to display.",
            required=False,
            action="store",
            dest="offset",
        )
        parser.add_argument(
            "-lang",
            "--languages",
            type=str,
            default="en,fr",
            help="Languages of news to display.",
            required=False,
            action="store",
            dest="languages",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            self.__degiro_view.companynews(
                symbol=ns_parser.symbol,
                limit=ns_parser.limit,
                offset=ns_parser.offset,
                languages=ns_parser.languages,
            )

    @log_start_end(log=logger)
    def call_create(self, other_args: List[str]):
        """Create an order."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="create",
        )
        parser.add_argument(
            "-a",
            "--action",
            choices=DegiroView.ORDER_ACTION.keys(),
            default="buy",
            help="Action wanted.",
            required=False,
            type=str,
        )
        product_group = parser.add_mutually_exclusive_group(
            required=True,
        )
        product_group.add_argument(
            "-prod",
            "--product",
            help="Id of the product wanted.",
            required=False,
            type=int,
        )
        product_group.add_argument(
            "-sym",
            "--symbol",
            help="Symbol wanted.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "-p",
            "--price",
            help="Price wanted.",
            required="-h" not in other_args,
            type=float,
        )
        size_group = parser.add_mutually_exclusive_group(required=True)
        size_group.add_argument(
            "-s",
            "--size",
            help="Price wanted.",
            required=False,
            type=int,
        )
        size_group.add_argument(
            "-up",
            "--up-to",
            help="Up to price.",
            required=False,
            type=float,
        )
        parser.add_argument(
            "-d",
            "--duration",
            default="gtd",
            choices=DegiroView.ORDER_DURATION.keys(),
            help="Duration of the Order.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "-t",
            "--type",
            choices=DegiroView.ORDER_TYPE.keys(),
            default="limit",
            help="Type of the Order.",
            required=False,
            type=str,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.create(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_hold(self, other_args):
        """Display held products."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="hold",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.hold(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_lastnews(self, other_args: List[str]):
        """Display latest news."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lastnews",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            type=int,
            help="Number of news to display.",
            required=False,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.lastnews(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_login(self, other_args: List[str]):
        """Connect to Degiro's API."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="login",
        )
        parser.add_argument(
            "-otp",
            "--one-time-password",
            default=None,
            help="One-time-password for 2FA.",
            required=False,
            type=int,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            self.__degiro_view.login(otp=ns_parser.one_time_password)

    @log_start_end(log=logger)
    def call_logout(self, other_args: List[str]):
        """Log out from Degiro's API."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="logout",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            self.__degiro_view.logout()

    @log_start_end(log=logger)
    def call_lookup(self, other_args: List[str]):
        """Search for products by their name."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lookup",
        )
        parser.add_argument(
            "search_text",
            type=str,
            help="Name of the company or a text.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            default=10,
            help="Number of result expected (0 for unlimited).",
        )
        parser.add_argument(
            "-o",
            "--offset",
            type=int,
            default=0,
            help="To use an offset.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.lookup(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_pending(self, other_args: List[str]):
        """Display pending orders."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pending",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.pending(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_topnews(self, other_args: List[str]):
        """Display top news."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="topnews",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.topnews(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_update(self, other_args: List[str]):
        """Update an order."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="update",
        )
        parser.add_argument(
            "id",
            help="Order's id.",
            type=str,
        )
        parser.add_argument(
            "-p",
            "--price",
            help="Price wanted.",
            required="-h" not in other_args,
            type=float,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.update(ns_parser=ns_parser)

    @log_start_end(log=logger)
    def call_paexport(self, other_args: List[str]):
        """Export transactions for Portfolio menu into csv format. The transactions
        file is exported to the portfolio/holdings folder and can be loaded directly
        in the Portfolio menu."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="paexport",
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start date.",
            required=True,
            type=valid_date,
        )
        parser.add_argument(
            "-e",
            "--end",
            help="End date.",
            type=valid_date,
            default=datetime.datetime.now(),
        )
        parser.add_argument(
            "-c",
            "--currency",
            help="Used currency.",
            default="USD",
            type=str,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
        )

        if ns_parser:
            self.__degiro_view.transactions_export(ns_parser=ns_parser)
