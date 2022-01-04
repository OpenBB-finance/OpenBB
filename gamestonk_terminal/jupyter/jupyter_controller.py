"""Jupyter Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    system_clear,
)
from gamestonk_terminal.menu import session

# pylint: disable=too-many-public-methods,import-outside-toplevel


class JupyterController:
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
        "reports",
        "dashboards",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.rc_parser = argparse.ArgumentParser(add_help=False, prog="jupyter")
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
>   reports     creates jupyter reports
>   dashboards  shows interactive jupyter dashboards
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
        self.queue.insert(0, "jupyter")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")

    def call_reports(self, _):
        """Process reports command"""
        from gamestonk_terminal.jupyter.reports import reports_controller

        self.queue = reports_controller.menu(self.queue)

    def call_dashboards(self, _):
        """Process dashboards command"""
        from gamestonk_terminal.jupyter.dashboards import dashboards_controller

        self.queue = dashboards_controller.menu(self.queue)


def menu(queue: List[str] = None):
    """Jupyter Menu"""
    jupyter_controller = JupyterController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if jupyter_controller.queue and len(jupyter_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if jupyter_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(jupyter_controller.queue) > 1:
                    return jupyter_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = jupyter_controller.queue[0]
            jupyter_controller.queue = jupyter_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in jupyter_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /jupyter/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                jupyter_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and jupyter_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /jupyter/ $ ",
                    completer=jupyter_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /jupyter/ $ ")

        try:
            # Process the input command
            jupyter_controller.queue = jupyter_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /jupyter menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                jupyter_controller.CHOICES,
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
                        jupyter_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                jupyter_controller.queue.insert(0, an_input)
            else:
                print("\n")
