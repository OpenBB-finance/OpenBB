""" Payoff Controller Module """
__docformat__ = "numpy"

import argparse
import os
from typing import List, Dict

import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    try_except,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.options.yfinance_model import get_option_chain, get_price
from gamestonk_terminal.options.yfinance_view import plot_payoff


class Payoff:

    CHOICES = ["cls", "?", "help", "q", "quit", "list"]
    CHOICES_COMMANDS = [
        "list",
        "add",
        "rmv",
        "pick",
        "plot",
    ]
    CHOICES += CHOICES_COMMANDS

    # pylint: disable=dangerous-default-value
    def __init__(self, ticker: str, expiration: str):
        """Construct Payoff"""

        self.po_parser = argparse.ArgumentParser(add_help=False, prog="po")
        self.po_parser.add_argument("cmd", choices=self.CHOICES)
        self.chain = get_option_chain(ticker, expiration)
        self.calls = list(
            zip(
                self.chain.calls["strike"].tolist(),
                self.chain.calls["lastPrice"].tolist(),
            )
        )
        self.puts = list(
            zip(
                self.chain.puts["strike"].tolist(),
                self.chain.puts["lastPrice"].tolist(),
            )
        )
        self.ticker = ticker
        self.expiration = expiration
        self.options: List[Dict[str, str]] = []
        self.underlying = 0
        self.current_price = get_price(ticker)

    @staticmethod
    def print_help(underlying):
        """Print help"""
        if underlying == 1:
            text = "Long"
        elif underlying == 0:
            text = "None"
        elif underlying == -1:
            text = "Short"

        help_text = f"""
>>OPTION PAYOFF DIAGRAM<<

Underlying Asset: {text}

    list          list available strike prices for calls and puts

    pick          long, short, or none (default) underlying asset
    add           add option to the list of the options to be plotted
    rmv           remove option from the list of the options to be plotted

    plot          show the option payoff diagram
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

        (known_args, other_args) = self.po_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help(self.underlying)
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
        self.print_help(self.underlying)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_list(self, _):
        """Lists available calls and puts"""
        length = max(len(self.calls), len(self.puts)) - 1
        print(
            "Add an option using the index on the left, and not the actual strike price"
        )
        print("#\tcall\tput")
        for i in range(length):
            call = self.calls[i][0] if i < len(self.calls) else ""
            put = self.puts[i][0] if i < len(self.puts) else ""
            print(f"{i}\t{call}\t{put}")
        print("")

    def call_add(self, other_args: List[str]):
        """Process add command"""
        self.add_option(other_args)

    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        self.rmv_option(other_args)

    def call_pick(self, other_args: List[str]):
        """Process pick command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="long",
            description="This function plots option payoff diagrams",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            type=str,
            help="choose what you would like to do with the underlying asset, choose from: long, short, or none",
            required="-h" not in other_args,
        )

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.type == "long":
            self.underlying = 1
        elif ns_parser.type == "none":
            self.underlying = 0
        elif ns_parser.type == "short":
            self.underlying = -1

        self.print_help(self.underlying)

    @try_except
    def call_plot(self, other_args):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="This function plots option payoff diagrams",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        plot_payoff(
            self.current_price,
            self.options,
            self.underlying,
            self.ticker,
            self.expiration,
        )

    def show_setup(self, nl: bool = False):
        """Shows the current assets to display in the diagram"""
        print("#\tType\tHold\tStrike\tCost")
        for i, o in enumerate(self.options):
            sign = "Long" if o["sign"] == 1 else "Short"
            print(f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['cost']}")
        if nl:
            print("")

    @try_except
    def add_option(self, other_args: List[str]):
        """Add an option to the diagram"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add",
            description="""Add options to the diagram.""",
        )
        parser.add_argument(
            "-p",
            "--put",
            dest="put",
            action="store_true",
            help="buy a put instead of a call",
            default=False,
        )
        parser.add_argument(
            "-s",
            "--short",
            dest="short",
            action="store_true",
            help="short the option instead of buying it",
            default=False,
        )
        parser.add_argument(
            "-i",
            "--index",
            dest="index",
            type=int,
            help="list index of the option",
            required="-h" not in other_args and "-k" not in other_args,
        )

        parser.add_argument(
            "-k",
            "--strike",
            dest="strike",
            type=float,
            help="strike price for the option",
            default=None,
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        opt_type = "put" if ns_parser.put else "call"
        sign = -1 if ns_parser.short else 1
        options_list = self.puts if ns_parser.put else self.calls
        if ns_parser.strike is None:
            index = ns_parser.index
        elif float(ns_parser.strike) in [float(x[0]) for x in options_list]:
            index = filter(
                lambda x: float(x[0]) == float(ns_parser.strike), options_list
            )
            index = options_list.index(list(index)[0])
            print(index)
        else:
            print("Invalid strike price, please select a valid price from the list")
            return
        try:
            strike = options_list[index][0]
            cost = options_list[index][1]
        except IndexError:
            print("Please use the index, and not the strike price\n")
            return

        option = {"type": opt_type, "sign": sign, "strike": strike, "cost": cost}
        self.options.append(option)

        self.show_setup(True)

    @try_except
    def rmv_option(self, other_args: List[str]):
        """Remove one of the options from the diagram"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="""Remove one of the options to be shown in the payoff.""",
        )

        parser.add_argument(
            "-k",
            "--strike",
            dest="strike",
            type=int,
            help="strike price for option",
        )

        parser.add_argument(
            "-a",
            "--all",
            dest="all",
            action="store_true",
            help="remove all of the options",
            default=False,
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-k")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.all:
            self.options = []
        else:
            try:
                del self.options[ns_parser.strike]
            except IndexError:
                print("Please use the index, and not the strike price\n")
                return

        self.show_setup(True)


def menu(ticker: str, expiration: str):
    """Portfolio Optimization Menu"""
    plt.close("all")
    po_controller = Payoff(ticker, expiration)
    po_controller.call_help(None)

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
