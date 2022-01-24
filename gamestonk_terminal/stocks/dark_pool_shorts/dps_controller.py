""" Dark Pool and Shorts Controller Module """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime, timedelta
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    valid_date,
    check_int_range,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
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


class DarkPoolShortsController(BaseController):
    """Dark Pool Shorts Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "shorted",
        "hsi",
        "prom",
        "pos",
        "sidtc",
        "psi",
        "dpotc",
        "ftd",
        "spos",
        "volexch",
    ]
    PATH = "/stocks/dps/"

    def __init__(
        self, ticker: str, start: str, stock: pd.DataFrame, queue: List[str] = None
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start
        self.stock = stock

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "dps"]
        return []

    def print_help(self):
        """Print help"""
        has_ticker_start = "" if self.ticker else "[unvl]"
        has_ticker_end = "" if self.ticker else "[/unvl]"
        help_text = f"""[cmds]
    load           load a specific stock ticker for analysis

[src][Yahoo Finance][/src]
    shorted        show most shorted stocks
[src][Shortinterest.com][/src]
    hsi            show top high short interest stocks of over 20% ratio
[src][FINRA][/src]
    prom           promising tickers based on dark pool shares regression
[src][Stockgrid][/src]
    pos            dark pool short position
    sidtc          short interest and days to cover
{has_ticker_start}
[param]Ticker: [/param]{self.ticker or None}

[src][FINRA][/src]
    dpotc          dark pools (ATS) vs OTC data
[src][SEC][/src]
    ftd            fails-to-deliver data
[src][Stockgrid][/src]
    spos           net short vs position
[src][Quandl/Stockgrid][/src]
    psi            price vs short interest volume
[src][NYSE][/src]
    volexch        short volume for ARCA,Amex,Chicago,NYSE and national exchanges[/cmds]
{has_ticker_end}"""
        console.print(text=help_text, menu="Stocks - Dark Pool and Short data")

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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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

    def call_shorted(self, other_args: List[str]):
        """Process shorted command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="shorted",
            description="Print up to 25 top ticker most shorted. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=10,
            help="Limit of the most shorted stocks to retrieve.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_most_shorted(
                num_stocks=ns_parser.limit,
                export=ns_parser.export,
            )

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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=10,
            help="Limit of the top heavily shorted stocks to retrieve.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            shortinterest_view.high_short_interest(
                num=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_prom(self, other_args: List[str]):
        """Process prom command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="prom",
            description="Display dark pool (ATS) data of tickers with growing trades activity using linear regression.",
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of most promising tickers to display.",
        )
        parser.add_argument(
            "-t",
            "--tier",
            action="store",
            dest="tier",
            type=str,
            choices=["T1", "T2", "OTCE"],
            default="",
            help="Tier to process data from.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finra_view.darkpool_otc(
                num=ns_parser.n_num,
                promising=ns_parser.limit,
                tier=ns_parser.tier,
                export=ns_parser.export,
            )

    def call_pos(self, other_args: List[str]):
        """Process pos command"""
        parser = argparse.ArgumentParser(
            prog="pos",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Get dark pool short positions. [Source: Stockgrid]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of tickers to display.",
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stockgrid_view.dark_pool_short_positions(
                num=ns_parser.limit,
                sort_field=ns_parser.sort_field,
                ascending=ns_parser.ascending,
                export=ns_parser.export,
            )

    def call_sidtc(self, other_args: List[str]):
        """Process sidtc command"""
        parser = argparse.ArgumentParser(
            prog="sidtc",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Print short interest and days to cover. [Source: Stockgrid]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of tickers to display.",
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stockgrid_view.short_interest_days_to_cover(
                num=ns_parser.limit,
                sort_field=ns_parser.sort_field,
                export=ns_parser.export,
            )

    def call_dpotc(self, other_args: List[str]):
        """Process dpotc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dpotc",
            description="Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                finra_view.darkpool_ats_otc(
                    ticker=self.ticker,
                    export=ns_parser.export,
                )
            else:
                console.print("No ticker loaded.\n")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                sec_view.fails_to_deliver(
                    ticker=self.ticker,
                    stock=self.stock,
                    start=ns_parser.start,
                    end=ns_parser.end,
                    num=ns_parser.n_num,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                console.print("No ticker loaded.\n")

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
            "--raw",
            action="store_true",
            default=False,
            help="Flag to print raw data instead",
            dest="raw",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                stockgrid_view.net_short_position(
                    ticker=self.ticker,
                    num=ns_parser.num,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                console.print("No ticker loaded.\n")

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
        if "quandl" in other_args:
            parser.add_argument(
                "--nyse",
                action="store_true",
                default=False,
                dest="b_nyse",
                help="Data from NYSE flag. Otherwise comes from NASDAQ.",
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
            "--raw",
            action="store_true",
            default=False,
            help="Flag to print raw data instead",
            dest="raw",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
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
            else:
                console.print("No ticker loaded.\n")

    def call_volexch(self, other_args: List[str]):
        """Process volexch command"""
        parser = argparse.ArgumentParser(
            prog="volexch",
            add_help=False,
            description="Displays short volume based on exchange.",
        )
        parser.add_argument(
            "-r",
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
            "-p",
            "--plotly",
            help="Display plot using interactive plotly.",
            dest="plotly",
            action="store_false",
            default=True,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                nyse_view.display_short_by_exchange(
                    ticker=self.ticker,
                    raw=ns_parser.raw,
                    sort=ns_parser.sort,
                    asc=ns_parser.asc,
                    mpl=ns_parser.plotly,
                    export=ns_parser.export,
                )
            else:
                console.print("No ticker loaded.  Use `load ticker` first.")
