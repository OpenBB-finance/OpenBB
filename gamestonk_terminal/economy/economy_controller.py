""" Econ Controller """
__docformat__ = "numpy"
# pylint:disable=too-many-lines
import argparse
import difflib
from datetime import datetime, timedelta
import os
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import (
    alphavantage_view,
    cnn_view,
    finnhub_view,
    finviz_view,
    fred_view,
    nasdaq_model,
    wsj_view,
    nasdaq_view,
)
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    valid_date,
    MENU_GO_BACK,
    MENU_QUIT,
    MENU_RESET,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session

# pylint: disable=R1710,R0904


class EconomyController:
    """Economy Controller"""

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

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "reset",
    ]

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
        "search",
        "series",
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

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.econ_parser = argparse.ArgumentParser(add_help=False, prog="economy")
        self.econ_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """
What do you want to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program
    reset         reset terminal and reload configs

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
FRED:
    search        search FRED series notes
    series        plot series from https://fred.stlouisfed.org
NASDAQ DataLink (formerly Quandl):
    bigmac        the economists Big Mac index
"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        MENU_GO_BACK, MENU_QUIT, MENU_RESET
            MENU_GO_BACK - Show main context menu again
            MENU_QUIT - Quit terminal
            MENU_RESET - Reset terminal and go back to same previous menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.econ_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return MENU_GO_BACK

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return MENU_QUIT

    def call_reset(self, _):
        """Process Reset command - reset the program"""
        return MENU_RESET

    @try_except
    def call_events(self, other_args: List[str]):
        """Process events command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="events",
            description="""
                Output economy impact calendar impact events. [Source: Finnhub]
            """,
        )
        parser.add_argument(
            "-c",
            "--country",
            action="store",
            dest="country",
            type=str,
            default="US",
            choices=["NZ", "AU", "ERL", "CA", "EU", "US", "JP", "CN", "GB", "CH"],
            help="Country from where to get economy calendar impact events",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="Number economy calendar impact events to display",
        )
        parser.add_argument(
            "-i",
            "--impact",
            action="store",
            dest="impact",
            type=str,
            default="all",
            choices=["low", "medium", "high", "all"],
            help="Impact of the economy event",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finnhub_view.economy_calendar_events(
            country=ns_parser.country,
            num=ns_parser.num,
            impact=ns_parser.impact,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["jbd", "mv", "pco", "mm", "sps", "spb", "shd", "index"],
            help="""
                CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
                Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
                Safe Heaven Demand, and Index.
            """,
        )
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        cnn_view.fear_and_greed_index(
            indicator=ns_parser.indicator,
            export=ns_parser.export,
        )

    @try_except
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="Market overview. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        wsj_view.display_overview(
            export=ns_parser.export,
        )

    @try_except
    def call_indices(self, other_args: List[str]):
        """Process indices command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="indices",
            description="US indices. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        wsj_view.display_indices(
            export=ns_parser.export,
        )

    @try_except
    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="futures",
            description="Futures/Commodities. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        wsj_view.display_futures(
            export=ns_parser.export,
        )

    @try_except
    def call_usbonds(self, other_args: List[str]):
        """Process usbonds command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="usbonds",
            description="US Bonds. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        wsj_view.display_usbonds(
            export=ns_parser.export,
        )

    @try_except
    def call_glbonds(self, other_args: List[str]):
        """Process glbonds command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="glbonds",
            description="Global Bonds. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        wsj_view.display_glbonds(
            export=ns_parser.export,
        )

    @try_except
    def call_currencies(self, other_args: List[str]):
        """Process currencies command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="currencies",
            description="Currencies. [Source: Wall St. Journal]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        wsj_view.display_currencies(
            export=ns_parser.export,
        )

    @try_except
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
            choices=["ticker", "last", "change", "prevClose"],
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finviz_view.display_future(
            future_type="Energy",
            sort_col=ns_parser.sort_col,
            ascending=ns_parser.ascend,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["ticker", "last", "change", "prevClose"],
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finviz_view.display_future(
            future_type="Metals",
            sort_col=ns_parser.sort_col,
            ascending=ns_parser.ascend,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["ticker", "last", "change", "prevClose"],
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finviz_view.display_future(
            future_type="Meats",
            sort_col=ns_parser.sort_col,
            ascending=ns_parser.ascend,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["ticker", "last", "change", "prevClose"],
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finviz_view.display_future(
            future_type="Grains",
            sort_col=ns_parser.sort_col,
            ascending=ns_parser.ascend,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["ticker", "last", "change", "prevClose"],
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finviz_view.display_future(
            future_type="Softs",
            sort_col=ns_parser.sort_col,
            ascending=ns_parser.ascend,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["1d", "1w", "1m", "3m", "6m", "1y"],
            help="Performance period.",
        )
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="s_type",
            type=str,
            default="sp500",
            choices=["sp500", "world", "full", "etf"],
            help="Map filter type.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finviz_view.map_sp500_view(
            period=ns_parser.s_period,
            map_type=ns_parser.s_type,
        )

    @try_except
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
            choices=[
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
            ],
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

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

    @try_except
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
            choices=[
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
            ],
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
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

    @try_except
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
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        group = (
            " ".join(ns_parser.group)
            if isinstance(ns_parser.group, list)
            else ns_parser.group
        )
        finviz_view.display_spectrum(s_group=self.d_GROUPS[group])

        # Due to Finviz implementation of Spectrum, we delete the generated spectrum figure
        # after saving it and displaying it to the user
        os.remove(self.d_GROUPS[group] + ".jpg")

    @try_except
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
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"]
            if "--raw" in other_args
            else ["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export data to csv,json,xlsx or png,jpg,pdf,svg file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        alphavantage_view.realtime_performance_sector(
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["a", "q"],
            default="a",
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
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if not ns_parser:
            return

        alphavantage_view.display_real_gdp(
            interval=ns_parser.interval,
            start_year=ns_parser.start,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
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

        if not ns_parser:
            return

        alphavantage_view.display_gdp_capita(
            start_year=ns_parser.start,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
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

        if not ns_parser:
            return

        alphavantage_view.display_inflation(
            start_year=ns_parser.start,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["s", "m"],
            default="s",
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

        if not ns_parser:
            return

        alphavantage_view.display_cpi(
            interval=ns_parser.interval,
            start_year=ns_parser.start,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
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
            choices=["d", "w", "m"],
            default="w",
        )
        parser.add_argument(
            "-m",
            "--maturity",
            help="Maturity timeline for treasury",
            dest="maturity",
            choices=["3m", "5y", "10y", "30y"],
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

        if not ns_parser:
            return

        alphavantage_view.display_treasury_yield(
            interval=ns_parser.interval,
            maturity=ns_parser.maturity,
            start_date=ns_parser.start,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
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

        if not ns_parser:
            return

        alphavantage_view.display_unemployment(
            start_year=ns_parser.start,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
    def call_series(self, other_args: List[str]):
        """Process series command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="series",
            description="""
                Display (multiple) series from https://fred.stlouisfed.org. [Source: FRED]
            """,
        )
        parser.add_argument(
            "-i",
            "--id",
            dest="series_id",
            required="-h" not in other_args,
            type=str,
            help="FRED Series from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3",
        )
        parser.add_argument(
            "-s",
            dest="start_date",
            type=valid_date,
            default="2019-01-01",
            help="Starting date (YYYY-MM-DD) of data",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"]
            if "--raw" in other_args
            else ["png", "jpg", "pdf", "svg"],
            default="",
            type=str,
            dest="export",
            help="Export data to csv,json,xlsx or png,jpg,pdf,svg file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        fred_view.display_series(
            series=ns_parser.series_id,
            start_date=ns_parser.start_date,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
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
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        fred_view.notes(
            series_term=ns_parser.series_term,
            num=ns_parser.num,
        )

    @try_except
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
        if not ns_parser:
            return

        if ns_parser.codes:
            file = os.path.join(os.path.dirname(__file__), "NASDAQ_CountryCodes.csv")
            print(pd.read_csv(file, index_col=0).to_string(index=False), "\n")
            return

        nasdaq_view.display_big_mac_index(
            country_codes=ns_parser.countries,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )


def menu():
    """Econ Menu"""

    econ_controller = EconomyController()
    econ_controller.print_help()

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in econ_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (economy)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (economy)> ")
        try:
            process_input = econ_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, econ_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
