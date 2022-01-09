"""Dashboards Module"""
__docformat__ = "numpy"

import argparse
import subprocess
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session

# pylint: disable=consider-using-with


class DashboardsController(BaseController):
    """Dashboards Controller class"""

    CHOICES_COMMANDS = [
        "stocks",
    ]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/jupyter/dashboard/", queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_str = """
   stocks        interactive dashboard with ticker information
        """
        print(help_str)

    def call_stocks(self, other_args: List[str]):
        """Process stocks command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stocks",
            description="""Shows an interactive stock dashboard""",
        )
        parser.add_argument(
            "-j",
            "--jupyter",
            action="store_true",
            default=False,
            dest="jupyter",
            help="Shows dashboard in jupyter-lab.",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            cmd = "jupyter-lab" if ns_parser.jupyter else "voila"
            file = "gamestonk_terminal/jupyter/dashboards/stocks.ipynb"

            print(
                f"Warning: this command will open a port on your computer to run a {cmd} server."
            )
            response = input("Would you like us to run the server for you? y/n\n")
            if response.lower() == "y":

                subprocess.Popen(
                    f"{cmd} {file}",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
            else:
                print(
                    f"To run manually type: {cmd} {file}\ninto a terminal after"
                    " entering the environment you use to run the terminal."
                )
        print("")
