"""Sector and Industry Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union
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
from gamestonk_terminal.stocks import stocks_helper
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

    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]
    CHOICES_COMMANDS = [
        "load",
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
        "sama",
        "metric",
    ]
    CHOICES_MENUS = [
        "ca",
    ]
    CHOICES += CHOICES_COMMANDS + CHOICES_MENUS

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
    mktcap_choices = ["Small", "Mid", "Large", "small", "mid", "large"]
    clear_choices = ["industry", "sector", "country", "mktcap"]

    def __init__(
        self,
        ticker: str,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.sia_parser = argparse.ArgumentParser(add_help=False, prog="sia")
        self.sia_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            self.choices: dict = {c: {} for c in self.CHOICES}
            self.choices["mktcap"] = {c: None for c in self.mktcap_choices}
            self.choices["clear"] = {c: None for c in self.clear_choices}
            self.choices["metric"] = {c: None for c in self.metric_choices}

        if queue:
            self.queue = queue
        else:
            self.queue = list()

        self.country = "United States"
        self.sector = "Financial Services"
        self.industry = "Financial Data & Stock Exchanges"
        self.mktcap = "Large"
        self.exclude_exhanges = True

        self.ticker = ticker

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

    def print_help(self):
        """Print help"""
        params = not any([self.industry, self.sector, self.country])
        s = Style.DIM if not self.sector else ""
        i = Style.DIM if not self.industry else ""
        c = Style.DIM if not self.country else ""
        m = Style.DIM if not self.mktcap else ""
        r = Style.RESET_ALL
        help_text = f"""
    load          load a specific ticker and all it's corresponding parameters

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
    sama          see all metrics available
    metric        visualise financial metric across filters selected
{r if params else ''}{Style.DIM if len(self.tickers) == 0 else ''}
Returned tickers: {', '.join(self.tickers)}
>   ca            take these to comparison analysis menu
{r if len(self.tickers) == 0 else ''}"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.sia_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        if self.ticker:
            self.queue.insert(0, f"load {self.ticker}")
        self.queue.insert(0, "sia")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be"
            " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
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

                data = yf.utils.get_json(
                    f"https://finance.yahoo.com/quote/{self.ticker}"
                )

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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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
            choices=self.mktcap_choices,
            help="market cap to select",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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
        if ns_parser:
            self.exclude_exhanges = not self.exclude_exhanges
            print(
                f"Internationa exchanges {'excluded' if self.exclude_exhanges else 'included'}",
                "\n",
            )

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
            "--param",
            type=str,
            dest="parameter",
            choices=self.clear_choices,
            help="parameter to clear",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
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

            self.exclude_exhanges = True
            self.ticker = ""

            self.stocks_data = {}
            print("")

    @try_except
    def call_sama(self, other_args: List[str]):
        """Process sama command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sama",
            description="See all metrics available",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            help_text = """
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
        sr            short ratio
        peg           peg ratio
        ev            enterprise value
        fpe           forward P/E
            """
            print(help_text)

    @try_except
    def call_metric(self, other_args: List[str]):
        """Process metric command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="metric",
            description="Visualise a particular metric with the filters selected",
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
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
        if ns_parser:
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
        if ns_parser:
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
        if ns_parser:
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
        if ns_parser:
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
        if ns_parser:
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
            self.queue = ca_controller.menu(self.tickers, self.queue, from_submenu=True)
        else:
            print("No main ticker loaded to go into comparison analysis menu", "\n")


def menu(
    ticker: str,
    queue: List[str] = None,
):
    """Sector and Industry Analysis Menu"""
    sia_controller = SectorIndustryAnalysisController(ticker, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if sia_controller.queue and len(sia_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if sia_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(sia_controller.queue) > 1:
                    return sia_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = sia_controller.queue[0]
            sia_controller.queue = sia_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in sia_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/sia/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                sia_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and sia_controller.choices:
                sia_controller.choices["industry"] = {
                    i: None
                    for i in financedatabase_model.get_industries(
                        country=sia_controller.country, sector=sia_controller.sector
                    )
                }
                sia_controller.choices["sector"] = {
                    s: None
                    for s in financedatabase_model.get_sectors(
                        industry=sia_controller.industry, country=sia_controller.country
                    )
                }
                sia_controller.choices["country"] = {
                    c: None
                    for c in financedatabase_model.get_countries(
                        industry=sia_controller.industry, sector=sia_controller.sector
                    )
                }
                completer = NestedCompleter.from_nested_dict(sia_controller.choices)
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /stocks/sia/ $ ",
                        completer=completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/sia/ $ ")

        try:
            # Process the input command
            sia_controller.queue = sia_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/sia menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                sia_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        sia_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                sia_controller.queue.insert(0, an_input)
            else:
                print("\n")
