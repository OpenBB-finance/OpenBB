"""Government Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.government import quiverquant_view


class GovController:
    """Gov Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "last_congress",
        "buy_congress",
        "sell_congress",
        "congress",
        "raw_congress",
        "last_senate",
        "buy_senate",
        "sell_senate",
        "senate",
        "raw_senate",
        "last_house",
        "buy_house",
        "sell_house",
        "house",
        "raw_house",
        "last_contracts",
        "sum_contracts",
        "raw_contracts",
        "contracts",
        "qtr_contracts",
        "qtr_contracts_hist",
        "top_lobbying",
        "lobbying",
    ]

    def __init__(
        self,
        ticker: str,
    ):
        """Constructor"""
        self.ticker = ticker
        self.gov_parser = argparse.ArgumentParser(add_help=False, prog="gov")
        self.gov_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/government"
        )
        print("\nExploratory Data Analysis:")
        print("   cls         clear screen")
        print("   ?/help      show this menu again")
        print("   q                quit this menu, and shows back to main menu")
        print("   quit             quit to abandon program")
        print("")
        print("Explore:")
        print("   last_congress        last congress trading")
        print("   buy_congress         plot top buy congress tickers")
        print("   sell_congress        plot top sell congress tickers")
        print("   last_senate          last senate trading")
        print("   buy_senate           plot top buy senate tickers")
        print("   sell_senate          plot top sell senate tickers")
        print("   last_house           last house trading")
        print("   buy_house            plot top buy house tickers")
        print("   sell_house           plot top sell house tickers")
        print("   last_contracts       last government contracts")
        print("   sum_contracts        plot sum of last government contracts")
        print("   qtr_contracts        quarterly government contracts best regression")
        print("   top_lobbying         top corporate lobbying tickers")
        print("")
        if self.ticker:
            print(f"Ticker: {self.ticker}")
            print("   raw_congress         raw congress trades on the ticker")
            print("   congress             plot congress trades on the ticker")
            print("   raw_senate           raw senate trades on the ticker")
            print("   senate               plot senate trades on the ticker")
            print("   raw_house            raw house trades on the ticker")
            print("   house                plot house trades on the ticker")
            print("   raw_contracts        raw contracts on the ticker")
            print("   contracts            plot sum of contracts on the ticker")
            print("   qtr_contracts_hist   quarterly government contracts historical")
            print("   lobbying             corporate lobbying details")
            print("")
        return

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

        (known_args, other_args) = self.gov_parser.parse_known_args(an_input.split())

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

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_last_congress(self, other_args: List[str]):
        """Process last_congress command"""
        quiverquant_view.last_government(other_args, "congress")

    def call_buy_congress(self, other_args: List[str]):
        """Process buy_congress command"""
        quiverquant_view.buy_government(other_args, "congress")

    def call_sell_congress(self, other_args: List[str]):
        """Process sell_congress command"""
        quiverquant_view.sell_government(other_args, "congress")

    def call_raw_congress(self, other_args: List[str]):
        """Process raw_congress command"""
        quiverquant_view.raw_government(other_args, self.ticker, "congress")

    def call_congress(self, other_args: List[str]):
        """Process congress command"""
        quiverquant_view.government_trading(other_args, self.ticker, "congress")

    def call_last_senate(self, other_args: List[str]):
        """Process last_senate command"""
        quiverquant_view.last_government(other_args, "senate")

    def call_buy_senate(self, other_args: List[str]):
        """Process buy_senate command"""
        quiverquant_view.buy_government(other_args, "senate")

    def call_sell_senate(self, other_args: List[str]):
        """Process sell_senate command"""
        quiverquant_view.sell_government(other_args, "senate")

    def call_raw_senate(self, other_args: List[str]):
        """Process raw_senate command"""
        quiverquant_view.raw_government(other_args, self.ticker, "senate")

    def call_senate(self, other_args: List[str]):
        """Process senate command"""
        quiverquant_view.government_trading(other_args, self.ticker, "senate")

    def call_last_house(self, other_args: List[str]):
        """Process last_house command"""
        quiverquant_view.last_government(other_args, "house")

    def call_buy_house(self, other_args: List[str]):
        """Process buy_house command"""
        quiverquant_view.buy_government(other_args, "house")

    def call_sell_house(self, other_args: List[str]):
        """Process sell_house command"""
        quiverquant_view.sell_government(other_args, "house")

    def call_raw_house(self, other_args: List[str]):
        """Process raw_house command"""
        quiverquant_view.raw_government(other_args, self.ticker, "house")

    def call_house(self, other_args: List[str]):
        """Process house command"""
        quiverquant_view.government_trading(other_args, self.ticker, "house")

    def call_last_contracts(self, other_args: List[str]):
        """Process last_contracts command"""
        quiverquant_view.last_contracts(other_args)

    def call_sum_contracts(self, other_args: List[str]):
        """Process sum_contracts command"""
        quiverquant_view.sum_contracts(other_args)

    def call_raw_contracts(self, other_args: List[str]):
        """Process raw_contracts command"""
        quiverquant_view.raw_contracts(other_args, self.ticker)

    def call_contracts(self, other_args: List[str]):
        """Process contracts command"""
        quiverquant_view.contracts(other_args, self.ticker)

    def call_qtr_contracts(self, other_args: List[str]):
        """Process qtr_contracts command"""
        quiverquant_view.qtr_contracts(other_args)

    def call_qtr_contracts_hist(self, other_args: List[str]):
        """Process qtr_contracts_hist command"""
        quiverquant_view.qtr_contracts_hist(other_args, self.ticker)

    def call_top_lobbying(self, other_args: List[str]):
        """Process top_lobbying command"""
        quiverquant_view.top_lobbying(other_args)

    def call_lobbying(self, other_args: List[str]):
        """Process lobbying command"""
        quiverquant_view.lobbying(other_args, self.ticker)


def menu(ticker: str):
    """Government Menu"""

    gov_controller = GovController(ticker)
    gov_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in gov_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (gov)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (gov)> ")

        try:
            plt.close("all")

            process_input = gov_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
