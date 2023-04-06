""" Dark Pool and Shorts Controller Module """
__docformat__ = "numpy"

import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_int_range,
    check_positive,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks.dark_pool_shorts import (
    finra_view,
    ibkr_view,
    quandl_view,
    sec_view,
    shortinterest_view,
    stockgrid_view,
    stocksera_view,
    yahoofinance_view,
)

logger = logging.getLogger(__name__)


class DarkPoolShortsController(StockBaseController):
    """Dark Pool Shorts Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "shorted",
        "ctb",
        "hsi",
        "prom",
        "pos",
        "sidtc",
        "psi",
        "dpotc",
        "ftd",
        "spos",
        # "volexch",
    ]
    POS_CHOICES = ["sv", "sv_pct", "nsv", "nsv_dollar", "dpp", "dpp_dollar"]
    PATH = "/stocks/dps/"
    CHOICES_GENERATION = True

    def __init__(
        self,
        ticker: str,
        start: str,
        stock: pd.DataFrame,
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.start = start
        self.stock = stock

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "dps"]
        return []

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/dps/")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_cmd("shorted")
        mt.add_cmd("ctb")
        mt.add_cmd("hsi")
        mt.add_cmd("prom")
        mt.add_cmd("pos")
        mt.add_cmd("sidtc")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.ticker or "")
        mt.add_raw("\n")
        mt.add_cmd("dpotc", self.ticker)
        mt.add_cmd("ftd", self.ticker)
        mt.add_cmd("spos", self.ticker)
        mt.add_cmd("psi", self.ticker)
        console.print(text=mt.menu_text, menu="Stocks - Dark Pool and Short data")

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_most_shorted(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ctb(self, other_args: List[str]):
        """Process CTB command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ctb",
            description="Show cost to borrow of stocks. [Source: Stocksera/Interactive Broker]",
        )
        parser.add_argument(
            "-n",
            "--number",
            action="store",
            dest="number",
            type=check_int_range(1, 10000),
            default=20,
            help="Number of records to retrieve.",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.source == "InteractiveBrokers":
                ibkr_view.display_cost_to_borrow(
                    limit=ns_parser.number,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "Stocksera":
                stocksera_view.cost_to_borrow(
                    self.ticker, limit=ns_parser.number, raw=ns_parser.raw
                )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            shortinterest_view.high_short_interest(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finra_view.darkpool_otc(
                input_limit=ns_parser.n_num,
                limit=ns_parser.limit,
                tier=ns_parser.tier,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            help="Field for which to sort by, where 'sv': Short Vol. [1M], "
            "'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M], "
            "'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M], "
            "'dpp_dollar': DP Position ($1B)",
            choices=self.POS_CHOICES,
            default="dpp_dollar",
            dest="sort_field",
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stockgrid_view.dark_pool_short_positions(
                limit=ns_parser.limit,
                sortby=ns_parser.sort_field,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stockgrid_view.short_interest_days_to_cover(
                limit=ns_parser.limit,
                sortby=ns_parser.sort_field,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_dpotc(self, other_args: List[str]):
        """Process dpotc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dpotc",
            description="Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                finra_view.darkpool_ats_otc(
                    symbol=self.ticker,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded.\n")

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                sec_view.fails_to_deliver(
                    symbol=self.ticker,
                    data=self.stock,
                    start_date=ns_parser.start.strftime("%Y-%m-%d"),
                    end_date=ns_parser.end.strftime("%Y-%m-%d"),
                    limit=ns_parser.n_num,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded.\n")

    @log_start_end(log=logger)
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
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                stockgrid_view.net_short_position(
                    symbol=self.ticker,
                    limit=ns_parser.num,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("No ticker loaded.\n")

    @log_start_end(log=logger)
    def call_psi(self, other_args: List[str]):
        """Process psi command"""
        parser = argparse.ArgumentParser(
            prog="psi",
            add_help=False,
            description="Shows price vs short interest volume. [Source: Quandl/Stockgrid]",
        )
        parser.add_argument(
            "--nyse",
            action="store_true",
            default=False,
            dest="b_nyse",
            help="Data from NYSE flag. Otherwise comes from NASDAQ. Only works for Quandl.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10 if "-r" in other_args else 120,
        )
        if ns_parser:
            if self.ticker:
                if ns_parser.source == "Quandl":
                    quandl_view.short_interest(
                        symbol=self.ticker,
                        nyse=ns_parser.b_nyse,
                        limit=ns_parser.limit,
                        raw=ns_parser.raw,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
                    )
                else:
                    stockgrid_view.short_interest_volume(
                        symbol=self.ticker,
                        limit=ns_parser.limit,
                        raw=ns_parser.raw,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
                    )
            else:
                console.print("No ticker loaded.\n")

    # TODO: Load back in once data is properly stored
    # @log_start_end(log=logger)
    # def call_volexch(self, other_args: List[str]):
    #     """Process volexch command"""
    #     parser = argparse.ArgumentParser(
    #         prog="volexch",
    #         add_help=False,
    #         description="Displays short volume based on exchange.",
    #     )
    #     parser.add_argument(
    #         "-r",
    #         "--raw",
    #         help="Display raw data",
    #         dest="raw",
    #         action="store_true",
    #         default=False,
    #     )
    #     parser.add_argument(
    #         "-s",
    #         "--sort",
    #         help="Column to sort by",
    #         dest="sort",
    #         type=str,
    #         default="",
    #         choices=["", "NetShort", "Date", "TotalVolume", "PctShort"],
    #     )
    #     parser.add_argument(
    #         "-a",
    #         "--asc",
    #         help="Sort in ascending order",
    #         dest="asc",
    #         action="store_true",
    #         default=False,
    #     )
    #     parser.add_argument(
    #         "-p",
    #         "--plotly",
    #         help="Display plot using interactive plotly.",
    #         dest="plotly",
    #         action="store_false",
    #         default=True,
    #     )
    #     ns_parser =  self.parse_known_args_and_warn(
    #         parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
    #     )
    #     if ns_parser:
    #         if self.ticker:
    #             nyse_view.display_short_by_exchange(
    #                 ticker=self.ticker,
    #                 raw=ns_parser.raw,
    #                 sort=ns_parser.sort,
    #                 asc=ns_parser.asc,
    #                 mpl=ns_parser.plotly,
    #                 export=ns_parser.export,
    #                 sheet_name= " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None,
    #             )
    #         else:
    #             console.print("No ticker loaded.  Use `load ticker` first.")
