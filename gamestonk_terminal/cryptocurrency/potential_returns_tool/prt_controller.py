import argparse
import difflib
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    try_except,
    system_clear,
    get_flair,
    parse_known_args_and_warn,
)


class PRTController:
    """PRT Controller class"""

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

    CHOICES_COMMANDS = ["load"]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.nft_parser = argparse.ArgumentParser(add_help=False, prog="prt")
        self.nft_parser.add_argument(
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

        help_text = """
temporary
"""
        print(help_text)

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

        (known_args, other_args) = self.nft_parser.parse_known_args(an_input.split())

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
        self.queue.insert(0, "prt")
        self.queue.insert(0, "crypto")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_stats(self, other_args: List[str]):
        """Process stats command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="""
                Display stats about an opensea nft collection. e.g. alien-frens
                [Source: opensea.io]
            """,
        )

        parser.add_argument(
            "-s",
            "--slug",
            type=str,
            help="Opensea collection slug (e.g., mutant-ape-yacht-club)",
            dest="slug",
            required=True,
        )
        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "--slug")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pass


def menu(queue: List[str] = None):
    """PRT Menu"""
    prt_controller = PRTController(queue=queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if prt_controller.queue and len(prt_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if prt_controller.queue[0] in ("q", "..", "quit"):
                if len(prt_controller.queue) > 1:
                    return prt_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = prt_controller.queue[0]
            prt_controller.queue = prt_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in prt_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /crypto/prt/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                prt_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and prt_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /crypto/prt/ $ ",
                        completer=prt_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/prt/ $ ")

        try:
            # Process the input command
            prt_controller.queue = prt_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /crypto/prt menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                prt_controller.CHOICES,
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
                        prt_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                prt_controller.queue.insert(0, an_input)
            else:
                print("\n")
