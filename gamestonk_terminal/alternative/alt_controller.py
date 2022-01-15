"""Alternative Data Controller Module"""
__docformat__ = "numpy"

import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.menu import session

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class AlternativeDataController(BaseController):
    """Alternative Controller class"""

    CHOICES_COMMANDS: List[str] = []
    CHOICES_MENUS = ["covid"]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/alternative/", queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """[menu]
>   covid     COVID menu,                    e.g.: cases, deaths, rates[/menu]
        """
        console.print(text=help_text, menu="Alternative")

    def call_covid(self, _):
        """Process covid command"""
        from gamestonk_terminal.alternative.covid.covid_controller import (
            CovidController,
        )

        self.queue = CovidController(self.queue).menu()
