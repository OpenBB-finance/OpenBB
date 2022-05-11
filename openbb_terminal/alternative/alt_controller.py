"""Alternative Data Controller Module"""
__docformat__ = "numpy"

import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class AlternativeDataController(BaseController):
    """Alternative Controller class"""

    CHOICES_COMMANDS: List[str] = []
    CHOICES_MENUS = ["covid", "oss"]
    PATH = "/alternative/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices = {**choices, **self.SUPPORT_CHOICES}

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[menu]
>   covid     COVID menu,                    e.g.: cases, deaths, rates
>   oss       Open Source menu,              e.g.: star history, repos information[/menu]
        """
        console.print(text=help_text, menu="Alternative")

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
