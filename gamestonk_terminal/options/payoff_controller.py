""" Payoff Controller Module """
__docformat__ = "numpy"

import argparse
import os
from typing import List
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_non_negative,
)
from gamestonk_terminal.menu import session


class Payoff:

    CHOICES = ["cls", "?", "help", "q", "quit"]
    CHOICES_COMMANDS = [
        "select",
        "add",
        "rmv",
        "long",
        "short",
        "none",
        "plot",
    ]
    CHOICES += CHOICES_COMMANDS

    # pylint: disable=dangerous-default-value
    def __init__(self, ticker: str, expiration: str):
        """Construct Payoff"""

        self.po_parser = argparse.ArgumentParser(add_help=False, prog="po")
        self.po_parser.add_argument("cmd", choices=self.CHOICES)
        self.ticker = ticker
        self.expiration = expiration
        self.options: List[dict[str, str]] = []
        self.underlying = 0

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """
>>OPTION PAYOFF DIAGRAM<<

What would you like to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

Options:
    add           add tickers to the list of the tickers to be optimized
    rmv           remove tickers from the list of the tickers to be optimized"

Underlying Asset:
    long          long the underlying asset
    short         short the underlying asset
    none          do not hold the underlying asset

Show:
    plot          show the efficient frontier
        """
        # {('None', ', '.join(tickers))[bool(tickers)]}
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

        (known_args, other_args) = self.po_parser.parse_known_args(an_input.split())

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

    def call_help(self):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_add(self, other_args: List[str]):
        """Process add command"""
        self.add_option(other_args)

    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        self.rmv_option(other_args)

    def call_long(self):
        """Process call command"""
        self.underlying = 1

    def call_short(self):
        """Process short command"""
        self.underlying = -1

    def call_none(self):
        """Process none command"""
        self.underlying = 0

    def call_plot(self, other_args):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="""This function plots random portfolios based
                        on their risk and returns and shows the efficient frontier.""",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-n")
        parser.add_argument(
            "-n",
            "--number-portfolios",
            default=300,
            type=check_non_negative,
            dest="n_port",
            help="number of portfolios to simulate",
        )
        parser.add_argument(
            "-r",
            "--risk-free",
            action="store_true",
            dest="risk_free",
            default=False,
            help="Adds the optimal line with the risk-free asset",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            print("Graph should show")

        except Exception as e:
            print(e, "\n")

    def add_option(self, other_args: List[str]):
        """Add ticker or Select tickes for portfolio to be optimized"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add/select",
            description="""Add/Select tickers for portfolio to be optimized.""",
        )
        parser.add_argument(
            "-t",
            "--tickers",
            dest="add_tickers",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="tickers to be used in the portfolio to optimize.",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-t")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            self.options.append(ns_parser.add_tickers)

            for option in self.options:
                print(option)

            # self.tickers = list(tickers)
            print("")

        except Exception as e:
            print(e, "\n")

    def rmv_option(self, other_args: List[str]):
        """Remove one of the tickers to be optimized"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="""Remove one of the options to be shown in the payoff.""",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="rmv_tickers",
            type=str,
            help="whether you want a call or a put",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="rmv_tickers",
            type=str,
            help="whether you want a call or a put",
            required=True,
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-t")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            # tickers = set(self.tickers)
            for option in ns_parser.rmv_tickers:
                self.options.remove(option)

            for option in self.options:
                print(option)

            print("")

        except Exception as e:
            print(e, "\n")


def menu(ticker: str, expiration: str):
    """Portfolio Optimization Menu"""
    plt.close("all")
    po_controller = Payoff(ticker, expiration)
    po_controller.call_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in po_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (options)>(payoff)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (options)>(payoff)> ")

        try:
            plt.close("all")

            process_input = po_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
