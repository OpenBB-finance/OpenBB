"""Sources Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
from typing import List

# IMPORTATION THIRDPARTY
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


class SourcesController(BaseController):
    """Sources Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "get",
        "set",
    ]
    PATH = "/sources/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        console.print("hello")

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("sources/")
        mt.add_raw("Set default data sources")
        mt.add_cmd("get")
        mt.add_cmd("set")

        console.print(text=mt.menu_text, menu="Data Sources")

    @log_start_end(log=logger)
    def call_get(self, _):
        """Process get command"""
        console.print("hello")
