"""Alternative Data Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.alternative import hackernews_view, collectapi_view

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class AlternativeDataController(BaseController):
    """Alternative Controller class"""

    CHOICES_COMMANDS: List[str] = ["hn", "gp"]
    CHOICES_MENUS = ["covid", "oss"]
    PATH = "/alternative/"
    CHOICES_GENERATION = True

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("alternative/")
        mt.add_menu("covid")
        mt.add_menu("oss")
        mt.add_raw("\n")
        mt.add_cmd("hn")
        mt.add_cmd("gp")
        console.print(text=mt.menu_text, menu="Alternative")

    @log_start_end(log=logger)
    def call_covid(self, _):
        """Process covid command"""
        from openbb_terminal.alternative.covid.covid_controller import CovidController

        self.queue = self.load_class(CovidController, self.queue)

    @log_start_end(log=logger)
    def call_oss(self, _):
        """Process oss command"""
        from openbb_terminal.alternative.oss.oss_controller import OSSController

        self.queue = self.load_class(OSSController, self.queue)

    @log_start_end(log=logger)
    def call_hn(self, other_args: List[str]):
        """Process hn command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hn",
            description="Display Hacker News",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        )

        if ns_parser:
            hackernews_view.display_stories(limit=ns_parser.limit)

    @log_start_end(log=logger)
    def call_gp(self, other_args: List[str]):
        """Process gp command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gp",
            description="Display Google Trends",
        )

        parser.add_argument(
            "--sortby",
            type=str,
            choices=collectapi_view.SORTBY_EUROPEAN_GAS_PRICES,
            dest="sortby",
            help="Sort by column",
        )

        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )

        parser.add_argument(
            "-c",
            "--country",
            type=str,
            dest="country",
            nargs="+",
            help="Country to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        )

        if ns_parser:
            collectapi_view.display_european_gas_prices(
                country=" ".join(ns_parser.country) if ns_parser.country else "",
                limit=ns_parser.limit,
                sortby=ns_parser.sortby.lower() if ns_parser.sortby else "",
                reverse=ns_parser.reverse,
            )
