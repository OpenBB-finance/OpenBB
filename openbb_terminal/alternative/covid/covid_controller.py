"""COVID Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
import pathlib
from typing import List, Optional

import pandas as pd

from openbb_terminal.alternative.covid import covid_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)

country_file = pathlib.Path(__file__).parent.joinpath("countries.txt")


class CovidController(BaseController):
    """Covid Controller class"""

    CHOICES_COMMANDS = ["country", "ov", "deaths", "cases", "rates", "slopes"]
    PATH = "/alternative/covid/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.country = "US"
        countries_df = pd.read_csv(country_file, sep="|", index_col=None)
        countries_list = countries_df["Countries"].to_list()
        self.COUNTRY_LIST = [x.lower().replace(" ", "_") for x in countries_list]

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("alternative/covid/")
        mt.add_cmd("slopes")
        mt.add_cmd("country")
        mt.add_raw("\n")
        mt.add_param("_country", self.country)
        mt.add_raw("\n")
        mt.add_cmd("ov")
        mt.add_cmd("deaths")
        mt.add_cmd("cases")
        mt.add_cmd("rates")
        console.print(text=mt.menu_text, menu="Alternative - COVID")

    def custom_reset(self):
        """Class specific component of reset command"""
        return ["alternative", "covid", f"country {self.country}"]

    @log_start_end(log=logger)
    def call_country(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="country",
            description="Select a country to look at data for.",
        )
        parser.add_argument(
            "-c",
            "--country",
            type=str.lower,
            choices=self.COUNTRY_LIST,
            metavar="country_name",
            dest="country",
            help="Country to get data for.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.country:
                if ns_parser.country not in self.COUNTRY_LIST:
                    logger.error("%s not a valid selection", ns_parser.country)
                    console.print(
                        f"[red]{ns_parser.country} not a valid selection.[/red]\n"
                    )
                    return
                country = ns_parser.country.title().replace("_", " ")
                if country == "Us":
                    country = "US"
                self.country = country
                console.print(f"[cyan]{country}[/cyan] loaded\n")
            else:
                logger.error("No country provided")
                console.print("[red]Please input a country.[/red]\n")

    @log_start_end(log=logger)
    def call_ov(self, other_args: List[str]):
        """Process ov command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ov",
            description="Show historical cases and deaths by country.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_ov(
                self.country,
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rates(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rates",
            description="Show historical death/cases rates for a country.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="rates",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_deaths(self, other_args: List[str]):
        """Process deaths command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="deaths",
            description="Show historical deaths by country.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="deaths",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_cases(self, other_args: List[str]):
        """Process cases command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cases",
            description="Show historical cases for country.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="cases",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_slopes(self, other_args: List[str]):
        """Process cases command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="slopes",
            description="Show countries with highest slopes.",
        )
        parser.add_argument(
            "-d",
            "--days",
            type=check_positive,
            help="Number of days back to look",
            dest="days",
            default=30,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        parser.add_argument(
            "-t",
            "--threshold",
            default=10000,
            dest="threshold",
            help="Threshold for total cases over period",
            type=check_positive,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )
        if ns_parser:
            if ns_parser.days < 2:
                console.print("[red]Days must be greater than 1[/red]")
                return
            covid_view.display_case_slopes(
                days_back=ns_parser.days,
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                threshold=ns_parser.threshold,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
