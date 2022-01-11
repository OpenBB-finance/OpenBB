"""Coinbase Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
from typing import List, Union
import difflib

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
    try_except,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)


class CoinbaseController:
    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]

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

    def __init__(self, queue: List[str] = None):
        """CONSTRUCTOR"""

        self._cb_parser = argparse.ArgumentParser(add_help=False, prog="cb")
        self.CHOICES.extend(self.CHOICES_COMMANDS)

        self._cb_parser.add_argument("cmd", choices=self.CHOICES)
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["orders"]["-s"] = {c: None for c in self.order_sortby}
            choices["orders"]["--sortby"] = {c: None for c in self.order_sortby}
            choices["deposits"]["-s"] = {c: None for c in self.deposit_sort}
            choices["deposits"]["--sortby"] = {c: None for c in self.deposit_sort}
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.queue = queue if queue else list()

    def print_help(self):
        """Print help"""
        help_text = """
Coinbase:
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
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self._cb_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "cb")
        self.queue.insert(0, "bro")
        self.queue.insert(0, "portfolio")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_view.display_account(
                currency=ns_parser.currency,
                export=ns_parser.export,
            )

    @try_except
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_view.display_history(
                ns_parser.account, ns_parser.export, ns_parser.limit
            )

    @try_except
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
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--acc")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coinbase_view.display_orders(
                ns_parser.limit, ns_parser.sortby, ns_parser.descend, ns_parser.export
            )

    @try_except
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
            choices=self.deposit_sort,
        )
        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinbase_view.display_deposits(
                ns_parser.limit,
                ns_parser.sortby,
                ns_parser.type,
                ns_parser.descend,
                ns_parser.export,
            )


def menu(queue: List[str] = None):
    """Coinbase Menu"""
    cb_controller = CoinbaseController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if cb_controller.queue and len(cb_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if cb_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(cb_controller.queue) > 1:
                    return cb_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = cb_controller.queue[0]
            cb_controller.queue = cb_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in cb_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /portfolio/bro/cb/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                cb_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and cb_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /portfolio/bro/cb/ $ ",
                        completer=cb_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /portfolio/bro/cb/ $ ")

        try:
            # Process the input command
            cb_controller.queue = cb_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /portfolio/bro/cb menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                cb_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        cb_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                cb_controller.queue.insert(0, an_input)
            else:
                print("\n")
