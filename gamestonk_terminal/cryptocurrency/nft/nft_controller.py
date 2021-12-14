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

from gamestonk_terminal.cryptocurrency.nft import nftcalendar_view


class NFTController:
    """NFT Controller class"""

    CHOICES = [
        "cls",
        "cd",
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
        "today",
        "upcoming",
        "ongoing",
        "newest",
    ]

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
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.nft_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue if len(self.queue) > 0 else []

    def call_cd(self, other_args):
        """Process cd command"""
        if other_args and "-" not in other_args[0]:
            args = other_args[0].split("/")
            if len(args) > 0:
                for m in args[::-1]:
                    if m:
                        self.queue.insert(0, m)
            else:
                self.queue.insert(0, args[0])

        self.queue.insert(0, "q")
        self.queue.insert(0, "q")

        return self.queue

    def call_h(self, _):
        """Process help command"""
        self.print_help()
        return self.queue if len(self.queue) > 0 else []

    def call_q(self, _):
        """Process quit menu command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            return self.queue
        return ["q"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            self.queue.insert(0, "q")
            self.queue.insert(0, "q")
            return self.queue
        return ["q", "q", "q"]

    def call_r(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "nft")
            self.queue.insert(0, "crypto")
            self.queue.insert(0, "r")
            self.queue.insert(0, "q")
            self.queue.insert(0, "q")
            return self.queue
        return ["q", "q", "r", "crypto", "nft"]

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
        return self.queue if len(self.queue) > 0 else []

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
        return self.queue if len(self.queue) > 0 else []

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
        return self.queue if len(self.queue) > 0 else []

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
        return self.queue if len(self.queue) > 0 else []


def menu(queue: List[str] = None):
    """NFT Menu"""
    nft_controller = NFTController(queue=queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if nft_controller.queue and len(nft_controller.queue) > 0:
            if nft_controller.queue[0] in ("q", ".."):
                if len(nft_controller.queue) > 1:
                    return nft_controller.queue[1:]
                return []

            an_input = nft_controller.queue[0]
            nft_controller.queue = nft_controller.queue[1:]
            if an_input and an_input in nft_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /crypto/nft/ $ {an_input}")

        # Get input command from user
        else:
            if an_input == "HELP_ME" or an_input in nft_controller.CHOICES:
                nft_controller.print_help()

            if session and gtff.USE_PROMPT_TOOLKIT and nft_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /crypto/nft/ $ ",
                    completer=nft_controller.completer,
                    search_ignore_case=True,
                )

            else:
                an_input = input(f"{get_flair()} /crypto/nft/ $ ")

        try:
            nft_controller.queue = nft_controller.switch(an_input)

        except SystemExit:
            print(f"\nThe command '{an_input}' doesn't exist.", end="")
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                nft_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    an_input = f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                else:
                    an_input = similar_cmd[0]
                print(f" Replacing by '{an_input}'.")
                nft_controller.queue.insert(0, an_input)
            print("\n")
