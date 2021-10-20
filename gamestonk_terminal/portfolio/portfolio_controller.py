"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime

from prompt_toolkit.completion import NestedCompleter
import pandas as pd

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers import bro_controller
from gamestonk_terminal.portfolio.portfolio_analysis import pa_controller
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.portfolio import portfolio_view
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

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
        "load",
        "save",
        "show",
        "add",
        "rmv",
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
        self.portfolio = self.load_df()
        self.loaded = True

    def print_help(self):
        """Print help"""
        help_text = f"""
>> PORTFOLIO <<

{'Portfolio successfully loaded' if self.loaded else 'Could not load portfolio'}

What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

>   bro         brokers holdings, \t\t supports: robinhood, alpaca, ally, degiro
>   pa          portfolio analysis, \t\t analyses your custom portfolio
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt

Portfolio:
    load        instructions on how to load data
    save        updated your csv portfolio
    show        show existing portfolio
    add         add a security to your portfolio
    rmv         remove a security from your portfolio

Reports:
    ar          annual report for performance of a given portfolio
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

    def call_load(self, _):
        """Process load command"""
        portfolio_view.get_load()

    def call_save(self, _):
        """Process save command"""
        portfolio_view.save_df(self.portfolio)

    def call_show(self, _):
        """Process show command"""
        portfolio_view.show_df(self.portfolio, False)

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
            type=str,
            choices=["stock", "bond", "option", "crypto"],
            default="stock",
            help="Type of asset to add",
        )
        parser.add_argument(
            "-v",
            "--volume",
            dest="volume",
            type=float,
            default=1,
            help="Amounts of the asset owned",
        )
        parser.add_argument(
            "-b",
            "--buy",
            dest="buy",
            type=str,
            default=datetime.now().strftime("%Y/%m/%d %H:%M"),
            help="Datetime asset was purchased format: yyyy/mm/dd_hh:mm",
        )
        parser.add_argument(
            "-s",
            "--sell",
            dest="sell",
            type=str,
            help="Datetime asset was sold format: yyyy/mm/dd_hh:mm",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.buy:
            buy = ns_parser.buy.replace("_", " ")
        else:
            buy = ""

        if ns_parser.sell:
            sell = ns_parser.sell.replace("_", " ")
        else:
            sell = ""

        data = {
            "Name": ns_parser.name,
            "Type": ns_parser.type,
            "Volume": ns_parser.volume,
            "BDatetime": buy,
            "SDatetime": sell,
        }
        self.portfolio = self.portfolio.append([data])
        self.portfolio.index = list(range(0, len(self.portfolio.values)))
        print(f"{ns_parser.name.upper()} successfully added\n")

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

    def load_df(self) -> pd.DataFrame:
        """Loads the user's portfolio"""
        try:
            df = pd.read_csv("exports/portfolio/portfolio.csv")
            df.index = list(range(0, len(self.portfolio.values)))
            return df
        except FileNotFoundError:
            self.loaded = False
            return pd.DataFrame(
                columns=[
                    "Name",
                    "Type",
                    "Volume",
                    "BDatetime",
                    "SDatetime",
                ]
            )


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
