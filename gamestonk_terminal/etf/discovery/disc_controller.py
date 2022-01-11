"""Discovery Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
    check_positive,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.etf.discovery import wsj_view


class DiscoveryController:
    """Discovery Controller class"""

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
        "gainers",
        "decliners",
        "active",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(
        self,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.disc_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self.disc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_str = """
    gainers     show top gainers [WSJ]
    decliners   show top decliners [WSJ]
    active      show most active [WSJ]
"""
        print(help_str)

    def switch(self, an_input: str):
        """Process and dispatch input
        Parameters
        -------
        an_input : str
            string with input arguments
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

        (known_args, other_args) = self.disc_parser.parse_known_args(an_input.split())

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
        self.queue.insert(0, "disc")
        self.queue.insert(0, "etf")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_gainers(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="gainers",
            description="Displays top ETF/Mutual fund gainers from wsj.com/market-data",
            add_help=False,
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Limit of ETFs to display",
            type=check_positive,
            default=10,
            dest="limit",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.show_top_mover("gainers", ns_parser.limit, ns_parser.export)

    def call_decliners(self, other_args):
        """Process decliners command"""
        parser = argparse.ArgumentParser(
            prog="decliners",
            description="Displays top ETF/Mutual fund decliners from wsj.com/market-data",
            add_help=False,
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Limit of ETFs to display",
            type=check_positive,
            default=10,
            dest="limit",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.show_top_mover("decliners", ns_parser.limit, ns_parser.export)

    def call_active(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="active",
            description="Displays most active ETF/Mutual funds from wsj.com/market-data",
            add_help=False,
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Limit of ETFs to display",
            type=check_positive,
            default=10,
            dest="limit",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.show_top_mover("active", ns_parser.limit, ns_parser.export)


def menu(
    queue: List[str] = None,
):
    """Discovery Menu"""
    disc_controller = DiscoveryController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if disc_controller.queue and len(disc_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if disc_controller.queue[0] in ("q", "..", "quit"):
                if len(disc_controller.queue) > 1:
                    return disc_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = disc_controller.queue[0]
            disc_controller.queue = disc_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in disc_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /etf/disc/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                disc_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and disc_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /etf/disc/ $ ",
                        completer=disc_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /etf/disc/ $ ")

        try:
            # Process the input command
            disc_controller.queue = disc_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /etf/disc menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                disc_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                else:
                    candidate_input = similar_cmd[0]

                if candidate_input == an_input:
                    an_input = ""
                    disc_controller.queue = []
                    print("\n")
                    continue

                print(f" Replacing by '{candidate_input}'.")
                disc_controller.queue.insert(0, candidate_input)
            else:
                print("\n")
                an_input = ""
                disc_controller.queue = []
