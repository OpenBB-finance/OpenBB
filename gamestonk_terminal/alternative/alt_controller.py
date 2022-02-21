"""Alternative Data Controller Module"""
__docformat__ = "numpy"

import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class AlternativeDataController(BaseController):
    """Alternative Controller class"""

    CHOICES_COMMANDS: List[str] = []
    CHOICES_MENUS = ["covid"]
    PATH = "/alternative/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[menu]
>   covid     COVID menu,                    e.g.: cases, deaths, rates[/menu]
        """
        console.print(text=help_text, menu="Alternative")

    @log_start_end(log=logger)
    def call_covid(self, _):
        """Process covid command"""
        from gamestonk_terminal.alternative.covid.covid_controller import (
            CovidController,
        )

        self.queue = self.load_class(CovidController, self.queue)
