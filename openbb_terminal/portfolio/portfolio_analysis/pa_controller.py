"""Portfolio Analysis Controller"""
__docformat__ = "numpy"

import argparse
import logging
from pathlib import Path
from typing import List, Optional

import pandas as pd

from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.config.paths import USER_PORTFOLIO_DATA_DIRECTORY
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.portfolio_analysis import portfolio_model, portfolio_view
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

portfolios_path = USER_PORTFOLIO_DATA_DIRECTORY / "portfolios"
port_types = [".csv", ".json", ".xlsx"]
possible_paths = {
    portpath.name: portpath
    for port_type in port_types
    for portpath in portfolios_path.rglob(f"*.{port_type}")
}

possible_paths.update(
    {
        portpath.name: portpath
        for port_type in port_types
        for portpath in (Path(__file__).parent / "portfolios").rglob(f"*.{port_type}")
    }
)


class PortfolioAnalysisController(BaseController):
    """Portfolio Controller"""

    CHOICES_COMMANDS = [
        "view",
        "load",
        "group",
    ]
    PATH = "/portfolio/pa/"

    def __init__(self, queue: Optional[List[str]] = None):
        super().__init__(queue)

        self.portfolio_name = ""
        self.portfolio = pd.DataFrame()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""[cmds]
    view          view available portfolios
    load          load portfolio from a file[/cmds]

[param]Portfolio: [/param]{self.portfolio_name}[cmds]

    group         view holdings grouped by parameter[/cmds]
        """
        console.print(text=help_text, menu="Portfolio - Portfolio Analysis")

    @log_start_end(log=logger)
    def call_load(self, other_args):
        """Process load command"""
        parser = argparse.ArgumentParser(
            prog="load",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Function to get portfolio from predefined "
            "csv/json/xlsx file inside portfolios folder",
            epilog="usage: load file_name",
        )
        parser.add_argument(
            "-s",
            "--sector",
            action="store_true",
            default=False,
            help="Add sector to dataframe",
            dest="sector",
        )
        parser.add_argument(
            "-c",
            "--country",
            action="store_true",
            default=False,
            help="Add country to dataframe",
            dest="country",
        )
        parser.add_argument(
            "--no_last_price",
            action="store_false",
            default=True,
            help="Don't add last price from yfinance",
            dest="last_price",
        )
        parser.add_argument(
            "--nan",
            action="store_true",
            default=False,
            help="Show nan entries",
            dest="show_nan",
        )
        parser.add_argument(
            "-p",
            "--path",
            default="my_portfolio.csv",
            choices=possible_paths,
            help="Path to portfolio file",
            dest="path",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.portfolio_name = ns_parser.path
            self.portfolio = portfolio_model.load_portfolio(
                full_path=possible_paths[ns_parser.path],
                sector=ns_parser.sector,
                country=ns_parser.country,
                last_price=ns_parser.last_price,
                show_nan=ns_parser.show_nan,
            )
            if not self.portfolio.empty:
                console.print(f"Successfully loaded: {self.portfolio_name}\n")

    @log_start_end(log=logger)
    def call_group(self, other_args):
        """Process group command"""
        parser = argparse.ArgumentParser(
            prog="group",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Displays portfolio grouped by a given column",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            dest="group",
            default="Ticker",
            choices=self.portfolio.columns,
            help="Column to group by",
        )
        parser.add_argument(
            "-a",
            "--allocation",
            action="store_true",
            default=False,
            help="Add allocation column in % to dataframe",
            dest="allocation",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if "value" in self.portfolio.columns:
                portfolio_view.display_group_holdings(
                    portfolio=self.portfolio,
                    group_column=ns_parser.group,
                    allocation=ns_parser.allocation,
                )
            else:
                console.print(
                    "'value' column not in portfolio.  "
                    "Either add manually or load without --no_last_price flag\n"
                )

    @log_start_end(log=logger)
    def call_view(self, other_args):
        parser = argparse.ArgumentParser(
            prog="view",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Show available portfolios to load.",
        )
        parser.add_argument(
            "-format",
            choices=["csv", "json", "xlsx", "all"],
            help="Format of portfolios to view.  'csv' will show all csv files available, etc.",
            default="all",
            dest="file_format",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            available_ports = list(possible_paths)
            if ns_parser.file_format != "all":
                available_ports = [
                    port
                    for port in available_ports
                    if port.endswith(ns_parser.file_format)
                ]

            console.print("\nAvailable Portfolios:\n")
            for port in available_ports:
                console.print(port)
