""" Econ Controller """
__docformat__ = "numpy"
# pylint:disable=too-many-lines,R1710,R0904,C0415
import argparse
from datetime import datetime, timedelta
import os
from typing import List

from rich.console import Console
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import (
    alphavantage_view,
    cnn_view,
    finviz_view,
    nasdaq_model,
    wsj_view,
    nasdaq_view,
)
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_ONLY_FIGURES_ALLOWED,
    parse_known_args_and_warn,
    valid_date,
)
from gamestonk_terminal.menu import session

t_console = Console()


class EconomyController(BaseController):
    """Economy Controller class"""

    CHOICES_COMMANDS = [
        "feargreed",
        "overview",
        "indices",
        "futures",
        "usbonds",
        "glbonds",
        "futures",
        "currencies",
        "energy",
        "metals",
        "meats",
        "grains",
        "softs",
        "valuation",
        "performance",
        "spectrum",
        "map",
        "rtps",
        "gdp",
        "gdpc",
        "inf",
        "cpi",
        "tyld",
        "unemp",
        "industry",
        "bigmac",
    ]
    CHOICES_MENUS = ["fred"]

    fear_greed_indicators = ["jbd", "mv", "pco", "mm", "sps", "spb", "shd", "index"]
    wsj_sortby_cols_dict = {c: None for c in ["ticker", "last", "change", "prevClose"]}
    map_period_list = ["1d", "1w", "1m", "3m", "6m", "1y"]
    map_type_list = ["sp500", "world", "full", "etf"]
    gdp_interval = ["annual", "quarter"]
    cpi_interval = ["semiannual", "monthly"]
    tyld_interval = ["daily", "weekly", "monthly"]
    tyld_maturity = ["3m", "5y", "10y", "30y"]
    valuation_sort_cols = [
        "Name",
        "MarketCap",
        "P/E",
        "FwdP/E",
        "PEG",
        "P/S",
        "P/B",
        "P/C",
        "P/FCF",
        "EPSpast5Y",
        "EPSnext5Y",
        "Salespast5Y",
        "Change",
        "Volume",
    ]
    performance_sort_list = [
        "Name",
        "Week",
        "Month",
        "3Month",
        "6Month",
        "1Year",
        "YTD",
        "Recom",
        "AvgVolume",
        "RelVolume",
        "Change",
        "Volume",
    ]
    d_GROUPS = {
        "sector": "Sector",
        "industry": "Industry",
        "basic materials": "Industry (Basic Materials)",
        "communication services": "Industry (Communication Services)",
        "consumer cyclical": "Industry (Consumer Cyclical)",
        "consumer defensive": "Industry (Consumer Defensive)",
        "energy": "Industry (Energy)",
        "financial": "Industry (Financial)",
        "healthcare": "Industry (Healthcare)",
        "industrials": "Industry (Industrials)",
        "real Estate": "Industry (Real Estate)",
        "technology": "Industry (Technology)",
        "utilities": "Industry (Utilities)",
        "country": "Country (U.S. listed stocks only)",
        "capitalization": "Capitalization",
    }

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/economy/", queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["feargreed"]["-i"] = {c: None for c in self.fear_greed_indicators}
            choices["feargreed"]["--indicator"] = {
                c: None for c in self.fear_greed_indicators
            }
            for command in ["energy", "meats", "metals", "grains", "softs"]:
                choices[command]["-s"] = self.wsj_sortby_cols_dict
                choices[command]["--sortby"] = self.wsj_sortby_cols_dict

            choices["map"]["-p"] = {c: None for c in self.map_period_list}
            choices["map"]["--period"] = {c: None for c in self.map_period_list}

            choices["valuation"]["-s"] = {c: None for c in self.valuation_sort_cols}
            choices["valuation"]["--sortby"] = {
                c: None for c in self.valuation_sort_cols
            }

            choices["performance"]["-s"] = {c: None for c in self.performance_sort_list}
            choices["performance"]["--sortby"] = {
                c: None for c in self.performance_sort_list
            }

            choices["gdp"]["-i"] = {c: None for c in self.gdp_interval}
            choices["gdp"]["--interval"] = {c: None for c in self.gdp_interval}

            choices["cpi"]["-i"] = {c: None for c in self.cpi_interval}
            choices["cpi"]["--interval"] = {c: None for c in self.cpi_interval}

            choices["tyld"]["-i"] = {c: None for c in self.tyld_interval}
            choices["tyld"]["--interval"] = {c: None for c in self.tyld_interval}
            choices["tyld"]["-m"] = {c: None for c in self.tyld_maturity}
            choices["tyld"]["--maturity"] = {c: None for c in self.tyld_maturity}

            self.completer = NestedCompleter.from_nested_dict(choices)

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """
CNN:
    feargreed     CNN Fear and Greed Index
Wall St. Journal:
    overview      market data overview
    indices       US indices overview
    futures       futures and commodities overview
    usbonds       US bonds overview
    glbonds       global bonds overview
    currencies    currencies overview
Finviz:
    energy        energy futures overview
    metals        metals futures overview
    meats         meats futures overview
    grains        grains futures overview
    softs         softs futures overview
    map           S&P500 index stocks map
    valuation     valuation of sectors, industry, country
    performance   performance of sectors, industry, country
    spectrum      spectrum of sectors, industry, country
Alpha Vantage:
    rtps          real-time performance sectors
    gdp           real GDP for United States
    gdpc          quarterly real GDP per Capita data of the United States
    inf           infation rates for United States
    cpi           consumer price index for United States
    tyld          treasury yields for United States
    unemp         United States unemployment rates
NASDAQ DataLink (formerly Quandl):
    bigmac        the economists Big Mac index

>   fred          Federal Reserve Economic Data submenu
"""
        print(type(help_text))
        t_console.print(help_text)

    def call_feargreed(self, other_args: List[str]):
        """Process feargreed command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="feargreed",
            description="""
                Display CNN Fear And Greed Index from https://money.cnn.com/data/fear-and-greed/.
            """,
        )
        parser.add_argument(
            "-i",
            "--indicator",
            dest="indicator",
            required=False,
            type=str,
            choices=self.fear_greed_indicators,
            help="""
                CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
                Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
                Safe Heaven Demand, and Index.
            """,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            cnn_view.fear_and_greed_index(
                indicator=ns_parser.indicator,
                export=ns_parser.export,
            )

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="Market overview. [Source: Wall St. Journal]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.display_overview(
                export=ns_parser.export,
            )

    def call_indices(self, other_args: List[str]):
        """Process indices command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="indices",
            description="US indices. [Source: Wall St. Journal]",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.display_indices(
                export=ns_parser.export,
            )

    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="futures",
            description="Futures/Commodities. [Source: Wall St. Journal]",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.display_futures(
                export=ns_parser.export,
            )

    def call_usbonds(self, other_args: List[str]):
        """Process usbonds command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="usbonds",
            description="US Bonds. [Source: Wall St. Journal]",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.display_usbonds(
                export=ns_parser.export,
            )

    def call_glbonds(self, other_args: List[str]):
        """Process glbonds command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="glbonds",
            description="Global Bonds. [Source: Wall St. Journal]",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.display_glbonds(
                export=ns_parser.export,
            )

    def call_currencies(self, other_args: List[str]):
        """Process currencies command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="currencies",
            description="Currencies. [Source: Wall St. Journal]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.display_currencies(
                export=ns_parser.export,
            )

    def call_energy(self, other_args: List[str]):
        """Process energy command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="energy",
            description="Energy future overview. [Source: Finviz]",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            type=str,
            choices=self.wsj_sortby_cols_dict.keys(),
            default="ticker",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_future(
                future_type="Energy",
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )

    def call_metals(self, other_args: List[str]):
        """Process metals command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="metals",
            description="Metals future overview. [Source: Finviz]",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            type=str,
            choices=self.wsj_sortby_cols_dict.keys(),
            default="ticker",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_future(
                future_type="Metals",
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )

    def call_meats(self, other_args: List[str]):
        """Process meats command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="meats",
            description="Meats future overview. [Source: Finviz]",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            type=str,
            choices=self.wsj_sortby_cols_dict.keys(),
            default="ticker",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_future(
                future_type="Meats",
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )

    def call_grains(self, other_args: List[str]):
        """Process grains command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="grains",
            description="Grains future overview. [Source: Finviz]",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            type=str,
            choices=self.wsj_sortby_cols_dict.keys(),
            default="ticker",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_future(
                future_type="Grains",
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )

    def call_softs(self, other_args: List[str]):
        """Process softs command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="softs",
            description="Softs future overview. [Source: Finviz]",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            type=str,
            choices=self.wsj_sortby_cols_dict.keys(),
            default="ticker",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.display_future(
                future_type="Softs",
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )

    def call_map(self, other_args: List[str]):
        """Process map command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="map",
            description="""
                Performance index stocks map categorized by sectors and industries.
                Size represents market cap. Opens web-browser. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-p",
            "--period",
            action="store",
            dest="s_period",
            type=str,
            default="1d",
            choices=self.map_period_list,
            help="Performance period.",
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="s_type",
            type=str,
            default="sp500",
            choices=self.map_type_list,
            help="Map filter type.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            finviz_view.map_sp500_view(
                period=ns_parser.s_period,
                map_type=ns_parser.s_type,
            )

    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="valuation",
            description="""
                View group (sectors, industry or country) valuation data. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            default="sector",
            nargs="+",
            dest="group",
            help="Data group (sector, industry or country)",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            type=str,
            choices=self.valuation_sort_cols,
            default="Name",
            help="Column to sort by",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            group = (
                " ".join(ns_parser.group)
                if isinstance(ns_parser.group, list)
                else ns_parser.group
            )
            finviz_view.display_valuation(
                s_group=self.d_GROUPS[group],
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )

    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="performance",
            description="""
                View group (sectors, industry or country) performance data. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            default="sector",
            nargs="+",
            dest="group",
            help="Data group (sector, industry or country)",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            choices=self.performance_sort_list,
            default="Name",
            help="Column to sort by",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            group = (
                " ".join(ns_parser.group)
                if isinstance(ns_parser.group, list)
                else ns_parser.group
            )
            finviz_view.display_performance(
                s_group=self.d_GROUPS[group],
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )

    def call_spectrum(self, other_args: List[str]):
        """Process spectrum command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="spectrum",
            description="""
                View group (sectors, industry or country) spectrum data. [Source: Finviz]
            """,
        )
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            default="sector",
            nargs="+",
            dest="group",
            help="Data group (sector, industry or country)",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            group = (
                " ".join(ns_parser.group)
                if isinstance(ns_parser.group, list)
                else ns_parser.group
            )
        finviz_view.display_spectrum(s_group=self.d_GROUPS[group])

        # Due to Finviz implementation of Spectrum, we delete the generated spectrum figure
        # after saving it and displaying it to the user
        os.remove(self.d_GROUPS[group] + ".jpg")

    def call_rtps(self, other_args: List[str]):
        """Process rtps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rtps",
            description="""
                Real-time and historical sector performances calculated from
                S&P500 incumbents. Pops plot in terminal. [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            alphavantage_view.realtime_performance_sector(
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    def call_gdp(self, other_args: List[str]):
        """Process gdp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gdp",
            description="""
                Get real GDP for US on either annual or quarterly interval [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-i",
            "--interval",
            help="Interval for GDP data",
            dest="interval",
            choices=self.gdp_interval,
            default="annual",
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start year.  Quarterly only goes back to 2002.",
            dest="start",
            type=int,
            default=2010,
        )
        parser.add_argument(
            "--raw",
            help="Display raw data",
            action="store_true",
            dest="raw",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            alphavantage_view.display_real_gdp(
                interval=ns_parser.interval[0],
                start_year=ns_parser.start,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    def call_gdpc(self, other_args: List[str]):
        """Process gdpc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gdpc",
            description="""
                Get real GDP per capita for United States[Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start year.",
            dest="start",
            type=int,
            default=2010,
        )
        parser.add_argument(
            "--raw",
            help="Display raw data",
            action="store_true",
            dest="raw",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            alphavantage_view.display_gdp_capita(
                start_year=ns_parser.start,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    def call_inf(self, other_args: List[str]):
        """Process inf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="inf",
            description="""
                Get historical Inflation for United States[Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start year.",
            dest="start",
            type=int,
            default=2010,
        )
        parser.add_argument(
            "--raw",
            help="Display raw data",
            action="store_true",
            dest="raw",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            alphavantage_view.display_inflation(
                start_year=ns_parser.start,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    def call_cpi(self, other_args: List[str]):
        """Process cpi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="inf",
            description="""
                Get historical CPI for United States [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-i",
            "--interval",
            help="Interval for GDP data",
            dest="interval",
            choices=self.cpi_interval,
            default="semiannual",
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start year.",
            dest="start",
            type=int,
            default=2010,
        )
        parser.add_argument(
            "--raw",
            help="Display raw data",
            action="store_true",
            dest="raw",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            alphavantage_view.display_cpi(
                interval=ns_parser.interval[0],
                start_year=ns_parser.start,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    def call_tyld(self, other_args: List[str]):
        """Process tyld command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tyld",
            description="""
                Get historical Treasury Yield [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-i",
            "--interval",
            help="Interval for treasury data",
            dest="interval",
            choices=self.tyld_interval,
            default="weekly",
        )
        parser.add_argument(
            "-m",
            "--maturity",
            help="Maturity timeline for treasury",
            dest="maturity",
            choices=self.tyld_maturity,
            default="5y",
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start date.",
            dest="start",
            type=valid_date,
            default=datetime.now() - timedelta(days=366),
        )
        parser.add_argument(
            "--raw",
            help="Display raw data",
            action="store_true",
            dest="raw",
            default=False,
        )

        if other_args and "-m" not in other_args[0]:
            other_args.insert(0, "-m")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            alphavantage_view.display_treasury_yield(
                interval=ns_parser.interval[0],
                maturity=ns_parser.maturity,
                start_date=ns_parser.start,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    def call_unemp(self, other_args: List[str]):
        """Process unemp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="unemp",
            description="""
                Get United States Unemployment data [Source: Alpha Vantage]
            """,
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start year.",
            dest="start",
            type=int,
            default=2015,
        )
        parser.add_argument(
            "--raw",
            help="Display raw data",
            action="store_true",
            dest="raw",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            alphavantage_view.display_unemployment(
                start_year=ns_parser.start,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    def call_bigmac(self, other_args: List[str]):
        """Process bigmac command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bigmac",
            description="""
                Get historical Big Mac Index [Nasdaq Data Link]
            """,
        )
        parser.add_argument(
            "--codes",
            help="Flag to show all country codes",
            dest="codes",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-c",
            "--countries",
            help="Country codes to get data for.",
            dest="countries",
            default="USA",
            type=nasdaq_model.check_country_code_type,
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            help="Show raw data",
            dest="raw",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.codes:
                file = os.path.join(
                    os.path.dirname(__file__), "NASDAQ_CountryCodes.csv"
                )
                t_console.print(
                    pd.read_csv(file, index_col=0).to_string(index=False), "\n"
                )
            else:
                nasdaq_view.display_big_mac_index(
                    country_codes=ns_parser.countries,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )

    def call_fred(self, _):
        """Process fred command"""
        from gamestonk_terminal.economy.fred.fred_controller import FredController

        self.queue = FredController(self.queue).menu()
