"""Resource Collection Controller Module"""
__docformat__ = "numpy"

import argparse
import webbrowser
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    menu_decorator,
    system_clear,
)
from gamestonk_terminal.menu import session

# pylint: disable=W0613


class ResourceCollectionController:
    """Resources Controller class"""

    # Command choices
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

    CHOICES_COMMANDS = [
        "hfletters",
        "arxiv",
        "finra",
        "edgar",
        "fred",
        "learn",
        "econiverse",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.rc_parser = argparse.ArgumentParser(add_help=False, prog="resources")
        self.rc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.queue = queue if queue else list()
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}

            self.completer = NestedCompleter.from_nested_dict(choices)

    @staticmethod
    def print_help():
        """Print help"""
        help_str = """
Resource Collection:
   hfletters     hedge fund letters or reports
   arxiv         open-access archive for academic articles
   finra         self-regulatory organization
   edgar         online public database from SEC
   fred          economic research data
   learn         trading analysis, tips and resources
   econiverse    compilation of free knowledge and educational resources
        """
        print(help_str)

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

        (known_args, other_args) = self.rc_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
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

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")

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
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "resources")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")

    def call_hfletters(self, _):
        """Process hfletters command"""
        webbrowser.open("https://miltonfmr.com/hedge-fund-letters/")
        print("")

    def call_arxiv(self, _):
        """Process arxiv command"""
        webbrowser.open("https://arxiv.org")
        print("")

    def call_finra(self, _):
        """Process finra command"""
        webbrowser.open("https://www.finra.org/#/")
        print("")

    def call_edgar(self, _):
        """Process edgar command"""
        webbrowser.open("https://www.sec.gov/edgar.shtml")
        print("")

    def call_fred(self, _):
        """Process fred command"""
        webbrowser.open("https://fred.stlouisfed.org")
        print("")

    def call_learn(self, _):
        """Process learn command"""
        webbrowser.open("https://moongangcapital.com/free-stock-market-resources/")
        print("")

    def call_econiverse(self, _):
        """Process econiverse command"""
        webbrowser.open("https://econiverse.github.io")
        print("")


@menu_decorator("/resources/", ResourceCollectionController)
def menu(queue: List[str] = None):
    """Resource Collection Menu"""
