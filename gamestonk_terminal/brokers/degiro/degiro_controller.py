# IMPORTATION STANDARD
import argparse
import os

# IMPORTATION THIRDPARTY
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
import gamestonk_terminal.config_terminal as config

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.brokers.degiro.degiro_view import DegiroView


class DegiroController:
    CHOICES = [
        "?",
        "cls",
        "cancel",
        "companynews",
        "create",
        "hold",
        "lastnews",
        "login",
        "logout",
        "lookup",
        "pending",
        "q",
        "quit",
        "topnews",
        "update",
        "help",
    ]

    def __init__(self):
        self.__degiro_view = DegiroView()
        self.__degiro_parser = argparse.ArgumentParser(
            add_help=False,
            prog="degiro",
        )
        self.__degiro_parser.add_argument("cmd", choices=self.CHOICES)

    def cancel(self, l_args):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.cancel(ns_parser=ns_parser)

    def companynews(self, l_args):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.companynews(ns_parser=ns_parser)

    def create(self, l_args):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.create(ns_parser=ns_parser)

    def help(self, _):
        """Show the help menu."""
        DegiroView.help_display()

    def hold(self, l_args):
        """Display held products."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="hold",
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.hold(ns_parser=ns_parser)

    def lastnews(self, l_args):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.lastnews(ns_parser=ns_parser)

    def login(self, l_args):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.login(ns_parser=ns_parser)

    def logout(self, l_args):
        """Log out from Degiro's API."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="logout",
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.logout(ns_parser=ns_parser)

    def lookup(self, l_args):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.lookup(ns_parser=ns_parser)

    def pending(self, l_args):
        """Display pending orders."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pending",
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.pending(ns_parser=ns_parser)

    def q(self, _):
        """Process Q command - quit the menu."""
        return False

    def quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def topnews(self, l_args):
        """Display top news."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="topnews",
        )
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.topnews(ns_parser=ns_parser)

    def update(self, l_args):
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
        ns_parser = parse_known_args_and_warn(parser, l_args)

        self.__degiro_view.update(ns_parser=ns_parser)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        try:
            degiro_parser = self.__degiro_parser

            # Empty command
            if not an_input:
                print("")
                return None

            (known_args, other_args) = degiro_parser.parse_known_args(an_input.split())

            # Help menu again
            if known_args.cmd == "?":
                DegiroView.help_display()
                return None

            # Clear screen
            if known_args.cmd == "cls":
                os.system("cls||clear")
                return None

            return getattr(
                self,
                known_args.cmd,
                lambda: "Command not recognized!",
            )(other_args)
        except Exception as e:
            print(e)
            print("")

            return None


def menu():
    """Degiro Menu"""

    # SETUP CONTROLLER
    degiro_controller = DegiroController()
    degiro_controller.help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in degiro_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (bro)>(degiro)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (bro)>(degiro)> ")

        try:
            process_input = degiro_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
