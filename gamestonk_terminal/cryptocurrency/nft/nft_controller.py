import argparse
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.decorators import try_except, menu_decorator
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    system_clear,
    check_positive,
    parse_known_args_and_warn,
)

from gamestonk_terminal.cryptocurrency.nft import nftcalendar_view, opensea_view

# pylint: disable=W0613


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


@menu_decorator("/crypto/nft", NFTController)
def menu(queue: List[str] = None):
    """NFT Menu"""
