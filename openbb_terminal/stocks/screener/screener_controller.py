""" Screener Controller Module """
__docformat__ = "numpy"

import argparse
import datetime
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
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    parse_and_split_input,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks.comparison_analysis import ca_controller
from openbb_terminal.stocks.screener import (
    ark_view,
    finviz_model,
    finviz_view,
    screener_helper,
    screener_view,
    yahoofinance_view,
)

logger = logging.getLogger(__name__)

# pylint: disable=E1121


class ScreenerController(BaseController):
    """Screener Controller class"""

    CHOICES_MENUS = ["ca"]

    CHOICES_COMMANDS = [
        "view",
        "set",
        "historical",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
        "arktrades",
    ]
    PRESETS_PATH = (
        get_current_user().preferences.USER_PRESETS_DIRECTORY / "stocks" / "screener"
    )
    PRESETS_PATH_DEFAULT = MISCELLANEOUS_DIRECTORY / "stocks" / "screener"

    preset_choices: Dict[str, Union[str, Path]] = {}

    if PRESETS_PATH.exists():
        preset_choices.update(
            {
                filepath.name.strip(".ini"): filepath
                for filepath in PRESETS_PATH.iterdir()
                if filepath.suffix == ".ini"
            }
        )

    if PRESETS_PATH_DEFAULT.exists():
        preset_choices.update(
            {
                filepath.name.strip(".ini"): filepath
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

        self.preset = "top_gainers.ini"
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
        mt.add_cmd("historical")
        mt.add_cmd("overview")
        mt.add_cmd("valuation")
        mt.add_cmd("financial")
        mt.add_cmd("ownership")
        mt.add_cmd("performance")
        mt.add_cmd("technical")
        mt.add_cmd("arktrades")
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
            if ns_parser.preset:
                if ns_parser.preset in finviz_model.d_signals:
                    console.print("This is a Finviz preset.\n")
                    return
                ns_parser.preset += ".ini"
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
            self.preset = ns_parser.preset + ".ini"

    @log_start_end(log=logger)
    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="historical",
            description="""Historical price comparison between similar companies [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of the most shorted stocks to retrieve.",
        )
        parser.add_argument(
            "-n",
            "--no-scale",
            action="store_false",
            dest="no_scale",
            default=False,
            help="Flag to not put all prices on same 0-1 scale",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(
                datetime.datetime.now() - datetime.timedelta(days=6 * 30)
            ).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the historical price to plot",
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="type_candle",
            choices=self.historical_candle_choices,
            default="a",  # in case it's adjusted close
            help="type of candles: o-open, h-high, l-low, c-close, a-adjusted close.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            preset = (
                self.preset.strip(".ini")
                if self.preset.strip(".ini") in finviz_model.d_signals
                else self.preset
            )
            self.screen_tickers = yahoofinance_view.historical(
                preset,
                ns_parser.limit,
                ns_parser.start,
                ns_parser.type_candle,
                not ns_parser.no_scale,
                ns_parser.export,
            )

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
            type=check_positive,
            default=10,
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
            default="Ticker",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.strip(".ini")
                if self.preset.strip(".ini") in finviz_model.d_signals
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
            type=check_positive,
            default=10,
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
            default="Ticker",
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
                self.preset.strip(".ini")
                if self.preset.strip(".ini") in finviz_model.d_signals
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
            type=check_positive,
            default=10,
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
            default="Ticker",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.strip(".ini")
                if self.preset.strip(".ini") in finviz_model.d_signals
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
            type=check_positive,
            default=10,
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
            default="Ticker",
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
                self.preset.strip(".ini")
                if self.preset.strip(".ini") in finviz_model.d_signals
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
            type=check_positive,
            default=10,
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
            default="Ticker",
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
                self.preset.strip(".ini")
                if self.preset.strip(".ini") in finviz_model.d_signals
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
            type=check_positive,
            default=10,
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
            default="Ticker",
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            preset = (
                self.preset.strip(".ini")
                if self.preset.strip(".ini") in finviz_model.d_signals
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

    @log_start_end(log=logger)
    def call_arktrades(self, other_args):
        """Process arktrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="arktrades",
            description="""
                Get trades for ticker across all ARK funds.
            """,
        )
        parser.add_argument(
            "-t",
            "--ticker",
            help="The ticker to use for searching.",
            dest="ticker",
            required=True,
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Limit of rows to show",
            dest="limit",
            default=10,
            type=check_positive,
        )
        parser.add_argument(
            "-s",
            "--show_symbol",
            action="store_true",
            default=False,
            help="Flag to show ticker in table",
            dest="show_symbol",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ark_view.display_ark_trades(
                symbol=ns_parser.ticker,
                limit=ns_parser.limit,
                show_symbol=ns_parser.show_symbol,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
