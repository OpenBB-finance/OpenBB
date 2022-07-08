"""Discovery Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf.discovery import wsj_view
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class DiscoveryController(BaseController):
    """Discovery Controller class"""

    CHOICES_COMMANDS = [
        "gainers",
        "decliners",
        "active",
    ]
    PATH = "/etf/disc/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("etf/disc/", 60)
        mt.add_cmd("gainers", "Wall Street Journal")
        mt.add_cmd("decliners", "Wall Street Journal")
        mt.add_cmd("active", "Wall Street Journal")
        console.print(text=mt.menu_text, menu="ETF - Discovery")

    @log_start_end(log=logger)
    def call_gainers(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="gainers",
            description="Displays top ETF/Mutual fund gainers from wsj.com/market-data",
            add_help=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )
        if ns_parser:
            wsj_view.show_top_mover("gainers", ns_parser.limit, ns_parser.export)

    @log_start_end(log=logger)
    def call_decliners(self, other_args):
        """Process decliners command"""
        parser = argparse.ArgumentParser(
            prog="decliners",
            description="Displays top ETF/Mutual fund decliners from wsj.com/market-data",
            add_help=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        )
        if ns_parser:
            wsj_view.show_top_mover("decliners", ns_parser.limit, ns_parser.export)

    @log_start_end(log=logger)
    def call_active(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="active",
            description="Displays most active ETF/Mutual funds from wsj.com/market-data",
            add_help=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        )
        if ns_parser:
            wsj_view.show_top_mover("active", ns_parser.limit, ns_parser.export)
