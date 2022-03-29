"""Jupyter Controller Module"""
__docformat__ = "numpy"

import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console

# pylint: disable=import-outside-toplevel


logger = logging.getLogger(__name__)


class JupyterController(BaseController):
    """Resources Controller class"""

    CHOICES_COMMANDS = [
        "reports",
        "dashboards",
    ]
    PATH = "/jupyter/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[menu]
>   reports     creates jupyter reports
>   dashboards  shows interactive jupyter dashboards[/menu]
        """
        console.print(text=help_text, menu="Jupyter")

    @log_start_end(log=logger)
    def call_reports(self, _):
        """Process reports command"""
        from openbb_terminal.jupyter.reports.reports_controller import (
            ReportController,
        )

        self.queue = self.load_class(ReportController, self.queue)

    @log_start_end(log=logger)
    def call_dashboards(self, _):
        """Process dashboards command"""
        from openbb_terminal.jupyter.dashboards.dashboards_controller import (
            DashboardsController,
        )

        self.queue = self.load_class(DashboardsController, self.queue)
