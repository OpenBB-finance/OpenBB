""" Government Controller Module """
__docformat__ = "numpy"

import argparse
import difflib
from datetime import datetime, timedelta
from typing import List, Union
from colorama import Style
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.government import quiverquant_view
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_positive,
    try_except,
    system_clear,
    valid_date,
)
from gamestonk_terminal.stocks import stocks_helper
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
)


class GovController:
    """Gov Controller class"""

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
        "lasttrades",
        "topbuys",
        "topsells",
        "qtrcontracts",
        "toplobbying",
        "gtrades",
        "lastcontracts",
        "contracts",
        "histcont",
        "lobbying",
    ]
    CHOICES += CHOICES_COMMANDS

    gov_type_choices = ["congress", "senate", "house"]
    analysis_choices = ["total", "upmom", "downmom"]

    def __init__(
        self,
        ticker: str,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.gov_parser = argparse.ArgumentParser(add_help=False, prog="gov")
        self.gov_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["lasttrades"] = {c: {} for c in self.gov_type_choices}
            choices["topbuys"] = {c: {} for c in self.gov_type_choices}
            choices["topsells"] = {c: {} for c in self.gov_type_choices}
            choices["qtrcontracts"]["-a"] = {c: {} for c in self.analysis_choices}
            choices["qtrcontracts"]["--analysis"] = {
                c: {} for c in self.analysis_choices
            }
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

        self.ticker = ticker

    def print_help(self):
        """Print help"""
        dim_no_ticker = Style.DIM if not self.ticker else ""
        reset_style = Style.RESET_ALL
        help_txt = f"""
Explore:
    lasttrades           last trades
    topbuys              show most purchased stocks
    topsells             show most sold stocks
    lastcontracts        show last government contracts given out
    qtrcontracts         quarterly government contracts analysis
    toplobbying          top corporate lobbying tickers

    load                 load a specific ticker for analysis

Ticker: {self.ticker or None}{dim_no_ticker}

    gtrades              show government trades for ticker
    contracts            show government contracts for ticker
    histcont             show historical quarterly government contracts for ticker
    lobbying             corporate lobbying details for ticker{reset_style}
            """
        print(help_txt)

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

        (known_args, other_args) = self.gov_parser.parse_known_args(an_input.split())

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
        self.queue.insert(0, "gov")
        if self.ticker:
            self.queue.insert(0, f"load {self.ticker}")
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
                self.ticker = ns_parser.ticker.upper()
            else:
                print("Ticker selected does not exist!", "\n")

    @try_except
    def call_lasttrades(self, other_args: List[str]):
        """Process lasttrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lasttrades",
            description="Last government trading trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_days",
            action="store",
            dest="past_transactions_days",
            type=check_positive,
            default=5,
            help="Past transaction days",
        )
        parser.add_argument(
            "-r",
            "--representative",
            action="store",
            dest="representative",
            type=str,
            default="",
            help="Representative",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            quiverquant_view.display_last_government(
                gov_type=ns_parser.gov,
                past_days=ns_parser.past_transactions_days,
                representative=ns_parser.representative,
                export=ns_parser.export,
            )

    @try_except
    def call_topbuys(self, other_args: List[str]):
        """Process topbuys command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="topbuys",
            description="Top buys for government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_months",
            action="store",
            dest="past_transactions_months",
            type=check_positive,
            default=6,
            help="Past transaction months",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of top tickers to display",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_government_buys(
                gov_type=ns_parser.gov,
                past_transactions_months=ns_parser.past_transactions_months,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @try_except
    def call_topsells(self, other_args: List[str]):
        """Process topsells command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="topsells",
            description="Top sells for government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_months",
            action="store",
            dest="past_transactions_months",
            type=check_positive,
            default=6,
            help="Past transaction months",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of top tickers to display",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_government_sells(
                gov_type=ns_parser.gov,
                past_transactions_months=ns_parser.past_transactions_months,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @try_except
    def call_lastcontracts(self, other_args: List[str]):
        """Process lastcontracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lastcontracts",
            description="Last government contracts. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-p",
            "--past_transaction_days",
            action="store",
            dest="past_transaction_days",
            type=check_positive,
            default=2,
            help="Past transaction days",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=20,
            help="Limit of contracts to display",
        )
        parser.add_argument(
            "-s",
            "--sum",
            action="store_true",
            dest="sum",
            default=False,
            help="Flag to show total amount of contracts.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_last_contracts(
                past_transaction_days=ns_parser.past_transaction_days,
                num=ns_parser.limit,
                sum_contracts=ns_parser.sum,
                export=ns_parser.export,
            )

    @try_except
    def call_qtrcontracts(self, other_args: List[str]):
        """Process qtrcontracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="qtrcontracts",
            description="Look at government contracts [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="Limit of tickers to get",
        )
        parser.add_argument(
            "-a",
            "--analysis",
            action="store",
            dest="analysis",
            choices=self.analysis_choices,
            type=str,
            default="total",
            help="""Analysis to look at contracts. 'Total' shows summed contracts.
            'Upmom' shows highest sloped contacts while 'downmom' shows highest decreasing slopes.""",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_qtr_contracts(
                analysis=ns_parser.analysis,
                num=ns_parser.limit,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

    @try_except
    def call_toplobbying(self, other_args: List[str]):
        """Process toplobbying command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="toplobbying",
            description="Top lobbying. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of stocks to display",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            quiverquant_view.display_top_lobbying(
                num=ns_parser.limit, raw=ns_parser.raw, export=ns_parser.export
            )

    @try_except
    def call_gtrades(self, other_args: List[str]):
        """Process gtrades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gtrades",
            description="Government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-p",
            "--past_transactions_months",
            action="store",
            dest="past_transactions_months",
            type=check_positive,
            default=6,
            help="Past transaction months",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=self.gov_type_choices,
            type=str,
            default="congress",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_government_trading(
                    ticker=self.ticker,
                    gov_type=ns_parser.gov,
                    past_transactions_months=ns_parser.past_transactions_months,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                print("No ticker loaded. Use `load <ticker>` first.\n")

    @try_except
    def call_contracts(self, other_args: List[str]):
        """Process contracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="contracts",
            description="Contracts associated with ticker. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-p",
            "--past_transaction_days",
            action="store",
            dest="past_transaction_days",
            type=check_positive,
            default=10,
            help="Past transaction days",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_contracts(
                    ticker=self.ticker,
                    past_transaction_days=ns_parser.past_transaction_days,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                )
            else:
                print("No ticker loaded. Use `load <ticker>` first.\n")

    @try_except
    def call_histcont(self, other_args: List[str]):
        """Process histcont command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="histcont",
            description="Quarterly-contracts historical [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_hist_contracts(
                    ticker=self.ticker, raw=ns_parser.raw, export=ns_parser.export
                )
            else:
                print("No ticker loaded. Use `load <ticker>` first.\n")

    @try_except
    def call_lobbying(self, other_args: List[str]):
        """Process lobbying command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lobbying",
            description="Lobbying details [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of events to show",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                quiverquant_view.display_lobbying(
                    ticker=self.ticker,
                    num=ns_parser.limit,
                )
            else:
                print("No ticker loaded. Use `load <ticker>` first.\n")


def menu(ticker: str, queue: List[str] = None):
    """Government Menu"""
    gov_controller = GovController(ticker, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if gov_controller.queue and len(gov_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if gov_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(gov_controller.queue) > 1:
                    return gov_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = gov_controller.queue[0]
            gov_controller.queue = gov_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in gov_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/gov/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                gov_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and gov_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/gov/ $ ",
                    completer=gov_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/gov/ $ ")

        try:
            # Process the input command
            gov_controller.queue = gov_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/gov menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                gov_controller.CHOICES,
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
                        gov_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                gov_controller.queue.insert(0, an_input)
            else:
                print("\n")
