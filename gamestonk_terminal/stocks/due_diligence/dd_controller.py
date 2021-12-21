""" Due Diligence Controller """
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union
from datetime import datetime, timedelta
from pandas.core.frame import DataFrame
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.stocks.due_diligence import (
    fmp_view,
    business_insider_view,
    finviz_view,
    marketwatch_view,
    finnhub_view,
    csimarket_view,
    ark_view,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    try_except,
    system_clear,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks import stocks_helper


class DueDiligenceController:
    """Due Diligence Controller"""

    # Command choices
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
        "sec",
        "rating",
        "pt",
        "rot",
        "est",
        "analyst",
        "supplier",
        "customer",
        "arktrades",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(
        self,
        ticker: str,
        start: str,
        interval: str,
        stock: DataFrame,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.stock = stock

        self.dd_parser = argparse.ArgumentParser(add_help=False, prog="dd")
        self.dd_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["load"]["-i"] = {c: {} for c in stocks_helper.INTERVALS}
            choices["load"]["-s"] = {c: {} for c in stocks_helper.SOURCES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = f"""
Ticker: {self.ticker}

Finviz:
    analyst       analyst prices and ratings of the company
FMP:
    rating        rating over time (daily)
Finnhub:
    rot           number of analysts ratings over time (monthly)
Business Insider:
    pt            price targets over time
    est           quarter and year analysts earnings estimates
Market Watch:
    sec           SEC filings
csimarket:
    supplier      list of suppliers
    customer      list of customers
cathiesark.com
    arktrades     get ARK trades for ticker
        """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input
        Parameters
        -------
        an_input : str
            string with input arguments
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

        (known_args, other_args) = self.dd_parser.parse_known_args(an_input.split())

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
            self.queue.insert(0, "dd")
            if self.ticker:
                self.queue.insert(0, f"load {self.ticker}")
            self.queue.insert(0, "stocks")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue

        reset_commands = ["quit", "quit", "reset", "stocks"]
        if self.ticker:
            reset_commands.append(f"load {self.ticker}")
        reset_commands.append("dd")
        return reset_commands

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
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=int,
            default=1440,
            choices=stocks_helper.INTERVALS,
            help="Intraday stock minutes",
        )
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=stocks_helper.SOURCES,
            default="yf",
            help="Source of historical data.",
        )
        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            df_stock_candidate = stocks_helper.load(
                ticker=ns_parser.ticker,
                start=ns_parser.start,
                interval=ns_parser.interval,
                source=ns_parser.source,
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
    def call_analyst(self, other_args: List[str]):
        """Process analyst command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="analyst",
            description="""
                Print analyst prices and ratings of the company. The following fields are expected:
                date, analyst, category, price from, price to, and rating. [Source: Finviz]
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finviz_view.analyst(ticker=self.ticker, export=ns_parser.export)

        return self.queue

    @try_except
    def call_pt(self, other_args: List[str]):
        """Process pt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pt",
            description="""Prints price target from analysts. [Source: Business Insider]""",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of latest price targets from analysts to print.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            business_insider_view.price_target_from_analysts(
                ticker=self.ticker,
                start=self.start,
                interval=self.interval,
                stock=self.stock,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_est(self, other_args: List[str]):
        """Process est command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="est",
            description="""Yearly estimates and quarter earnings/revenues. [Source: Business Insider]""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            business_insider_view.estimates(
                ticker=self.ticker,
                export=ns_parser.export,
            )

        return self.queue

    @try_except
    def call_rot(self, other_args: List[str]):
        """Process rot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rot",
            description="""
                Rating over time (monthly). [Source: Finnhub]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of last months",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            help="Only output raw data",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finnhub_view.rating_over_time(
                ticker=self.ticker,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_rating(self, other_args: List[str]):
        """Process rating command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rating",
            description="""
                Based on specific ratios, prints information whether the company
                is a (strong) buy, neutral or a (strong) sell. The following fields are expected:
                P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="limit of last days to display ratings",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fmp_view.rating(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_sec(self, other_args: List[str]):
        """Process sec command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="sec",
            description="""
                Prints SEC filings of the company. The following fields are expected: Filing Date,
                Document Date, Type, Category, Amended, and Link. [Source: Market Watch]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="number of latest SEC filings.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            marketwatch_view.sec_filings(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
            )

        return self.queue

    @try_except
    def call_supplier(self, other_args: List[str]):
        """Process supplier command"""
        parser = argparse.ArgumentParser(
            prog="supplier",
            add_help=False,
            description="List of suppliers from ticker provided. [Source: CSIMarket]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            csimarket_view.suppliers(
                ticker=self.ticker,
                export=ns_parser.export,
            )
        return self.queue

    def call_customer(self, other_args: List[str]):
        """Process customer command"""
        parser = argparse.ArgumentParser(
            prog="customer",
            add_help=False,
            description="List of customers from ticker provided. [Source: CSIMarket]",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            csimarket_view.customers(
                ticker=self.ticker,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_arktrades(self, other_args):
        """Process arktrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="arktrades",
            description="""
                Get trades for ticker across all ARK funds.
            """,
        )
        parser.add_argument(
            "-l",
            "--limi",
            help="Limit of rows to show",
            dest="limit",
            default=10,
            type=check_positive,
        )
        parser.add_argument(
            "-s",
            "--show_ticker",
            action="store_true",
            default=False,
            help="Flag to show ticker in table",
            dest="show_ticker",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ark_view.display_ark_trades(
                ticker=self.ticker,
                num=ns_parser.limit,
                export=ns_parser.export,
                show_ticker=ns_parser.show_ticker,
            )
        return self.queue


def menu(
    ticker: str,
    start: str,
    interval: str,
    stock: DataFrame,
    queue: List[str] = None,
):
    """Due Diligence Menu

    Parameters
    ----------
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    stock : DataFrame
        Due diligence stock dataframe
    queue: List[str]
        List with commands in queue to run
    """

    dd_controller = DueDiligenceController(ticker, start, interval, stock, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if dd_controller.queue and len(dd_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if dd_controller.queue[0] in ("q", "..", "quit"):
                if len(dd_controller.queue) > 1:
                    return dd_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = dd_controller.queue[0]
            dd_controller.queue = dd_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in dd_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/dd/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                dd_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and dd_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/dd/ $ ",
                    completer=dd_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/dd/ $ ")

        try:
            # Process the input command
            dd_controller.queue = dd_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                dd_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                else:
                    candidate_input = similar_cmd[0]

                if candidate_input == an_input:
                    an_input = ""
                    dd_controller.queue = []
                    print("\n")
                    continue

                print(f" Replacing by '{an_input}'.")
                dd_controller.queue.insert(0, an_input)
            else:
                print("\n")
                an_input = ""
                dd_controller.queue = []
