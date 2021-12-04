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
        "cpi",
        "cps",
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

    def print_help(self):
        """Print help"""
        params = not any([self.industry, self.sector, self.country])

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
{Style.DIM if not self.country else ''}
Country (and Market Cap)
    cpi           companies per industry in country
    cps           companies per sector in country{Style.RESET_ALL if not self.country else ''}
{Style.DIM if params else ''}
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
    rec           recommendation mean{Style.RESET_ALL if params else ''}
{Style.DIM if not self.tickers else ''}
Returned tickers: {', '.join(self.tickers)}
>   ca            take these to comparison analysis menu
{Style.RESET_ALL if not self.tickers else ''}"""
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

        if ns_parser.name:
            if " ".join(ns_parser.name) in financedatabase_model.get_industries():
                self.industry = " ".join(ns_parser.name)
            else:
                print(f"Industry '{' '.join(ns_parser.name)}' does not exist.")

                similar_cmd = difflib.get_close_matches(
                    " ".join(ns_parser.name),
                    financedatabase_model.get_industries(),
                    n=1,
                    cutoff=0.75,
                )

                if similar_cmd:
                    print(f"Replacing by '{similar_cmd[0]}'")
                    self.industry = similar_cmd[0]

                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        financedatabase_model.get_industries(),
                        n=1,
                        cutoff=0.5,
                    )
                    if similar_cmd:
                        print(f"Did you mean '{similar_cmd[0]}'?")

        else:
            financedatabase_view.display_industries()

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

        if ns_parser.name:
            if " ".join(ns_parser.name) in financedatabase_model.get_sectors():
                self.sector = " ".join(ns_parser.name)
            else:
                print(f"Sector '{' '.join(ns_parser.name)}' does not exist.")

                similar_cmd = difflib.get_close_matches(
                    " ".join(ns_parser.name),
                    financedatabase_model.get_sectors(),
                    n=1,
                    cutoff=0.75,
                )

                if similar_cmd:
                    print(f"Replacing by '{similar_cmd[0]}'")
                    self.sector = similar_cmd[0]

                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        financedatabase_model.get_sectors(),
                        n=1,
                        cutoff=0.5,
                    )
                    if similar_cmd:
                        print(f"Did you mean '{similar_cmd[0]}'?")

        else:
            financedatabase_view.display_sectors()

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

        if ns_parser.name:
            if " ".join(ns_parser.name) in financedatabase_model.get_countries():
                self.country = " ".join(ns_parser.name)
            else:
                print(f"Country '{' '.join(ns_parser.name)}' does not exist.")

                similar_cmd = difflib.get_close_matches(
                    " ".join(ns_parser.name),
                    financedatabase_model.get_countries(),
                    n=1,
                    cutoff=0.75,
                )

                if similar_cmd:
                    print(f"Replacing by '{similar_cmd[0]}'")
                    self.country = similar_cmd[0]

                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(ns_parser.name),
                        financedatabase_model.get_countries(),
                        n=1,
                        cutoff=0.5,
                    )
                    if similar_cmd:
                        print(f"Did you mean '{similar_cmd[0]}'?")

        else:
            financedatabase_view.display_countries()

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
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="roa",
            description="Return on Assets",
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
            "returnOnAssets",
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

    @try_except
    def call_roe(self, other_args: List[str]):
        """Process roe command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="roe",
            description="Return on Equity",
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
            "returnOnEquity",
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

    @try_except
    def call_qr(self, other_args: List[str]):
        """Process qr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="qr",
            description="Quick Ratio",
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
            "quickRatio",
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

    @try_except
    def call_cr(self, other_args: List[str]):
        """Process cr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cr",
            description="Current Ratio",
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
            "currentRatio",
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

    @try_except
    def call_rg(self, other_args: List[str]):
        """Process rg command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rg",
            description="Revenue Growth",
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
            "revenueGrowth",
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

    @try_except
    def call_rec(self, other_args: List[str]):
        """Process rec command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rec",
            description="Recommendation mean from multiple analysts",
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
            "recommendationMean",
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

    @try_except
    def call_td(self, other_args: List[str]):
        """Process td command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="td",
            description="Total Debt",
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
            "totalDebt",
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

    @try_except
    def call_ebitda(self, other_args: List[str]):
        """Process ebitda command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ebitda",
            description="Earnings before interest, taxes, depreciation and amortization",
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
            "ebitda",
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

    @try_except
    def call_cps(self, other_args: List[str]):
        """Process cps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cps",
            description="Companies per sector in a country",
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
            print("The country parameter needs to be selected!")
        else:
            financedatabase_view.display_companies_per_sector(
                self.country,
                self.mktcap,
                ns_parser.export,
                ns_parser.raw,
                ns_parser.max_sectors_to_display,
                ns_parser.min_pct_to_display_sector,
            )
        print("")

    @try_except
    def call_cpi(self, other_args: List[str]):
        """Process cpi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpi",
            description="Companies per industry in a country",
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
            print("The country parameter needs to be selected!")
        else:
            financedatabase_view.display_companies_per_industry(
                self.country,
                self.mktcap,
                ns_parser.export,
                ns_parser.raw,
                ns_parser.max_sectors_to_display,
                ns_parser.min_pct_to_display_sector,
            )
        print("")

    @try_except
    def call_de(self, other_args: List[str]):
        """Process de command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="de",
            description="Debt to equity",
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
            "debtToEquity",
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

    @try_except
    def call_tc(self, other_args: List[str]):
        """Process tc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tc",
            description="Total cash",
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
            "totalCash",
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

    @try_except
    def call_tcs(self, other_args: List[str]):
        """Process tcs command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tcs",
            description="Total cash per share",
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
            "totalCashPerShare",
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

    @try_except
    def call_tr(self, other_args: List[str]):
        """Process tr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tr",
            description="Total revenue",
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
            "totalRevenue",
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

    @try_except
    def call_rps(self, other_args: List[str]):
        """Process rps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rps",
            description="Revenue per share",
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
            "revenuePerShare",
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

    @try_except
    def call_eg(self, other_args: List[str]):
        """Process eg command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="eg",
            description="Earnings growth",
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
            "earningsGrowth",
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

    @try_except
    def call_pm(self, other_args: List[str]):
        """Process pm command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pm",
            description="Profit margins",
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
            "profitMargins",
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

    @try_except
    def call_gp(self, other_args: List[str]):
        """Process gp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gp",
            description="Gross profits",
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
            "grossProfits",
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

    @try_except
    def call_gm(self, other_args: List[str]):
        """Process gm command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gm",
            description="Gross margins",
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
            "grossMargins",
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

    @try_except
    def call_ocf(self, other_args: List[str]):
        """Process ocf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ocf",
            description="Operating cash flow",
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
            "operatingCashflow",
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

    @try_except
    def call_om(self, other_args: List[str]):
        """Process om command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="om",
            description="Operating margins",
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
            "operatingMargins",
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

    @try_except
    def call_fcf(self, other_args: List[str]):
        """Process fcf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fcf",
            description="Free cash flow",
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
            "freeCashflow",
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

    @try_except
    def call_ebitdam(self, other_args: List[str]):
        """Process ebitdam command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ebitdam",
            description="Ebitda margins",
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
            "ebitdaMargins",
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
