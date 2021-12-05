"""Insider Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List
import pandas as pd
import yfinance as yf
from colorama import Style
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
    check_positive,
    check_proportion_range,
)
from gamestonk_terminal.stocks.stocks_helper import load
from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.stocks.sector_industry_analysis import (
    financedatabase_model,
    financedatabase_view,
)
from gamestonk_terminal.stocks.comparison_analysis import ca_controller


# pylint: disable=inconsistent-return-statements,too-many-public-methods,C0302,R0902


class SectorIndustryAnalysisController:
    """Sector Industry Analysis Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "load",
    ]

    CHOICES_COMMANDS = [
        "clear",
        "industry",
        "sector",
        "country",
        "mktcap",
        "exchange",
        "cps",
        "cpic",
        "cpis",
        "cpcs",
        "cpci",
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
        "yield",
        "ldv",
    ]

    CHOICES_MENUS = [
        "ca",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor

        Parameters
        ----------
        ticker : str
            Ticker to be used to analyse sector and industry
        start : str
            Start time
        interval : str
            Time interval
        stock : pd.DataFrame
            Stock data
        """
        self.country = "United States"
        self.sector = ""
        self.industry = ""
        self.mktcap = "Large"
        self.exclude_exhanges = True

        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        self.stocks_data: dict = {}
        self.tickers: List = list()

        if ticker:
            data = yf.utils.get_json(f"https://finance.yahoo.com/quote/{ticker}")

            if "summaryProfile" in data:
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

                if mktcap < 2_000_000_000:
                    self.mktcap = "Small"
                elif mktcap > 10_000_000_000:
                    self.mktcap = "Large"
                else:
                    self.mktcap = "Mid"

        self.insider_parser = argparse.ArgumentParser(add_help=False, prog="sia")
        self.insider_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def display_metric_financials(
        self,
        other_args: List[str],
        cmd: str,
        cmd_desc: str,
        finance_key: str,
        finance_metric: str,
    ):
        """Get metric financials

        Parameters
        ----------
        other_args: List[str]
            List of arguments given by user
        cmd: str
            Command name
        cmd_desc: str
            Command description
        finance_key: str
            Select finance key from Yahoo Finance(e.g. financialData, defaultKeyStatistics, summaryProfile)
        finance_metric: str
            Select finance metric from Yahoo Finance (e.g. operatingCashflow, revenueGrowth, ebitda, freeCashflow)
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog=cmd,
            description=cmd_desc,
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        self.stocks_data, self.tickers = financedatabase_view.display_bars_financials(
            finance_key,
            finance_metric,
            self.country,
            self.sector,
            self.industry,
            self.mktcap,
            self.exclude_exhanges,
            ns_parser.limit,
            ns_parser.export,
            ns_parser.raw,
            self.stocks_data,
        )

    def print_help(self):
        """Print help"""
        params = not any([self.industry, self.sector, self.country])
        s = Style.DIM if not self.sector else ""
        i = Style.DIM if not self.industry else ""
        c = Style.DIM if not self.country else ""
        m = Style.DIM if not self.mktcap else ""
        r = Style.RESET_ALL
        help_text = f"""
Sector and Industry Analysis:
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program
    load          load a ticker and get its industry, sector, country and market cap

    clear         clear all or one of industry, sector, country and market cap parameters
    industry      see existing industries, or set industry if arg specified
    sector        see existing sectors, or set sector if arg specified
    country       see existing countries, or set country if arg specified
    mktcap        set mktcap between small, mid or large
    exchange      revert exclude international exchanges flag

Industry          : {self.industry}
Sector            : {self.sector}
Country           : {self.country}
Market Cap        : {self.mktcap}
Exclude Exchanges : {self.exclude_exhanges}

Statistics{c}
    cps           companies per Sector based on Country{m} and Market Cap{r}{c}
    cpic          companies per Industry based on Country{m} and Market Cap{r}{s}
    cpis          companies per Industry based on Sector{m} and Market Cap{r}{s}
    cpcs          companies per Country based on Sector{m} and Market Cap{r}{i}
    cpci          companies per Country based on Industry{m} and Market Cap{r}
{r}{Style.DIM if params else ''}
Financials {'- loaded data (fast mode) 'if self.stocks_data else ''}
    roa           return on assets
    roe           return on equity
    cr            current ratio
    qr            quick ratio
    de            debt to equity
    tc            total cash
    tcs           total cash per share
    tr            total revenue
    rps           revenue per share
    rg            revenue growth
    eg            earnings growth
    pm            profit margins
    gp            gross profits
    gm            gross margins
    ocf           operating cash flow
    om            operating margins
    fcf           free cash flow
    td            total debt
    ebitda        earnings before interest, taxes, depreciation and amortization
    ebitdam       ebitda margins
    rec           recommendation mean
    mc            market cap
    fte           full time employees
    er            enterprise to revenue
    bv            book value
    ss            shares short
    pb            price to book
    beta          beta
    fs            float shares
    peg           peg ratio
    ev            enterprise value
    yield         yield
    ldv           last dividend value
{r if params else ''}{Style.DIM if not self.tickers else ''}
Returned tickers: {', '.join(self.tickers)}
>   ca            take these to comparison analysis menu
{r if not self.tickers else ''}"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.insider_parser.parse_known_args(
            an_input.split()
        )

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
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    @try_except
    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker, self.start, self.interval, self.stock = load(
            other_args, self.ticker, self.start, self.interval, self.stock
        )
        if self.ticker:
            data = yf.utils.get_json(f"https://finance.yahoo.com/quote/{self.ticker}")

            if "summaryProfile" in data:
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

                if mktcap < 2_000_000_000:
                    self.mktcap = "Small"
                elif mktcap > 10_000_000_000:
                    self.mktcap = "Large"
                else:
                    self.mktcap = "Mid"

            self.stocks_data = {}

    @try_except
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

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        possible_industries = financedatabase_model.get_industries(
            country=self.country,
            sector=self.sector,
        )

        if ns_parser.name:
            if " ".join(ns_parser.name) in possible_industries:
                self.industry = " ".join(ns_parser.name)
                # if we get the industry, then we also automatically know the sector
                self.sector = financedatabase_model.get_sectors(industry=self.industry)[
                    0
                ]
            else:
                print(f"Industry '{' '.join(ns_parser.name)}' does not exist.")

                similar_cmd = difflib.get_close_matches(
                    " ".join(ns_parser.name),
                    possible_industries,
                    n=1,
                    cutoff=0.75,
                )

                if similar_cmd:
                    print(f"Replacing by '{similar_cmd[0]}'")
                    self.industry = similar_cmd[0]
                    # if we get the industry, then we also automatically know the sector
                    self.sector = financedatabase_model.get_sectors(
                        industry=self.industry
                    )[0]

                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        possible_industries,
                        n=1,
                        cutoff=0.5,
                    )
                    if similar_cmd:
                        print(f"Did you mean '{similar_cmd[0]}'?")

        else:
            for industry in possible_industries:
                print(industry)

        self.stocks_data = {}
        print("")

    @try_except
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

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        possible_sectors = financedatabase_model.get_sectors(
            self.industry, self.country
        )

        if ns_parser.name:
            if " ".join(ns_parser.name) in possible_sectors:
                self.sector = " ".join(ns_parser.name)
            else:
                print(f"Sector '{' '.join(ns_parser.name)}' does not exist.")

                similar_cmd = difflib.get_close_matches(
                    " ".join(ns_parser.name),
                    possible_sectors,
                    n=1,
                    cutoff=0.75,
                )

                if similar_cmd:
                    print(f"Replacing by '{similar_cmd[0]}'")
                    self.sector = similar_cmd[0]

                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        possible_sectors,
                        n=1,
                        cutoff=0.5,
                    )
                    if similar_cmd:
                        print(f"Did you mean '{similar_cmd[0]}'?")

        else:
            for sector in possible_sectors:
                print(sector)

        self.stocks_data = {}
        print("")

    @try_except
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

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        possible_countries = financedatabase_model.get_countries(
            industry=self.industry, sector=self.sector
        )

        if ns_parser.name:
            if " ".join(ns_parser.name) in possible_countries:
                self.country = " ".join(ns_parser.name)
            else:
                print(f"Country '{' '.join(ns_parser.name)}' does not exist.")

                similar_cmd = difflib.get_close_matches(
                    " ".join(ns_parser.name),
                    possible_countries,
                    n=1,
                    cutoff=0.75,
                )

                if similar_cmd:
                    print(f"Replacing by '{similar_cmd[0]}'")
                    self.country = similar_cmd[0]

                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        possible_countries,
                        n=1,
                        cutoff=0.5,
                    )
                    if similar_cmd:
                        print(f"Did you mean '{similar_cmd[0]}'?")

        else:
            for country in possible_countries:
                print(country)

        self.stocks_data = {}
        print("")

    @try_except
    def call_mktcap(self, other_args: List[str]):
        """Process mktcap command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mktcap",
            description="Set mktcap between small, mid or large",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            choices=["Small", "Mid", "Large", "small", "mid", "large"],
            help="market cap to select",
        )

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.name:
            self.mktcap = ns_parser.name.capitalize()

        else:
            print("Select between market cap: Small, Mid and Large")

        self.stocks_data = {}
        print("")

    @try_except
    def call_exchange(self, other_args: List[str]):
        """Process exchange command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="exchange",
            description="Swap exclude international exchanges flag",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        self.exclude_exhanges = not self.exclude_exhanges

        self.stocks_data = {}
        print("")

    @try_except
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
            "--parameter",
            type=str,
            dest="parameter",
            choices=["industry", "sector", "country", "mktcap"],
            help="parameter to clear",
        )

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

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

        self.exclude_exhanges = True
        self.ticker = ""
        self.stocks_data = {}

        print("")

    @try_except
    def call_roa(self, other_args: List[str]):
        """Process roa command"""
        self.display_metric_financials(
            other_args, "roa", "Return on Assets", "financialData", "returnOnAssets"
        )

    @try_except
    def call_roe(self, other_args: List[str]):
        """Process roe command"""
        self.display_metric_financials(
            other_args, "roe", "Return on Equity", "financialData", "returnOnEquity"
        )

    @try_except
    def call_qr(self, other_args: List[str]):
        """Process qr command"""
        self.display_metric_financials(
            other_args, "qr", "Quick Ratio", "financialData", "quickRatio"
        )

    @try_except
    def call_cr(self, other_args: List[str]):
        """Process cr command"""
        self.display_metric_financials(
            other_args, "cr", "Current Ratio", "financialData", "currentRatio"
        )

    @try_except
    def call_rg(self, other_args: List[str]):
        """Process rg command"""
        self.display_metric_financials(
            other_args, "rg", "Revenue Growth", "financialData", "revenueGrowth"
        )

    @try_except
    def call_rec(self, other_args: List[str]):
        """Process rec command"""
        self.display_metric_financials(
            other_args,
            "rec",
            "Recommendation mean from multiple analysts",
            "financialData",
            "recommendationMean",
        )

    @try_except
    def call_td(self, other_args: List[str]):
        """Process td command"""
        self.display_metric_financials(
            other_args, "td", "Total Debt", "financialData", "totalDebt"
        )

    @try_except
    def call_ebitda(self, other_args: List[str]):
        """Process ebitda command"""
        self.display_metric_financials(
            other_args,
            "ebitda",
            "Earnings before interest, taxes, depreciation and amortization",
            "financialData",
            "ebitda",
        )

    @try_except
    def call_de(self, other_args: List[str]):
        """Process de command"""
        self.display_metric_financials(
            other_args, "de", "Debt to Equity", "financialData", "debtToEquity"
        )

    @try_except
    def call_tc(self, other_args: List[str]):
        """Process tc command"""
        self.display_metric_financials(
            other_args, "tc", "Total Cash", "financialData", "totalCash"
        )

    @try_except
    def call_tcs(self, other_args: List[str]):
        """Process tcs command"""
        self.display_metric_financials(
            other_args,
            "tcs",
            "Total Cash per Share",
            "financialData",
            "totalCashPerShare",
        )

    @try_except
    def call_tr(self, other_args: List[str]):
        """Process tr command"""
        self.display_metric_financials(
            other_args, "tr", "Total Revenue", "financialData", "totalRevenue"
        )

    @try_except
    def call_rps(self, other_args: List[str]):
        """Process rps command"""
        self.display_metric_financials(
            other_args, "rps", "Revenue per Share", "financialData", "revenuePerShare"
        )

    @try_except
    def call_eg(self, other_args: List[str]):
        """Process eg command"""
        self.display_metric_financials(
            other_args, "eg", "Earnings growth", "financialData", "earningsGrowth"
        )

    @try_except
    def call_pm(self, other_args: List[str]):
        """Process pm command"""
        self.display_metric_financials(
            other_args, "pm", "Profit margins", "financialData", "profitMargins"
        )

    @try_except
    def call_gp(self, other_args: List[str]):
        """Process gp command"""
        self.display_metric_financials(
            other_args, "gp", "Gross profits", "financialData", "grossProfits"
        )

    @try_except
    def call_gm(self, other_args: List[str]):
        """Process gm command"""
        self.display_metric_financials(
            other_args, "gm", "Gross margins", "financialData", "grossMargins"
        )

    @try_except
    def call_ocf(self, other_args: List[str]):
        """Process ocf command"""
        self.display_metric_financials(
            other_args,
            "ocf",
            "Operating cash flow",
            "financialData",
            "operatingCashflow",
        )

    @try_except
    def call_om(self, other_args: List[str]):
        """Process om command"""
        self.display_metric_financials(
            other_args, "om", "Operating margins", "financialData", "operatingMargins"
        )

    @try_except
    def call_fcf(self, other_args: List[str]):
        """Process fcf command"""
        self.display_metric_financials(
            other_args, "fcf", "Free Cash Flow", "financialData", "freeCashflow"
        )

    @try_except
    def call_ebitdam(self, other_args: List[str]):
        """Process ebitdam command"""
        self.display_metric_financials(
            other_args, "ebitdam", "EBITDA margins", "financialData", "ebitdaMargins"
        )

    @try_except
    def call_mc(self, other_args: List[str]):
        """Process mc command"""
        self.display_metric_financials(
            other_args, "mc", "Market Cap", "price", "marketCap"
        )

    @try_except
    def call_fte(self, other_args: List[str]):
        """Process fte command"""
        self.display_metric_financials(
            other_args,
            "fte",
            "Full Time Employees",
            "summaryProfile",
            "fullTimeEmployees",
        )

    @try_except
    def call_er(self, other_args: List[str]):
        """Process er command"""
        self.display_metric_financials(
            other_args,
            "er",
            "Enterprise to Revenue",
            "defaultKeyStatistics",
            "enterpriseToRevenue",
        )

    @try_except
    def call_bv(self, other_args: List[str]):
        """Process bv command"""
        self.display_metric_financials(
            other_args, "bv", "Book value", "defaultKeyStatistics", "bookValue"
        )

    @try_except
    def call_ss(self, other_args: List[str]):
        """Process ss command"""
        self.display_metric_financials(
            other_args, "ss", "Shares Short", "defaultKeyStatistics", "sharesShort"
        )

    @try_except
    def call_pb(self, other_args: List[str]):
        """Process pb command"""
        self.display_metric_financials(
            other_args, "pb", "Price to Book", "defaultKeyStatistics", "priceToBook"
        )

    @try_except
    def call_beta(self, other_args: List[str]):
        """Process beta command"""
        self.display_metric_financials(
            other_args, "beta", "Beta", "defaultKeyStatistics", "beta"
        )

    @try_except
    def call_fs(self, other_args: List[str]):
        """Process fs command"""
        self.display_metric_financials(
            other_args, "fs", "Float Shares", "defaultKeyStatistics", "floatShares"
        )

    @try_except
    def call_sr(self, other_args: List[str]):
        """Process sr command"""
        self.display_metric_financials(
            other_args, "sr", "Short Ratio", "defaultKeyStatistics", "shortRatio"
        )

    @try_except
    def call_peg(self, other_args: List[str]):
        """Process peg command"""
        self.display_metric_financials(
            other_args, "peg", "PEG Ratio", "defaultKeyStatistics", "pegRatio"
        )

    @try_except
    def call_ev(self, other_args: List[str]):
        """Process ev command"""
        self.display_metric_financials(
            other_args,
            "ev",
            "Enterprise Value",
            "defaultKeyStatistics",
            "enterpriseValue",
        )

    @try_except
    def call_yield(self, other_args: List[str]):
        """Process yield command"""
        self.display_metric_financials(
            other_args, "yield", "Yield", "defaultKeyStatistics", "yield"
        )

    @try_except
    def call_ldv(self, other_args: List[str]):
        """Process ldv command"""
        self.display_metric_financials(
            other_args,
            "ldv",
            "Last Dividend Value",
            "defaultKeyStatistics",
            "lastDividendValue",
        )

    @try_except
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        if not self.country:
            print("The country parameter needs to be selected!\n")
        else:
            financedatabase_view.display_companies_per_sector_in_country(
                self.country,
                self.mktcap,
                self.exclude_exhanges,
                ns_parser.export,
                ns_parser.raw,
                ns_parser.max_sectors_to_display,
                ns_parser.min_pct_to_display_sector,
            )

    @try_except
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        if not self.country:
            print("The country parameter needs to be selected!\n")
        else:
            financedatabase_view.display_companies_per_industry_in_country(
                self.country,
                self.mktcap,
                self.exclude_exhanges,
                ns_parser.export,
                ns_parser.raw,
                ns_parser.max_industries_to_display,
                ns_parser.min_pct_to_display_industry,
            )

    @try_except
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        if not self.sector:
            print("The sector parameter needs to be selected!\n")
        else:
            financedatabase_view.display_companies_per_industry_in_sector(
                self.sector,
                self.mktcap,
                self.exclude_exhanges,
                ns_parser.export,
                ns_parser.raw,
                ns_parser.max_industries_to_display,
                ns_parser.min_pct_to_display_industry,
            )

    @try_except
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        if not self.sector:
            print("The sector parameter needs to be selected!\n")
        else:
            financedatabase_view.display_companies_per_country_in_sector(
                self.sector,
                self.mktcap,
                self.exclude_exhanges,
                ns_parser.export,
                ns_parser.raw,
                ns_parser.max_countries_to_display,
                ns_parser.min_pct_to_display_country,
            )

    @try_except
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        if not self.industry:
            print("The industry parameter needs to be selected!\n")
        else:
            financedatabase_view.display_companies_per_country_in_industry(
                self.industry,
                self.mktcap,
                self.exclude_exhanges,
                ns_parser.export,
                ns_parser.raw,
                ns_parser.max_countries_to_display,
                ns_parser.min_pct_to_display_country,
            )

    def call_ca(self, _):
        """Call the comparison analysis menu with selected tickers"""
        if self.tickers:
            return ca_controller.menu(self.tickers)

        print("No main ticker loaded to go into comparison analysis menu", "\n")


def menu(
    ticker: str,
    start: str,
    interval: str,
    stock: pd.DataFrame,
):
    """Sector and Industry Analysis Menu"""
    sia_controller = SectorIndustryAnalysisController(ticker, start, interval, stock)
    sia_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in sia_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(sia)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(sia)> ")

        try:
            process_input = sia_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, sia_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
