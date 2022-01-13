"""Insider Controller Module"""
__docformat__ = "numpy"

import os
import argparse
import configparser
from typing import List
import pandas as pd
from colorama import Style
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    check_positive,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.stocks.insider import (
    openinsider_view,
    businessinsider_view,
    finviz_view,
)

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

# pylint: disable=,inconsistent-return-statements

# TODO: HELP WANTED! This menu required some refactoring. Things that can be addressed:
#       - better preset management (MVC style)
#       - unification of model return types (now some return dataframes other records list)


class InsiderController(BaseController):
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

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: pd.DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__("/stocks/ins/", queue)

        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock
        self.preset = "whales"

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["view"] = {c: None for c in self.preset_choices}
            choices["set"] = {c: None for c in self.preset_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
    view          view available presets
    set           set one of the available presets

PRESET: {self.preset}

    filter        filter insiders based on preset

    load          load a specific stock ticker for analysis
{Style.DIM if not self.ticker else ''}
Ticker: {self.ticker}

    stats         insider stats of the company [Open Insider]
    act           insider activity over time [Business Insider]
    lins          last insider trading of the company [Finviz]
{Style.RESET_ALL if not self.ticker else ''}
Latest Insiders:
    lcb           latest cluster boys
    lpsb          latest penny stock buys
    lit           latest insider trading (all filings)
    lip           latest insider purchases
    blip          big latest insider purchases ($25k+)
    blop          big latest officer purchases ($25k+)
    blcp          big latest CEO/CFO purchases ($25k+)
    lis           latest insider sales
    blis          big latest insider sales ($100k+)
    blos          big latest officer sales ($100k+)
    blcs          big latest CEO/CFO sales ($100k+)
Top Insiders:
    topt          top officer purchases today
    toppw         top officer purchases past week
    toppm         top officer purchases past month
    tipt          top insider purchases today
    tippw         top insider purchases past week
    tippm         top insider purchases past month
    tist          top insider sales today
    tispw         top insider sales past week
    tispm         top insider sales past month
"""
        print(help_text)

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "ins"]
        return []

    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source"
            + " is 'yf', an Indian ticker can be loaded by using '.NS' at the end,"
            + " e.g. 'SBIN.NS'. See available market in"
            + " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            df_stock_candidate = stocks_helper.load(
                ns_parser.ticker,
            )
            if not df_stock_candidate.empty:
                if "." in ns_parser.ticker:
                    self.ticker = ns_parser.ticker.upper().split(".")[0]
                else:
                    self.ticker = ns_parser.ticker.upper()

                self.stock = df_stock_candidate
                self.start = self.stock.index[0].strftime("%Y-%m-%d")
                self.interval = "1440min"

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
                    print(f"\nPRESET: {preset}")
                    print(description.split("Description: ")[1].replace("#", ""))
                print("")

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
            print("")

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
                print("Please use `load <ticker>` before.\n")

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
                print("No ticker loaded. First use `load {ticker}`\n")

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
                print("No ticker loaded. First use `load {ticker}`\n")
