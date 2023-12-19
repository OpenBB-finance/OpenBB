""" Econ Controller """
__docformat__ = "numpy"
# pylint: disable=C0302 ,R1710,R0904,C0415,too-many-branches,unnecessary-dict-index-lookup

import argparse
import itertools
import logging
import os
from datetime import (
    date,
    datetime as dt,
)
from typing import Any, Dict, List, Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.economy import (
    commodity_view,
    econdb_model,
    econdb_view,
    economy_helpers,
    fedreserve_model,
    fedreserve_view,
    finviz_model,
    finviz_view,
    fred_model,
    fred_view,
    nasdaq_model,
    nasdaq_view,
    oecd_model,
    oecd_view,
    plot_view,
    wsj_view,
    yfinance_model,
    yfinance_view,
)
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    list_from_str,
    parse_and_split_input,
    print_rich_table,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class EconomyController(BaseController):
    """Economy Controller class"""

    CHOICES_COMMANDS = [
        "eval",
        "overview",
        "futures",
        "gdp",
        "rgdp",
        "fgdp",
        "debt",
        "cpi",
        "ccpi",
        "balance",
        "revenue",
        "spending",
        "trust",
        "macro",
        "fred",
        "index",
        "treasury",
        "plot",
        "valuation",
        "performance",
        "map",
        "bigmac",
        "events",
        "edebt",
        "usdli",
    ]

    CHOICES_MENUS = [
        "qa",
    ]

    wsj_sortby_cols_dict = {c: None for c in ["ticker", "last", "change", "prevClose"]}
    map_period_list = ["1d", "1w", "1m", "3m", "6m", "1y"]
    map_filter_list = ["sp500", "world", "full", "etf"]
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
    tyld_maturity = ["3m", "5y", "10y", "30y"]
    valuation_sort_cols_dict = {
        "Name": "Name",
        "MarketCap": "Market Cap",
        "P/E": "P/E",
        "FwdP/E": "Fwd P/E",
        "PEG": "PEG",
        "P/S": "P/S",
        "P/B": "P/B",
        "P/C": "P/C",
        "P/FCF": "P/FCF",
        "EPSpast5Y": "EPS past 5Y",
        "EPSnext5Y": "EPS next 5Y",
        "Salespast5Y": "Sales past 5Y",
        "Change": "Change",
        "Volume": "Volume",
    }
    performance_sort_dict = {
        "Name": "Name",
        "1W": "1W",
        "1M": "1M",
        "3M": "3M",
        "6M": "6M",
        "1Y": "1Y",
        "YTD": "YTD",
        "Recom": "Recom",
        "AvgVolume": "Avg Volume",
        "RelVolume": "Rel Volume",
        "Change": "Change",
        "Volume": "Volume",
    }
    index_interval = [
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
    ]
    futures_commodities = ["energy", "metals", "meats", "grains", "softs"]
    macro_show = ["parameters", "countries", "transform"]
    d_GROUPS = finviz_model.GROUPS
    PATH = "/economy/"

    stored_datasets = ""

    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.current_series: Dict = dict()
        self.fred_query: pd.Series = pd.Series(dtype=float)
        self.DATASETS: Dict[Any, pd.DataFrame] = dict()
        self.UNITS: Dict[Any, Dict[Any, Any]] = dict()
        self.FRED_TITLES: Dict = dict()
        self.choices: Dict = dict()

        self.DATASETS["macro"] = pd.DataFrame()
        self.DATASETS["treasury"] = pd.DataFrame()
        self.DATASETS["fred"] = pd.DataFrame()
        self.DATASETS["index"] = pd.DataFrame()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            # This is still needed because we can't use choices and nargs separated by comma
            choices["gdp"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_GDP
            }
            choices["gdp"]["-c"] = "--countries"

            choices["rgdp"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_RGDP
            }
            choices["rgdp"]["-c"] = "--countries"

            choices["fgdp"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_GDP_FORECAST
            }
            choices["fgdp"]["-c"] = "--countries"

            choices["debt"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_DEBT
            }
            choices["debt"]["-c"] = "--countries"

            choices["cpi"]["--countries"] = {c: None for c in fred_model.CPI_COUNTRIES}
            choices["cpi"]["-c"] = "--countries"

            choices["ccpi"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_CPI
            }
            choices["ccpi"]["-c"] = "--countries"

            choices["balance"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_BALANCE
            }
            choices["balance"]["-c"] = "--countries"

            choices["revenue"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_REVENUE
            }
            choices["revenue"]["-c"] = "--countries"

            choices["spending"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_SPENDING
            }
            choices["spending"]["-c"] = "--countries"

            choices["trust"]["--countries"] = {
                c: {} for c in oecd_model.COUNTRY_TO_CODE_TRUST
            }
            choices["trust"]["-c"] = "--countries"

            choices["macro"]["--parameters"] = {c: {} for c in econdb_model.PARAMETERS}
            choices["macro"]["-p"] = "--parameters"
            choices["macro"]["--countries"] = {
                c: {} for c in econdb_model.COUNTRY_CODES
            }
            choices["macro"]["-c"] = "--countries"
            choices["fred"]["--parameter"] = {c: {} for c in self.fred_query.tolist()}
            choices["fred"]["-p"] = "--parameter"
            choices["index"]["--indices"] = {c: {} for c in yfinance_model.INDICES}
            choices["index"]["-i"] = "--indices"
            choices["bigmac"]["--countries"] = {
                c: {} for c in nasdaq_model.get_country_codes()["Code"].values
            }
            choices["bigmac"]["-c"] = "--countries"
            choices["events"]["--countries"] = {
                c: {} for c in nasdaq_model.get_country_names()
            }
            choices["events"]["-c"] = "--countries"
            choices["treasury"]["--maturity"] = {
                c: None for c in fedreserve_model.all_mat
            }
            choices["treasury"]["-m"] = "--maturity"
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def parse_input(self, an_input: str) -> List:
        """Parse controller input

        Overrides the parent class function to handle github org/repo path convention.
        See `BaseController.parse_input()` for details.
        """
        # Filtering out sorting parameters with forward slashes like P/E
        sort_filter = r"((\ -s |\ --sortby ).*?(P\/E|Fwd|P\/E|P\/S|P\/B|P\/C|P\/FCF)*)"

        custom_filters = [sort_filter]

        commands = parse_and_split_input(
            an_input=an_input, custom_filters=custom_filters
        )
        return commands

    def update_runtime_choices(self):
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            if not self.fred_query.empty:
                self.choices["fred"]["--parameter"] = {c: None for c in self.fred_query}

            if self.DATASETS:
                options = [
                    option for _, values in self.DATASETS.items() for option in values
                ]

                # help users to select multiple timeseries for one axis
                economicdata = list()
                for L in [1, 2]:
                    for subset in itertools.combinations(options, L):
                        economicdata.append(",".join(subset))
                        if len(subset) > 1:
                            economicdata.append(",".join(subset[::-1]))

                for argument in [
                    "--y1",
                    "--y2",
                ]:
                    self.choices["plot"][argument] = {
                        option: None for option in economicdata
                    }
        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("economy/", column_sources=115)
        mt.add_cmd("overview")
        mt.add_cmd("futures")
        mt.add_cmd("map")
        mt.add_cmd("bigmac")
        mt.add_cmd("events")
        mt.add_cmd("edebt")
        mt.add_raw("\n")
        mt.add_cmd("valuation")
        mt.add_cmd("performance")
        mt.add_cmd("usdli")
        mt.add_raw("\n")
        mt.add_info("_country_")
        mt.add_cmd("gdp")
        mt.add_cmd("rgdp")
        mt.add_cmd("fgdp")
        mt.add_cmd("debt")
        mt.add_cmd("cpi")
        mt.add_cmd("ccpi")
        mt.add_cmd("balance")
        mt.add_cmd("revenue")
        mt.add_cmd("spending")
        mt.add_cmd("trust")
        mt.add_raw("\n")
        mt.add_info("_database_")
        mt.add_cmd("macro")
        mt.add_cmd("treasury")
        mt.add_cmd("fred")
        mt.add_cmd("index")
        mt.add_raw("\n")
        mt.add_param("_stored", self.stored_datasets)
        mt.add_raw("\n")
        mt.add_cmd("eval")
        mt.add_cmd("plot")
        mt.add_raw("\n")
        mt.add_menu("qa")

        console.print(text=mt.menu_text, menu="Economy")

    @log_start_end(log=logger)
    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="""
            Provide a market overview of a variety of options. This can be a general overview,
            indices, bonds and currencies. [Source: Wall St. Journal]
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if not ns_parser.type:
                wsj_view.display_overview(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.type == "indices":
                wsj_view.display_indices(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            if ns_parser.type == "usbonds":
                wsj_view.display_usbonds(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            if ns_parser.type == "glbonds":
                wsj_view.display_glbonds(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            if ns_parser.type == "currencies":
                wsj_view.display_currencies(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
            choices=self.futures_commodities,
            default="",
        )

        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            choices=self.wsj_sortby_cols_dict.keys(),
            default="ticker",
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
            other_args.insert(0, "-c")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.source == "Finviz":
                if ns_parser.commodity:
                    finviz_view.display_future(
                        future_type=ns_parser.commodity.capitalize(),
                        sortby=ns_parser.sortby,
                        ascend=ns_parser.reverse,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
                    )
                else:
                    console.print(
                        "[red]Commodity group must be specified on Finviz.[/red]"
                    )
            elif ns_parser.source == "WallStreetJournal":
                if ns_parser.commodity:
                    console.print("[red]Commodity flag valid with Finviz only.[/red]")
                wsj_view.display_futures(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
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
            choices=self.map_filter_list,
            help="Map filter type.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            finviz_view.display_performance_map(
                period=ns_parser.s_period,
                map_filter=ns_parser.s_type,
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
            type=str,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            ns_parser.countries = list_from_str(ns_parser.countries)
            if ns_parser.codes:
                console.print(
                    nasdaq_model.get_country_codes().to_string(index=False), "\n"
                )
            else:
                nasdaq_view.display_big_mac_index(
                    country_codes=ns_parser.countries,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_gdp(self, other_args: List[str]):
        """Process gdp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gdp",
            description="This indicator is based on nominal GDP (also called GDP at current prices or GDP in value)"
            " and is available in different measures: US dollars and US dollars per capita (current PPPs).",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-u",
            "--units",
            type=str,
            dest="units",
            help="Use either USD or USD_CAP (USD Per Capita)",
            choices=["USD", "USD_CAP"],
            default="USD",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=30)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=dt.now().date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_gdp(
                countries=countries,
                units=ns_parser.units,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rgdp(self, other_args: List[str]):
        """Process rgdp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rgdp",
            description="This indicator is based on real GDP (also called GDP at constant prices or GDP in volume), "
            "i.e. the developments over time are adjusted for price changes.",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-u",
            "--units",
            type=str,
            dest="units",
            help="Use either PC_CHGPP (percentage change previous quarter), PC_CHGPY (percentage "
            "change from the same quarter of the previous year) or IDX (index with base at 2015) "
            "for units",
            choices=["PC_CHGPP", "PC_CHGPY", "IDX"],
            default="PC_CHGPY",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=10)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=dt.now().date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_real_gdp(
                countries=countries,
                units=ns_parser.units,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_fgdp(self, other_args: List[str]):
        """Process fgdp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fgdp",
            description="Forecast is based on an assessment of the economic climate in "
            "individual countries and the world economy, using a combination of model-based "
            "analyses and expert judgement. This indicator is measured in growth rates compared to previous year.",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-t",
            "--types",
            type=str,
            dest="types",
            help="Use either 'real' or 'nominal'",
            choices=["real", "nominal"],
            default="real",
        )

        parser.add_argument(
            "-q",
            "--quarterly",
            action="store_true",
            dest="quarterly",
            help="Whether to plot quarterly results.",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=10)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=(dt.now() + relativedelta(years=10)).date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_gdp_forecast(
                countries=countries,
                types=ns_parser.types,
                quarterly=ns_parser.quarterly,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_debt(self, other_args: List[str]):
        """Process debt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="debt",
            description="General government debt-to-GDP ratio measures the gross debt of the general "
            "government as a percentage of GDP. It is a key indicator for the sustainability of government finance.",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=30)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=dt.now().date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_debt(
                countries=countries,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balance",
            description=" General government balance is defined as the balance of income and expenditure of government,"
            " including capital income and capital expenditures. 'Net lending' means that government has a surplus, "
            "and is providing financial resources to other sectors, while  'net borrowing' means that "
            "government has a deficit, and requires financial resources from other sectors. "
            "This indicator is measured as a percentage of GDP.",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=30)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=dt.now().date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_balance(
                countries=countries,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_revenue(self, other_args: List[str]):
        """Process revenue command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="revenue",
            description="Governments collect revenues mainly for two purposes: to finance the goods "
            "and services they provide to citizens and businesses, and to fulfil their redistributive "
            "role. Comparing levels of government revenues across countries provides an "
            "indication of the importance of the government sector in the economy in "
            "terms of available financial resources.",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-u",
            "--units",
            type=str,
            dest="units",
            help="Use either THND_USD_CAP (thousands of USD per capity) "
            "or PC_GDP (percentage of GDP)",
            choices=["PC_GDP", "THND_USD_CAP"],
            default="PC_GDP",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=30)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=dt.now().date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_revenue(
                countries=countries,
                units=ns_parser.units,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_spending(self, other_args: List[str]):
        """Process spending command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="spending",
            description="General government spending provides an indication of the size "
            "of government across countries. The large variation in this indicator highlights "
            "the variety of countries' approaches to delivering public goods and services "
            "and providing social protection, not necessarily differences in resources spent",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-p",
            "--perspective",
            type=str,
            dest="perspective",
            help="Use either TOT (Total),  RECULTREL (Recreation, culture and religion), "
            "HOUCOMM (Housing and community amenities), PUBORD (Public order and safety), "
            "EDU (Education), ENVPROT (Environmental protection), GRALPUBSER (General public services), "
            "SOCPROT (Social protection), ECOAFF (Economic affairs), DEF (Defence), HEALTH (Health)",
            choices=[
                "TOT",
                "RECULTREL",
                "HOUCOMM",
                "PUBORD",
                "EDU",
                "ENVPROT",
                "GRALPUBSER",
                "SOCPROT",
                "ECOAFF",
                "DEF",
                "HEALTH",
            ],
            default="TOT",
        )

        parser.add_argument(
            "-u",
            "--units",
            type=str,
            dest="units",
            help="Use either THND_USD_CAP (thousands of USD per capity) "
            "or PC_GDP (percentage of GDP)",
            choices=["PC_GDP", "THND_USD_CAP"],
            default="PC_GDP",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=30)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=dt.now().date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_spending(
                countries=countries,
                perspective=ns_parser.perspective,
                units=ns_parser.units,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_trust(self, other_args: List[str]):
        """Process trust command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="trust",
            description="Trust in government refers to the share of people who report "
            "having confidence in the national government.",
        )

        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="Countries to get data for",
            default="united_states",
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=(dt.now() - relativedelta(years=30)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=dt.now().date(),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            countries = (
                list_from_str(ns_parser.countries.lower())
                if ns_parser.countries
                else None
            )

            oecd_view.plot_trust(
                countries=countries,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
            type=str,
            dest="parameters",
            help="Abbreviation(s) of the Macro Economic data",
            default="CPI",
        )
        parser.add_argument(
            "-c",
            "--countries",
            type=str,
            dest="countries",
            help="The country or countries you wish to show data for",
            default="united_states",
        )
        parser.add_argument(
            "-t",
            "--transform",
            dest="transform",
            help="The transformation to apply to the data",
            default="",
            choices=econdb_model.TRANSFORM,
        )
        parser.add_argument(
            "--show",
            dest="show",
            help="Show parameters and what they represent using 'parameters'"
            " or countries and their currencies using 'countries'",
            choices=self.macro_show,
            default=None,
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            help="The end date of the data (format: YEAR-MONTH-DAY, i.e. 2021-06-20)",
            default=None,
        )
        parser.add_argument(
            "--convert",
            dest="currency",
            help="Convert the currency of the chosen country to a specified currency. To find the "
            "currency symbols use '--show countries'",
            choices=econdb_model.COUNTRY_CURRENCIES.values(),
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            parameters = list_from_str(ns_parser.parameters.upper())
            countries = list_from_str(ns_parser.countries.lower())
            if ns_parser.show:
                if ns_parser.show == "parameters":
                    print_rich_table(
                        pd.DataFrame.from_dict(econdb_model.PARAMETERS, orient="index"),
                        show_index=True,
                        index_name="Parameter",
                        headers=["Name", "Period", "Description"],
                    )
                elif ns_parser.show == "countries":
                    print_rich_table(
                        pd.DataFrame(econdb_model.COUNTRY_CURRENCIES.items()),
                        show_index=False,
                        headers=["Country", "Currency"],
                    )
                elif ns_parser.show == "transform":
                    print_rich_table(
                        pd.DataFrame(econdb_model.TRANSFORM.items()),
                        show_index=False,
                        headers=["Code", "Transform"],
                    )
                return self.queue

            if ns_parser.parameters and ns_parser.countries:
                # Store data
                (df, units, _) = econdb_model.get_aggregated_macro_data(
                    parameters=parameters,
                    countries=countries,
                    transform=ns_parser.transform,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    symbol=ns_parser.currency,
                )

                if not df.empty:
                    if ns_parser.transform:
                        df.columns = [
                            f"_{ns_parser.transform}_".join(column)
                            for column in df.columns
                        ]
                    else:
                        df.columns = ["_".join(column) for column in df.columns]

                    for column in df.columns:
                        if column in self.DATASETS["macro"].columns:
                            self.DATASETS["macro"].drop(column, axis=1, inplace=True)

                    self.DATASETS["macro"] = pd.concat(
                        [self.DATASETS["macro"], df],
                        axis=1,
                    )

                    # update units dict
                    for country, data in units.items():
                        if country not in self.UNITS:
                            self.UNITS[country] = {}

                        for key, value in data.items():
                            self.UNITS[country][key] = value

                    self.stored_datasets = (
                        economy_helpers.update_stored_datasets_string(self.DATASETS)
                    )

                    # Display data just loaded
                    econdb_view.show_macro_data(
                        parameters=parameters,
                        countries=countries,
                        transform=ns_parser.transform,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                        symbol=ns_parser.currency,
                        raw=ns_parser.raw,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
                    )

                    self.update_runtime_choices()
                    if get_current_user().preferences.ENABLE_EXIT_AUTO_HELP:
                        self.print_help()

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
            type=str,
            dest="parameter",
            default="",
            help="Series ID of the Macro Economic data from FRED",
            required="-h" not in other_args
            and "--help" not in other_args
            and "-q" not in other_args
            and "--query" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-q",
            "--query",
            type=str,
            action="store",
            nargs="+",
            dest="query",
            help="Query the FRED database to obtain Series IDs given the query search term.",
            required="-h" not in other_args
            and "--help" not in other_args
            and "-p" not in other_args
            and "--parameter" not in other_args,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=100,
        )
        if ns_parser:
            parameters = list_from_str(ns_parser.parameter.upper())
            if ns_parser.query:
                query = " ".join(ns_parser.query)
                df_search = fred_model.get_series_notes(search_query=query)

                if not df_search.empty:
                    fred_view.notes(search_query=query, limit=ns_parser.limit)

                    self.fred_query = df_search["id"].head(ns_parser.limit)
                    self.update_runtime_choices()

                if parameters:
                    console.print(
                        "\nWarning: -p/--parameter is ignored when using -q/--query."
                    )

                return self.queue

            if parameters:
                series_dict = {}
                for series in parameters:
                    information = fred_model.check_series_id(series)

                    if "seriess" in information:
                        series_dict[series] = {
                            "title": information["seriess"][0]["title"],
                            "units": information["seriess"][0]["units_short"],
                        }

                        self.current_series = {series: series_dict[series]}

                if not series_dict:
                    return self.queue

                df, detail = fred_view.display_fred_series(
                    series_ids=parameters,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    limit=ns_parser.limit,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    get_data=True,
                )

                if not df.empty:
                    for series_id, data in detail.items():
                        self.FRED_TITLES[
                            series_id
                        ] = f"{data['title']} ({data['units']})"

                        # Making data available at the class level
                        self.DATASETS["fred"][series_id] = df[series_id]

                    self.stored_datasets = (
                        economy_helpers.update_stored_datasets_string(self.DATASETS)
                    )

                    self.update_runtime_choices()
                    if get_current_user().preferences.ENABLE_EXIT_AUTO_HELP:
                        self.print_help()

                else:
                    console.print("[red]No data found for the given Series ID[/red]")

            elif not parameters and ns_parser.raw:
                console.print(
                    "Warning: -r/--raw should be combined with -p/--parameter."
                )

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
            type=str,
            dest="indices",
            help="One or multiple indices",
        )
        parser.add_argument(
            "--show",
            dest="show_indices",
            help="Show the major indices, their arguments and ticker",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--interval",
            type=str,
            dest="interval",
            help="The preferred interval data is shown at. This can be 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, "
            "1d, 5d, 1wk, 1mo or 3mo",
            choices=self.index_interval,
            default="1d",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default="2000-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
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
            "-r",
            "--returns",
            help="Flag to show compounded returns over interval.",
            dest="returns",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
            limit=10,
        )
        if ns_parser:
            indices = list_from_str(ns_parser.indices)
            if ns_parser.query and ns_parser.limit:
                query = " ".join(ns_parser.query)
                yfinance_view.search_indices(query, ns_parser.limit)
                return self.queue

            if ns_parser.show_indices:
                print_rich_table(
                    pd.DataFrame.from_dict(yfinance_model.INDICES, orient="index"),
                    show_index=True,
                    index_name="Argument",
                    headers=["Name", "Ticker"],
                    title="Major Indices",
                )
                return self.queue

            if indices:
                # We create a list of dataframes and a list of columns
                # We then concatenate the dataframes and set the columns
                dfs_indices, columns = [], []

                for index in indices:
                    df = yfinance_model.get_index(
                        index,
                        interval=ns_parser.interval,
                        start_date=ns_parser.start_date,
                        end_date=ns_parser.end_date,
                        column=ns_parser.column,
                    )
                    dfs_indices.append(df)

                    if not df.empty:
                        self.DATASETS["index"][index] = df

                        self.stored_datasets = (
                            economy_helpers.update_stored_datasets_string(self.DATASETS)
                        )
                        columns.append(index)

                # If no data is found, we print a message and return
                if not dfs_indices:
                    text = "Indices" if len(indices) > 1 else "Index"
                    console.print(f"[red]No data found for the given {text}[/red]")
                    return self.queue

                # We concatenate the dataframes here to avoid having
                # to regrab the data in the view
                indices_data = pd.concat(dfs_indices, axis=1)
                indices_data.columns = columns

                # If returns are requested, we calculate them here as well
                if ns_parser.returns:
                    indices_data = indices_data.pct_change().dropna()
                    indices_data = indices_data + 1
                    indices_data = indices_data.cumprod()

                yfinance_view.show_indices(
                    indices=indices_data,
                    interval=ns_parser.interval,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    column=ns_parser.column,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    returns=ns_parser.returns,
                )

                self.update_runtime_choices()
                if get_current_user().preferences.ENABLE_EXIT_AUTO_HELP:
                    self.print_help()

    @log_start_end(log=logger)
    def call_treasury(self, other_args: List[str]):
        """Process treasury command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="treasury",
            description="Obtain US treasury rates.  Note: 3-month and 10-year treasury yields for other countries "
            "are available via the command 'macro' and parameter 'M3YD' and 'Y10YD'. [Source: EconDB / FED]",
        )
        parser.add_argument(
            "-m",
            "--maturity",
            type=str,
            dest="maturity",
            help="The preferred maturity which is dependent on the type of the treasury",
            default="10y",
        )
        parser.add_argument(
            "--show",
            dest="show_maturities",
            help="Show the maturities available for every instrument.",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default="1934-01-31",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            help="The end date of the data (format: YEAR-DAY-MONTH, i.e. 2021-06-02)",
            default=date.today(),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-m")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
            limit=10,
        )
        if ns_parser:
            maturities = list_from_str(ns_parser.maturity)
            if ns_parser.show_maturities:
                console.print(",".join(fedreserve_model.all_mat))
                return None

            fedreserve_view.show_treasuries(
                maturities=maturities,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

            if get_current_user().preferences.ENABLE_EXIT_AUTO_HELP:
                self.print_help()

    @log_start_end(log=logger)
    def call_cpi(self, other_args: List[str]):
        """Process cpi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpi",
            description="Plot (harmonized) consumer price indices for a "
            "variety of countries and regions.",
        )

        parser.add_argument(
            "-c",
            "--countries",
            dest="countries",
            type=str,
            help="What countries you'd like to collect data for",
            default="united_states",
        )

        parser.add_argument(
            "-u",
            "--units",
            dest="units",
            type=str,
            help="What units you'd like to collect data for",
            default="growth_same",
            choices=fred_model.CPI_UNITS,
        )

        parser.add_argument(
            "--frequency",
            dest="frequency",
            type=str,
            help="What frequency you'd like to collect data for",
            default="monthly",
            choices=fred_model.CPI_FREQUENCY,
        )

        parser.add_argument(
            "--harmonized",
            action="store_true",
            dest="harmonized",
            help="Whether to use harmonized cpi data",
            default=False,
        )

        parser.add_argument(
            "--no-smart-select",
            action="store_false",
            dest="smart_select",
            help="Whether to assist with selection",
            default=True,
        )

        parser.add_argument(
            "-o",
            "--options",
            dest="options",
            action="store_true",
            help="See the available options",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=(dt.now() - relativedelta(years=30)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=dt.now().date(),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            countries = list_from_str(ns_parser.countries)

            fred_view.plot_cpi(
                countries=countries,
                units=ns_parser.units,
                frequency=ns_parser.frequency,
                harmonized=ns_parser.harmonized,
                smart_select=ns_parser.smart_select,
                options=ns_parser.options,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ccpi(self, other_args: List[str]):
        """Process ccpi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ccpi",
            description="Inflation is measured in terms of the annual growth rate and in index, "
            "2015 base year with a breakdown for food, energy and total excluding food and energy. "
            "Inflation measures the erosion of living standards",
        )

        parser.add_argument(
            "-c",
            "--countries",
            dest="countries",
            type=str,
            help="What countries you'd like to collect data for",
            default="united_states",
        )

        parser.add_argument(
            "-p",
            "--perspective",
            dest="perspective",
            type=str,
            help="Perspective of CPI you wish to obtain. This can be ENRG (energy), FOOD (food), "
            "TOT (total) or TOT_FOODENRG (total excluding food and energy)",
            default="TOT",
            choices=["ENRG", "FOOD", "TOT", "TOT_FOODENRG"],
        )

        parser.add_argument(
            "--frequency",
            dest="frequency",
            type=str,
            help="What frequency you'd like to collect data for",
            default="M",
            choices=["M", "Q", "A"],
        )

        parser.add_argument(
            "-u",
            "--units",
            dest="units",
            type=str,
            help="Units to get data in. Either 'AGRWTH' (annual growth rate) or IDX2015 (base = 2015)."
            " Default is Annual Growth Rate (AGRWTH).",
            default="AGRWTH",
            choices=["AGRWTH", "IDX2015"],
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=(dt.now() - relativedelta(years=5)).date(),
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=dt.now().date(),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            countries = list_from_str(ns_parser.countries)

            oecd_view.plot_cpi(
                countries=countries,
                perspective=ns_parser.perspective,
                frequency=ns_parser.frequency,
                units=ns_parser.units,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_events(self, other_args: List[str]):
        """Process events command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="events",
            description="Economic calendar. If no start or end dates,"
            "default is the current day high importance events.",
        )
        parser.add_argument(
            "-c",
            "--countries",
            action="store",
            dest="countries",
            type=str,
            default="",
            help="Display calendar for specific country.",
        )
        parser.add_argument(
            "-n",
            "--names",
            help="Flag to show all available country names",
            dest="names",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default=dt.now().strftime("%Y-%m-%d"),
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31)",
            default=dt.now().strftime("%Y-%m-%d"),
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="spec_date",
            type=valid_date,
            help="Get a specific date for events. Overrides start and end dates.",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
            limit=100,
        )

        if ns_parser:
            if ns_parser.names:
                for name in nasdaq_model.get_country_names():
                    console.print(name)
                return

            if ns_parser.names:
                for name in nasdaq_model.get_country_names():
                    console.print(name)
                return

            if ns_parser.names:
                for name in nasdaq_model.get_country_names():
                    console.print(name)
                return

            start_date = (
                ns_parser.start_date.strftime("%Y-%m-%d")
                if ns_parser.start_date
                else None
            )

            end_date = (
                ns_parser.end_date.strftime("%Y-%m-%d") if ns_parser.end_date else None
            )

            # TODO: Add `Investing` to sources again when `investpy` is fixed

            if ns_parser.spec_date:
                start_date = ns_parser.spec_date.strftime("%Y-%m-%d")
                end_date = ns_parser.spec_date.strftime("%Y-%m-%d")

            else:
                start_date, end_date = sorted([start_date, end_date])

            countries = list_from_str(ns_parser.countries)

            nasdaq_view.display_economic_calendar(
                countries=countries,
                start_date=start_date,
                end_date=end_date,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="This command can plot any data on two y-axes obtained from the macro, fred, index and "
            "treasury commands. To be able to use this data, just load the available series from the previous "
            "commands. For example 'macro -p GDP -c Germany Netherlands' will store the data for usage "
            "in this command. Therefore, it allows you to plot different time series in one graph. "
            "The example above could be plotted the following way: 'plot --y1 Germany_GDP --y2 Netherlands_GDP' "
            "or 'plot --y1 Germany_GDP Netherlands_GDP'",
        )
        parser.add_argument(
            "--y1",
            type=str,
            dest="yaxis1",
            help="Select the data you wish to plot on the first y-axis. You can select multiple variables here.",
            default="",
        )
        parser.add_argument(
            "--y2",
            type=str,
            dest="yaxis2",
            help="Select the data you wish to plot on the second y-axis. You can select multiple variables here.",
            default="",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--y1")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            limit=10,
        )

        if ns_parser:
            y1s = list_from_str(ns_parser.yaxis1)
            y2s = list_from_str(ns_parser.yaxis2)
            if not self.DATASETS:
                console.print(
                    "There is no data stored yet. Please use either the 'macro', 'fred', 'index' and/or "
                    "'treasury' command."
                )
                return
            dataset_yaxis1 = economy_helpers.get_yaxis_data(
                self.DATASETS, self.UNITS, self.FRED_TITLES, y1s
            )
            if dataset_yaxis1.empty:
                console.print(
                    f"[red]Not able to find any data for the --y1 argument. The currently available "
                    f"options are: {', '.join(self.choices['plot']['--y1'])}[/red]\n"
                )

            dataset_yaxis2 = economy_helpers.get_yaxis_data(
                self.DATASETS, self.UNITS, self.FRED_TITLES, y2s
            )
            if dataset_yaxis2.empty:
                console.print(
                    f"[red]Not able to find any data for the --y2 argument. The currently available "
                    f"options are: {', '.join(self.choices['plot']['--y2'])}[/red]\n"
                )

            if y1s or y2s:
                plot_view.show_plot(
                    dataset_yaxis_1=dataset_yaxis1,
                    dataset_yaxis_2=dataset_yaxis2,
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
            choices=list(self.d_GROUPS.keys()),
            default="sector",
            dest="group",
            help="Data group (sectors, industry or country)",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            choices=list(self.valuation_sort_cols_dict.keys()),
            default="Name",
            help="Column to sort by",
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
            other_args.insert(0, "-g")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ns_group = (
                " ".join(ns_parser.group)
                if isinstance(ns_parser.group, list)
                else ns_parser.group
            )
            finviz_view.display_valuation(
                group=ns_group,
                sortby=self.valuation_sort_cols_dict[ns_parser.sortby],
                ascend=ns_parser.reverse,
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
            choices=list(self.d_GROUPS.keys()),
            default="sector",
            dest="group",
            help="Data group (sector, industry or country)",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            choices=list(self.performance_sort_dict.keys()),
            default="Name",
            help="Column to sort by",
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
            other_args.insert(0, "-g")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ns_group = (
                " ".join(ns_parser.group)
                if isinstance(ns_parser.group, list)
                else ns_parser.group
            )
            finviz_view.display_performance(
                group=ns_group,
                sortby=self.performance_sort_dict[ns_parser.sortby],
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_edebt(self, other_args: List[str]):
        """Process edebt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="edebt",
            description="""
                National debt statistics for various countries. [Source: Wikipedia]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, limit=20
        )
        if ns_parser:
            commodity_view.display_debt(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                limit=ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_usdli(self, other_args: List[str]):
        """Process usdli command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="usdli",
            description="""
            The USD Liquidity Index is defined as: [WALCL - WLRRAL - WDTGAL]. It is expressed in billions of USD.
            """,
        )
        parser.add_argument(
            "-o",
            "--overlay",
            type=str,
            choices=list(fred_model.EQUITY_INDICES.keys()),
            default="SP500",
            dest="overlay",
            help="The equity index to compare against.  Set `show = True` for the list of choices.",
        )
        parser.add_argument(
            "-s",
            "--show",
            action="store_true",
            dest="show",
            default=False,
            help="Show the list of available equity indices to overlay.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser:
            fred_view.display_usd_liquidity(
                overlay=ns_parser.overlay,
                show=ns_parser.show,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_eval(self, other_args):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="eval",
            description="""Create custom data column from loaded datasets.  Can be mathematical expressions supported
            by pandas.eval() function.

            Example.  If I have loaded `fred DGS2,DGS5` and I want to create a new column that is the difference
            between these two, I can create a new column by doing `eval spread = DGS2 - DGS5`.
            Notice that the command is case sensitive, i.e., `DGS2` is not the same as `dgs2`.
            """,
        )
        parser.add_argument(
            "-q",
            "--query",
            type=str,
            nargs="+",
            dest="query",
            required="-h" not in other_args and "--help" not in other_args,
            help="Query to evaluate on loaded datasets",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-q")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.DATASETS = economy_helpers.create_new_entry(
                self.DATASETS, " ".join(ns_parser.query)
            )

            self.stored_datasets = economy_helpers.update_stored_datasets_string(
                self.DATASETS
            )
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_qa(self, _):
        """Process qa command"""
        if not any(True for x in self.DATASETS.values() if not x.empty):
            console.print(
                "There is no data stored. Please use either the 'macro', 'fred', 'index' and/or "
                "'treasury' command in combination with the -st argument to plot data.\n"
            )
            return

        from openbb_terminal.economy.quantitative_analysis.qa_controller import (
            QaController,
        )

        data: Dict = {}  # type: ignore
        for source, _ in self.DATASETS.items():
            if not self.DATASETS[source].empty:
                if len(self.DATASETS[source].columns) == 1:
                    data[self.DATASETS[source].columns[0]] = self.DATASETS[source]
                else:
                    for col in list(self.DATASETS[source].columns):
                        data[col] = self.DATASETS[source][col].to_frame()

        if data:
            self.queue = self.load_class(QaController, data, self.queue)
        else:
            console.print(
                "[red]Please load a dataset before moving to the qa menu[/red]\n"
            )
