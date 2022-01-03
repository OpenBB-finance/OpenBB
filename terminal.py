#!/usr/bin/env python
"""Main Terminal Module"""
__docformat__ = "numpy"

import os
import argparse
import difflib
import logging
import sys
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    system_clear,
)
from gamestonk_terminal.loggers import setup_logging
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

logger = logging.getLogger(__name__)


class TerminalController:
    """Terminal Controller class"""

    CHOICES = [
        "cls",
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
        "funds",
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
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: None for c in self.CHOICES}

            self.completer = NestedCompleter.from_nested_dict(choices)

        self.queue: List[str] = list()

        if jobs_cmds:
            # close the eyes if the user forgets the initial `/`
            if len(jobs_cmds) > 0:
                if jobs_cmds[0][0] != "/":
                    jobs_cmds[0] = f"/{jobs_cmds[0]}"

            self.queue = " ".join(jobs_cmds).split("/")

        self.update_succcess = False

    def print_help(self):
        """Print help"""
        help_text = """
Multiple jobs queue (where each '/' denotes a new command). E.g.
    /stocks $ disc/ugs -n 3/../load tsla/candle

If you want to jump from crypto/ta to stocks you can use an absolute path that starts with a slash (/). E.g.
    /crypto/ta $ /stocks

The previous logic also holds for when launching the terminal. E.g.
    $ python terminal.py /stocks/disc/ugs -n 3/../load tsla/candle

The main commands you should be aware when navigating through the terminal are:
    cls             clear the screen
    help / h / ?    help menu
    quit / q / ..   quit this menu and go one menu above
    exit            exit the terminal
    reset / r       reset the terminal and reload configs from the current location

    about           about us
    update          update terminal automatically
    keys            check for status of API keys

>   stocks
>   crypto
>   etf
>   economy
>   forex
>   funds
>   portfolio
>   reports
>   resources
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
            # Absolute path is specified.
            if not actions[0]:
                # Since we are already in home we can pick up the first instruction
                an_input = actions[1]
                idx_to_start = 2
            # Relative path so execute first instruction
            else:
                an_input = actions[0]
                idx_to_start = 1

            # Add all instructions to the queue
            for cmd in actions[idx_to_start:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.t_parser.parse_known_args(an_input.split())

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

    def call_reset(self, _):
        """Process reset command"""
        # has been dealt with before

    def call_update(self, _):
        """Process update command"""
        self.update_succcess = not update_terminal()

    def call_keys(self, _):
        """Process keys command"""
        check_api_keys()

    def call_about(self, _):
        """Process about command"""
        about_us()

    def call_stocks(self, _):
        """Process stocks command"""
        from gamestonk_terminal.stocks import stocks_controller

        self.queue = stocks_controller.menu("", self.queue)

    def call_crypto(self, _):
        """Process crypto command"""
        from gamestonk_terminal.cryptocurrency import crypto_controller

        self.queue = crypto_controller.menu(queue=self.queue)

    def call_economy(self, _):
        """Process economy command"""
        from gamestonk_terminal.economy import economy_controller

        self.queue = economy_controller.menu(self.queue)

    def call_etf(self, _):
        """Process etf command"""
        from gamestonk_terminal.etf import etf_controller

        self.queue = etf_controller.menu(self.queue)

    def call_funds(self, _):
        """Process etf command"""
        from gamestonk_terminal.mutual_funds import mutual_fund_controller

        self.queue = mutual_fund_controller.menu(self.queue)

    def call_forex(self, _):
        """Process forex command"""
        from gamestonk_terminal.forex import forex_controller

        self.queue = forex_controller.menu(self.queue)

    def call_reports(self, _):
        """Process reports command"""
        from gamestonk_terminal.reports import reports_controller

        self.queue = reports_controller.menu(self.queue)

    def call_resources(self, _):
        """Process resources command"""
        from gamestonk_terminal.resources import resources_controller

        self.queue = resources_controller.menu(self.queue)

    def call_portfolio(self, _):
        """Process portfolio command"""
        from gamestonk_terminal.portfolio import portfolio_controller

        self.queue = portfolio_controller.menu(self.queue)


def terminal(jobs_cmds: List[str] = None):
    """Terminal Menu"""
    setup_logging()

    logger.info("Terminal started")

    ret_code = 1
    t_controller = TerminalController(jobs_cmds)
    an_input = ""

    if not jobs_cmds:
        bootup()

    while ret_code:
        if gtff.ENABLE_QUICK_EXIT:
            print("Quick exit enabled")
            break

        # There is a command in the queue
        if t_controller.queue and len(t_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if t_controller.queue[0] in ("q", "..", "quit"):
                print_goodbye()
                break

            # Consume 1 element from the queue
            an_input = t_controller.queue[0]
            t_controller.queue = t_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in t_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} / $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if not an_input:
                t_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} / $ ",
                        completer=t_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    print_goodbye()
                    break
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} / $ ")

        try:
            # Process the input command
            t_controller.queue = t_controller.switch(an_input)
            if an_input in ("q", "quit", "..", "exit"):
                print_goodbye()
                break

            # Check if the user wants to reset application
            if an_input in ("r", "reset") or t_controller.update_succcess:
                ret_code = reset(
                    t_controller.queue if len(t_controller.queue) > 0 else []
                )
                if ret_code != 0:
                    print_goodbye()
                    break

        except SystemExit:
            print(f"\nThe command '{an_input}' doesn't exist on the / menu", end="")
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                t_controller.CHOICES,
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
                        t_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                t_controller.queue.insert(0, an_input)
            else:
                print("\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if ".gst" in sys.argv[1]:
            if os.path.isfile(sys.argv[1]):
                with open(sys.argv[1]) as fp:
                    simulate_argv = f"/{'/'.join([line.rstrip() for line in fp])}"
                    terminal(simulate_argv.replace("//", "/home/").split())
            else:
                print(
                    f"The file '{sys.argv[1]}' doesn't exist. Launching terminal without any configuration.\n"
                )
                terminal()
        else:
            terminal(sys.argv[1:])
    else:
        terminal()
