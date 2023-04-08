"""Alternative Data Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional

from openbb_terminal.alternative import hackernews_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class AlternativeDataController(BaseController):
    """Alternative Controller class"""

    CHOICES_COMMANDS: List[str] = ["hn"]
    CHOICES_MENUS = ["covid", "oss", "realestate", "companieshouse"]
    PATH = "/alternative/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("alternative/")
        mt.add_menu("covid")
        mt.add_menu("oss")
        mt.add_menu("realestate")
        mt.add_menu("companieshouse")
        mt.add_raw("\n")
        mt.add_cmd("hn")
        console.print(text=mt.menu_text, menu="Alternative")

    @log_start_end(log=logger)
    def call_covid(self, _):
        """Process covid command"""
        from openbb_terminal.alternative.covid.covid_controller import CovidController

        self.queue = self.load_class(CovidController, self.queue)

    @log_start_end(log=logger)
    def call_oss(self, _):
        """Process oss command."""
        from openbb_terminal.alternative.oss.oss_controller import OSSController

        self.queue = self.load_class(OSSController, self.queue)

    @log_start_end(log=logger)
    def call_hn(self, other_args: List[str]):
        """Process hn command."""

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
            hackernews_view.display_stories(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_realestate(self, _):
        """Process realestate command."""
        from openbb_terminal.alternative.realestate.realestate_controller import (
            RealEstateController,
        )

        self.queue = self.load_class(RealEstateController, self.queue)

    @log_start_end(log=logger)
    def call_companieshouse(self, _):
        """Process companieshouse command."""
        from openbb_terminal.alternative.companieshouse.companieshouse_controller import (
            CompaniesHouseController,
        )

        self.queue = self.load_class(CompaniesHouseController, self.queue)
