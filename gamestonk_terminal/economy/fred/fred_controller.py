"""FRED Controller"""
__docformat__ = "numpy"

import argparse
import logging
from typing import Dict, List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.decorators import check_api_key
from gamestonk_terminal.economy.fred import fred_model, fred_view
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    check_positive,
    parse_known_args_and_warn,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console

# pylint: disable=import-outside-toplevel


logger = logging.getLogger(__name__)


class FredController(BaseController):
    """FRED Controller Class"""

    CHOICES_COMMANDS = ["search", "add", "rmv", "plot"]
    CHOICES_MENUS = ["pred"]
    PATH = "/economy/fred/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.current_series: Dict = dict()
        self.long_id = 0

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        id_string = ""
        for s_id, sub_dict in self.current_series.items():
            id_string += (
                f"    {s_id.upper()}{(self.long_id-len(s_id)) * ' '} :"
                f" [italic]{sub_dict['title']}[/italic]\n"
            )
        if not id_string:
            id_string += "    [bold][red]None[/red][/bold]\n"
        help_text = f"""[cmds]
    search        search FRED series notes
    add           add series ID to list
    rmv           remove series ID from list[/cmds]

[param]Current Series IDs:[/param]
{id_string}{'[dim]'if not self.current_series else ""}[cmds]
    plot          plot selected series [/cmds]{'[/dim]'if not self.current_series else ""}
{'[dim]'if len(self.current_series.keys())!=1 else ""}[menu]
>   pred          prediction techniques (single SeriesID)[/menu]{'[/dim]'if len(self.current_series.keys())!=1 else ""}
        """
        console.print(text=help_text, menu="Economy - Federal Reserve Economic Data")

    @log_start_end(log=logger)
    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Print series notes when searching for series. [Source: FRED]",
        )
        parser.add_argument(
            "-s",
            "--series",
            action="store",
            dest="series_term",
            type=str,
            required="-h" not in other_args,
            help="Search for this series term.",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=5,
            help="Maximum number of series notes to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:

            fred_view.notes(
                series_term=ns_parser.series_term,
                num=ns_parser.num,
            )

    @log_start_end(log=logger)
    @check_api_key(["API_FRED_KEY"])
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add",
            description="Add a FRED series to current selection",
        )
        parser.add_argument(
            "-i",
            "--id",
            dest="series_id",
            required="-h" not in other_args,
            type=str,
            help="FRED Series from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            # Loop through entries.  If it exists, save title in dictionary
            for s_id in ns_parser.series_id.split(","):
                information = fred_model.check_series_id(s_id)
                if "seriess" in information:
                    self.current_series[s_id] = {
                        "title": information["seriess"][0]["title"],
                        "units": information["seriess"][0]["units_short"],
                    }
                    self.long_id = max(self.long_id, len(s_id))

            console.print(
                f"Current Series:[blue] {', '.join(self.current_series.keys()) .upper() or None}[/blue]\n"
            )

    @log_start_end(log=logger)
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="Remove a FRED series from current selection",
        )
        parser.add_argument(
            "-a",
            "--all",
            help="Flag to remove all selections",
            dest="all",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-i",
            "--id",
            type=lambda x: x.lower(),
            choices=[key.lower() for key in self.current_series],
            required="-h" not in other_args
            and "-a" not in other_args
            and "--all" not in other_args,
            dest="series_id",
            help="Specific id's to remove",
        )

        if other_args:
            if (
                "-h" not in other_args
                and "-i" not in other_args
                and "--id" not in other_args
                and "-a" not in other_args
                and "--all" not in other_args
            ):
                other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.all:
                self.current_series = {}
                self.long_id = 0
                console.print("")
            else:
                self.current_series.pop(ns_parser.series_id)
                console.print(
                    f"Current Series Ids: [blue]{', '.join(self.current_series.keys()) .upper() or None}[/blue]\n"
                )

    @log_start_end(log=logger)
    def call_plot(self, other_args):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="plot",
            description="Plot selected FRED Series",
        )
        parser.add_argument(
            "-s",
            dest="start_date",
            type=valid_date,
            default="2020-01-01",
            help="Starting date (YYYY-MM-DD) of data",
        )
        parser.add_argument(
            "--raw",
            help="Flag to show raw data",
            dest="raw",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-l",
            "--lim",
            dest="limit",
            help="Number of rows to show for limit",
            type=check_positive,
            default=10,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.display_fred_series(
                self.current_series,
                ns_parser.start_date,
                ns_parser.raw,
                ns_parser.export,
                ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_pred(self, _):
        """Process pred command"""
        if not self.current_series:
            console.print("Please select 1 Series to use.\n")
            return
        if len(self.current_series.keys()) != 1:
            console.print("Only 1 Series can be input into prediction.\n")
            return
        from gamestonk_terminal.economy.fred.prediction.pred_controller import (
            PredictionTechniquesController,
        )

        self.queue = self.load_class(
            PredictionTechniquesController, self.current_series, self.queue
        )
