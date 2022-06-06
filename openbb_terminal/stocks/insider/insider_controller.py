"""Insider Controller Module"""
__docformat__ = "numpy"

import argparse
import configparser
import logging
import os
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    parse_known_args_and_warn,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.stocks.insider import (
    businessinsider_view,
    finviz_view,
    openinsider_view,
)

logger = logging.getLogger(__name__)

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

# pylint: disable=,inconsistent-return-statements

# TODO: HELP WANTED! This menu required some refactoring. Things that can be addressed:
#       - better preset management (MVC style)
#       - unification of model return types (now some return dataframes other records list)


class InsiderController(StockBaseController):
    """Screener Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "view",
        "set",
        "filter",
        "lcb",
        "lpsb",
        "lit",
        "lip",
        "blip",
        "blop",
        "blcp",
        "lis",
        "blis",
        "blos",
        "blcs",
        "topt",
        "toppw",
        "toppm",
        "tipt",
        "tippw",
        "tippm",
        "tist",
        "tispw",
        "tispm",
        "act",
        "lins",
        "stats",
    ]

    preset_choices = [
        preset.split(".")[0]
        for preset in os.listdir(presets_path)
        if preset[-4:] == ".ini"
    ]
    PATH = "/stocks/ins/"

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: pd.DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock
        self.preset = "whales"

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["view"] = {c: None for c in self.preset_choices}
            choices["set"] = {c: None for c in self.preset_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/ins/", 80)
        mt.add_cmd("view")
        mt.add_cmd("set")
        mt.add_raw("\n")
        mt.add_param("_preset", self.preset)
        mt.add_raw("\n")
        mt.add_cmd("filter", "Open Insider")
        mt.add_raw("\n\n")
        mt.add_param("_ticker", self.ticker)
        mt.add_raw("\n")
        mt.add_cmd("stats", "Open Insider", self.ticker)
        mt.add_cmd("act", "Business Insider", self.ticker)
        mt.add_cmd("lins", "Finviz", self.ticker)
        mt.add_raw("\n")
        mt.add_info("_last_insiders")
        mt.add_cmd("lcb", "Open Insider")
        mt.add_cmd("lpsb", "Open Insider")
        mt.add_cmd("lit", "Open Insider")
        mt.add_cmd("lip", "Open Insider")
        mt.add_cmd("blip", "Open Insider")
        mt.add_cmd("blop", "Open Insider")
        mt.add_cmd("bclp", "Open Insider")
        mt.add_cmd("lis", "Open Insider")
        mt.add_cmd("blis", "Open Insider")
        mt.add_cmd("blos", "Open Insider")
        mt.add_cmd("blcs", "Open Insider")
        mt.add_info("_top_insiders")
        mt.add_cmd("topt", "Open Insider")
        mt.add_cmd("toppw", "Open Insider")
        mt.add_cmd("toppm", "Open Insider")
        mt.add_cmd("tipt", "Open Insider")
        mt.add_cmd("tippw", "Open Insider")
        mt.add_cmd("tippm", "Open Insider")
        mt.add_cmd("tist", "Open Insider")
        mt.add_cmd("tispw", "Open Insider")
        mt.add_cmd("tispm", "Open Insider")
        console.print(text=mt.menu_text, menu="Stocks - Insider Trading")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "ins"]
        return []

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
            help="View specific preset",
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

                filters_headers = [
                    "General",
                    "Date",
                    "TransactionFiling",
                    "Industry",
                    "InsiderTitle",
                    "Others",
                    "CompanyTotals",
                ]

                console.print("")
                for filter_header in filters_headers:
                    console.print(f" - {filter_header} -")
                    d_filters = {**preset_filter[filter_header]}
                    d_filters = {k: v for k, v in d_filters.items() if v}
                    if d_filters:
                        max_len = len(max(d_filters, key=len))
                        for key, value in d_filters.items():
                            console.print(f"{key}{(max_len-len(key))*' '}: {value}")
                    console.print("")

            else:
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
                    console.print(f"\nPRESET: {preset}")
                    console.print(
                        description.split("Description: ")[1].replace("#", "")
                    )
                console.print("")

    @log_start_end(log=logger)
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="set",
            description="""Set preset from under presets folder.""",
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
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.preset = ns_parser.preset
            console.print("")

    @log_start_end(log=logger)
    def call_filter(self, other_args: List[str]):
        """Process filter command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="filter",
            description="Print open insider filtered data using loaded preset. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        parser.add_argument(
            "-u",
            "--urls",
            action="store_true",
            default=False,
            help="Flag to show hyperlinks",
            dest="urls",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_filter(
                preset_loaded=self.preset,
                ticker="",
                limit=ns_parser.limit,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_stats(self, other_args: List[str]):
        """Process stats command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stats",
            description="Print open insider filtered data using selected ticker. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        parser.add_argument(
            "-u",
            "--urls",
            action="store_true",
            default=False,
            help="Flag to show hyperlinks",
            dest="urls",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                openinsider_view.print_insider_filter(
                    preset_loaded="",
                    ticker=self.ticker,
                    limit=ns_parser.limit,
                    links=ns_parser.urls,
                    export=ns_parser.export,
                )
            else:
                console.print("Please use `load <ticker>` before.\n")

    @log_start_end(log=logger)
    def call_lcb(self, other_args: List[str]):
        """Process latest-cluster-buys"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lcb",
            description="Print latest cluster buys. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "lcb", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_lpsb(self, other_args: List[str]):
        """Process latest-penny-stock-buys"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lpsb",
            description="Print latest penny stock buys. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "lpsb", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_lit(self, other_args: List[str]):
        """Process latest-insider-trading"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lit",
            description="Print latest insider trading. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "lit", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_lip(self, other_args: List[str]):
        """Process insider-purchases"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lip",
            description="Print latest insider purchases. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "lip", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_blip(self, other_args: List[str]):
        """Process latest-insider-purchases-25k"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="blip",
            description="Print latest insider purchases 25k. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "blip", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_blop(self, other_args: List[str]):
        """Process latest-officer-purchases-25k"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="blop",
            description="Print latest officer purchases 25k. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "blop", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_blcp(self, other_args: List[str]):
        """Process latest-ceo-cfo-purchases-25k"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="blcp",
            description="Print latest CEO/CFO purchases 25k. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "blcp", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_lis(self, other_args: List[str]):
        """Process insider-sales"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lis",
            description="Print latest insider sales. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "lis", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_blis(self, other_args: List[str]):
        """Process latest-insider-sales-100k"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="blis",
            description="Print latest insider sales 100k. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "blis", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_blos(self, other_args: List[str]):
        """Process latest-officer-sales-100k"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="blos",
            description="Print latest officer sales 100k. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "blos", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_blcs(self, other_args: List[str]):
        """Process latest-ceo-cfo-sales-100k"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="blcs",
            description="Print latest CEO/CFO sales 100k. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "blcs", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_topt(self, other_args: List[str]):
        """Process top-officer-purchases-of-the-day"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="topt",
            description="Print top officer purchases of the day. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "topt", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_toppw(self, other_args: List[str]):
        """Process top-officer-purchases-of-the-week"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="toppw",
            description="Print top officer purchases of the week. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "toppw", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_toppm(self, other_args: List[str]):
        """Process top-officer-purchases-of-the-month"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="toppm",
            description="Print top officer purchases of the month. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "toppm", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_tipt(self, other_args: List[str]):
        """Process top-insider-purchases-of-the-day"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tipt",
            description="Print top insider purchases of the day. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "tipt", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_tippw(self, other_args: List[str]):
        """Process top-insider-purchases-of-the-week"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tippw",
            description="Print top insider purchases of the week. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "tippw", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_tippm(self, other_args: List[str]):
        """Process top-insider-purchases-of-the-month"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tippm",
            description="Print top insider purchases of the month. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "tippm", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_tist(self, other_args: List[str]):
        """Process top-insider-sales-of-the-day"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tist",
            description="Print top insider sales of the day. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "tist", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_tispw(self, other_args: List[str]):
        """Process top-insider-sales-of-the-week"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tispw",
            description="Print top insider sales of the week. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "tispw", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_tispm(self, other_args: List[str]):
        """Process top-insider-sales-of-the-month"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tispm",
            description="Print top insider sales of the month. [Source: OpenInsider]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of datarows to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            openinsider_view.print_insider_data(
                "tispm", ns_parser.limit, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_act(self, other_args: List[str]):
        """Process act command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="act",
            description="""Prints insider activity over time [Source: Business Insider]""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of latest insider activity.",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                businessinsider_view.insider_activity(
                    stock=self.stock,
                    ticker=self.ticker,
                    start=self.start,
                    interval=self.interval,
                    num=ns_parser.limit,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                console.print("No ticker loaded. First use `load {ticker}`\n")

    @log_start_end(log=logger)
    def call_lins(self, other_args: List[str]):
        """Process lins command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="lins",
            description="""
                Prints information about inside traders. The following fields are expected: Date, Relationship,
                Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading, SEC Form 4. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of latest inside traders.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                finviz_view.last_insider_activity(
                    ticker=self.ticker,
                    num=ns_parser.limit,
                    export=ns_parser.export,
                )
            else:
                console.print("No ticker loaded. First use `load {ticker}`\n")
