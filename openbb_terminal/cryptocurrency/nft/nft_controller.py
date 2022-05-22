import argparse
import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.cryptocurrency.nft import nftcalendar_view, opensea_view
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    parse_known_args_and_warn,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


class NFTController(BaseController):
    """NFT Controller class"""

    CHOICES_COMMANDS = ["today", "upcoming", "ongoing", "newest", "stats"]
    PATH = "/crypto/nft/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""

        help_text = """[cmds]
[src][Nftcalendar.io][/src]
    today            today's NFT drops
    upcoming         upcoming NFT drops
    ongoing          Ongoing NFT drops
    newest           Recently NFTs added
[src][Opensea.io][/src]
    stats            check open sea collection stats[/cmds]
"""
        console.print(text=help_text, menu="Cryptocurrency - Non Fungible Token")

    @log_start_end(log=logger)
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
            required="-h" not in other_args,
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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
