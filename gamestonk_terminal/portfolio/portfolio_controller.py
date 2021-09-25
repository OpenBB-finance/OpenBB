"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import os

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers import bro_controller
from gamestonk_terminal.portfolio.portfolio_analysis import pa_controller
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller

# pylint: disable=R1710


class PortfolioController:
    """Portfolio Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_MENUS = [
        "bro",
        "pa",
        "po",
    ]

    CHOICES += CHOICES_MENUS

    def __init__(self):
        """Constructor"""
        self.port_parser = argparse.ArgumentParser(add_help=False, prog="portfolio")
        self.port_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer = NestedCompleter.from_nested_dict(
            {c: None for c in self.CHOICES}
        )

    def print_help(self):
        """Print help"""
        help_text = """
>> PORTFOLIO <<

What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

>   bro         brokers holdings, \t\t supports: robinhood, alpaca, ally, degiro
>   pa          portfolio analysis, \t\t analyses your custom portfolio
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt
        """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False, or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.port_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    # MENUS
    def call_bro(self, _):
        """Process bro command"""
        ret = bro_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_pa(self, _):
        """Process pa command"""
        ret = pa_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_po(self, _):
        """Process po command"""
        ret = po_controller.menu([])
        if ret is False:
            self.print_help()
        else:
            return True


def menu():
    """Portfolio Menu"""
    portfolio_controller = PortfolioController()
    portfolio_controller.call_help(None)
    while True:
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in portfolio_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (portfolio)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (portfolio)> ")

        try:
            process_input = portfolio_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exit\n")
            continue
