__docformat__ = "numpy"

import argparse
from typing import List
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio import (
    rh_api,
    alp_api,
    ally_api,
    degiro_api,
)
from gamestonk_terminal.portfolio.portfolio_helpers import (
    merge_portfolios,
    print_portfolio,
)


class PortfolioController:
    """Portfolio Controller"""

    CHOICES = [
        "alphist",
        "alphold",
        "allyhold",
        "degiro",
        "help",
        "hold",
        "login",
        "q",
        "quit",
        "rhhold",
        "rhhist",
    ]

    BROKERS = [
        "alp",
        "ally",
        "rh",
    ]

    def __init__(self):
        self.port_parser = argparse.ArgumentParser(add_help=False, prog="port")
        self.port_parser.add_argument("cmd", choices=self.CHOICES)
        self.broker_list = set()
        self.merged_holdings = None

    @classmethod
    def print_help(cls, broker_list):
        """Print help"""

        print(
            "Brokers Supported:\n"
            "   ally - Ally Invest\n"
            "   alp  - Alpaca\n"
            "   rh   - Robinhood\n"
            "\nPortfolio:\n"
            "   help          show this menu again\n"
            "   q             quit this menu, and shows back to main menu, logs out of brokers\n"
            "   quit          quit to abandon program, logs out of brokers\n"
        )
        cls.print_portfolio_menu(broker_list)

    @staticmethod
    def print_portfolio_menu(broker_list):
        print(
            f"\nCurrent Broker: {('None', ', '.join(broker_list))[bool(broker_list)]}\n\n"
            "Ally:\n"
            "   allyhold      view ally holdings\n"
            "Alpaca:\n"
            "   alphold       view alp holdings\n"
            "   alphist       view alp portfolio history\n"
            "Degiro:\n"
            "   degiro        view degiro sub-menu\n"
            "Merge:\n"
            "   login         login to your brokers\n"
            "   hold          view net holdings across all logins\n"
            "Robinhood:\n"
            "   rhhold        view rh holdings\n"
            "   rhhist        plot rh portfolio history\n"
        )

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        (known_args, other_args) = self.port_parser.parse_known_args(an_input.split())

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""

        self.print_help(self.broker_list)

    def call_q(self, _):
        """Process Q command - quit the menu"""

        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""

        return True

    def call_login(self, other_args):
        broker_list = self.broker_list
        logged_in = False
        if not other_args:
            print("Please enter brokers you wish to login to")
            print("")
            return
        for broker in other_args:
            if broker in self.BROKERS:
                api = broker + "_api"
                try:
                    # pylint: disable=eval-used
                    eval(api + ".login()")
                    self.broker_list.add(broker)
                    logged_in = True
                except Exception as e:
                    print("")
                    print(f"Error at broker : {broker}")
                    print(e)
                    print("Make sure credentials are defined in config_terminal.py ")
                    print("")
            else:
                print(f"{broker} not supported")

        if logged_in:
            self.print_portfolio_menu(broker_list)

    def call_rhhist(self, other_args: List[str]):
        rh_api.plot_historical(other_args)

    def call_rhhold(self, _):
        try:
            rh_api.show_holdings()
        except Exception as e:
            print(e)
            print("")

    def call_alphold(self, _):
        try:
            alp_api.show_holdings()
        except Exception as e:
            print(e)
            print("")

    def call_alphist(self, other_args: List[str]):
        alp_api.plot_historical(other_args)

    def call_allyhold(self, _):
        try:
            ally_api.show_holdings()
        except Exception as e:
            print(e)
            print("")

    def call_degiro(self, _):
        """"Process degiro command."""

        return degiro_api.menu()

    def call_hold(self, _):
        holdings = pd.DataFrame(
            columns=["Symbol", "MarketValue", "Quantity", "CostBasis"]
        )
        if not self.broker_list:
            print("Login to desired brokers\n")
        for broker in self.broker_list:
            holdings = pd.concat(
                # pylint: disable=eval-used
                [holdings, eval(broker + "_api.return_holdings()")],
                axis=0,
            )
        self.merged_holdings = merge_portfolios(holdings)
        print_portfolio(self.merged_holdings)


def menu():
    """Portfolio Analysis Menu"""

    port_controller = PortfolioController()
    port_controller.print_help(port_controller.broker_list)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in port_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (pa)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (pa)> ")

        try:
            process_input = port_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
