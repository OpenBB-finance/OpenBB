"""Jupyter Controller Module"""
__docformat__ = "numpy"

from typing import List

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff

from gamestonk_terminal.menu import session

# pylint: disable=import-outside-toplevel


class JupyterController(BaseController):
    """Resources Controller class"""

    CHOICES_COMMANDS = [
        "reports",
        "dashboards",
    ]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/jupyter/", queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[menu]
>   reports     creates jupyter reports
>   dashboards  shows interactive jupyter dashboards[/menu]
        """
        console.print(text=help_text, menu="Jupyter")

    def call_reports(self, _):
        """Process reports command"""
        from gamestonk_terminal.jupyter.reports.reports_controller import (
            ReportController,
        )

        self.queue = ReportController(self.queue).menu()

    def call_dashboards(self, _):
        """Process dashboards command"""
        from gamestonk_terminal.jupyter.dashboards.dashboards_controller import (
            DashboardsController,
        )

        self.queue = DashboardsController(self.queue).menu()
