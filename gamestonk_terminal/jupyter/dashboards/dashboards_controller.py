"""Dashboards Module"""
__docformat__ = "numpy"

import argparse
import difflib
import subprocess
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    get_flair,
    system_clear,
)
from gamestonk_terminal.menu import session

# pylint: disable=consider-using-with


class DashboardsController:
    """Dashboards Controller class"""

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
        "stocks",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.rc_parser = argparse.ArgumentParser(add_help=False, prog="dashboards")
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
   stocks        interactive dashboard with ticker information
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
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "dashboards")
        self.queue.insert(0, "jupyter")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")

    def call_stocks(self, other_args: List[str]):
        """Process stocks command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stocks",
            description="""Shows an interactive stock dashboard""",
        )
        parser.add_argument(
            "-j",
            "--jupyter",
            action="store_true",
            default=False,
            dest="jupyter",
            help="Shows dashboard in jupyter-lab.",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            cmd = "jupyter-lab" if ns_parser.jupyter else "voila"
            file = "gamestonk_terminal/jupyter/dashboards/stocks.ipynb"

            print(
                f"Warning: this command will open a port on your computer to run a {cmd} server."
            )
            response = input("Would you like us to run the server for you? y/n\n")
            if response.lower() == "y":

                subprocess.Popen(
                    f"{cmd} {file}",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
            else:
                print(
                    f"To run manually type: {cmd} {file}\ninto a terminal after"
                    " entering the environment you use to run the terminal."
                )
        print("")


def menu(queue: List[str] = None):
    """Jupyter Menu"""
    dashboard_controller = DashboardsController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if dashboard_controller.queue and len(dashboard_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if dashboard_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(dashboard_controller.queue) > 1:
                    return dashboard_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = dashboard_controller.queue[0]
            dashboard_controller.queue = dashboard_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in dashboard_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /jupyter/dashboard/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                dashboard_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and dashboard_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /jupyter/dashboard/ $ ",
                    completer=dashboard_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /jupyter/dashboard/ $ ")

        try:
            # Process the input command
            dashboard_controller.queue = dashboard_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /jupyter menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                dashboard_controller.CHOICES,
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
                        dashboard_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                dashboard_controller.queue.insert(0, an_input)
            else:
                print("\n")
