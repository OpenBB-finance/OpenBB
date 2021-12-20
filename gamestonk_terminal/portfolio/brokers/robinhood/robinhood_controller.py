"""Robinhood Controller"""
__docformat__ = "numpy"

import argparse
from typing import List
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
)

valid_span = ["day", "week", "month", "3month", "year", "5year", "all"]
valid_interval = ["5minute", "10minute", "hour", "day", "week"]


class RobinhoodController:

    CHOICES = ["?", "cls", "help", "q", "quit", "login"]

    Robinhood_CHOICES = ["holdings", "history", "balances"]

    def __init__(self):
        """CONSTRUCTOR"""

        self._robinhood_parser = argparse.ArgumentParser(
            add_help=False, prog="robinhood"
        )
        self.CHOICES.extend(self.Robinhood_CHOICES)

        self._robinhood_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Robinhood:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

    login       login to robinhood

    holdings    show account holdings in stocks
    history     show equity history of your account
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

        (known_args, other_args) = self._robinhood_parser.parse_known_args(
            an_input.split()
        )

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu."""
        try:
            robinhood_model.logoff()
        except Exception:
            # Exception would be not logged in - perfectly fine
            pass
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        try:
            robinhood_model.logoff()
        except Exception:
            # Exception would be not logged in - perfectly fine
            pass
        return True

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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
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
            choices=valid_span,
            default="3month",
            help="Span of historical data",
        )
        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
            default="day",
            choices=valid_interval,
            type=str,
            help="Interval to look at portfolio",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        robinhood_view.display_historical(
            interval=ns_parser.interval,
            span=ns_parser.span,
            export=ns_parser.export,
        )


def menu():

    robinhood_controller = RobinhoodController()
    robinhood_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in robinhood_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (bro)>(rh)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (bro)>(rh)> ")

        try:
            process_input = robinhood_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
