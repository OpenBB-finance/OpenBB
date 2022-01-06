"""Alternative Data Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
import logging
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter
from rich.console import Console
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    system_clear,
)
from gamestonk_terminal.menu import session

t_console = Console()
logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class AlternativeDataController:
    """alternative Controller class"""

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

    CHOICES_COMMANDS: List[str] = []
    CHOICES_MENUS = ["covid"]
    CHOICES += CHOICES_COMMANDS + CHOICES_MENUS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.alt_parser = argparse.ArgumentParser(add_help=False, prog="alternative")
        self.alt_parser.add_argument(
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
>   covid           cases, deaths, rates
        """
        t_console.print(help_str)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            t_console.print("")
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
        logger.info(an_input)
        (known_args, other_args) = self.alt_parser.parse_known_args(an_input.split())

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
        t_console.print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "alternative")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")

    def call_covid(self, _):
        """Process covid command"""
        from gamestonk_terminal.alternative.covid import covid_controller

        self.queue = covid_controller.menu(self.queue)


def menu(queue: List[str] = None):
    """Resoualte Collection Menu"""
    alt_controller = AlternativeDataController(queue)
    an_input = "HELP_ME"
    logger.info("AlternativeMenu")

    while True:
        # There is a command in the queue
        if alt_controller.queue and len(alt_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if alt_controller.queue[0] in ("q", "..", "quit"):
                t_console.print("")
                if len(alt_controller.queue) > 1:
                    return alt_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = alt_controller.queue[0]
            alt_controller.queue = alt_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in alt_controller.CHOICES_COMMANDS:
                t_console.print(f"{get_flair()} /alternative/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                alt_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and alt_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /alternative/ $ ",
                        completer=alt_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /alternative/ $ ")

        try:
            # Process the input command
            alt_controller.queue = alt_controller.switch(an_input)

        except SystemExit:
            t_console.print(
                f"\nThe command '{an_input}' doesn't exist on the /alternative menu.\n"
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                alt_controller.CHOICES,
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
                        alt_controller.queue = []
                        t_console.print("")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                t_console.print(f" Replacing by '{an_input}'.")
                alt_controller.queue.insert(0, an_input)
            else:
                print("")
