#!/usr/bin/env python
"""Main Terminal Module"""
__docformat__ = "numpy"

import argparse
import os
import sys
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.terminal_helper import (
    print_goodbye,
    update_terminal,
    about_us,
    bootup,
    reset,
    check_api_keys,
)
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import config_terminal

from gamestonk_terminal.stocks import stocks_controller
from gamestonk_terminal.cryptocurrency import crypto_controller
from gamestonk_terminal.economy import economy_controller
from gamestonk_terminal.options import options_controller
from gamestonk_terminal.etf import etf_controller
from gamestonk_terminal.forex import forex_controller
from gamestonk_terminal.resources import resources_controller
from gamestonk_terminal.portfolio import portfolio_controller


# pylint: disable=too-many-public-methods


class TerminalController:
    """Terminal Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "reset",
        "update",
        "about",
        "keys",
    ]

    CHOICES_MENUS = [
        "stocks",
        "economy",
        "crypto",
        "portfolio",
        "forex",
        "options",
        "etf",
        "resources",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(self):
        """Constructor"""
        self.update_succcess = False
        self.t_parser = argparse.ArgumentParser(add_help=False, prog="terminal")
        self.t_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer = NestedCompleter.from_nested_dict(
            {c: None for c in self.CHOICES}
        )

    def print_help(self):
        """Print help"""
        help_text = """
What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    update      update terminal from remote
    keys        check for defined api keys
    reset       reset terminal and reload configs
    about       about us
    q(uit)      to abandon the program

>>  stocks
>>  crypto
>>  economy
>>  options
>>  portfolio
>>  etf
>>  forex
>>  resources
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

        (known_args, other_args) = self.t_parser.parse_known_args(an_input.split())

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

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_q(self, _):
        """Process Quit command - quit the program"""
        return True

    # COMMANDS
    def call_reset(self, _):
        """Process reset command"""
        return True

    def call_update(self, _):
        """Process update command"""
        self.update_succcess = not update_terminal()
        return True

    def call_keys(self, _):
        """Process keys command"""
        check_api_keys()

    def call_about(self, _):
        """Process about command"""
        about_us()

    # MENUS
    def call_stocks(self, _):
        """Process stocks command"""
        return stocks_controller.menu()

    def call_crypto(self, _):
        """Process crypto command"""
        return crypto_controller.menu()

    def call_economy(self, _):
        """Process econ command"""
        return economy_controller.menu()

    def call_options(self, _):
        """Process op command"""
        return options_controller.menu()

    def call_etf(self, _):
        """Process etf command"""
        return etf_controller.menu()

    def call_forex(self, _):
        """Process fx command"""
        return forex_controller.menu()

    def call_resources(self, _):
        """Process resources command"""
        return resources_controller.menu()

    def call_portfolio(self, _):
        """Process portfolio command"""
        return portfolio_controller.menu()


def terminal():
    """Terminal Menu"""

    bootup()

    t_controller = TerminalController()

    if config_terminal.DEFAULT_CONTEXT:
        if config_terminal.DEFAULT_CONTEXT in t_controller.CHOICES_MENUS:
            try:
                print("")
                t_controller.switch(config_terminal.DEFAULT_CONTEXT.lower())
            except SystemExit:
                print("")
        else:
            print("\nInvalid DEFAULT_CONTEXT config selected!", "\n")

    t_controller.print_help()
    parsed_stdin = False

    while True:
        if gtff.ENABLE_QUICK_EXIT:
            print("Quick exit enabled")
            break

        # Get input command from stdin or user
        if not parsed_stdin and len(sys.argv) > 1:
            an_input = " ".join(sys.argv[1:])
            print(f"{get_flair()}> {an_input}")
            parsed_stdin = True

        elif session and gtff.USE_PROMPT_TOOLKIT:
            an_input = session.prompt(
                f"{get_flair()}> ", completer=t_controller.completer
            )

        else:
            an_input = input(f"{get_flair()}> ")

        # Is command empty
        if not an_input:
            print("")
            continue

        # Process list of commands selected by user
        try:
            process_input = t_controller.switch(an_input)
            # None - Keep loop
            # True - Quit or Reset based on flag
            # False - Keep loop and show help menu

            if process_input is not None:
                # Quit terminal
                if process_input:
                    break

                t_controller.print_help()

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

    if not gtff.ENABLE_QUICK_EXIT:
        # Check if the user wants to reset application
        if an_input == "reset" or t_controller.update_succcess:
            ret_code = reset()
            if ret_code != 0:
                print_goodbye()
        else:
            print_goodbye()


if __name__ == "__main__":
    terminal()
