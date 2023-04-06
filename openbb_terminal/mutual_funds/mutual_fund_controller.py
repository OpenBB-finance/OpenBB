"""Mutual Fund Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_FIGURES_ALLOWED,
    check_positive,
    lower_str,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.mutual_funds import avanza_view, mstarpy_view
from openbb_terminal.mutual_funds.mutual_funds_utils import mapping_country
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class FundController(BaseController):
    """Fund Controller class"""

    CHOICES_COMMANDS = [
        "resources",
        "country",
        "search",
        "load",
        "plot",
        "sector",
        "alswe",
        "infoswe",
        "holdings",
        "carbon",
        "exclusion",
    ]

    fund_countries = list(mapping_country.keys())
    PATH = "/funds/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.country = "united_states"
        self.funds_loaded = None
        self.fund_name = ""
        self.fund_symbol = ""
        self.fund_isin = ""
        self.TRY_RELOAD = True
        self.end_date = ""
        self.start_date = ""

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            choices["country"].update({c: {} for c in self.fund_countries})
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        if self.fund_name:
            fund_string = (
                f"{self.fund_name} ({self.fund_symbol})"
                if self.fund_symbol
                else f"{self.fund_name}"
            )
        else:
            fund_string = ""
        mt = MenuText("funds/")
        mt.add_cmd("country")
        mt.add_raw("\n")
        mt.add_param("_country", self.country)
        mt.add_raw("\n")
        mt.add_cmd("search")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_fund", fund_string)
        mt.add_raw("\n")
        mt.add_cmd("plot", self.fund_symbol)
        mt.add_cmd("sector", self.fund_symbol)
        mt.add_cmd("holdings", self.fund_symbol)
        mt.add_cmd("carbon", self.fund_symbol)
        mt.add_cmd("exclusion", self.fund_symbol)
        mt.add_cmd("alswe", self.fund_symbol and self.country == "sweden")
        mt.add_cmd("infoswe", self.fund_symbol and self.country == "sweden")

        console.print(text=mt.menu_text, menu="Mutual Funds")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.fund_symbol and self.country:
            return ["funds", f"country {self.country}", f"load {self.fund_symbol}"]
        return []

    @log_start_end(log=logger)
    def call_alswe(self, other_args: List[str]):
        """Process alswe command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="alswe",
            description="Show allocation of a swedish fund. "
            "To get a list of available funds, check the file `avanza_fund_ID.csv`.",
        )
        parser.add_argument(
            "--focus",
            dest="focus",
            type=str,
            choices=["all", "country", "sector", "holding"],
            default="all",
            help="The focus of the funds exposure/allocation",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            ava_fund = pd.read_csv(
                os.path.join("openbb_terminal", "mutual_funds", "avanza_fund_ID.csv"),
                index_col=0,
            )
            if self.country != "sweden":
                console.print(
                    "Avanza implementation currently only supports funds from sweden."
                )
                return self.queue

            if self.fund_isin not in ava_fund["ISIN"].tolist():
                console.print("No fund data. Please use another fund.")
                return self.queue

            avanza_view.display_allocation(
                name=self.fund_name, isin=self.fund_isin, focus=ns_parser.focus
            )

        return self.queue

    @log_start_end(log=logger)
    def call_infoswe(self, other_args: List[str]):
        """Process infoswe command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="infoswe",
            description="Show fund info of a swedish fund. "
            "To get a list of available funds, check the file `avanza_fund_ID.csv`.",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            ava_fund = pd.read_csv(
                os.path.join("openbb_terminal", "mutual_funds", "avanza_fund_ID.csv"),
                index_col=0,
            )
            if self.country != "sweden":
                console.print(
                    "Avanza implementation currently only supports funds from sweden."
                )
                return self.queue

            if self.fund_isin not in ava_fund["ISIN"].tolist():
                console.print("No fund data. Please use another fund.")
                return self.queue

            avanza_view.display_info(self.fund_isin)

        return self.queue

    @log_start_end(log=logger)
    def call_country(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="country",
            description="Set a country for funds.",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=lower_str,
            choices=self.fund_countries,
            dest="name",
            help="country to select",
            default="united_states",
            metavar="NAME",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            country_candidate = ns_parser.name.lower()
            if country_candidate in self.fund_countries:
                self.country = country_candidate
                console.print(f"'{country_candidate}' selected.")

        return self.queue

    @log_start_end(log=logger)
    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Search mutual funds in selected country",
        )
        parser.add_argument(
            "--fund",
            help="Fund string to search for",
            dest="fund",
            type=str,
            required="-h" not in other_args,
        )

        parser.add_argument(
            "-l",
            "--limit",
            help="Number of search results to show",
            type=check_positive,
            dest="limit",
            default=10,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--fund")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            mstarpy_view.display_search(
                term=ns_parser.fund,
                country=self.country,
                limit=ns_parser.limit,
            )
        return self.queue

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load the fund to perform analysis on.",
        )
        parser.add_argument(
            "--fund",
            help="Fund string to search for",
            dest="fund",
            type=str,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the stock",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--fund")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.country:
                console.print(
                    "[yellow]Loading without a country selected "
                    " might result in unexpected results.[/yellow]"
                )

            funds_loaded = mstarpy_view.display_load(
                term=ns_parser.fund, country=self.country
            )

            if funds_loaded:
                self.funds_loaded = funds_loaded
                self.fund_name = funds_loaded.name
                self.fund_symbol = funds_loaded.code
                self.fund_isin = funds_loaded.isin
                self.end_date = ns_parser.end.strftime("%Y-%m-%d")
                self.start_date = ns_parser.start.strftime("%Y-%m-%d")

                console.print(
                    f"The fund {self.fund_name} - {self.fund_isin} ({self.fund_symbol})"
                    " was successfully loaded."
                )

            else:
                console.print("No funds were loaded.")
        return self.queue

    @log_start_end(log=logger)
    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Plot historical data.",
        )
        parser.add_argument(
            "-c",
            default="",
            choices=["category", "index", "both"],
            dest="compare",
            type=str.lower,
            help="Compare funds performance with its category or index",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if not self.fund_symbol:
                console.print("No fund loaded.  Please use `load` first to plot.")
                return self.queue
            mstarpy_view.display_historical(
                loaded_funds=self.funds_loaded,
                start_date=datetime.strptime(self.start_date, "%Y-%m-%d"),
                end_date=datetime.strptime(self.end_date, "%Y-%m-%d"),
                comparison=ns_parser.compare,
            )
        return self.queue

    @log_start_end(log=logger)
    def call_sector(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sector",
            description="Show funds, index, category sector breakdown.",
        )
        parser.add_argument(
            "-t",
            "--type",
            type=str,
            choices=["equity", "fixed_income"],
            dest="type",
            help="asset type to select",
            default="equity",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if not self.fund_symbol:
                console.print("No fund loaded.  Please use `load` first.")
                return self.queue

            mstarpy_view.display_sector(self.funds_loaded, asset_type=ns_parser.type)
        return self.queue

    @log_start_end(log=logger)
    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="holdings",
            description="Show funds holdings.",
        )
        parser.add_argument(
            "-t",
            "--type",
            type=str,
            choices=["all", "equity", "bond", "other"],
            dest="type",
            help="type of holdings",
            default="all",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if not self.fund_symbol:
                console.print("No fund loaded.  Please use `load` first.")
                return self.queue

            mstarpy_view.display_holdings(self.funds_loaded, ns_parser.type)

        return self.queue

    @log_start_end(log=logger)
    def call_carbon(self, other_args: List[str]):
        """Process carbon_metrics command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="carbon",
            description="Show funds carbon metrcis.",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.fund_symbol:
                console.print("No fund loaded.  Please use `load` first.")
                return self.queue

            mstarpy_view.display_carbon_metrics(self.funds_loaded)

        return self.queue

    @log_start_end(log=logger)
    def call_exclusion(self, other_args: List[str]):
        """Process exclusion_policy command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exclusion",
            description="Show funds exclsuion policy.",
        )

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.fund_symbol:
                console.print("No fund loaded.  Please use `load` first to plot.")
                return self.queue

            mstarpy_view.display_exclusion_policy(self.funds_loaded)

        return self.queue
