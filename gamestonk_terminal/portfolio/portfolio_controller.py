"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import difflib
import os
from os import listdir
from os.path import isfile, join
from typing import List, Union
from datetime import datetime

from prompt_toolkit.completion import NestedCompleter
import pandas as pd

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    try_except,
    valid_date,
    check_positive_float,
    system_clear,
)
from gamestonk_terminal.menu import session

from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.portfolio import (
    portfolio_view,
    portfolio_model,
    yfinance_model,
    portfolio_helper,
)
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

# pylint: disable=R1710,E1101,C0415


class PortfolioController:
    """Portfolio Controller class"""

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

    CHOICES_MENUS = [
        "bro",
        "po",
    ]
    CHOICES_COMMANDS = [
        "load",
        "save",
        "show",
        "add",
        "rmv",
        "ar",
        "rmr",
    ]

    CHOICES += CHOICES_MENUS + CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.port_parser = argparse.ArgumentParser(add_help=False, prog="portfolio")
        self.port_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

        self.portfolio = pd.DataFrame(
            columns=[
                "Name",
                "Type",
                "Quantity",
                "Date",
                "Price",
                "Fees",
                "Premium",
                "Side",
            ]
        )

    def print_help(self):
        """Print help"""
        help_text = """
What do you want to do?

>   bro         brokers holdings, \t\t supports: robinhood, ally, degiro, coinbase
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt

Portfolio:
    load        load data into the portfolio
    save        save your portfolio for future use
    show        show existing transactions
    add         add a security to your portfolio
    rmv         remove a security from your portfolio

Reports:
    ar          annual report for performance of a given portfolio

Graphs:
    rmr         graph your returns versus the market's returns
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

        (known_args, other_args) = self.port_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue

    def call_help(self, _):
        """Process help command"""
        self.print_help()
        return self.queue

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            return self.queue
        return ["q"]

    def call_exit(self, _):
        """Process exit terminal command"""
        print("")
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            self.queue.insert(0, "q")
            return self.queue
        return ["q", "q"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "portfolio")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "reset", "portfolio"]

    # MENUS
    def call_bro(self, _):
        """Process bro command"""
        from gamestonk_terminal.portfolio.brokers import bro_controller

        return bro_controller.menu(self.queue)

    def call_po(self, _):
        """Process po command"""
        return po_controller.menu([], self.queue)

    @try_except
    def call_load(self, other_args: List[str]):
        """Process load command"""
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(path, "portfolios"))
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            choices=[f for f in listdir(path) if isfile(join(path, f))],
            dest="name",
            required="-h" not in other_args,
            help="Name of file to be saved",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.portfolio = portfolio_model.load_df(ns_parser.name)
            print("")
        return self.queue

    @try_except
    def call_save(self, other_args: List[str]):
        """Process save command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="save",
            description="Save your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            required="-h" not in other_args,
            help="Name of file to be saved",
        )
        if other_args and "-n" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if (
                ".csv" in ns_parser.name
                or ".xlsx" in ns_parser.name
                or ".json" in ns_parser.name
            ):
                portfolio_model.save_df(self.portfolio, ns_parser.name)
            else:
                print(
                    "Please submit as 'filename.filetype' with filetype being csv, xlsx, or json\n"
                )

        return self.queue

    def call_show(self, _):
        """Process show command"""
        portfolio_view.show_df(self.portfolio, False)
        return self.queue

    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="Adds an item to your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            required="-h" not in other_args,
            help="Name of item to be added (for example a ticker for a stock)",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            type=lambda s: s.lower(),
            choices=["stock", "cash"],  # "bond", "option", "crypto",
            default="stock",
            help="Type of asset to add",
        )
        parser.add_argument(
            "-q",
            "--quantity",
            dest="quantity",
            type=check_positive_float,
            default=1,
            help="Amounts of the asset owned",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=valid_date,
            default=datetime.now(),
            help="Date: yyyy/mm/dd",
        )
        parser.add_argument(
            "-p",
            "--price",
            dest="price",
            type=check_positive_float,
            required="-h" not in other_args,
            help="Price purchased for asset",
        )
        parser.add_argument(
            "-f",
            "--fees",
            dest="fees",
            type=check_positive_float,
            help="Fees paid for transaction",
        )

        parser.add_argument(
            "-a",
            "--action",
            type=lambda s: s.lower(),
            dest="action",
            choices=["buy", "sell", "interest", "deposit", "withdrawal"],
            default="deposit" if "cash" in other_args else "buy",
            help="Select what you did in the transaction",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if ns_parser.type == "cash" and ns_parser.action not in [
            "deposit",
            "withdrawal",
        ]:
            print("Cash can only be deposited or withdrew\n")
            return
        if ns_parser.type != "cash" and ns_parser.action in ["deposit", "withdrawal"]:
            print("Only cash can be deposited or withdrew\n")
            return

        if ns_parser.type == "stock":
            if not portfolio_helper.is_ticker(ns_parser.name):
                print("Invalid ticker\n")
                return

        data = {
            "Name": ns_parser.name,
            "Type": ns_parser.type,
            "Quantity": ns_parser.quantity,
            "Date": ns_parser.date,
            "Price": ns_parser.price,
            "Fees": ns_parser.fees,
            "Premium": None,  # ns_parser.premium
            "Side": ns_parser.action,
        }
        self.portfolio = self.portfolio.append([data])
        self.portfolio.index = list(range(0, len(self.portfolio.values)))
        print(f"{ns_parser.name.upper()} successfully added\n")
        return self.queue

    def call_rmv(self, _):
        """Process rmv command"""
        portfolio_view.show_df(self.portfolio, True)
        to_rmv = int(input("\nType the index number you want to remove:\n"))
        if 0 <= to_rmv < len(self.portfolio.index):
            self.portfolio = self.portfolio.drop(self.portfolio.index[to_rmv])
            self.portfolio.index = list(range(0, len(self.portfolio.values)))
        else:
            print(
                f"Invalid index please use an integer between 0 and {len(self.portfolio.index)-1}\n"
            )
        return self.queue

    @try_except
    def call_ar(self, other_args: List[str]):
        """Process ar command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ar",
            description="Create an annual report based on given portfolio",
        )
        parser.add_argument(
            "-m",
            "--market",
            type=str,
            dest="market",
            default="SPY",
            help="Choose a ticker to be the market asset",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.portfolio.empty:
                val, hist = portfolio_model.convert_df(self.portfolio)
                if not val.empty:
                    portfolio_view.Report(
                        val, hist, ns_parser.market, 365
                    ).generate_report()
                else:
                    print("Cannot generate a graph from an empty dataframe\n")
            else:
                print("Please add items to the portfolio\n")
        return self.queue

    @try_except
    def call_rmr(self, other_args: List[str]):
        """Process rmr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rmr",
            description="Graph of portfolio returns versus market returns",
        )
        parser.add_argument(
            "-m",
            "--market",
            type=str,
            dest="market",
            default="SPY",
            help="Choose a ticker to be the market asset",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.portfolio.empty:
                val, _ = portfolio_model.convert_df(self.portfolio)
                if not val.empty:
                    df_m = yfinance_model.get_market(val.index[0], ns_parser.market)
                    returns, _ = portfolio_model.get_return(val, df_m, 365)
                    portfolio_view.plot_overall_return(returns, ns_parser.market, True)
                else:
                    print("Cannot generate a graph from an empty dataframe\n")
            else:
                print("Please add items to the portfolio\n")

        return self.queue


def menu(queue: List[str] = None):
    """Portfolio Menu"""
    port_controller = PortfolioController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if port_controller.queue and len(port_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if port_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(port_controller.queue) > 1:
                    return port_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = port_controller.queue[0]
            port_controller.queue = port_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in port_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /portfolio/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                port_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and port_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /portfolio/ $ ",
                    completer=port_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /portfolio/ $ ")

        try:
            # Process the input command
            port_controller.queue = port_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /portfolio menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                port_controller.CHOICES,
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
                        port_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                port_controller.queue.insert(0, an_input)
            else:
                print("\n")
