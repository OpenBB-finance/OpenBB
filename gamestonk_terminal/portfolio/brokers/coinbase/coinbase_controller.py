"""Coinbase Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import os
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.coinbase import (
    coinbase_view,
)
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
)


class CoinbaseController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
    ]

    CB_CHOICES = ["account", "history", "orders", "deposits"]

    def __init__(self):
        """CONSTRUCTOR"""

        self._cb_parser = argparse.ArgumentParser(add_help=False, prog="cb")
        self.CHOICES.extend(self.CB_CHOICES)

        self._cb_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Coinbase:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

    account     show balance of your account
    history     show history of your account
    deposits    show all your deposits or internal transfers
    orders      show all your orders

"""

        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self._cb_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

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
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "--acc")

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            coinbase_view.display_account(ns_parser.all, ns_parser.export)

        except Exception as e:
            print(e, "\n")

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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "--acc")

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            coinbase_view.display_history(
                ns_parser.account, ns_parser.export, ns_parser.limit
            )

        except Exception as e:
            print(e, "\n")

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
            choices=[
                "product_id",
                "side",
                "price",
                "size",
                "type",
                "created_at",
                "status",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "--acc")

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            coinbase_view.display_orders(
                ns_parser.limit, ns_parser.sortby, ns_parser.descend, ns_parser.export
            )

        except Exception as e:
            print(e, "\n")

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
            choices=["internal_deposit", "deposit"],
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
            choices=[
                "created_at",
                "amount",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            coinbase_view.display_deposits(
                ns_parser.limit,
                ns_parser.sortby,
                ns_parser.type,
                ns_parser.descend,
                ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")


def menu():

    cb_controller = CoinbaseController()
    cb_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in cb_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (bro)>(cb)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (bro)>(cb)> ")

        try:
            process_input = cb_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
