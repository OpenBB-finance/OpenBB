# IMPORTATION STANDARD
import argparse
from typing import List, Union
import difflib

# IMPORTATION THIRDPARTY
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
import gamestonk_terminal.config_terminal as config

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.degiro.degiro_view import DegiroView


class DegiroController:
    CHOICES = CHOICES = [
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
        "cancel",
        "companynews",
        "create",
        "hold",
        "lastnews",
        "login",
        "logout",
        "lookup",
        "pending",
        "topnews",
        "update",
    ]
    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        self.__degiro_view = DegiroView()
        self.__degiro_parser = argparse.ArgumentParser(
            add_help=False,
            prog="degiro",
        )
        self.__degiro_parser.add_argument("cmd", choices=self.CHOICES)
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.queue = queue if queue else list()

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

        (known_args, other_args) = self.__degiro_parser.parse_known_args(
            an_input.split()
        )

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        return self.queue

    def call_help(self, _):
        """Process help command"""
        DegiroView.help_display()
        return self.queue

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "quit", "quit"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "degiro")
            self.queue.insert(0, "bro")
            self.queue.insert(0, "portfolio")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "quit", "reset", "portfolio", "bro", "degiro"]

    def cancel(self, other_args: List[str]):
        """Cancel an order using the `id`."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="companynews",
        )
        parser.add_argument(
            "id",
            help="Order's id.",
            type=str,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.cancel(ns_parser=ns_parser)
        return self.queue

    def companynews(self, other_args: List[str]):
        """Display news related to a company using its ISIN."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="companynews",
        )
        parser.add_argument(
            "isin",
            type=str,
            help="ISIN code of the company.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.companynews(ns_parser=ns_parser)
        return self.queue

    def create(self, other_args: List[str]):
        """Create an order."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="create",
        )
        parser.add_argument(
            "-a",
            "--action",
            choices=DegiroView.ORDER_ACTION.keys(),
            default="buy",
            help="Action wanted.",
            required=False,
            type=str,
        )
        product_group = parser.add_mutually_exclusive_group(
            required=True,
        )
        product_group.add_argument(
            "-prod",
            "--product",
            help="Id of the product wanted.",
            required=False,
            type=int,
        )
        product_group.add_argument(
            "-sym",
            "--symbol",
            help="Symbol wanted.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "-p",
            "--price",
            help="Price wanted.",
            required=True,
            type=float,
        )
        size_group = parser.add_mutually_exclusive_group(required=True)
        size_group.add_argument(
            "-s",
            "--size",
            help="Price wanted.",
            required=False,
            type=int,
        )
        size_group.add_argument(
            "-up",
            "--up-to",
            help="Up to price.",
            required=False,
            type=float,
        )
        parser.add_argument(
            "-d",
            "--duration",
            default="gtd",
            choices=DegiroView.ORDER_DURATION.keys(),
            help="Duration of the Order.",
            required=False,
            type=str,
        )
        parser.add_argument(
            "-t",
            "--type",
            choices=DegiroView.ORDER_TYPE.keys(),
            default="limit",
            help="Type of the Order.",
            required=False,
            type=str,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.create(ns_parser=ns_parser)
        return self.queue

    def hold(self, other_args):
        """Display held products."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="hold",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.hold(ns_parser=ns_parser)
        return self.queue

    def lastnews(self, other_args: List[str]):
        """Display latest news."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lastnews",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            type=int,
            help="Number of news to display.",
            required=False,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.lastnews(ns_parser=ns_parser)
        return self.queue

    def login(self, other_args: List[str]):
        """Connect to Degiro's API."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="login",
        )
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            default=config.DG_USERNAME,
            help="Username in Degiro's account.",
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            default=config.DG_PASSWORD,
            help="Password in Degiro's account.",
        )
        parser.add_argument(
            "-o",
            "--otp",
            type=int,
            default=None,
            help="One time password (2FA).",
        )
        parser.add_argument(
            "-s",
            "--topt-secret",
            type=str,
            default=None,
            help="TOTP SECRET (2FA).",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.login(ns_parser=ns_parser)
        return self.queue

    def logout(self, other_args: List[str]):
        """Log out from Degiro's API."""

        # PARSE ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="logout",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.logout(ns_parser=ns_parser)

    def lookup(self, other_args: List[str]):
        """Search for products by their name."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lookup",
        )
        parser.add_argument(
            "search_text",
            type=str,
            help="Name of the company or a text.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            default=10,
            help="Number of result expected (0 for unlimited).",
        )
        parser.add_argument(
            "-o",
            "--offset",
            type=int,
            default=0,
            help="To use an offset.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.lookup(ns_parser=ns_parser)
        return self.queue

    def pending(self, other_args: List[str]):
        """Display pending orders."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pending",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.pending(ns_parser=ns_parser)
        return self.queue

    def topnews(self, other_args: List[str]):
        """Display top news."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="topnews",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.topnews(ns_parser=ns_parser)
        return self.queue

    def update(self, other_args: List[str]):
        """Update an order."""

        # PARSING ARGS
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="update",
        )
        parser.add_argument(
            "id",
            help="Order's id.",
            type=str,
        )
        parser.add_argument(
            "-p",
            "--price",
            help="Price wanted.",
            required=True,
            type=float,
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        self.__degiro_view.update(ns_parser=ns_parser)
        return self.queue


def menu(queue: List[str] = None):
    """Degiro Menu"""
    degiro_controller = DegiroController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if degiro_controller.queue and len(degiro_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if degiro_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(degiro_controller.queue) > 1:
                    return degiro_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = degiro_controller.queue[0]
            degiro_controller.queue = degiro_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in degiro_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /portfolio/bro/degiro/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                DegiroView.help_display()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and degiro_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /portfolio/bro/degiro/ $ ",
                    completer=degiro_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /portfolio/bro/degiro/ $ ")

        try:
            # Process the input command
            degiro_controller.queue = degiro_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /portfolio/bro/degiro menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                degiro_controller.CHOICES,
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
                        degiro_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                degiro_controller.queue.insert(0, an_input)
            else:
                print("\n")
