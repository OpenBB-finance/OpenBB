""" Screener Controller Module """
__docformat__ = "numpy"

import argparse
import configparser
import os
import datetime
from typing import List

from colorama import Style
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    parse_known_args_and_warn,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.stocks.comparison_analysis import ca_controller
from gamestonk_terminal.stocks.screener import (
    finviz_view,
    yahoofinance_view,
    finviz_model,
)

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

# pylint: disable=E1121


class ScreenerController(BaseController):
    """Screener Controller class"""

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
        "po",
        "ca",
    ]

    preset_choices = [
        preset.split(".")[0]
        for preset in os.listdir(presets_path)
        if preset[-4:] == ".ini"
    ]

    historical_candle_choices = ["o", "h", "l", "c", "a"]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/stocks/scr/", queue)

        self.preset = "top_gainers"
        self.screen_tickers: List = list()

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["view"] = {c: None for c in self.preset_choices}
            choices["set"] = {
                c: None
                for c in self.preset_choices + list(finviz_model.d_signals.keys())
            }
            choices["historical"]["-t"] = {
                c: None for c in self.historical_candle_choices
            }
            choices["overview"]["-s"] = {
                c: None for c in finviz_view.d_cols_to_sort["overview"]
            }
            choices["valuation"]["-s"] = {
                c: None for c in finviz_view.d_cols_to_sort["valuation"]
            }
            choices["financial"]["-s"] = {
                c: None for c in finviz_view.d_cols_to_sort["financial"]
            }
            choices["ownership"]["-s"] = {
                c: None for c in finviz_view.d_cols_to_sort["ownership"]
            }
            choices["performance"]["-s"] = {
                c: None for c in finviz_view.d_cols_to_sort["performance"]
            }
            choices["technical"]["-s"] = {
                c: None for c in finviz_view.d_cols_to_sort["technical"]
            }
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
    view          view available presets (defaults and customs)
    set           set one of the available presets

PRESET: {self.preset}

    historical     view historical price
    overview       overview (e.g. Sector, Industry, Market Cap, Volume)
    valuation      valuation (e.g. P/E, PEG, P/S, P/B, EPS this Y)
    financial      financial (e.g. Dividend, ROA, ROE, ROI, Earnings)
    ownership      ownership (e.g. Float, Insider Own, Short Ratio)
    performance    performance (e.g. Perf Week, Perf YTD, Volatility M)
    technical      technical (e.g. Beta, SMA50, 52W Low, RSI, Change)
    {Style.NORMAL if self.screen_tickers else Style.DIM}
