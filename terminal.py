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
    usage_instructions,
)
from gamestonk_terminal.paths import cd_CHOICES

# pylint: disable=too-many-public-methods,import-outside-toplevel


class TerminalController:
    """Terminal Controller class"""

    CHOICES = [
        "cls",
        "cd",
        "h",
        "?",
        "q",
        "..",
        "exit",
        "r",
    ]

    CHOICES_COMMANDS = [
        "update",
        "about",
        "keys",
        "usage",
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
        self.t_parser = argparse.ArgumentParser(add_help=False, prog="terminal")
        self.t_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: None for c in self.CHOICES}
            choices["cd"] = {c: None for c in cd_CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)
        else:
            self.completer = None

        self.queue: List[str] = list()
        if jobs_cmds:
            self.queue = " ".join(jobs_cmds).split("/")[1:]

        self.update_succcess = False

    def print_help(self):
        """Print help"""
        help_text = """
    about       about us
    usage       usage instructions
    update      update terminal automatically
    keys        check for status of API keys

Menus:
    /stocks
    /crypto
    /etf
    /economy
    /forex
    /portfolio
    /reports
    /resources"""
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
            return self.queue if len(self.queue) > 0 else []

        if "/" in an_input:
            actions = an_input.split("/")
            an_input = actions[0]
            for cmd in actions[1:][::-1]:
                self.queue.insert(0, cmd)

        (known_args, other_args) = self.t_parser.parse_known_args(an_input.split())

        if known_args.cmd:
            if known_args.cmd == "..":
                known_args.cmd = "q"
            elif known_args.cmd == "?":
                known_args.cmd = "h"

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue if len(self.queue) > 0 else []

    def call_cd(self, other_args):
        """Process cd command"""
        if other_args:
            args = other_args[0].split("/")
            if len(args) > 0:
                for m in args[::-1]:
                    if m:
                        self.queue.insert(0, m)
            else:
                self.queue.insert(0, args[0])

        return self.queue if len(self.queue) > 0 else []

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

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            return self.queue
        return ["q"]

    def call_r(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue = [f"/{arg}" for arg in self.queue]
            return self.queue
        return []

    # COMMANDS
    def call_update(self, _):
        """Process update command"""
        self.update_succcess = not update_terminal()
        return self.queue if len(self.queue) > 0 else []

    def call_keys(self, _):
        """Process keys command"""
        check_api_keys()
        return self.queue if len(self.queue) > 0 else []

    def call_about(self, _):
        """Process about command"""
        about_us()
        return self.queue if len(self.queue) > 0 else []

    def call_usage(self, _):
        """Process usage command"""
        usage_instructions()
        return self.queue if len(self.queue) > 0 else []

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

    usage_instructions()

    while ret_code:
        if gtff.ENABLE_QUICK_EXIT:
            print("Quick exit enabled")
            break

        # There is a command in the queue
        if t_controller.queue and len(t_controller.queue) > 0:
            if t_controller.queue[0] in ("q", ".."):
                if len(t_controller.queue) > 1:
                    return t_controller.queue[1:]
                return []

            an_input = t_controller.queue[0]
            t_controller.queue = t_controller.queue[1:]
            if an_input and an_input != "r":
                print(f"{get_flair()} / $ {an_input}\n")

        # Get input command from user
        else:
            if session and gtff.USE_PROMPT_TOOLKIT:
                an_input = session.prompt(
                    f"{get_flair()} / $ ",
                    completer=t_controller.completer,
                    search_ignore_case=True,
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

            if an_input in ("q", "..", "exit"):
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
            print(f"The command '{an_input}' doesn't exist.", end="")
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                t_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )

            if similar_cmd:
                if " " in an_input:
                    an_input = f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                else:
                    an_input = similar_cmd[0]
                print(f" Replacing by '{an_input}'.")
                t_controller.queue.insert(0, an_input)
            print("")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        terminal(sys.argv)
    else:
        terminal()
