"""Robinhood Controller"""
__docformat__ = "numpy"

import argparse
from typing import List, Union
import difflib

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.robinhood import (
    robinhood_view,
    robinhood_model,
)
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)


class RobinhoodController:

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

    CHOICES_COMMANDS = ["holdings", "history", "login"]

    valid_span = ["day", "week", "month", "3month", "year", "5year", "all"]
    valid_interval = ["5minute", "10minute", "hour", "day", "week"]

    def __init__(self, queue: List[str] = None):
        """CONSTRUCTOR"""

        self._rh_parser = argparse.ArgumentParser(add_help=False, prog="robinhood")
        self.CHOICES.extend(self.CHOICES_COMMANDS)

        self._rh_parser.add_argument("cmd", choices=self.CHOICES)
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["history"]["-i"] = {c: None for c in self.valid_interval}
            choices["history"]["--interval"] = {c: None for c in self.valid_interval}
            choices["history"]["-s"] = {c: None for c in self.valid_span}
            choices["history"]["--span"] = {c: None for c in self.valid_span}
            self.completer = NestedCompleter.from_nested_dict(choices)
        self.queue = queue if queue else list()

    def print_help(self):
        """Print help"""
        help_text = """
Robinhood:
    login       login to robinhood

    holdings    show account holdings in stocks
    history     show equity history of your account
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

        (known_args, other_args) = self._rh_parser.parse_known_args(an_input.split())

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
        self.queue.insert(0, "rh")
        self.queue.insert(0, "bro")
        self.queue.insert(0, "portfolio")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_login(self, _):
        """Process login"""
        robinhood_model.login()

    @try_except
    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            prog="holdings",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Robinhood",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            robinhood_view.display_holdings(export=ns_parser.export)

    @try_except
    def call_history(self, other_args: List[str]):
        """Process history command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="history",
            description="""Historical Portfolio Info""",
        )
        parser.add_argument(
            "-s",
            "--span",
            dest="span",
            type=str,
            choices=self.valid_span,
            default="3month",
            help="Span of historical data",
        )
        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
            default="day",
            choices=self.valid_interval,
            type=str,
            help="Interval to look at portfolio",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            robinhood_view.display_historical(
                interval=ns_parser.interval,
                span=ns_parser.span,
                export=ns_parser.export,
            )


def menu(queue: List[str] = None):
    """Robinhood Menu"""
    rh_controller = RobinhoodController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if rh_controller.queue and len(rh_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if rh_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(rh_controller.queue) > 1:
                    return rh_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = rh_controller.queue[0]
            rh_controller.queue = rh_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in rh_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /portfolio/bro/rh/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                rh_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and rh_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /portfolio/bro/rh/ $ ",
                    completer=rh_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /portfolio/bro/rh/ $ ")

        try:
            # Process the input command
            rh_controller.queue = rh_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /portfolio/bro/rh menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                rh_controller.CHOICES,
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
                        rh_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                rh_controller.queue.insert(0, an_input)
            else:
                print("\n")
