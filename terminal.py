#!/usr/bin/env python
"""Main Terminal Module"""
__docformat__ = "numpy"

import argparse
import difflib
import sys
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.terminal_helper import (
    about_us,
    bootup,
    check_api_keys,
    print_goodbye,
    reset,
    update_terminal,
)

# pylint: disable=too-many-public-methods,import-outside-toplevel


class TerminalController:
    """Terminal Controller class"""

    CHOICES = [
        "cls",
        "?",
        "h",
        "q",
        "e",
        "r",
    ]

    CHOICES_COMMANDS = [
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
        "etf",
        "reports",
        "resources",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(self, jobs_cmds: List[str] = None):
        """Constructor"""

        self.queue: List[str] = list()
        command: List[str] = list()

        if jobs_cmds:
            for arg in jobs_cmds[1:]:
                if arg[0] == ".":
                    if command:
                        self.queue.append(" ".join(command))
                    command = list()
                    command.append(arg[1:])
                else:
                    command.append(arg)

            self.queue.append(" ".join(command))

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
    about       about us
    update      update terminal automatically
    keys        check for status of API keys

>>  stocks
>>  crypto
>>  etf
>>  economy
>>  forex
>>  portfolio
>>  reports
>>  resources"""
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
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_h(self, _):
        """Process help command"""
        self.print_help()
        return self.queue if len(self.queue) > 0 else []

    def call_q(self, _):
        """Process quit menu command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            return self.queue
        return ["q"]

    def call_e(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            return self.queue
        return ["q"]

    def call_r(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue = [f".{arg}" for arg in self.queue]
            return self.queue
        return []

    # COMMANDS
    def call_reset(self, _):
        """Process reset command"""
        return self.queue if len(self.queue) > 0 else []

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
        from gamestonk_terminal.stocks import stocks_controller

        return stocks_controller.menu("", self.queue)

    def call_crypto(self, _):
        """Process crypto command"""
        from gamestonk_terminal.cryptocurrency import crypto_controller

        return crypto_controller.menu()

    def call_economy(self, _):
        """Process economy command"""
        from gamestonk_terminal.economy import economy_controller

        return economy_controller.menu()

    def call_etf(self, _):
        """Process etf command"""
        from gamestonk_terminal.etf import etf_controller

        return etf_controller.menu()

    def call_forex(self, _):
        """Process forex command"""
        from gamestonk_terminal.forex import forex_controller

        return forex_controller.menu()

    def call_reports(self, _):
        """Process reports command"""
        from gamestonk_terminal.reports import reports_controller

        return reports_controller.menu()

    def call_resources(self, _):
        """Process resources command"""
        from gamestonk_terminal.resources import resources_controller

        return resources_controller.menu()

    def call_portfolio(self, _):
        """Process portfolio command"""
        from gamestonk_terminal.portfolio import portfolio_controller

        return portfolio_controller.menu()


def terminal(jobs_cmds: List[str] = None):
    """Terminal Menu"""

    bootup()
    ret_code = 1
    t_controller = TerminalController(jobs_cmds)
    t_controller.print_help()

    navigate_text = """
In order to improve the speed of execution of the most experienced users, these are our new navigation keys:
    cls  clear the screen
    cd   jump directly into a particular menu (e.g. cd stocks/disc)
    h    help menu
    q    quit this menu and go one menu above
    e    exit the terminal
    r    reset the terminal and reload configs from the current location"""
    print(navigate_text)

    while ret_code:
        if gtff.ENABLE_QUICK_EXIT:
            print("Quick exit enabled")
            break

        # There is a command in the queue
        if t_controller.queue and len(t_controller.queue) > 0:
            if t_controller.queue[0] == "q":
                if len(t_controller.queue) > 1:
                    return t_controller.queue[1:]
                return []

            an_input = t_controller.queue[0]
            t_controller.queue = t_controller.queue[1:]
            if an_input:
                print(f"{get_flair()} / $ {an_input}")

        # Get input command from user
        else:
            if session and gtff.USE_PROMPT_TOOLKIT:
                an_input = session.prompt(
                    f"{get_flair()} / $ ", completer=t_controller.completer
                )

            else:
                an_input = input(f"{get_flair()} / $ ")

        # Is command empty
        if not an_input:
            print("")
            continue

        # Process list of commands selected by user
        try:
            t_controller.queue = t_controller.switch(an_input)

            if an_input in ("q", "e"):
                print_goodbye()
                break

            # Check if the user wants to reset application
            if an_input == "r" or t_controller.update_succcess:
                ret_code = reset(
                    t_controller.queue if len(t_controller.queue) > 0 else []
                )

                if ret_code != 0:
                    print_goodbye()
                    break

        except SystemExit:
            print(f"The command '{an_input}' doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, t_controller.CHOICES, n=1, cutoff=0.7
            )
            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
                continue


if __name__ == "__main__":
    if len(sys.argv) > 1:
        terminal(sys.argv)
    else:
        terminal()
