__docformat__ = "numpy"

import argparse
from typing import List
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio import rh_api


class PortfolioController:

    CHOICES = [
        "help",
        "q",
        "quit",
        "login",
        "hold",
        "rhhist",
    ]

    BROKERS = [
        "rh",
    ]

    def __init__(self):
        self.port_parser = argparse.ArgumentParser(add_help=False, prog="port")
        self.port_parser.add_argument("cmd", choices=self.CHOICES)
        self.brokers_list = set()

    @staticmethod
    def print_help(broker_list):
        if not broker_list:
            print_broke = " None"
        if broker_list:
            print_broke = " "
            for broker in broker_list:
                print_broke += broker + " "

        """ Print help """
        print("\nPortfolio:")
        print("   help          show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("   login         login to your brokers")
        print("\nCurrent Brokers :" + print_broke)
        print("")
        print("\nCurrently Supported :")
        print("   rh             Robinhood - fuck these guys")
        print("")

    def print_portfolio_menu(self):

        print_broke = " "
        for broker in self.brokers_list:
            print_broke += broker + " "
        print("\nCurrent Brokers :" + print_broke)
        print("")
        print("    hold       check holdings")
        print("   rhhist      plot historical RH portfolio")
        print("")

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
        self.print_help(self.brokers_list)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_login(self, other_args):

        if not other_args:
            print("Please enter brokers you wish to login to")
            print("")
            return
        for broker in other_args:
            api = broker + "_api"
            self.brokers_list.add(broker)
            try:
                eval(api + ".login()")
            except Exception as e:
                print("")
                print(f"Error at broker : {broker}")
                print(e)
                print("Make sure credentials are defined in config_terminal.py ")
                print("")

        self.print_portfolio_menu()

    def call_rhhist(self, other_args: List[str]):
        rh_api.plot_historical(other_args)

    def call_hold(self, _):
        try:
            rh_api.show_holdings()
        except Exception as e:
            print(e)
            print("")


def menu():
    """Portfolio Analysis Menu"""

    port_controller = PortfolioController()
    port_controller.print_help(port_controller.brokers_list)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in port_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (port)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (port)> ")

        try:
            process_input = port_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