Last screened tickers: {', '.join(self.screen_tickers)}
>   ca             take these to comparison analysis menu
>   po             take these to portfolio optimization menu{Style.RESET_ALL}
        """
        print(help_text)

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
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.preset:
                preset_filter = configparser.RawConfigParser()
                preset_filter.optionxform = str  # type: ignore
                preset_filter.read(presets_path + ns_parser.preset + ".ini")

                filters_headers = ["General", "Descriptive", "Fundamental", "Technical"]

                print("")
                for filter_header in filters_headers:
                    print(f" - {filter_header} -")
                    d_filters = {**preset_filter[filter_header]}
                    d_filters = {k: v for k, v in d_filters.items() if v}
                    if d_filters:
                        max_len = len(max(d_filters, key=len))
                        for key, value in d_filters.items():
                            print(f"{key}{(max_len-len(key))*' '}: {value}")
                    print("")

            else:
                print("\nCustom Presets:")
                for preset in self.preset_choices:
                    with open(
                        presets_path + preset + ".ini",
                        encoding="utf8",
                    ) as f:
                        description = ""
                        for line in f:
                            if line.strip() == "[General]":
                                break
                            description += line.strip()
                    print(
                        f"   {preset}{(50-len(preset)) * ' '}{description.split('Description: ')[1].replace('#', '')}"
                    )

                print("\nDefault Presets:")
                for signame, sigdesc in finviz_model.d_signals_desc.items():
                    print(f"   {signame}{(50-len(signame)) * ' '}{sigdesc}")
                print("")

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
            choices=self.preset_choices + list(finviz_model.d_signals.keys()),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.preset = ns_parser.preset
        print("")

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
            default=datetime.datetime.now() - datetime.timedelta(days=6 * 30),
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            self.screen_tickers = yahoofinance_view.historical(
                self.preset,
                ns_parser.limit,
                ns_parser.start,
                ns_parser.type_candle,
                not ns_parser.no_scale,
                ns_parser.export,
            )

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
            choices=self.preset_choices + list(finviz_model.d_signals.keys()),
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
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            dest="ascend",
            help="Set order to Ascend, the default is Descend",
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            dest="sort",
            default="",
            nargs="+",
            choices=finviz_view.d_cols_to_sort["overview"],
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.screen_tickers = finviz_view.screener(
                loaded_preset=self.preset,
                data_type="overview",
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                sort=ns_parser.sort,
                export=ns_parser.export,
            )

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
            choices=self.preset_choices + list(finviz_model.d_signals.keys()),
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
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            dest="ascend",
            help="Set order to Ascend, the default is Descend",
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            dest="sort",
            default="",
            nargs="+",
            choices=finviz_view.d_cols_to_sort["valuation"],
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.screen_tickers = finviz_view.screener(
                loaded_preset=self.preset,
                data_type="valuation",
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                sort=ns_parser.sort,
                export=ns_parser.export,
            )

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
            choices=self.preset_choices + list(finviz_model.d_signals.keys()),
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
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            dest="ascend",
            help="Set order to Ascend, the default is Descend",
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            dest="sort",
            default="",
            nargs="+",
            choices=finviz_view.d_cols_to_sort["financial"],
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.screen_tickers = finviz_view.screener(
                loaded_preset=self.preset,
                data_type="financial",
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                sort=ns_parser.sort,
                export=ns_parser.export,
            )

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
            choices=self.preset_choices + list(finviz_model.d_signals.keys()),
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
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            dest="ascend",
            help="Set order to Ascend, the default is Descend",
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            dest="sort",
            default="",
            nargs="+",
            choices=finviz_view.d_cols_to_sort["ownership"],
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.screen_tickers = finviz_view.screener(
                loaded_preset=self.preset,
                data_type="ownership",
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                sort=ns_parser.sort,
                export=ns_parser.export,
            )

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
            choices=self.preset_choices + list(finviz_model.d_signals.keys()),
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
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            dest="ascend",
            help="Set order to Ascend, the default is Descend",
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            dest="sort",
            default="",
            nargs="+",
            choices=finviz_view.d_cols_to_sort["performance"],
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.screen_tickers = finviz_view.screener(
                loaded_preset=self.preset,
                data_type="performance",
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                sort=ns_parser.sort,
                export=ns_parser.export,
            )

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
            choices=self.preset_choices + list(finviz_model.d_signals.keys()),
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
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            dest="ascend",
            help="Set order to Ascend, the default is Descend",
        )
        parser.add_argument(
            "-s",
            "--sort",
            action="store",
            dest="sort",
            default="",
            nargs="+",
            choices=finviz_view.d_cols_to_sort["technical"],
            help="Sort elements of the table.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.screen_tickers = finviz_view.screener(
                loaded_preset=self.preset,
                data_type="technical",
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                sort=ns_parser.sort,
                export=ns_parser.export,
            )

    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        if self.screen_tickers:
            self.queue = po_controller.PortfolioOptimization(self.screen_tickers).menu(
                custom_path_menu_above="/portfolio/"
            )
        else:
            print("Some tickers must be screened first through one of the presets!\n")

    def call_ca(self, _):
        """Call the comparison analysis menu with selected tickers"""
        if self.screen_tickers:
            self.queue = ca_controller.ComparisonAnalysisController(
                self.screen_tickers, self.queue
            ).menu(custom_path_menu_above="/stocks/")
        else:
            print("Some tickers must be screened first through one of the presets!\n")
