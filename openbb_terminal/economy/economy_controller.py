""" Econ Controller """
__docformat__ = "numpy"
# pylint:disable=too-many-lines,R1710,R0904,C0415,too-many-branches

import argparse
import logging
import os
from datetime import date
from typing import List, Dict, Any

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal.decorators import check_api_key
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import (
    alphavantage_view,
    finviz_view,
    nasdaq_model,
    nasdaq_view,
    wsj_view,
    econdb_view,
    econdb_model,
    fred_view,
    fred_model,
    yfinance_model,
    yfinance_view,
    investingcom_model,
    investingcom_view,
    plot_view,
)
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    print_rich_table,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


class EconomyController(BaseController):
    """Economy Controller class"""

    CHOICES_COMMANDS = [
        "overview",
        "futures",
        "macro",
        "fred",
        "index",
        "treasury",
        "plot",
        "options",
        "valuation",
        "performance",
        "spectrum",
        "map",
        "rtps",
        "industry",
        "bigmac",
        "ycrv",
    ]

    CHOICES_MENUS = ["pred", "qa"]

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
    overview_options = ["indices", "usbonds", "glbonds", "currencies"]
    futures_options = ["energy", "metals", "meats", "grains", "softs"]
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
    ycrv_sources = ["FRED", "investpy"]
    PATH = "/economy/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.current_series: Dict = dict()
        self.fred_query: pd.Series = pd.Series()
        self.DATASETS: Dict[Any, pd.DataFrame] = dict()
        self.UNITS: Dict[Any, Dict[Any, Any]] = dict()
        self.FRED_TITLES: Dict = dict()

        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices: dict = {c: {} for c in self.controller_choices}
            self.choices["overview"] = {c: None for c in self.overview_options}

            self.choices["futures"] = {c: None for c in self.futures_options}

            self.choices["index"] = {c: None for c in yfinance_model.INDICES}

            self.choices["macro"]["-p"] = {c: None for c in econdb_model.PARAMETERS}
            self.choices["macro"]["--parameter"] = {
                c: None for c in econdb_model.PARAMETERS
            }
            self.choices["macro"]["-c"] = {c: None for c in econdb_model.COUNTRY_CODES}
            self.choices["macro"]["--countries"] = {
                c: None for c in econdb_model.COUNTRY_CODES
            }

            self.choices["ycrv"]["-c"] = {c: None for c in investingcom_model.COUNTRIES}
            self.choices["ycrv"]["--countries"] = {
                c: None for c in investingcom_model.COUNTRIES
            }

            self.choices["valuation"]["-s"] = {
                c: None for c in self.valuation_sort_cols
            }
            self.choices["valuation"]["--sortby"] = {
                c: None for c in self.valuation_sort_cols
            }

            self.choices["performance"]["-s"] = {
                c: None for c in self.performance_sort_list
            }
            self.choices["performance"]["--sortby"] = {
                c: None for c in self.performance_sort_list
            }

            self.choices["map"]["-p"] = {c: None for c in self.map_period_list}
            self.choices["map"]["--period"] = {c: None for c in self.map_period_list}

            self.choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def update_runtime_choices(self):
        if session and obbff.USE_PROMPT_TOOLKIT:
            if not self.fred_query.empty:
                self.choices["fred"] = {c: None for c in self.fred_query}
            if self.DATASETS:
                options = [
                    option
                    for _, values in self.DATASETS.items()
                    for option in values.keys()
                ]

                for argument in ["-y1", "--yaxis1", "-y2", "--yaxis2"]:
                    self.choices["plot"][argument] = {
                        option: None for option in options
                    }

        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        help_text = """[cmds]
[info]Overview[/info]
    overview         show a market overview of either indices, bonds or currencies [src][Source: Wall St. Journal][/src]
    futures          display a futures and commodities overview [src][Source: Wall St. Journal / FinViz][/src]
    map              S&P500 index stocks map [src][Source: FinViz][/src]
    bigmac           The Economist Big Mac index [src][Source: NASDAQ Datalink][/src]

[info]Macro Data[/info]
    macro            collect macro data for a country or countries [src][Source: EconDB][/src]
    fred             collect macro data from FRED based on a series ID [src][Source: FRED][/src]
    index            find and plot any (major) index on the market [src][Source: Yahoo Finance][/src]
    treasury         obtain U.S. treasury rates [src][Source: EconDB][/src]
    ycrv             show sovereign yield curves [src][Source: Investing.com/FRED][/src]
    plot             plot data from the above commands together
    options          show the available options for 'plot' or show/export the data

[info]Performance & Valuations[/info]
    rtps             real-time performance sectors [src][Source: Alpha Vantage][/src]
    valuation        valuation of sectors, industry, country [src][Source: FinViz][/src]
    performance      performance of sectors, industry, country [src][Source: FinViz][/src]
    spectrum         spectrum of sectors, industry, country [src][Source: FinViz][/src][/cmds]
[menu]
>   pred             Open the prediction menu to analyse stored data
>   qa               Open quantitative analysis menu with stored data[/menu]
"""
        console.print(text=help_text, menu="Economy")

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
            if ns_parser.type == "glbonds":
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
            description="Futures/Commodities from Wall St. Journal and FinViz.",
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

        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
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
    def call_macro(self, other_args: List[str]):
        """Process macro command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="macro",
            description="Get a broad selection of macro data from one or multiple countries. This includes Gross "
            "Domestic Product (RGDP & GDP) and the underlying components, Treasury Yields (Y10YD & M3YD), "
            "Employment figures (URATE, EMP, AC0I0 and EMRATIO), Government components (e.g. GBAL & GREV), "
            "Consumer and Producer Indices (CPI & PPI) and a variety of other indicators. [Source: EconDB]",
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
            "-c",
            "--countries",
            nargs="+",
            dest="countries",
            help="The country or countries you wish to show data for",
            default=["United_States"],
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
            help="Convert the currency of the chosen country to a specified currency. To find the "
            "currency symbols use the argument -sc",
            default=False,
        )

        parser.add_argument(
            "-st",
            "--store",
            dest="store",
            help="Store the data to be used for plotting with the 'plot' command.",
            action="store_true",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, raw=True
        )
        if ns_parser:
            if ns_parser.show_parameters:
                print_rich_table(
                    pd.DataFrame.from_dict(econdb_model.PARAMETERS, orient="index"),
                    show_index=True,
                    index_name="Parameter",
                    headers=["Name", "Period", "Description"],
                )
            elif ns_parser.show_countries:
                print_rich_table(
                    pd.DataFrame(econdb_model.COUNTRY_CURRENCIES.items()),
                    show_index=False,
                    headers=["Country", "Currency"],
                )
            elif ns_parser.parameters and ns_parser.countries:
                if ns_parser.store:
                    (
                        self.DATASETS["macro"],
                        self.UNITS,
                    ) = econdb_model.get_aggregated_macro_data(
                        parameters=ns_parser.parameters,
                        countries=ns_parser.countries,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                        convert_currency=ns_parser.convert_currency,
                    )

                    self.DATASETS["macro"].columns = [
                        "_".join(column) for column in self.DATASETS["macro"].columns
                    ]
                else:
                    econdb_view.show_macro_data(
                        parameters=ns_parser.parameters,
                        countries=ns_parser.countries,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                        convert_currency=ns_parser.convert_currency,
                        raw=ns_parser.raw,
                        export=ns_parser.export,
                    )

                self.update_runtime_choices()

    @check_api_key(["API_FRED_KEY"])
    def call_fred(self, other_args: List[str]):
        """Process fred command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fred",
            description="Query the FRED database and plot data based on the Series ID. [Source: FRED]",
        )

        parser.add_argument(
            "-p",
            "--parameter",
            nargs="+",
            dest="parameter",
            help="Series ID of the Macro Economic data from FRED",
        )

        parser.add_argument(
            "-s",
            "--start_date",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )

        parser.add_argument(
            "-e",
            "--end_date",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )

        parser.add_argument(
            "-q",
            "--query",
            nargs="+",
            action="store",
            dest="query",
            help="Query the FRED database to obtain Series IDs given the query seaarch term.",
        )

        parser.add_argument(
            "-st",
            "--store",
            dest="store",
            help="Store the data to be used for plotting with the 'plot' command.",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=5,
        )
        if ns_parser:
            if ns_parser.query:
                query = " ".join(ns_parser.query)
                df_search = fred_model.get_series_notes(query)

                if not df_search.empty:
                    fred_view.notes(series_term=query, num=ns_parser.limit)

                    self.fred_query = df_search["id"].head(ns_parser.limit)
                    self.update_runtime_choices()

            if ns_parser.parameter:
                series_dict = {}
                for series in ns_parser.parameter:
                    information = fred_model.check_series_id(series)

                    if "seriess" in information:
                        series_dict[series] = {
                            "title": information["seriess"][0]["title"],
                            "units": information["seriess"][0]["units_short"],
                        }

                        self.current_series = {series: series_dict[series]}

                if ns_parser.store:
                    for series_id, data in series_dict.items():
                        self.FRED_TITLES[
                            series_id
                        ] = f"{data['title']} ({data['units']})"

                    self.DATASETS["fred"] = fred_model.get_aggregated_series_data(
                        series_dict, ns_parser.start_date, ns_parser.end_date
                    )
                else:
                    fred_view.display_fred_series(
                        d_series=series_dict,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                        raw=ns_parser.raw,
                        export=ns_parser.export,
                        limit=ns_parser.limit,
                    )

                self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_index(self, other_args: List[str]):
        """Process index command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="index",
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
            "-st",
            "--store",
            dest="store",
            help="Store the data to be used for plotting with the 'plot' command.",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-r",
            "--returns",
            help="Flag to show compounded returns over interval.",
            dest="returns",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
            limit=10,
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
                if ns_parser.store:
                    self.DATASETS["index"] = pd.DataFrame()
                    for index in ns_parser.indices:
                        self.DATASETS["index"][index] = yfinance_model.get_index(
                            index,
                            interval=ns_parser.interval,
                            start_date=ns_parser.start_date,
                            end_date=ns_parser.end_date,
                            column=ns_parser.column,
                        )
                else:
                    yfinance_view.show_indices(
                        indices=ns_parser.indices,
                        interval=ns_parser.interval,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                        column=ns_parser.column,
                        store=ns_parser.store,
                        raw=ns_parser.raw,
                        export=ns_parser.export,
                        returns=ns_parser.returns,
                    )

                self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_treasury(self, other_args: List[str]):
        """Process treasury command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="treasury",
            description="Obtain any set of U.S. treasuries and plot them together. These can be a range of maturities "
            "for nominal, inflation-adjusted (on long term average of inflation adjusted) and secondary "
            "markets over a lengthy period. Note: 3-month and 10-year treasury yields for other countries "
            "are available via the command 'macro' and parameter 'M3YD' and 'Y10YD'. [Source: EconDB / FED]",
        )

        parser.add_argument(
            "-m",
            "--maturity",
            nargs="+",
            type=str,
            dest="maturity",
            help="The preferred maturity which is dependent on the type of the treasury",
            default=["1y"],
        )

        parser.add_argument(
            "-sm",
            "--show_maturities",
            dest="show_maturities",
            help="Show the maturities available for every instrument.",
            action="store_true",
            default=False,
        )

        parser.add_argument(
            "-f",
            "--frequency",
            type=str,
            dest="frequency",
            choices=econdb_model.TREASURIES["frequencies"],
            help="The frequency, this can be annually, monthly, weekly or daily",
            default="monthly",
        )

        parser.add_argument(
            "-t",
            "--type",
            nargs="+",
            type=str,
            dest="type",
            choices=econdb_model.TREASURIES["instruments"],
            help="Whether to select nominal, inflation indexed, average inflation indexed or "
            "secondary market treasury rates",
            default=["nominal"],
        )

        parser.add_argument(
            "-s",
            "--start_date",
            dest="start_date",
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default="1934-01-31",
        )

        parser.add_argument(
            "-e",
            "--end_date",
            dest="end_date",
            help="The end date of the data (format: YEAR-DAY-MONTH, i.e. 2021-06-02)",
            default=date.today(),
        )

        parser.add_argument(
            "-st",
            "--store",
            dest="store",
            help="Store the data to be used for plotting with the 'plot' command.",
            action="store_true",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-m")
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
            limit=10,
        )

        if ns_parser:
            if ns_parser.show_maturities:
                econdb_view.show_treasury_maturities(econdb_model.TREASURIES)
            elif ns_parser.maturity and ns_parser.type:
                if ns_parser.store:
                    treasury_data = econdb_model.get_treasuries(
                        instruments=ns_parser.type,
                        maturities=ns_parser.maturity,
                        frequency=ns_parser.frequency,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                    )

                    df = (
                        pd.DataFrame.from_dict(treasury_data, orient="index")
                        .stack()
                        .to_frame()
                    )
                    self.DATASETS["treasury"] = pd.DataFrame(
                        df[0].values.tolist(), index=df.index
                    ).T
                    self.DATASETS["treasury"].columns = [
                        "_".join(column) for column in self.DATASETS["treasury"].columns
                    ]
                else:
                    econdb_view.show_treasuries(
                        types=ns_parser.type,
                        maturities=ns_parser.maturity,
                        frequency=ns_parser.frequency,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                        raw=ns_parser.raw,
                        export=ns_parser.export,
                    )

            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_ycrv(self, other_args: List[str]):
        """Process ycrv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ycrv",
            description="Generate country yield curve. The yield curve shows the bond rates"
            " at different maturities.",
        )
        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="source",
            choices=self.ycrv_sources,
            type=str,
            default="investpy",
            help="Source for the data. If not supplied, the most recent entry from investpy will be used.",
        )
        parser.add_argument(
            "-c",
            "--country",
            action="store",
            dest="country",
            nargs="+",
            default="united states",
            help="Display yield curve for specific country.",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=valid_date,
            help="Date to get data from FRED. If not supplied, the most recent entry will be used.",
            dest="date",
            default=None,
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            if isinstance(ns_parser.country, list):
                ns_parser.country = " ".join(ns_parser.country)

            investingcom_model.check_correct_country(ns_parser.country)

            if ns_parser.source == "FRED":
                fred_view.display_yield_curve(ns_parser.date)
            elif ns_parser.source == "investpy":
                investingcom_view.display_yieldcurve(
                    country=ns_parser.country,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="This command can plot any data on two y-axes obtained from the macro, fred, index and "
            "treasury commands. To be able to use this data, use the -st argument available within these "
            "commands. For example 'macro -p GDP -c Germany Netherlands -st' will store the data for usage "
            "in this command. Therefore, it allows you to plot different time series in one graph. You can use "
            "the 'options' command to show the required arguments to be entered. The example above could be plotted "
            "the following way: 'plot -y1 Germany_GDP -y2 Netherlands_GDP' or 'plot -y1 Germany_GDP Netherlands_GDP'",
        )

        parser.add_argument(
            "-y1",
            "--yaxis1",
            nargs="+",
            dest="yaxis1",
            help="Select the data you wish to plot on the first y-axis. You can select multiple variables here.",
            default="",
        )

        parser.add_argument(
            "-y2",
            "--yaxis2",
            nargs="+",
            dest="yaxis2",
            help="Select the data you wish to plot on the second y-axis. You can select multiple variables here.",
            default="",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-y1")
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
            limit=10,
        )

        if ns_parser:
            if not self.DATASETS:
                console.print(
                    "There is no data stored yet. Please use either the 'macro', 'fred', 'index' and/or "
                    "'treasury' command in combination with the -st argument to be able to plot data."
                )
            else:
                dataset_yaxis1 = pd.DataFrame()
                dataset_yaxis2 = pd.DataFrame()

                if ns_parser.yaxis1:
                    for variable in ns_parser.yaxis1:
                        for key, data in self.DATASETS.items():
                            if variable in data.columns:
                                if key == "macro":
                                    split = variable.split("_")
                                    if len(split) == 2:
                                        country, parameter_abbreviation = split
                                    else:
                                        country = f"{split[0]} {split[1]}"
                                        parameter_abbreviation = split[2]

                                    parameter = econdb_model.PARAMETERS[
                                        parameter_abbreviation
                                    ]["name"]
                                    units = self.UNITS[country.replace(" ", "_")][
                                        parameter_abbreviation
                                    ]
                                    dataset_yaxis1[
                                        f"{country} [{parameter}, Units: {units}]"
                                    ] = data[variable]
                                elif key == "fred":
                                    dataset_yaxis1[self.FRED_TITLES[variable]] = data[
                                        variable
                                    ]
                                elif (
                                    key == "index"
                                    and variable in yfinance_model.INDICES
                                ):
                                    dataset_yaxis1[
                                        yfinance_model.INDICES[variable]["name"]
                                    ] = data[variable]
                                elif key == "treasury":
                                    parameter, maturity = variable.split("_")
                                    dataset_yaxis1[f"{parameter} [{maturity}]"] = data[
                                        variable
                                    ]
                                else:
                                    dataset_yaxis1[variable] = data[variable]
                                break
                    if dataset_yaxis1.empty:
                        return console.print(
                            f"Not able to find any data for the -y1 argument. The currently available "
                            f"options are: {', '.join(self.choices['plot']['-y1'])}"
                        )

                if ns_parser.yaxis2:
                    for variable in ns_parser.yaxis2:
                        for key, data in self.DATASETS.items():
                            if variable in data.columns:
                                if key == "macro":
                                    split = variable.split("_")
                                    if len(split) == 2:
                                        country, parameter_abbreviation = split
                                    else:
                                        country = f"{split[0]} {split[1]}"
                                        parameter_abbreviation = split[2]

                                    parameter = econdb_model.PARAMETERS[
                                        parameter_abbreviation
                                    ]["name"]
                                    units = self.UNITS[country.replace(" ", "_")][
                                        parameter_abbreviation
                                    ]
                                    dataset_yaxis2[
                                        f"{country} [{parameter}, Units: {units}]"
                                    ] = data[variable]
                                elif key == "fred":
                                    dataset_yaxis2[self.FRED_TITLES[variable]] = data[
                                        variable
                                    ]
                                elif (
                                    key == "index"
                                    and variable in yfinance_model.INDICES
                                ):
                                    dataset_yaxis2[
                                        yfinance_model.INDICES[variable]["name"]
                                    ] = data[variable]
                                elif key == "treasury":
                                    parameter, maturity = variable.split("_")
                                    dataset_yaxis2[f"{parameter} [{maturity}]"] = data[
                                        variable
                                    ]
                                else:
                                    dataset_yaxis2[variable] = data[variable]
                                break
                    if dataset_yaxis2.empty:
                        return console.print(
                            f"Not able to find any data for the -y2 argument. The currently available "
                            f"options are: {', '.join(self.choices['plot']['-y2'])}"
                        )

                if ns_parser.yaxis1 or ns_parser.yaxis2:
                    return plot_view.show_plot(
                        dataset_yaxis_1=dataset_yaxis1,
                        dataset_yaxis_2=dataset_yaxis2,
                        export=ns_parser.export,
                    )

            console.print()

    @log_start_end(log=logger)
    def call_options(self, other_args: List[str]):
        """Process options command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="options",
            description="Show the available options for the 'plot' command. To save data, use the command -st on "
            "'macro', 'fred', 'index' and 'treasury'. You can use these commands to plot data on a multi-"
            "axes graph. Furthermore, this command also allows you to see and export all stored data.",
        )

        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
            limit=10,
        )

        if ns_parser:
            if not self.DATASETS:
                console.print(
                    "There is no data stored yet. Please use either the 'macro', 'fred', 'index' and/or "
                    "'treasury' command in combination with the -st argument to be able to plot data."
                )
            else:
                plot_view.show_options(
                    datasets=self.DATASETS,
                    raw=ns_parser.raw,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                )

            console.print()

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

        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            alphavantage_view.realtime_performance_sector(
                raw=ns_parser.raw,
                export=ns_parser.export,
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
    def call_pred(self, _):
        """Process pred command"""
        if not self.DATASETS:
            console.print(
                "There is no data stored yet. Please use either the 'macro', 'fred', 'index' and/or "
                "'treasury' command in combination with the -st argument to be able to plot data.\n"
            )
            return

        from openbb_terminal.economy.prediction.pred_controller import (
            PredictionTechniquesController,
        )

        self.queue = self.load_class(
            PredictionTechniquesController, self.DATASETS, self.queue
        )

    @log_start_end(log=logger)
    def call_qa(self, _):
        """Process pred command"""
        if not self.DATASETS:
            console.print(
                "There is no data stored yet. Please use either the 'macro', 'fred', 'index' and/or "
                "'treasury' command in combination with the -st argument to be able to plot data.\n"
            )
            return

        from openbb_terminal.economy.quantitative_analysis.qa_controller import (
            QaController,
        )

        self.queue = self.load_class(QaController, self.DATASETS, self.queue)
