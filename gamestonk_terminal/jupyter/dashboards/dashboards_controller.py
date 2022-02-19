"""Dashboards Module"""
__docformat__ = "numpy"

import argparse
import logging
import os
import subprocess
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console

# pylint: disable=consider-using-with


logger = logging.getLogger(__name__)


class DashboardsController(BaseController):
    """Dashboards Controller class"""

    CHOICES_COMMANDS = ["stocks", "correlation", "vsurf", "chains", "shortdata"]
    PATH = "/jupyter/dashboard/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[cmds]
   stocks        historic stock information
   correlation   stock correlations
   vsurf         options volatility surface
   chains        options chain analysis
   shortdata     finra shortdata analysis[/cmds]
        """
        console.print(text=help_text, menu="Jupyter - Dashboards")

    @log_start_end(log=logger)
    def call_stocks(self, other_args: List[str]):
        """Process stocks command"""
        create_call(other_args, "stocks", "stocks")

    @log_start_end(log=logger)
    def call_correlation(self, other_args: List[str]):
        """Process correlation command"""
        create_call(other_args, "correlation", "correlation")

    @log_start_end(log=logger)
    def call_vsurf(self, other_args: List[str]):
        """Process vsurf command"""
        create_call(other_args, "vsurf", "")

    @log_start_end(log=logger)
    def call_chains(self, other_args: List[str]):
        """Process vsurf command"""
        create_call(other_args, "chains", "")

    @log_start_end(log=logger)
    def call_shortdata(self, other_args: List[str]):
        """Process vsurf command"""
        create_call(other_args, "shortdata", "")


def create_call(other_args: List[str], name: str, filename: str = None) -> None:
    filename = filename if filename else name

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=name,
        description=f"""Shows {name} dashboard""",
    )
    parser.add_argument(
        "-j",
        "--jupyter",
        action="store_true",
        default=False,
        dest="jupyter",
        help="Shows dashboard in jupyter-lab.",
    )
    parser.add_argument(
        "-n",
        "--no-input",
        action="store_true",
        default=False,
        dest="input",
        help="Skips confirmation to run server.",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)

    if ns_parser:
        cmd = "jupyter-lab" if ns_parser.jupyter else "voila"
        file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), f"{filename}.ipynb"
        )
        if not ns_parser.input:
            console.print(
                f"Warning: opens a port on your computer to run a {cmd} server."
            )
            response = input("Would you like us to run the server for you? y/n\n")
        if ns_parser.input or response.lower() == "y":
            subprocess.Popen(
                f"{cmd} {file}",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
            )
        else:
            console.print(f"Type: {cmd} {file}\ninto a terminal to run.")
        console.print("")
