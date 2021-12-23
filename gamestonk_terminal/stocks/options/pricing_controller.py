""" Pricing Controller Module """
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union
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
    """Pricing Controller class"""

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
    CHOICES_COMMANDS = [
        "add",
        "rmv",
        "show",
        "rnval",
    ]
    CHOICES += CHOICES_COMMANDS

    def __init__(
        self,
        ticker: str,
        selected_date: str,
        prices: pd.DataFrame,
        queue: List[str] = None,
    ):
        """Construct"""
        self.pricing_parser = argparse.ArgumentParser(add_help=False, prog="pricing")
        self.pricing_parser.add_argument("cmd", choices=self.CHOICES)

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:

            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

        self.ticker = ticker
        self.selected_date = selected_date
        self.prices = prices

    def print_help(self):
        """Print help"""
        help_text = f"""
Ticker: {self.ticker or None}
Expiry: {self.selected_date or None}

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

        (known_args, other_args) = self.pricing_parser.parse_known_args(
            an_input.split()
        )

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
        self.queue.insert(0, "pricing")
        if self.selected_date:
            self.queue.insert(0, f"exp {self.selected_date}")
        if self.ticker:
            self.queue.insert(0, f"load {self.ticker}")
        self.queue.insert(0, "options")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.all:
                self.prices = pd.DataFrame(columns=["Price", "Chance"])
            else:
                self.prices = self.prices[(self.prices["Price"] != ns_parser.price)]
            print("")

    @try_except
    def call_show(self, other_args):
        """Process show command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Display prices",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if sum(self.prices["Chance"]) == 1:
                        yfinance_view.risk_neutral_vals(
                            self.ticker,
                            self.selected_date,
                            ns_parser.put,
                            self.prices,
                            ns_parser.mini,
                            ns_parser.maxi,
                            ns_parser.risk,
                        )
                    else:
                        print("Total chances must equal one\n")
                else:
                    print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                print("No ticker loaded. First use `load <ticker>`\n")


def menu(
    ticker: str, selected_date: str, prices: pd.DataFrame, queue: List[str] = None
):
    """Pricing Menu"""
    pricing_controller = PricingController(ticker, selected_date, prices, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if pricing_controller.queue and len(pricing_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if pricing_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(pricing_controller.queue) > 1:
                    return pricing_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = pricing_controller.queue[0]
            pricing_controller.queue = pricing_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in pricing_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /stocks/options/pricing/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                pricing_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and pricing_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/options/pricing/ $ ",
                    completer=pricing_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/options/pricing/ $ ")

        try:
            # Process the input command
            pricing_controller.queue = pricing_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options/pricing menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                pricing_controller.CHOICES,
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
                        pricing_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                pricing_controller.queue.insert(0, an_input)
            else:
                print("\n")
