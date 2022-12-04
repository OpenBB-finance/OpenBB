"""Sector and Industry Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
import logging
from typing import List

import yfinance as yf

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    check_positive,
    check_proportion_range,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.stocks.comparison_analysis import ca_controller
from openbb_terminal.stocks.sector_industry_analysis import (
    financedatabase_model,
    financedatabase_view,
    stockanalysis_model,
    stockanalysis_view,
)

# pylint: disable=inconsistent-return-statements,C0302,R0902


logger = logging.getLogger(__name__)


class SectorIndustryAnalysisController(BaseController):
    """Sector Industry Analysis Controller class"""

    CHOICES_COMMANDS = [
        "select",
        "clear",
        "industry",
        "sector",
        "country",
        "mktcap",
        "exchange",
        "period",
        "cps",
        "cpic",
        "cpis",
        "cpcs",
        "cpci",
        "metric",
        "vis",
    ]
    CHOICES_MENUS = [
        "ca",
    ]

    metric_choices = [
        "roa",
        "roe",
        "cr",
        "qr",
        "de",
        "tc",
        "tcs",
        "tr",
        "rps",
        "rg",
        "eg",
        "pm",
        "gp",
        "gm",
        "ocf",
        "om",
        "fcf",
        "td",
        "ebitda",
        "ebitdam",
        "rec",
        "mc",
        "fte",
        "er",
        "bv",
        "ss",
        "pb",
        "beta",
        "fs",
        "peg",
        "ev",
        "fpe",
    ]
    metric_yf_keys = {
        "roa": ("financialData", "returnOnAssets"),
        "roe": ("financialData", "returnOnEquity"),
        "cr": ("financialData", "currentRatio"),
        "qr": ("financialData", "quickRatio"),
        "de": ("financialData", "debtToEquity"),
        "tc": ("financialData", "totalCash"),
        "tcs": ("financialData", "totalCashPerShare"),
        "tr": ("financialData", "totalRevenue"),
        "rps": ("financialData", "revenuePerShare"),
        "rg": ("financialData", "revenueGrowth"),
        "eg": ("financialData", "earningsGrowth"),
        "pm": ("financialData", "profitMargins"),
        "gp": ("financialData", "grossProfits"),
        "gm": ("financialData", "grossMargins"),
        "ocf": ("financialData", "operatingCashflow"),
        "om": ("financialData", "operatingMargins"),
        "fcf": ("financialData", "freeCashflow"),
        "td": ("financialData", "totalDebt"),
        "ebitda": ("financialData", "ebitda"),
        "ebitdam": ("financialData", "ebitdaMargins"),
        "rec": ("financialData", "recommendationMean"),
        "mc": ("price", "marketCap"),
        "fte": ("summaryProfile", "fullTimeEmployees"),
        "er": ("defaultKeyStatistics", "enterpriseToRevenue"),
        "bv": ("defaultKeyStatistics", "bookValue"),
        "ss": ("defaultKeyStatistics", "sharesShort"),
        "pb": ("defaultKeyStatistics", "priceToBook"),
        "beta": ("defaultKeyStatistics", "beta"),
        "fs": ("defaultKeyStatistics", "floatShares"),
        "sr": ("defaultKeyStatistics", "shortRatio"),
        "peg": ("defaultKeyStatistics", "pegRatio"),
        "ev": ("defaultKeyStatistics", "enterpriseValue"),
        "fpe": ("defaultKeyStatistics", "forwardPE"),
    }

    vis_choices = (
        list(stockanalysis_model.SA_KEYS["BS"].keys())
        + list(stockanalysis_model.SA_KEYS["CF"].keys())
        + list(stockanalysis_model.SA_KEYS["IS"].keys())
    )

    mktcap_choices = [
        "Nano",
        "Micro",
        "Small",
        "Mid",
        "Large",
        "Mega",
        "nano",
        "micro",
        "small",
        "mid",
        "large",
        "mega",
    ]
    clear_choices = ["industry", "sector", "country", "mktcap"]
    period_choices = [
        "Annual",
        "Quarterly",
        "Trailing",
        "annual",
        "quarterly",
        "trailing",
    ]
    PATH = "/stocks/sia/"
    CHOICES_GENERATION = True

    def __init__(
        self,
        ticker: str,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.country = ""
        self.sector = ""
        self.industry = ""
        self.mktcap = ""
        self.exclude_exchanges = True
        self.period = "Annual"

        self.ticker = ticker

        self.stocks_data: dict = {}
        self.tickers: List = list()
        self.currency: str = ""

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            # This menu contains dynamic choices that may change during runtime
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.__load()

    def update_runtime_choices(self):
        """Update runtime choices"""
        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices["industry"] = {
                i: {}
                for i in financedatabase_model.get_industries(
                    country=self.country, sector=self.sector
                )
            }
            self.choices["sector"] = {
                s: {}
                for s in financedatabase_model.get_sectors(
                    industry=self.industry, country=self.country
                )
            }
            self.choices["country"] = {
                c: {}
                for c in financedatabase_model.get_countries(
                    industry=self.industry, sector=self.sector
                )
            }
            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/sia/")
        mt.add_cmd("select")
        mt.add_raw("\n")
        mt.add_cmd("clear")
        mt.add_cmd("industry")
        mt.add_cmd("sector")
        mt.add_cmd("country")
        mt.add_cmd("mktcap")
        mt.add_cmd("exchange")
        mt.add_cmd("period")
        mt.add_raw("\n")
        mt.add_param("_industry", self.industry, 18)
        mt.add_param("_sector", self.sector, 18)
        mt.add_param("_country", self.country, 18)
        mt.add_param("_mktcap", self.mktcap, 18)
        mt.add_param("_exclude_exchanges", self.exclude_exchanges, 18)
        mt.add_param("_period", self.period, 18)
        mt.add_raw("\n")
        mt.add_info("_statistics_")
        mt.add_cmd("cps", self.country)
        mt.add_cmd("cpic", self.country)
        mt.add_cmd("cpis", self.sector)
        mt.add_cmd("cpcs", self.sector)
        mt.add_cmd("cpci", self.industry)
        mt.add_raw("\n")
        if self.stocks_data:
            mt.add_info("_financials_")
        else:
            mt.add_info("_financials_loaded_")
        mt.add_cmd("metric")
        mt.add_cmd("vis")
        mt.add_raw("\n")
        mt.add_param("_returned_tickers", ", ".join(self.tickers))
        mt.add_menu("ca", self.tickers)
        console.print(text=mt.menu_text, menu="Stocks - Sector and Industry Analysis")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "sia"]
        return []

    @log_start_end(log=logger)
    def call_select(self, other_args: List[str]):
        """Process select command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="select",
            description="Select stock ticker and alter the industry, sector, country and market cap "
            "accordingly for this ticker.",
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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            # The historical data is not used, so this is a quick way to check if the ticker is valid
            df_stock_candidate = yf.download(
                ns_parser.ticker, period="1mo", progress=False
            )
            if not df_stock_candidate.empty:
                if "." in ns_parser.ticker:
                    self.ticker = ns_parser.ticker.upper().split(".")[0]
                else:
                    self.ticker = ns_parser.ticker.upper()

                self.__load()

    def __load(self):
        if self.ticker:
            data = yf.utils.get_json(f"https://finance.yahoo.com/quote/{self.ticker}")

            if "summaryProfile" not in data or data["summaryProfile"] is None:
                raise Exception(
                    f"Failed to load {self.ticker} Summary Profile from Yahoo Finance"
                )

            if not data["summaryProfile"]["country"]:
                raise Exception(
                    f"Failed to load {self.ticker} Country from Yahoo Finance"
                )

            if not data["summaryProfile"]["sector"]:
                raise Exception(
                    f"Failed to load {self.ticker} Sector from Yahoo Finance"
                )

            if not data["summaryProfile"]["industry"]:
                raise Exception(
                    f"Failed to load {self.ticker} Industry from Yahoo Finance"
                )

            self.country = data["summaryProfile"]["country"]
            if self.country not in financedatabase_model.get_countries():
                similar_cmd = difflib.get_close_matches(
                    self.country,
                    financedatabase_model.get_countries(),
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    self.country = similar_cmd[0]
            self.sector = data["summaryProfile"]["sector"]
            if self.sector not in financedatabase_model.get_sectors():
                similar_cmd = difflib.get_close_matches(
                    self.sector,
                    financedatabase_model.get_sectors(),
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    self.sector = similar_cmd[0]
            self.industry = data["summaryProfile"]["industry"]
            if self.industry not in financedatabase_model.get_industries():
                similar_cmd = difflib.get_close_matches(
                    self.industry,
                    financedatabase_model.get_industries(),
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    self.industry = similar_cmd[0]

            if "price" in data:
                mktcap = data["price"]["marketCap"]
                if mktcap < 50_000_000:
                    self.mktcap = "Nano"
                elif mktcap < 300_000_000:
                    self.mktcap = "Micro"
                elif mktcap < 2_000_000_000:
                    self.mktcap = "Small"
                elif mktcap > 200_000_000_000:
                    self.mktcap = "Mega"
                elif mktcap > 10_000_000_000:
                    self.mktcap = "Large"
                else:
                    self.mktcap = "Mid"

            self.stocks_data = {}
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_industry(self, other_args: List[str]):
        """Process industry command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="industry",
            description="See existing industries, or set industry if arg specified",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="industry to select",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            possible_industries = financedatabase_model.get_industries(
                country=self.country,
                sector=self.sector,
            )
            if ns_parser.name:
                if " ".join(ns_parser.name) in possible_industries:
                    self.industry = " ".join(ns_parser.name)
                    # if we get the industry, then we also automatically know the sector
                    self.sector = financedatabase_model.get_sectors(
                        industry=self.industry
                    )[0]
                    self.update_runtime_choices()
                else:
                    console.print(
                        f"Industry '{' '.join(ns_parser.name)}' does not exist."
                    )
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        possible_industries,
                        n=1,
                        cutoff=0.75,
                    )
                    if similar_cmd:
                        console.print(f"Replacing by '{similar_cmd[0]}'")
                        self.industry = similar_cmd[0]
                        # if we get the industry, then we also automatically know the sector
                        self.sector = financedatabase_model.get_sectors(
                            industry=self.industry
                        )[0]
                        self.update_runtime_choices()
                    else:
                        similar_cmd = difflib.get_close_matches(
                            " ".join(ns_parser.name),
                            possible_industries,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            console.print(f"Did you mean '{similar_cmd[0]}'?")
            else:
                for industry in possible_industries:
                    console.print(industry)

            self.stocks_data = {}
            console.print()

    @log_start_end(log=logger)
    def call_sector(self, other_args: List[str]):
        """Process sector command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sector",
            description="See existing sectors, or set sector if arg specified",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="sector to select",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            possible_sectors = financedatabase_model.get_sectors(
                self.industry, self.country
            )
            if ns_parser.name:
                if " ".join(ns_parser.name) in possible_sectors:
                    self.sector = " ".join(ns_parser.name)
                    self.update_runtime_choices()
                else:
                    console.print(
                        f"Sector '{' '.join(ns_parser.name)}' does not exist."
                    )

                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        possible_sectors,
                        n=1,
                        cutoff=0.75,
                    )

                    if similar_cmd:
                        console.print(f"Replacing by '{similar_cmd[0]}'")
                        self.sector = similar_cmd[0]
                        self.update_runtime_choices()
                    else:
                        similar_cmd = difflib.get_close_matches(
                            " ".join(ns_parser.name),
                            possible_sectors,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            console.print(f"Did you mean '{similar_cmd[0]}'?")

            else:
                for sector in possible_sectors:
                    console.print(sector)

            self.stocks_data = {}
            console.print()

    @log_start_end(log=logger)
    def call_country(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="country",
            description="See existing countries, or set country if arg specified",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="country to select",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            possible_countries = financedatabase_model.get_countries(
                industry=self.industry, sector=self.sector
            )
            if ns_parser.name:
                if " ".join(ns_parser.name) in possible_countries:
                    self.country = " ".join(ns_parser.name)
                    self.update_runtime_choices()
                else:
                    console.print(
                        f"Country '{' '.join(ns_parser.name)}' does not exist."
                    )
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        possible_countries,
                        n=1,
                        cutoff=0.75,
                    )
                    if similar_cmd:
                        console.print(f"Replacing by '{similar_cmd[0]}'")
                        self.country = similar_cmd[0]
                        self.update_runtime_choices()
                    else:
                        similar_cmd = difflib.get_close_matches(
                            " ".join(ns_parser.name),
                            possible_countries,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            console.print(f"Did you mean '{similar_cmd[0]}'?")
            else:
                for country in possible_countries:
                    console.print(country)

            self.stocks_data = {}
            console.print()

    @log_start_end(log=logger)
    def call_mktcap(self, other_args: List[str]):
        """Process mktcap command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mktcap",
            description="Set mktcap to nano, micro, small, mid, large or mega",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            choices=self.mktcap_choices,
            help="market cap to select",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.name:
                self.mktcap = ns_parser.name.capitalize()
            else:
                console.print(
                    "Select between market cap: Nano, Micro, Small, Mid, Large and Mega"
                )

            self.stocks_data = {}
            console.print()

    # pylint:disable=attribute-defined-outside-init
    @log_start_end(log=logger)
    def call_exchange(self, other_args: List[str]):
        """Process exchange command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exchange",
            description="Swap exclude international exchanges flag",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.exclude_exchanges = not self.exclude_exchanges
            console.print(
                f"International exchanges {'excluded' if self.exclude_exchanges else 'included'}",
                "\n",
            )

        self.stocks_data = {}
        console.print()

    @log_start_end(log=logger)
    def call_clear(self, other_args: List[str]):
        """Process clear command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clear",
            description="Clear all or a particular parameter",
        )
        parser.add_argument(
            "-p",
            "--param",
            type=str,
            dest="parameter",
            choices=self.clear_choices,
            help="parameter to clear",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.parameter == "industry":
                self.industry = ""
            elif ns_parser.parameter == "sector":
                self.sector = ""
            elif ns_parser.parameter == "country":
                self.country = ""
            elif ns_parser.parameter == "mktcap":
                self.mktcap = ""
            else:
                self.industry = ""
                self.sector = ""
                self.country = ""
                self.mktcap = ""

            self.exclude_exchanges = True
            self.ticker = ""
            self.update_runtime_choices()
            self.stocks_data = {}

    @log_start_end(log=logger)
    def call_period(self, other_args: List[str]):
        """Process period command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="period",
            description="Set period between annual, quarterly and trailing",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            choices=self.period_choices,
            help="period to select",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.name:
                self.period = ns_parser.name.capitalize()
            else:
                console.print("Select between period: Annual, Quarterly and Trailing")

            self.stocks_data = {}
            console.print()

    @log_start_end(log=logger)
    def call_metric(self, other_args: List[str]):
        """Process metric command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="metric",
            description=" Visualize a particular metric with the filters selected"
            " Available Metrics:"
            "    roa           return on assets"
            "    roe           return on equity"
            "    cr            current ratio"
            "    qr            quick ratio"
            "    de            debt to equity"
            "    tc            total cash"
            "    tcs           total cash per share"
            "    tr            total revenue"
            "    rps           revenue per share"
            "    rg            revenue growth"
            "    eg            earnings growth"
            "    pm            profit margins"
            "    gp            gross profits"
            "    gm            gross margins"
            "    ocf           operating cash flow"
            "    om            operating margins"
            "    fcf           free cash flow"
            "    td            total debt"
            "    ebitda        earnings before interest, taxes, depreciation and amortization"
            "    ebitdam       ebitda margins"
            "    rec           recommendation mean"
            "    mc            market cap"
            "    fte           full time employees"
            "    er            enterprise to revenue"
            "    bv            book value"
            "    ss            shares short"
            "    pb            price to book"
            "    beta          beta"
            "    fs            float shares"
            "    sr            short ratio"
            "    peg           peg ratio"
            "    ev            enterprise value"
            "    fpe           forward P/E,",
        )
        parser.add_argument(
            "-m",
            "--metric",
            dest="metric",
            required="-h" not in other_args,
            help="Metric to visualize",
            choices=self.metric_choices,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            default=10,
            help="Limit number of companies to display",
            type=check_positive,
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Output all raw data",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-m")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:

            if not self.country and not self.sector and not self.industry:
                console.print(
                    "[red]Select at least one filter from sector, country or industry.[/red]\n"
                )
            else:
                try:
                    console.print(
                        "[param]If it takes too long, you can use 'Ctrl + C' to cancel.\n[/param]"
                    )
                    (
                        self.stocks_data,
                        self.tickers,
                    ) = financedatabase_view.display_bars_financials(
                        self.metric_yf_keys[ns_parser.metric][0],
                        self.metric_yf_keys[ns_parser.metric][1],
                        self.country,
                        self.sector,
                        self.industry,
                        self.mktcap,
                        self.exclude_exchanges,
                        ns_parser.limit,
                        ns_parser.export,
                        ns_parser.raw,
                        self.stocks_data,
                    )
                except KeyboardInterrupt:
                    console.print(
                        "[param]For a faster search, ensure that you select at least one filter "
                        "from sector, country or industry.\n[/param]"
                    )

    @log_start_end(log=logger)
    def call_vis(self, other_args: List[str]):
        """Process vis command"""

        statement_string = {
            "BS": "Balance Sheet Statement",
            "IS": "Income Statement",
            "CF": "Cash Flow Statement",
        }
        help_text = "Visualize a particular metric with the filters selected\n"

        for statement, statement_value in stockanalysis_model.SA_KEYS.items():
            help_text += f"\n{statement_string[statement]}\n"
            for k, v in statement_value.items():
                help_text += f"  {k} {(10 - len(k)) * ' '} {v} \n"

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vis",
            description=help_text,
        )
        parser.add_argument(
            "-m",
            "--metric",
            dest="metric",
            required="-h" not in other_args,
            help="Metric to visualize",
            choices=self.vis_choices,
        )
        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            default=12,
            help="Limit number of periods to display",
            type=check_positive,
        )
        parser.add_argument(
            "-c",
            "--currency",
            dest="currency",
            help="Convert the currency of the chosen country to a specified currency. By default, this is set "
            "to USD (US Dollars).",
            default="USD",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-m")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, limit=10, raw=True
        )
        if ns_parser:

            if not self.country and not self.sector and not self.industry:
                console.print(
                    "[red]Select at least one filter from sector, country or industry.[/red]\n"
                )
            else:
                try:
                    console.print(
                        "[param]If it takes too long, you can use 'Ctrl + C' to cancel.\n[/param]"
                    )
                    if ns_parser.currency != self.currency:
                        self.stocks_data = {}
                    (
                        self.stocks_data,
                        self.tickers,
                    ) = stockanalysis_view.display_plots_financials(
                        finance_key=ns_parser.metric,
                        country=self.country,
                        sector=self.sector,
                        industry=self.industry,
                        period=self.period,
                        period_length=ns_parser.period,
                        marketcap=self.mktcap,
                        currency=ns_parser.currency,
                        exclude_exchanges=self.exclude_exchanges,
                        limit=ns_parser.limit,
                        export=ns_parser.export,
                        raw=ns_parser.raw,
                        already_loaded_stocks_data=self.stocks_data,
                    )

                    self.currency = ns_parser.currency
                except KeyboardInterrupt:
                    console.print(
                        "[param]For a faster search, ensure that you select at least one filter"
                        "from sector, country or industry.\n[/param]"
                    )

    @log_start_end(log=logger)
    def call_cps(self, other_args: List[str]):
        """Process cps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cps",
            description="Companies per Sectors based on Country and Market Cap",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max_sectors_to_display",
            default=15,
            help="Maximum number of sectors to display",
            type=check_positive,
        )
        parser.add_argument(
            "-m",
            "--min",
            action="store",
            dest="min_pct_to_display_sector",
            type=check_proportion_range,
            default=0.015,
            help="Minimum percentage to display sector",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Output all raw data",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if not self.country:
                console.print("The country parameter needs to be selected!\n")
            else:
                financedatabase_view.display_companies_per_sector_in_country(
                    self.country,
                    self.mktcap,
                    self.exclude_exchanges,
                    ns_parser.export,
                    ns_parser.raw,
                    ns_parser.max_sectors_to_display,
                    ns_parser.min_pct_to_display_sector,
                )

    @log_start_end(log=logger)
    def call_cpic(self, other_args: List[str]):
        """Process cpic command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpic",
            description="Companies per Industry based on Country and Market Cap",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max_industries_to_display",
            default=15,
            help="Maximum number of industries to display",
            type=check_positive,
        )
        parser.add_argument(
            "-m",
            "--min",
            action="store",
            dest="min_pct_to_display_industry",
            type=check_proportion_range,
            default=0.015,
            help="Minimum percentage to display industry",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Output all raw data",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if not self.country:
                console.print("The country parameter needs to be selected!\n")
            else:
                financedatabase_view.display_companies_per_industry_in_country(
                    self.country,
                    self.mktcap,
                    self.exclude_exchanges,
                    ns_parser.export,
                    ns_parser.raw,
                    ns_parser.max_industries_to_display,
                    ns_parser.min_pct_to_display_industry,
                )

    @log_start_end(log=logger)
    def call_cpis(self, other_args: List[str]):
        """Process cpis command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpis",
            description="Companies per Industry based on Sector and Market Cap",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max_industries_to_display",
            default=15,
            help="Maximum number of industries to display",
            type=check_positive,
        )
        parser.add_argument(
            "-m",
            "--min",
            action="store",
            dest="min_pct_to_display_industry",
            type=check_proportion_range,
            default=0.015,
            help="Minimum percentage to display industry",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Output all raw data",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if not self.sector:
                console.print("The sector parameter needs to be selected!\n")
            else:
                financedatabase_view.display_companies_per_industry_in_sector(
                    self.sector,
                    self.mktcap,
                    self.exclude_exchanges,
                    ns_parser.export,
                    ns_parser.raw,
                    ns_parser.max_industries_to_display,
                    ns_parser.min_pct_to_display_industry,
                )

    @log_start_end(log=logger)
    def call_cpcs(self, other_args: List[str]):
        """Process cpcs command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpcs",
            description="Companies per Country based on Sector and Market Cap",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max_countries_to_display",
            default=15,
            help="Maximum number of countries to display",
            type=check_positive,
        )
        parser.add_argument(
            "-m",
            "--min",
            action="store",
            dest="min_pct_to_display_country",
            type=check_proportion_range,
            default=0.015,
            help="Minimum percentage to display country",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Output all raw data",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if not self.sector:
                console.print("The sector parameter needs to be selected!\n")
            else:
                financedatabase_view.display_companies_per_country_in_sector(
                    self.sector,
                    self.mktcap,
                    self.exclude_exchanges,
                    ns_parser.export,
                    ns_parser.raw,
                    ns_parser.max_countries_to_display,
                    ns_parser.min_pct_to_display_country,
                )

    @log_start_end(log=logger)
    def call_cpci(self, other_args: List[str]):
        """Process cpci command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpci",
            description="Companies per Country based on Industry and Market Cap",
        )
        parser.add_argument(
            "-M",
            "--max",
            dest="max_countries_to_display",
            default=15,
            help="Maximum number of countries to display",
            type=check_positive,
        )
        parser.add_argument(
            "-m",
            "--min",
            action="store",
            dest="min_pct_to_display_country",
            type=check_proportion_range,
            default=0.015,
            help="Minimum percentage to display country",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Output all raw data",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if not self.industry:
                console.print("The industry parameter needs to be selected!\n")
            else:
                financedatabase_view.display_companies_per_country_in_industry(
                    self.industry,
                    self.mktcap,
                    self.exclude_exchanges,
                    ns_parser.export,
                    ns_parser.raw,
                    ns_parser.max_countries_to_display,
                    ns_parser.min_pct_to_display_country,
                )

    @log_start_end(log=logger)
    def call_ca(self, _):
        """Call the comparison analysis menu with selected tickers"""
        if self.tickers:
            self.queue = ca_controller.ComparisonAnalysisController(
                self.tickers, self.queue
            ).menu(custom_path_menu_above="/stocks/")
        else:
            console.print(
                "No main ticker loaded to go into comparison analysis menu", "\n"
            )
