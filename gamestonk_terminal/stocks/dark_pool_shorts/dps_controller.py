""" Dark Pool and Shorts Controller Module """
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union
from datetime import datetime, timedelta
from colorama import Style
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    valid_date,
    check_int_range,
    try_except,
    system_clear,
    get_flair,
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


class DarkPoolShortsController:
    """Dark Pool Shorts Controller class"""

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
    CHOICES += CHOICES_COMMANDS

    def __init__(
        self, ticker: str, start: str, stock: pd.DataFrame, queue: List[str] = None
    ):
        """Constructor"""
        self.dps_parser = argparse.ArgumentParser(add_help=False, prog="dps")
        self.dps_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

        self.ticker = ticker
        self.start = start
        self.stock = stock

    def print_help(self):
        """Print help"""
        help_text = f"""
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

        (known_args, other_args) = self.dps_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        return self.queue

    def call_help(self, _):
        """Process help command"""
        self.print_help()
        return self.queue

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "quit"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            if self.ticker:
                self.queue.insert(0, f"load {self.ticker}")
            self.queue.insert(0, "dps")
            self.queue.insert(0, "stocks")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        reset_commands = ["quit", "quit", "reset", "stocks", "dps"]
        if self.ticker:
            reset_commands.append(f"load {self.ticker}")
        return reset_commands

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

        return self.queue

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

        return self.queue

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

        return self.queue

    @try_except
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

        return self.queue

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

        return self.queue

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

        return self.queue

    @try_except
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
                print("No ticker loaded.\n")

        return self.queue

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
                print("No ticker loaded.\n")

        return self.queue

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
                print("No ticker loaded.\n")

        return self.queue

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
                print("No ticker loaded.\n")

        return self.queue

    @try_except
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
        if ns_parser:
            if self.ticker:
                nyse_view.display_short_by_exchange(
                    ticker=self.ticker,
                    raw=ns_parser.raw,
                    sort=ns_parser.sort,
                    asc=ns_parser.asc,
                    mpl=ns_parser.mpl,
                    export=ns_parser.export,
                )
            else:
                print("No ticker loaded.  Use `load ticker` first.")

        return self.queue


def menu(
    ticker: str = "",
    start: str = "",
    stock: pd.DataFrame = pd.DataFrame(),
    queue: List[str] = None,
):
    """Dark Pool Shorts Menu"""
    dps_controller = DarkPoolShortsController(ticker, start, stock, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if dps_controller.queue and len(dps_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if dps_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(dps_controller.queue) > 1:
                    return dps_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = dps_controller.queue[0]
            dps_controller.queue = dps_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in dps_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/dps/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                dps_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and dps_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/dps/ $ ",
                    completer=dps_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/dps/ $ ")

        try:
            # Process the input command
            dps_controller.queue = dps_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/dps menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                dps_controller.CHOICES,
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
                        dps_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                dps_controller.queue.insert(0, an_input)
            else:
                print("\n")
