"""Ally Controller"""
__docformat__ = "numpy"

import argparse
from typing import List, Union
import difflib
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.ally import ally_view
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)


class AllyController:
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

    CHOICES_COMMANDS = ["holdings", "history", "balances", "quote", "movers"]
    CHOICES += CHOICES_COMMANDS
    list_choices = [
        "toplosers",
        "toppctlosers",
        "topvolume",
        "topactive",
        "topgainers",
        "toppctgainers",
    ]

    def __init__(self, queue: List[str] = None):
        """CONSTRUCTOR"""

        self._ally_parser = argparse.ArgumentParser(add_help=False, prog="ally")
        self._ally_parser.add_argument("cmd", choices=self.CHOICES)
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["movers"]["-t"] = {c: None for c in self.list_choices}

            self.completer = NestedCompleter.from_nested_dict(choices)

        self.queue = queue or list()

    def print_help(self):
        """Print help"""
        help_text = """
Ally:
    holdings    show account holdings
    history     show history of your account
    balances    show balance details of account

Stock Information:
    quote       get stock quote
    movers      get ranked lists of movers
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

        (known_args, other_args) = self._ally_parser.parse_known_args(an_input.split())

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
        self.queue.insert(0, "ally")
        self.queue.insert(0, "bro")
        self.queue.insert(0, "portfolio")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            prog="holdings",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Ally",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_holdings(export=ns_parser.export)

    @try_except
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_history(
                n_to_show=ns_parser.limit, export=ns_parser.export
            )

    @try_except
    def call_balances(self, other_args: List[str]):
        """Process balances command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balances",
            description="""Account balance details""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_balances(export=ns_parser.export)

    @try_except
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            ally_view.display_stock_quote(ns_parser.ticker)

    @try_except
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
            choices=["A", "N", "Q", "U", "V"],
            default="N",
            dest="exchange",
        )
        parser.add_argument(
            "-l", "--limit", help="Number to show", type=int, default=15, dest="limit"
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:

            ally_view.display_top_lists(
                list_type=ns_parser.list_type,
                exchange=ns_parser.exchange,
                num_to_show=ns_parser.limit,
                export=ns_parser.export,
            )


def menu(queue: List[str] = None):
    """Ally Menu"""
    ally_controller = AllyController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if ally_controller.queue and len(ally_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if ally_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(ally_controller.queue) > 1:
                    return ally_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = ally_controller.queue[0]
            ally_controller.queue = ally_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in ally_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /portfolio/bro/ally/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                ally_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and ally_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /portfolio/bro/ally/ $ ",
                        completer=ally_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /portfolio/bro/ally/ $ ")

        try:
            # Process the input command
            ally_controller.queue = ally_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /portfolio/bro/ally menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                ally_controller.CHOICES,
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
                        ally_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                ally_controller.queue.insert(0, an_input)
            else:
                print("\n")
