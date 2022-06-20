"""Dashboards Module"""
__docformat__ = "numpy"

import argparse
import logging
import os
import subprocess
from typing import List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.helper_funcs import parse_simple_args

# pylint: disable=consider-using-with


logger = logging.getLogger(__name__)


class DashboardsController(BaseController):
    """Dashboards Controller class"""

    CHOICES_COMMANDS = [
        "stocks",
        "correlation",
        "vsurf",
        "chains",
        "shortdata",
        "crypto",
    ]
    PATH = "/dashboards/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("dashboards/")
        mt.add_cmd("stocks")
        mt.add_cmd("correlation")
        mt.add_cmd("vsurf")
        mt.add_cmd("chains")
        mt.add_cmd("shortdata")
        mt.add_cmd("crypto")
        console.print(text=mt.menu_text, menu="Dashboards")

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
        """Process chains command"""
        create_call(other_args, "chains", "")

    @log_start_end(log=logger)
    def call_shortdata(self, other_args: List[str]):
        """Process shortdata command"""
        create_call(other_args, "shortdata", "")

    @log_start_end(log=logger)
    def call_crypto(self, other_args: List[str]):
        """Process crypto command"""
        create_call(other_args, "crypto", "")


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
    parser.add_argument(
        "-d",
        "--dark",
        action="store_true",
        default=False,
        dest="dark",
        help="Whether to show voila in dark mode",
    )

    ns_parser = parse_simple_args(parser, other_args)

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
        args = ""
        if ns_parser.dark and not ns_parser.jupyter:
            args += "--theme=dark"
        if ns_parser.input or response.lower() == "y":
            subprocess.Popen(
                f"{cmd} {file} {args}",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
            )
        else:
            console.print(f"Type: {cmd} {file}\ninto a terminal to run.")
        console.print("")
