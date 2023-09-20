""" Screener Controller Module """
__docformat__ = "numpy"

import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_and_split_input,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks.comparison_analysis import ca_controller
from openbb_terminal.stocks.screener import (
    finviz_model,
    finviz_view,
    screener_helper,
    screener_view,
)

logger = logging.getLogger(__name__)

# pylint: disable=E1121


class ScreenerController(BaseController):
    """Screener Controller class"""

    CHOICES_MENUS = ["ca"]

    CHOICES_COMMANDS = [
        "view",
        "set",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
    ]
    PRESETS_PATH = (
        get_current_user().preferences.USER_PRESETS_DIRECTORY / "stocks" / "screener"
    )
    PRESETS_PATH_DEFAULT = MISCELLANEOUS_DIRECTORY / "stocks" / "screener"

    preset_choices: Dict[str, Union[str, Path]] = {}

    if PRESETS_PATH.exists():
        preset_choices.update(
            {
                filepath.name.replace(".ini", ""): filepath
                for filepath in PRESETS_PATH.iterdir()
                if filepath.suffix == ".ini"
            }
        )

    if PRESETS_PATH_DEFAULT.exists():
        preset_choices.update(
            {
                filepath.name.replace(".ini", ""): filepath
                for filepath in PRESETS_PATH_DEFAULT.iterdir()
                if filepath.suffix == ".ini"
            }
        )

    preset_choices.update(finviz_model.d_signals)

    historical_candle_choices = ["o", "h", "l", "c", "a"]
    PATH = "/stocks/scr/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.preset = "top_gainers"
        self.screen_tickers: List = list()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def parse_input(self, an_input: str) -> List:
        """Parse controller input

        Overrides the parent class function to handle github org/repo path convention.
        See `BaseController.parse_input()` for details.
        """
        # Filtering out sorting parameters with forward slashes like P/E
        f0 = r"(p\/e|fwd p\/e|p\/s|p\/b|p\/c|p\/fcf)"
        f1 = r"(P\/E|Fwd P\/E|P\/S|P\/B|P\/C|P\/FCF)"

        sort_filter = r"((\ -s |\ --sort ).*?" + r"(" + f0 + r"|" + f1 + r")" + r"*)"

        custom_filters = [sort_filter]

        commands = parse_and_split_input(
            an_input=an_input, custom_filters=custom_filters
        )
        return commands

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/scr/")
        mt.add_cmd("view")
        mt.add_cmd("set")
        mt.add_raw("\n")
        mt.add_param("_preset", self.preset)
        mt.add_raw("\n")
        mt.add_cmd("overview")
        mt.add_cmd("valuation")
        mt.add_cmd("financial")
        mt.add_cmd("ownership")
        mt.add_cmd("performance")
        mt.add_cmd("technical")
        mt.add_raw("\n")
        mt.add_param("_screened_tickers", ", ".join(self.screen_tickers))
        mt.add_raw("\n")
        mt.add_menu("ca", self.screen_tickers)
        console.print(text=mt.menu_text, menu="Stocks - Screener")

    @log_start_end(log=logger)
    def call_view(self, other_args: List[str]):
        """Process view command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="view",
            description="""View available presets under presets folder.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            help="View specific custom preset",
            default="",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.preset and ns_parser.preset in finviz_model.d_signals:
                console.print(
                    "This preset contains no parameters other than the signal.\n"
                )
                return
            screener_view.display_presets(ns_parser.preset)

    @log_start_end(log=logger)
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="set",
            description="""Set preset from custom and default ones.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default="template",
            help="Filter presets",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.preset = ns_parser.preset

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="overview",
            description="""
                Prints overview data of the companies that meet the pre-set filtering.
            """,
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default=self.preset,
            help="Filter presets",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=0,
            help="Limit of stocks to print",
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
            "-s",
            "--sort",
            choices=screener_helper.finviz_choices("overview"),
            type=str.lower,
            dest="sort",
            metavar="SORT",
            default="marketcap",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.replace(".ini", "")
                if self.preset.replace(".ini", "") in finviz_model.d_signals
                else self.preset
            )

            sort_map = screener_helper.finviz_map("overview")
            self.screen_tickers = finviz_view.screener(
                loaded_preset=preset,
                data_type="overview",
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                sortby=sort_map[ns_parser.sort],
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="valuation",
            description="""
                Prints valuation data of the companies that meet the pre-set filtering.
            """,
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default=self.preset,
            help="Filter presets",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=0,
            help="Limit of stocks to print",
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
            "-s",
            "--sort",
            dest="sort",
            default="marketcap",
            choices=screener_helper.finviz_choices("valuation"),
            type=str.lower,
            metavar="SORT",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.replace(".ini", "")
                if self.preset.replace(".ini", "") in finviz_model.d_signals
                else self.preset
            )
            sort_map = screener_helper.finviz_map("valuation")
            self.screen_tickers = finviz_view.screener(
                loaded_preset=preset,
                data_type="valuation",
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                sortby=sort_map[ns_parser.sort],
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_financial(self, other_args: List[str]):
        """Process financial command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="financial",
            description="""
                Prints financial data of the companies that meet the pre-set filtering.
            """,
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default=self.preset,
            help="Filter presets",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=0,
            help="Limit of stocks to print",
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
            "-s",
            "--sort",
            choices=screener_helper.finviz_choices("financial"),
            type=str.lower,
            dest="sort",
            metavar="SORT",
            default="marketcap",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.replace(".ini", "")
                if self.preset.replace(".ini", "") in finviz_model.d_signals
                else self.preset
            )
            sort_map = screener_helper.finviz_map("financial")
            self.screen_tickers = finviz_view.screener(
                loaded_preset=preset,
                data_type="financial",
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                sortby=sort_map[ns_parser.sort],
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ownership(self, other_args: List[str]):
        """Process ownership command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="ownership",
            description="""
                Prints ownership data of the companies that meet the pre-set filtering.
            """,
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default=self.preset,
            help="Filter presets",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=0,
            help="Limit of stocks to print",
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
            "-s",
            "--sort",
            dest="sort",
            metavar="SORT",
            default="marketcap",
            choices=screener_helper.finviz_choices("ownership"),
            type=str.lower,
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.replace(".ini", "")
                if self.preset.replace(".ini", "") in finviz_model.d_signals
                else self.preset
            )
            sort_map = screener_helper.finviz_map("ownership")
            self.screen_tickers = finviz_view.screener(
                loaded_preset=preset,
                data_type="ownership",
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                sortby=sort_map[ns_parser.sort],
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="performance",
            description="""
                Prints performance data of the companies that meet the pre-set filtering.
            """,
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default=self.preset,
            help="Filter presets",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=0,
            help="Limit of stocks to print",
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
            "-s",
            "--sort",
            choices=screener_helper.finviz_choices("performance"),
            type=str.lower,
            dest="sort",
            default="ytd",
            metavar="SORTBY",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        sort_map = screener_helper.finviz_map("performance")
        if ns_parser:
            preset = (
                self.preset.replace(".ini", "")
                if self.preset.replace(".ini", "") in finviz_model.d_signals
                else self.preset
            )
            self.screen_tickers = finviz_view.screener(
                loaded_preset=preset,
                data_type="performance",
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                sortby=sort_map[ns_parser.sort],
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_technical(self, other_args: List[str]):
        """Process technical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="technical",
            description="""
                Prints technical data of the companies that meet the pre-set filtering.
            """,
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default=self.preset,
            help="Filter presets",
            choices=self.preset_choices,
            metavar="Desired preset.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=int,
            default=0,
            help="Limit of stocks to print",
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
            "-s",
            "--sort",
            choices=screener_helper.finviz_choices("technical"),
            type=str.lower,
            dest="sort",
            default="rsi",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.replace(".ini", "")
                if self.preset.replace(".ini", "") in finviz_model.d_signals
                else self.preset
            )
            sort_map = screener_helper.finviz_map("technical")
            self.screen_tickers = finviz_view.screener(
                loaded_preset=preset,
                data_type="technical",
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                sortby=sort_map[ns_parser.sort],
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ca(self, _):
        """Call the comparison analysis menu with selected tickers"""
        if self.screen_tickers:
            self.queue = self.load_class(
                ca_controller.ComparisonAnalysisController,
                self.screen_tickers,
                self.queue,
            )
        else:
            console.print(
                "Please select a screener using 'set' and then run 'historical' "
                "before going to the CA menu.\n"
            )
