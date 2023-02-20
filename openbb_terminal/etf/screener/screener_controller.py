"""Screener Controller Module"""
__docformat__ = "numpy"
# pylint:disable=R0904,C0201

import argparse
import configparser
import logging
from typing import List, Optional

from openbb_terminal import feature_flags as obbff
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf import financedatabase_model, financedatabase_view
from openbb_terminal.etf.screener import screener_model, screener_view
from openbb_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED, check_positive
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class ScreenerController(BaseController):
    """Screener Controller class"""

    CHOICES_COMMANDS = [
        "view",
        "set",
        "screen",
        "sbc",
    ]

    PRESET_CHOICES = screener_model.get_preset_choices()
    ETF_CATEGORY_LIST = financedatabase_model.get_etfs_categories()

    sortby_screen_choices = [
        "Assets",
        "NAV",
        "Expense",
        "PE",
        "SharesOut",
        "Div",
        "DivYield",
        "Volume",
        "Open",
        "PrevClose",
        "YrLow",
        "YrHigh",
        "Beta",
        "N_Hold",
    ]

    PATH = "/etf/scr/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.preset = "etf_config"
        self.screen_tickers: List = list()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            choices["view"].update({c: None for c in self.PRESET_CHOICES})
            choices["set"].update({c: None for c in self.PRESET_CHOICES})
            choices["sbc"].update({c: None for c in self.ETF_CATEGORY_LIST})

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("etf/scr/", 70)
        mt.add_cmd("view")
        mt.add_cmd("set")
        mt.add_raw("\n")
        mt.add_param("_preset", self.preset)
        mt.add_raw("\n")
        mt.add_cmd("screen")
        mt.add_raw("\n")
        mt.add_cmd("sbc")
        console.print(text=mt.menu_text, menu="ETF - Screener")

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
            choices=self.PRESET_CHOICES,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.preset:
                preset_filter = configparser.RawConfigParser()
                preset_filter.optionxform = str  # type: ignore
                preset_filter.read(self.PRESET_CHOICES[ns_parser.preset])

                headers = [
                    "Price",
                    "Assets",
                    "NAV",
                    "Expense",
                    "PE",
                    "DivYield",
                    "Volume",
                    "Beta",
                    "N_Hold",
                    "Open",
                    "PrevClose",
                    "YrLow",
                    "YrHigh",
                ]

                for i, filter_header in enumerate(headers):
                    console.print(f" - {filter_header} -")
                    d_filters = {**preset_filter[filter_header]}
                    d_filters = {k: v for k, v in d_filters.items() if v}
                    if d_filters:
                        max_len = len(max(d_filters, key=len))
                        for key, value in d_filters.items():
                            console.print(f"{key}{(max_len-len(key))*' '}: {value}")

                    if i < len(headers) - 1:
                        console.print("\n")

            else:
                console.print("\nPresets:")
                for preset in self.PRESET_CHOICES:
                    with open(
                        self.PRESET_CHOICES[preset],
                        encoding="utf8",
                    ) as f:
                        description = ""
                        for line in f:
                            if line.strip() == "[Price]":
                                break
                            description += line.strip()
                    console.print(
                        f"   {preset}{(30-len(preset)) * ' '}{description.split('Description: ')[1].replace('#', '')}"
                    )

    @log_start_end(log=logger)
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="set",
            description="""Set preset.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default="template",
            help="Filter presets",
            choices=self.PRESET_CHOICES,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.preset = ns_parser.preset

    @log_start_end(log=logger)
    def call_screen(self, other_args):
        """Process screen command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="screen",
            add_help=False,
            description="Screens ETFS from a personal scraping github repository.  Data scraped from stockanalysis.com",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            help="Limit of etfs to display",
            dest="limit",
            default=10,
        )
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Assets",
            default="Assets",
            choices=self.sortby_screen_choices,
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            screener_view.view_screener(
                preset=self.preset,
                num_to_show=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_sbc(self, other_args: List[str]):
        """Process sbc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sbc",
            description="Search by category [Source: FinanceDatabase/StockAnalysis.com]",
        )
        parser.add_argument(
            "-c",
            "--category",
            type=str,
            dest="category",
            nargs="+",
            help="Category to look for",
            required="-h" not in other_args,
            choices=self.ETF_CATEGORY_LIST,
            metavar="CATEGORY",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            dest="limit",
            help="Limit of ETFs to display",
            default=5,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            category = " ".join(ns_parser.category)
            if category in self.ETF_CATEGORY_LIST:
                financedatabase_view.display_etf_by_category(
                    category=category,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print(
                    "The category selected does not exist, choose one from:"
                    f" {', '.join(self.ETF_CATEGORY_LIST)}\n"
                )
