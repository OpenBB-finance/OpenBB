""" Econ Controller """
__docformat__ = "numpy"
# pylint:disable=too-many-lines,R1710,R0904,C0415

import argparse
import logging
import os
from typing import List
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import (
    alphavantage_view,
    cnn_view,
    finviz_view,
    nasdaq_model,
    nasdaq_view,
    wsj_view,
    econdb_view,
    econdb_model,
    yfinance_model,
    yfinance_view,
)

from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    print_rich_table,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


class EconomyController(BaseController):
    """Economy Controller class"""

    CHOICES_COMMANDS = [
        "overview",
        "futures",
        "macro",
        "indices",
        "valuation",
        "performance",
        "spectrum",
        "map",
        "rtps",
        "industry",
        "feargreed",
        "bigmac",
        "resources",
    ]
    CHOICES_MENUS = ["fred"]

    fear_greed_indicators = ["jbd", "mv", "pco", "mm", "sps", "spb", "shd", "index"]
    wsj_sortby_cols_dict = {c: None for c in ["ticker", "last", "change", "prevClose"]}
    map_period_list = ["1d", "1w", "1m", "3m", "6m", "1y"]
    map_type_list = ["sp500", "world", "full", "etf"]
    macro_us_interval = [
        "annual",
        "quarter",
        "semiannual",
        "monthly",
        "weekly",
        "daily",
    ]
    macro_us_types = [
        "GDP",
        "GDPC",
        "INF",
        "CPI",
        "TYLD",
        "UNEMP",
        "gdp",
        "gpdc",
        "inf",
        "cpi",
        "tyld",
        "unemp",
    ]
    overview_options = ["indices", "usbonds", "gbonds", "currencies"]
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
    PATH = "/economy/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["overview"] = {c: None for c in self.overview_options}

            choices["futures"] = {
                c: None for c in ["energy", "metals", "meats", "grains", "softs"]
            }

            choices["indices"] = {c: None for c in yfinance_model.INDICES}

            choices["macro"]["-p"] = {c: None for c in econdb_model.PARAMETERS}
            choices["macro"]["--parameter"] = {c: None for c in econdb_model.PARAMETERS}
            choices["macro"]["-c"] = {c: None for c in econdb_model.COUNTRY_CODES}
            choices["macro"]["--countries"] = {
                c: None for c in econdb_model.COUNTRY_CODES
            }

            choices["valuation"]["-s"] = {c: None for c in self.valuation_sort_cols}
            choices["valuation"]["--sortby"] = {
                c: None for c in self.valuation_sort_cols
            }

            choices["performance"]["-s"] = {c: None for c in self.performance_sort_list}
            choices["performance"]["--sortby"] = {
                c: None for c in self.performance_sort_list
            }

            choices["map"]["-p"] = {c: None for c in self.map_period_list}
            choices["map"]["--period"] = {c: None for c in self.map_period_list}

            choices["feargreed"]["-i"] = {c: None for c in self.fear_greed_indicators}
            choices["feargreed"]["--indicator"] = {
                c: None for c in self.fear_greed_indicators
            }

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[cmds]
Overview
    overview      show a market overview of either indices, bonds or currencies [src][Source: Wall St. Journal][/src]
    futures       display a futures and commodities overview [src][Source: Wall St. Journal / FinViz][/src]
    map           S&P500 index stocks map [src][Source: FinViz][/src]

Macro Data
    macro         collect macro data for a country or countries [src][Source: EconDB][/src]
    indices       show the most important indices worldwide [src][Source: Yahoo Finance][/src]

Performance & Valuations
    rtps          real-time performance sectors [src][Source: Alpha Vantage][/src]
    valuation     valuation of sectors, industry, country [src][Source: FinViz][/src]
    performance   performance of sectors, industry, country [src][Source: FinViz][/src]
    spectrum      spectrum of sectors, industry, country [src][Source: FinViz][/src]

Index
    feargreed     CNN Fear and Greed Index [src][Source: CNN][/src]
    bigmac        the economists Big Mac index [src][Source: NASDAQ Datalink][/src][/cmds]

