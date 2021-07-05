__docformat__ = "numpy"

# pylint: disable=R1710

import argparse
import os
from typing import List
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.brokers import (
    rh_api,
    alp_api,
    ally_api,
)
from gamestonk_terminal.brokers.degiro import degiro_controller
from gamestonk_terminal.brokers.brokers_helpers import (
    merge_brokers_holdings,
    print_brokers_holdings,
)


class BrokersController:
    """Brokers Controller"""

    CHOICES = [
        "?",
        "cls",
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
        self.bro_parser = argparse.ArgumentParser(add_help=False, prog="bro")
        self.bro_parser.add_argument("cmd", choices=self.CHOICES)
        self.broker_list = set()
        self.merged_holdings = None

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/brokers"
        )
        print()
        print("   ?/help      show this menu again")
        print(
            "\nBrokers Supported:\n"
            "   ally - Ally Invest\n"
            "   alp  - Alpaca\n"
            "   rh   - Robinhood\n"
            "\nPortfolio:\n"
            "   cls           clear screen\n"
            "   ?/help        show this menu again\n"
            "   q             quit this menu, and shows back to main menu, logs out of brokers\n"
            "   quit          quit to abandon program, logs out of brokers\n"
        )
        self.print_brokers_menu()

    def print_brokers_menu(self):
        print(
            f"Current Broker: {('None', ', '.join(self.broker_list))[bool(self.broker_list)]}\n\n"
            "Ally:\n"
            "   allyhold      view ally holdings\n"
            "Alpaca:\n"
            "   alphold       view alp holdings\n"
            "   alphist       view alp brokers holdings history\n"
            "Robinhood:\n"
            "   rhhold        view rh holdings\n"
            "   rhhist        plot rh brokers holdings history\n"
            "\nDegiro:\n"
            ">  degiro        degiro standalone menu\n"
            "\nMerge:\n"
            "   login         login to your brokers\n"
            "   hold          view net holdings across all logins\n"
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

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.bro_parser.parse_known_args(an_input.split())

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
        """Process help command"""
        self.print_help()

    def call_q(self, _):
        """Process q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process quit command - quit the program"""
        return True

    def call_login(self, other_args):
        """Process login command"""
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
            self.print_brokers_menu()

    def call_rhhist(self, other_args: List[str]):
        """Process rhhist command"""
        rh_api.plot_historical(other_args)

    def call_rhhold(self, _):
        """Process rhhold command"""
        try:
            rh_api.show_holdings()
        except Exception as e:
            print(e)
            print("")

    def call_alphold(self, _):
        """Process alphold command"""
        try:
            alp_api.show_holdings()
        except Exception as e:
            print(e)
            print("")

    def call_alphist(self, other_args: List[str]):
        """Process alphist command"""
        alp_api.plot_historical(other_args)

    def call_allyhold(self, _):
        """Process allyhold command"""
        try:
            ally_api.show_holdings()
        except Exception as e:
            print(e)
            print("")

    def call_degiro(self, _):
        """Process degiro command."""
        if degiro_controller.menu():
            return True
        print("")

    def call_hold(self, _):
        """Process hold command."""
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
        self.merged_holdings = merge_brokers_holdings(holdings)
        print_brokers_holdings(self.merged_holdings)


def menu():
    """Brokers Menu"""
    bro_controller = BrokersController()
    print(
        "\nUSE THIS MENU AT YOUR OWN DISCRETION\n"
        "   - This menu is the only one in the entire repository that has access to your broker accounts. "
        "If you have provided your login details on the config_terminal.py file"
        "   - We review the code thoroughly from each contributor, hence, we can ensure that our codebase "
        "does not take advantage of your data.\n"
        "   - HOWEVER, our project imports almost 200 different open source python modules. Therefore, it "
        "is impossible for us to check the coding standards and security of each of these modules. "
        "Hence why adding this disclaimer here.\n"
    )
    bro_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in bro_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (bro)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (bro)> ")

        try:
            process_input = bro_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
