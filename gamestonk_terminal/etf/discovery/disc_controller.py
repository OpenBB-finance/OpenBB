"""Discovery Controller Module"""
__docformat__ = "numpy"

import argparse
from typing import List

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    check_positive,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.etf.discovery import wsj_view


class DiscoveryController(BaseController):
    """Discovery Controller class"""

    CHOICES_COMMANDS = [
        "gainers",
        "decliners",
        "active",
    ]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/etf/disc/", queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """
[src][Wall Street Journal][/src][cmds]
    gainers     top gainers
    decliners   top decliners
    active      most active[/cmds]
"""
        console.print(text=help_text, menu="ETF - Discovery")

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