[menu]
>   fred          Federal Reserve Economic Data submenu[/menu]
"""
        console.print(text=help_text, menu="Economy")

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="""
            Provide a market overview of a variety of options. This can be a general overview, indices,
            bonds and currencies. [Source: Wall St. Journal]
            """,
        )

        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            help="Obtain either US indices, US Bonds, Global Bonds or Currencies",
            type=str,
            choices=self.overview_options,
            default="",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not ns_parser.type:
                wsj_view.display_overview(
                    export=ns_parser.export,
                )
            elif ns_parser.type == "indices":
                wsj_view.display_indices(
                    export=ns_parser.export,
                )
            if ns_parser.type == "usbonds":
                wsj_view.display_usbonds(
                    export=ns_parser.export,
                )
            if ns_parser.type == "gbonds":
                wsj_view.display_glbonds(
                    export=ns_parser.export,
                )
            if ns_parser.type == "currencies":
                wsj_view.display_currencies(
                    export=ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="futures",
            description="Futures/Commodities frrom Wall St. Journal and FinViz.",
        )

        parser.add_argument(
            "-c",
            "--commodity",
            dest="commodity",
            help="Obtain commodity futures from FinViz",
            type=str,
            choices=["energy", "metals", "meats", "grains", "softs"],
            default="",
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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and ns_parser.commodity:
            finviz_view.display_future(
                future_type=ns_parser.commodity.capitalize(),
                sort_col=ns_parser.sort_col,
                ascending=ns_parser.ascend,
                export=ns_parser.export,
            )
        elif ns_parser:
            wsj_view.display_futures(
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_macro(self, other_args: List[str]):
        """Process macro command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="macro",
            description="Get a broad selection of macro data from one or multiple companies. [Source: EconDB]",
        )

        parser.add_argument(
            "-p",
            "--parameters",
            nargs="+",
            dest="parameters",
            help="Abbreviation(s) of the Macro Economic data",
            default=["CPI"],
        )

        parser.add_argument(
            "-sp",
            "--show_parameters",
            dest="show_parameters",
            help="Show all parameters and what they represent",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-c",
            "--countries",
            nargs="+",
            dest="countries",
            help="The country or countries you wish to show data for",
            default=["United_States"],
        )

        parser.add_argument(
            "-sc",
            "--show_countries",
            dest="show_countries",
            help="Show all countries and their currencies",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start_date",
            dest="start_date",
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default=None,
        )

        parser.add_argument(
            "-e",
            "--end_date",
            dest="end_date",
            help="The end date of the data (format: YEAR-MONTH-DAY, i.e. 2021-06-20)",
            default=None,
        )

        parser.add_argument(
            "-cc",
            "--convert_currency",
            dest="convert_currency",
            help="Convert the currency of the chosen country to a specified currency. By default, this will be USD "
            "unless specified with this command. To find the currencies use the option -sc",
            default="USD",
        )

        parser.add_argument(
            "-r",
            "--raw",
            dest="raw",
            help="Show raw data",
            action="store_true",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.show_parameters:
                print_rich_table(
                    pd.DataFrame(econdb_model.PARAMETERS.items()),
                    show_index=False,
                    headers=["Parameter", "Description"],
                )
            elif ns_parser.show_countries:
                print_rich_table(
                    pd.DataFrame(econdb_model.COUNTRY_CURRENCIES.items()),
                    show_index=False,
                    headers=["Country", "Currency"],
                )
            elif ns_parser.parameters and ns_parser.countries:
                econdb_view.show_data(
                    parameters=ns_parser.parameters,
                    countries=ns_parser.countries,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    convert_currency=ns_parser.convert_currency,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_indices(self, other_args: List[str]):
        """Process indices command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="indices",
            description="Obtain any set of indices and plot them together. With the -si argument the major indices are "
            "shown. By using the arguments (for example 'nasdaq' and 'sp500') you can collect data and "
            "plot the graphs together. [Source: Yahoo finance / FinanceDatabase]",
        )

        parser.add_argument(
            "-i",
            "--indices",
            nargs="+",
            dest="indices",
            help="One or multiple indices",
        )

        parser.add_argument(
            "-si",
            "--show_indices",
            dest="show_indices",
            help="Show the major indices, their arguments and ticker",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-iv",
            "--interval",
            type=str,
            dest="interval",
            help="The preferred interval data is shown at. This can be 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, "
            "1d, 5d, 1wk, 1mo or 3mo",
            choices=[
                "1m",
                "2m",
                "5m",
                "15m",
                "30m",
                "60m",
                "90m",
                "1h",
                "1d",
                "5d",
                "1wk",
                "1mo",
                "3mo",
            ],
            default="1d",
        )

        parser.add_argument(
            "-s",
            "--start_date",
            dest="start_date",
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default="2000-01-01",
        )

        parser.add_argument(
            "-e",
            "--end_date",
            dest="end_date",
            help="The end date of the data (format: YEAR-MONTH-DAY, i.e. 2021-06-20)",
            default=None,
        )

        parser.add_argument(
            "-c",
            "--column",
            type=str,
            dest="column",
            help="The column you wish to load in, by default this is the Adjusted Close column",
            default="Adj Close",
        )

        parser.add_argument(
            "-q",
            "--query",
            type=str,
            nargs="+",
            dest="query",
            help="Search for indices with given keyword",
        )

        parser.add_argument(
            "-l",
            "--limit",
            type=str,
            dest="limit",
            help="Takes into account the amount of rows you wish to see for your query ('-q').",
            default=10,
        )

        parser.add_argument(
            "-r",
            "--raw",
            dest="raw",
            help="Show raw data",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.query and ns_parser.limit:
                yfinance_view.search_indices(ns_parser.query, ns_parser.limit)
            if ns_parser.show_indices:
                print_rich_table(
                    pd.DataFrame.from_dict(yfinance_model.INDICES, orient="index"),
                    show_index=True,
                    index_name="Argument",
                    headers=["Name", "Ticker"],
                    title="Major Indices",
                )
            elif ns_parser.indices:
                yfinance_view.show_indices(
                    indices=ns_parser.indices,
                    interval=ns_parser.interval,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    column=ns_parser.column,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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
                console.print(
                    pd.read_csv(file, index_col=0).to_string(index=False), "\n"
                )
            else:
                nasdaq_view.display_big_mac_index(
                    country_codes=ns_parser.countries,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_fred(self, _):
        """Process fred command"""
        from gamestonk_terminal.economy.fred.fred_controller import FredController

        self.queue = self.load_class(FredController, self.queue)
