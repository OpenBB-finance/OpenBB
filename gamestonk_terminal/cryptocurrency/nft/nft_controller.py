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
    check_positive,
    parse_known_args_and_warn,
)

from gamestonk_terminal.cryptocurrency.nft import nftcalendar_view, opensea_view


class NFTController:
    """NFT Controller class"""

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

    CHOICES_COMMANDS = ["today", "upcoming", "ongoing", "newest", "stats"]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.nft_parser = argparse.ArgumentParser(add_help=False, prog="nft")
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
nftcalendar.io:
    today       today's NFT drops
    upcoming    upcoming NFT drops
    ongoing     Ongoing NFT drops
    newest      Recently NFTs added
opensea.io
    stats       check open sea collection stats
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
        self.queue.insert(0, "nft")
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
            opensea_view.display_collection_stats(
                slug=ns_parser.slug,
                export=ns_parser.export,
            )

    @try_except
    def call_today(self, other_args: List[str]):
        """Process today command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="today",
            description="Today's NFT drops [Source: nftcalendar.io]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="limit",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            nftcalendar_view.display_nft_today_drops(
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_upcoming(self, other_args: List[str]):
        """Process upcoming command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="upcoming",
            description="Upcoming's NFT drops [Source: nftcalendar.io]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="limit",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            nftcalendar_view.display_nft_upcoming_drops(
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_ongoing(self, other_args: List[str]):
        """Process ongoing command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ongoing",
            description="Ongoing's NFT drops [Source: nftcalendar.io]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="limit",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            nftcalendar_view.display_nft_ongoing_drops(
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_newest(self, other_args: List[str]):
        """Process newest command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="newest",
            description="Newest's NFT drops [Source: nftcalendar.io]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="limit",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            nftcalendar_view.display_nft_newest_drops(
                num=ns_parser.limit,
                export=ns_parser.export,
            )


def menu(queue: List[str] = None):
    """NFT Menu"""
    nft_controller = NFTController(queue=queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if nft_controller.queue and len(nft_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if nft_controller.queue[0] in ("q", "..", "quit"):
                if len(nft_controller.queue) > 1:
                    return nft_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = nft_controller.queue[0]
            nft_controller.queue = nft_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in nft_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /crypto/nft/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                nft_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and nft_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /crypto/nft/ $ ",
                        completer=nft_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/nft/ $ ")

        try:
            # Process the input command
            nft_controller.queue = nft_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /crypto/nft menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                nft_controller.CHOICES,
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
                        nft_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                nft_controller.queue.insert(0, an_input)
            else:
                print("\n")
