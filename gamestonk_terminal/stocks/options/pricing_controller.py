""" Pricing Controller Module """
__docformat__ = "numpy"

import argparse
from typing import List
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.options import yfinance_view


class PricingController:
    """Pricing Controller class."""

    CHOICES = ["cls", "?", "help", "q", "quit"]
    CHOICES_COMMANDS = [
        "add",
        "rmv",
        "show",
        "rnval",
    ]
    CHOICES += CHOICES_COMMANDS

    # pylint: disable=dangerous-default-value
    def __init__(self, ticker: str, selected_date: str, prices: pd.DataFrame):
        """Construct Pricing"""

        self.pricing_parser = argparse.ArgumentParser(add_help=False, prog="pricing")
        self.pricing_parser.add_argument("cmd", choices=self.CHOICES)

        self.ticker = ticker
        self.selected_date = selected_date
        self.prices = prices

    def print_help(self):
        """Print help"""
        help_text = f"""
What do you want to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

Current Ticker: {self.ticker or None}
Current Expiry: {self.selected_date or None}

Options Pricing:
    add           add an expected price to the list
    rmv           remove an expected price from the list
    show          show the listed of expected prices
    rnval         risk neutral valuation for an option
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

        (known_args, other_args) = self.pricing_parser.parse_known_args(
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
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    @try_except
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="Adds a price to the list",
        )
        parser.add_argument(
            "-p",
            "--price",
            type=float,
            required="-h" not in other_args,
            dest="price",
            help="Projected price of the stock at the expiration date",
        )
        parser.add_argument(
            "-c",
            "--chance",
            type=float,
            required="-h" not in other_args,
            dest="chance",
            help="Chance that the stock is at a given projected price",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if ns_parser.price in self.prices["Price"].to_list():
            df = self.prices[(self.prices["Price"] != ns_parser.price)]
        else:
            df = self.prices

        new = {"Price": ns_parser.price, "Chance": ns_parser.chance}
        df = df.append(new, ignore_index=True)
        self.prices = df.sort_values("Price")
        print("")

    @try_except
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rmv",
            description="Removes a price from the list",
        )
        parser.add_argument(
            "-p",
            "--price",
            type=float,
            required="-h" not in other_args and "-a" not in other_args,
            dest="price",
            help="Price you want to remove from the list",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            default=False,
            dest="all",
            help="Remove all prices from the list",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if ns_parser.all:
            self.prices = pd.DataFrame(columns=["Price", "Chance"])
            return

        self.prices = self.prices[(self.prices["Price"] != ns_parser.price)]
        print("")

    @try_except
    def call_show(self, _):
        """Process show command"""
        print(f"Estimated price(s) of {self.ticker} at {self.selected_date}")
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    self.prices,
                    headers=self.prices.columns,
                    floatfmt=".2f",
                    showindex=False,
                    tablefmt="fancy_grid",
                ),
                "\n",
            )
        else:
            print(self.prices.to_string, "\n")
            print("")

    @try_except
    def call_rnval(self, other_args: List[str]):
        """Process rnval command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rnval",
            description="The risk neutral value of the options",
        )
        parser.add_argument(
            "-p",
            "--put",
            action="store_true",
            default=False,
            help="Show puts instead of calls",
        )
        parser.add_argument(
            "-m",
            "--min",
            type=float,
            default=None,
            dest="mini",
            help="Minimum strike price shown",
        )
        parser.add_argument(
            "-M",
            "--max",
            type=float,
            default=None,
            dest="maxi",
            help="Maximum strike price shown",
        )
        parser.add_argument(
            "-r",
            "--risk",
            type=float,
            default=None,
            dest="risk",
            help="The risk-free rate to use",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required. \n")
            return
        if sum(self.prices["Chance"]) != 1:
            print("Total chances must equal one\n")
            return

        yfinance_view.risk_neutral_vals(
            self.ticker,
            self.selected_date,
            ns_parser.put,
            self.prices,
            ns_parser.mini,
            ns_parser.maxi,
            ns_parser.risk,
        )


def menu(ticker: str, selected_date: str, prices: pd.DataFrame):
    """Options Pricing Menu"""
    plt.close("all")
    pricing_controller = PricingController(ticker, selected_date, prices)
    pricing_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in pricing_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(options)>(pricing)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(options)>(pricing)> ")

        try:
            plt.close("all")

            process_input = pricing_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
