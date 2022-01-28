import argparse
from typing import List

from prompt_toolkit.completion import NestedCompleter
import gamestonk_terminal.config_terminal as config

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.degiro.degiro_view import DegiroView


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
    ]
    PATH = "/portfolio/bro/degiro/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.__degiro_view = DegiroView()

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        DegiroView.help_display()

    def call_cancel(self, other_args: List[str]):
        """Cancel an order using the `id`."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="companynews",
        )
        parser.add_argument(
            "id",
            help="Order's id.",
            type=str,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.cancel(ns_parser=ns_parser)

    def call_companynews(self, other_args: List[str]):
        """Display news related to a company using its ISIN."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="companynews",
        )
        parser.add_argument(
            "isin",
            type=str,
            help="ISIN code of the company.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.companynews(ns_parser=ns_parser)

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
            required=True,
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
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.create(ns_parser=ns_parser)

    def call_hold(self, other_args):
        """Display held products."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="hold",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.hold(ns_parser=ns_parser)

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
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.lastnews(ns_parser=ns_parser)

    def call_login(self, other_args: List[str]):
        """Connect to Degiro's API."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="login",
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            default=config.DG_USERNAME,
            help="Username in Degiro's account.",
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            default=config.DG_PASSWORD,
            help="Password in Degiro's account.",
        )
        parser.add_argument(
            "-o",
            "--otp",
            type=int,
            default=None,
            help="One time password (2FA).",
        )
        parser.add_argument(
            "-s",
            "--topt-secret",
            type=str,
            default=None,
            help="TOTP SECRET (2FA).",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.login(ns_parser=ns_parser)

    def call_logout(self, other_args: List[str]):
        """Log out from Degiro's API."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="logout",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.logout(ns_parser=ns_parser)

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
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.lookup(ns_parser=ns_parser)

    def call_pending(self, other_args: List[str]):
        """Display pending orders."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pending",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.pending(ns_parser=ns_parser)

    def call_topnews(self, other_args: List[str]):
        """Display top news."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="topnews",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.topnews(ns_parser=ns_parser)

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
            required=True,
            type=float,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.update(ns_parser=ns_parser)
