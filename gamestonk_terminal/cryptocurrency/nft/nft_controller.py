import argparse
from typing import List

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
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "today",
        "upcoming",
        "ongoing",
        "newest",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.nft_parser = argparse.ArgumentParser(add_help=False, prog="nft")
        self.nft_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer = NestedCompleter.from_nested_dict(
            {c: None for c in self.CHOICES}
        )

    def print_help(self):
        """Print help"""

        help_text = """
What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

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

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

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
            "-n",
            "--num",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="num",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not ns_parser:
            return

        nftcalendar_view.display_nft_today_drops(
            num=ns_parser.num,
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
            "-n",
            "--num",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="num",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not ns_parser:
            return

        nftcalendar_view.display_nft_upcoming_drops(
            num=ns_parser.num,
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
            "-n",
            "--num",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="num",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not ns_parser:
            return

        nftcalendar_view.display_nft_ongoing_drops(
            num=ns_parser.num,
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
            "-n",
            "--num",
            type=check_positive,
            help="Number of NFT collections to display",
            dest="num",
            default=5,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not ns_parser:
            return

        nftcalendar_view.display_nft_newest_drops(
            num=ns_parser.num,
            export=ns_parser.export,
        )


def menu():
    """NFT Menu"""
    nft_controller = NFTController()
    nft_controller.call_help(None)
    while True:
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in nft_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (nft)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (nft)> ")

        try:
            process_input = nft_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exit\n")
            continue
