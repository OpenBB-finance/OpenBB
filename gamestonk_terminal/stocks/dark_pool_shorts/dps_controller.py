""" Dark Pool Shorts Controller """
__docformat__ = "numpy"

import argparse
import difflib
from typing import List
from datetime import datetime, timedelta
from colorama import Style
import pandas as pd
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import EXPORT_BOTH_RAW_DATA_AND_FIGURES, get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    valid_date,
    check_int_range,
    try_except,
    system_clear,
)
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.stocks.dark_pool_shorts import (
    yahoofinance_view,
    stockgrid_view,
    shortinterest_view,
    quandl_view,
    sec_view,
    finra_view,
    nyse_view,
)


class DarkPoolShortsController:
    """Dark Pool Shorts Controller"""

    # Command choices
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "load",
    ]

    CHOICES_COMMANDS = [
        "shorted",
        "hsi",
        "prom",
        "pos",
        "sidtc",
    ]

    CHOICES_COMMANDS_WITH_TICKER = ["psi", "dpotc", "ftd", "spos", "volexch"]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_COMMANDS_WITH_TICKER

    def __init__(self, ticker: str, start: str, stock: pd.DataFrame):
        """Constructor"""
        self.ticker = ticker
        self.start = start
        self.stock = stock

        self.disc_parser = argparse.ArgumentParser(add_help=False, prog="dps")
        self.disc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        help_text = f"""
Dark Pool Shorts:
    cls            clear screen
    ?/help         show this menu again
    q              quit this menu, and shows back to main menu
    quit           quit to abandon program
    load           load a specific stock ticker for analysis

Yahoo Finance:
    shorted        show most shorted stocks
shortinterest.com:
    hsi            show top high short interest stocks of over 20% ratio
FINRA:
    prom           promising tickers based on dark pool shares regression
Stockgrid:
    pos            dark pool short position
    sidtc          short interest and days to cover
{Style.DIM if not self.ticker else ''}
Ticker: {self.ticker or None}

FINRA:
    dpotc          dark pools (ATS) vs OTC data
SEC:
    ftd            fails-to-deliver data
Stockgrid:
    spos           net short vs position
Quandl/Stockgrid:
    psi            price vs short interest volume
NYSE:
    volexch        short volume for ARCA,Amex,Chicago,NYSE and national exchanges
{Style.RESET_ALL if not self.ticker else ''}"""
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

        (known_args, other_args) = self.disc_parser.parse_known_args(an_input.split())

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
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_stock_candidate = stocks_helper.load(
            ns_parser.ticker,
            ns_parser.start,
        )

        if not df_stock_candidate.empty:
            self.stock = df_stock_candidate
            self.start = ns_parser.start
            if "." in ns_parser.ticker:
                self.ticker = ns_parser.ticker.upper().split(".")[0]
            else:
                self.ticker = ns_parser.ticker.upper()

    @try_except
    def call_shorted(self, other_args: List[str]):
        """Process shorted command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="shorted",
            description="Print up to 25 top ticker most shorted. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the most shorted stocks to retrieve.",
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
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_most_shorted(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_hsi(self, other_args: List[str]):
        """Process hsi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hsi",
            description="""
                Print top stocks being more heavily shorted. HighShortInterest.com provides
                a convenient sorted database of stocks which have a short interest of over
                20 percent. Additional key data such as the float, number of outstanding shares,
                and company industry is displayed. Data is presented for the Nasdaq Stock Market,
                the New York Stock Exchange, and the American Stock Exchange. [Source: www.highshortinterest.com]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=10,
            help="Number of top stocks to print.",
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

        shortinterest_view.high_short_interest(
            num=ns_parser.n_num,
            export=ns_parser.export,
        )

    @try_except
    def call_prom(self, other_args: List[str]):
        """Process prom command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="prom",
            description="Display dark pool (ATS) data of tickers with growing trades activity",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=1_000,
            help="Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity.",
        )
        parser.add_argument(
            "-t",
            "--top",
            action="store",
            dest="n_top",
            type=check_positive,
            default=5,
            help="List of tickers from most promising with better linear regression slope.",
        )
        parser.add_argument(
            "--tier",
            action="store",
            dest="tier",
            type=str,
            choices=["T1", "T2", "OTCE"],
            default="",
            help="Tier to process data from.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finra_view.darkpool_otc(
            num=ns_parser.n_num,
            promising=ns_parser.n_top,
            tier=ns_parser.tier,
            export=ns_parser.export,
        )

    @try_except
    def call_pos(self, other_args: List[str]):
        """Process pos command"""
        parser = argparse.ArgumentParser(
            prog="pos",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Get dark pool short positions. [Source: Stockgrid]",
        )
        parser.add_argument(
            "-n",
            "--number",
            help="Number of top tickers to show",
            type=check_positive,
            default=10,
            dest="num",
        )
        parser.add_argument(
            "-s",
            "--sort",
            help="Field for which to sort by, where 'sv': Short Vol. (1M), "
            "'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. (1M), "
            "'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position (1M), "
            "'dpp_dollar': DP Position ($1B)",
            choices=["sv", "sv_pct", "nsv", "nsv_dollar", "dpp", "dpp_dollar"],
            default="dpp_dollar",
            dest="sort_field",
        )
        parser.add_argument(
            "-a",
            "--ascending",
            action="store_true",
            default=False,
            dest="ascending",
            help="Data in ascending order",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stockgrid_view.dark_pool_short_positions(
            num=ns_parser.num,
            sort_field=ns_parser.sort_field,
            ascending=ns_parser.ascending,
            export=ns_parser.export,
        )

    @try_except
    def call_sidtc(self, other_args: List[str]):
        """Process sidtc command"""
        parser = argparse.ArgumentParser(
            prog="sidtc",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Print short interest and days to cover. [Source: Stockgrid]",
        )
        parser.add_argument(
            "-n",
            "--number",
            help="Number of top tickers to show",
            type=check_positive,
            default=10,
            dest="num",
        )
        parser.add_argument(
            "-s",
            "--sort",
            help="Field for which to sort by, where 'float': Float Short %%, "
            "'dtc': Days to Cover, 'si': Short Interest",
            choices=["float", "dtc", "si"],
            default="float",
            dest="sort_field",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stockgrid_view.short_interest_days_to_cover(
            num=ns_parser.num,
            sort_field=ns_parser.sort_field,
            export=ns_parser.export,
        )

    @try_except
    def call_dpotc(self, other_args: List[str]):
        """Process dpotc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dpotc",
            description="Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.\n")
            return

        finra_view.darkpool_ats_otc(
            ticker=self.ticker,
            export=ns_parser.export,
        )

    @try_except
    def call_ftd(self, other_args: List[str]):
        """Process ftd command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="ftd",
            description="""Prints latest fails-to-deliver data. [Source: SEC]""",
        )
        parser.add_argument(
            "-s",
            "--start",
            action="store",
            dest="start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
            help="start of datetime to see FTD",
        )
        parser.add_argument(
            "-e",
            "--end",
            action="store",
            dest="end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            help="end of datetime to see FTD",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=0,
            help="number of latest fails-to-deliver being printed",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.\n")
            return

        sec_view.fails_to_deliver(
            ticker=self.ticker,
            stock=self.stock,
            start=ns_parser.start,
            end=ns_parser.end,
            num=ns_parser.n_num,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
    def call_spos(self, other_args: List[str]):
        """Process spos command"""
        parser = argparse.ArgumentParser(
            prog="spos",
            add_help=False,
            description="Shows Net Short Vol. vs Position. [Source: Stockgrid]",
        )
        parser.add_argument(
            "-n",
            "--number",
            help="Number of last open market days to show",
            type=check_positive,
            default=10 if "-r" in other_args else 120,
            dest="num",
        )
        parser.add_argument(
            "-r",
            action="store_true",
            default=False,
            help="Flag to print raw data instead",
            dest="raw",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.\n")
            return

        stockgrid_view.net_short_position(
            ticker=self.ticker,
            num=ns_parser.num,
            raw=ns_parser.raw,
            export=ns_parser.export,
        )

    @try_except
    def call_psi(self, other_args: List[str]):
        """Process psi command"""
        parser = argparse.ArgumentParser(
            prog="psi",
            add_help=False,
            description="Shows price vs short interest volume. [Source: Quandl/Stockgrid]",
        )
        parser.add_argument(
            "--source",
            choices=["quandl", "stockgrid"],
            default="",
            dest="stockgrid",
            help="Source of short interest volume",
        )
        parser.add_argument(
            "--nyse",
            action="store_true",
            default=False,
            dest="b_nyse",
            help="ONLY QUANDL SOURCE. Data from NYSE flag. Otherwise comes from NASDAQ.",
        )
        parser.add_argument(
            "-n",
            "--number",
            help="Number of last open market days to show",
            type=check_positive,
            default=10 if "-r" in other_args else 120,
            dest="num",
        )
        parser.add_argument(
            "-r",
            action="store_true",
            default=False,
            help="Flag to print raw data instead",
            dest="raw",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.\n")
            return

        if "quandl" in other_args:
            quandl_view.short_interest(
                ticker=self.ticker,
                nyse=ns_parser.b_nyse,
                days=ns_parser.num,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )
        else:
            stockgrid_view.short_interest_volume(
                ticker=self.ticker,
                num=ns_parser.num,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @try_except
    def call_volexch(self, other_args: List[str]):
        """Process volexch command"""
        parser = argparse.ArgumentParser(
            prog="volexch",
            add_help=False,
            description="Displays short volume based on exchange.",
        )
        parser.add_argument(
            "--raw",
            help="Display raw data",
            dest="raw",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-s",
            "--sort",
            help="Column to sort by",
            dest="sort",
            type=str,
            default="",
            choices=["", "NetShort", "Date", "TotalVolume", "PctShort"],
        )
        parser.add_argument(
            "-a",
            "--asc",
            help="Sort in ascending order",
            dest="asc",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-m",
            "--mpl",
            help="Display plot using matplotlb.",
            dest="mpl",
            action="store_true",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded.  Use `load ticker` first.")
            return
        nyse_view.display_short_by_exchange(
            ticker=self.ticker,
            raw=ns_parser.raw,
            sort=ns_parser.sort,
            asc=ns_parser.asc,
            mpl=ns_parser.mpl,
            export=ns_parser.export,
        )


def menu(ticker: str = "", start: str = "", stock: pd.DataFrame = pd.DataFrame()):
    """Dark Pool Shorts Menu

    Parameters
    ----------
    stock : DataFrame
        Due diligence stock dataframe
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    """
    dps_controller = DarkPoolShortsController(ticker, start, stock)
    dps_controller.call_help(None)

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in dps_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (stocks)>(dps)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(dps)> ")

        try:
            plt.close("all")

            process_input = dps_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, dps_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
