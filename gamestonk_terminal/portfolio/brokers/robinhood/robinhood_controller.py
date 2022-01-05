"""Robinhood Controller"""
__docformat__ = "numpy"

import argparse
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.robinhood import (
    robinhood_view,
    robinhood_model,
)
from gamestonk_terminal.decorators import try_except, menu_decorator
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)

# pylint: disable=W0613


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


@menu_decorator("/portfolio/bro/rh/", RobinhoodController)
def menu(queue: List[str] = None):
    """Robinhood Menu"""
