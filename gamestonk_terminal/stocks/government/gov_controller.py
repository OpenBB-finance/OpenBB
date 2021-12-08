"""Government Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
from datetime import datetime, timedelta
from typing import List
from colorama import Style
from matplotlib import pyplot as plt
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

    # Command choices
    CHOICES = ["cls", "?", "help", "q", "quit", "load"]
    CHOICES_COMMANDS = [
        "lasttrades",
        "topbuys",
        "topsells",
        "qtrcontracts",
        "toplobbying",
    ]

    CHOICES_COMMANDS_TICKER = [
        "gtrades",
        "lastcontracts",
        "contracts",
        "histcont",
        "lobbying",
    ]
    CHOICES += CHOICES_COMMANDS + CHOICES_COMMANDS_TICKER

    def __init__(
        self,
        ticker: str,
    ):
        """Constructor"""
        self.ticker = ticker
        self.gov_parser = argparse.ArgumentParser(add_help=False, prog="gov")
        self.gov_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        dim_no_ticker = Style.DIM if not self.ticker else ""
        reset_style = Style.RESET_ALL
        help_string = f"""
Government:
    cls                  clear screen
    ?/help               show this menu again
    q                    quit this menu, and shows back to main menu
    quit                 quit to abandon program
    load                 load a ticker

Explore:
    lasttrades           last trades
    topbuys              show most purchased stocks
    topsells             show most sold stocks
    lastcontracts        show last government contracts given out
    qtrcontracts         quarterly government contracts analysis
    toplobbying          top corporate lobbying tickers

Ticker: {self.ticker or None}{dim_no_ticker}

    gtrades              show government trades for ticker
    contracts            show government contracts for ticker
    histcont             show historical quarterly government contracts for ticker
    lobbying             corporate lobbying details for ticker{reset_style}
            """
        print(help_string)

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

        (known_args, other_args) = self.gov_parser.parse_known_args(an_input.split())

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
            self.ticker = ns_parser.ticker.upper()

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
            choices=["congress", "senate", "house"],
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
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not ns_parser:
            return
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
            choices=["congress", "senate", "house"],
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
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="Number of top tickers",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return
        quiverquant_view.display_government_buys(
            gov_type=ns_parser.gov,
            past_transactions_months=ns_parser.past_transactions_months,
            num=ns_parser.num,
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
            choices=["congress", "senate", "house"],
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
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="Number of top tickers",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            default=False,
            dest="raw",
            help="Print raw data.",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return
        quiverquant_view.display_government_sells(
            gov_type=ns_parser.gov,
            past_transactions_months=ns_parser.past_transactions_months,
            num=ns_parser.num,
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
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=20,
            help="Number of contracts to display",
        )
        parser.add_argument(
            "-s",
            "--sum",
            action="store_true",
            dest="sum",
            default=False,
            help="Flag to show total amount of contracts.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return
        quiverquant_view.display_last_contracts(
            past_transaction_days=ns_parser.past_transaction_days,
            num=ns_parser.num,
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
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=5,
            help="Number of tickers to get",
        )
        parser.add_argument(
            "-a",
            "--analysis",
            action="store",
            dest="analysis",
            choices=["total", "upmom", "downmom"],
            type=str,
            default="total",
            help="""Analysis to look at contracts. 'Total' shows summed contracts.
            'Upmom' shows highest sloped contacts while 'downmom' shows highest decreasing slopes.""",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        quiverquant_view.display_qtr_contracts(
            analysis=ns_parser.analysis, num=ns_parser.num
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
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="Number to show",
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
        if not ns_parser:
            return

        quiverquant_view.display_top_lobbying(
            num=ns_parser.num, raw=ns_parser.raw, export=ns_parser.export
        )

    def _check_ticker(self):
        """Check if ticker loaded"""
        if self.ticker:
            return True
        print("No ticker loaded. Use `load <ticker>` first.\n")
        return False

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
            choices=["congress", "senate", "house"],
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
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        if self._check_ticker():
            quiverquant_view.display_government_trading(
                ticker=self.ticker,
                gov_type=ns_parser.gov,
                past_transactions_months=ns_parser.past_transactions_months,
                raw=ns_parser.raw,
            )

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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if self._check_ticker():
            quiverquant_view.display_contracts(
                ticker=self.ticker,
                past_transaction_days=ns_parser.past_transaction_days,
                raw=ns_parser.raw,
            )

    @try_except
    def call_histcont(self, other_args: List[str]):
        """Process histcont command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="histcont",
            description="Quarterly-contracts historical [Source: www.quiverquant.com]",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        if self._check_ticker():

            quiverquant_view.display_hist_contracts(
                ticker=self.ticker, export=ns_parser.export
            )

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
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="Number of events to show",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if self._check_ticker():
            quiverquant_view.display_lobbying(ticker=self.ticker, num=ns_parser.num)


def menu(ticker: str):
    """Government Menu"""

    gov_controller = GovController(ticker)
    gov_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in gov_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(gov)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(gov)> ")

        try:
            plt.close("all")

            process_input = gov_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, gov_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
