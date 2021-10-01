"""Government Controller Module"""
__docformat__ = "numpy"

import argparse
import os
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
)


class GovController:
    """Gov Controller class"""

    # Command choices
    CHOICES = ["cls", "?", "help", "q", "quit", "load"]
    CHOICES_COMMANDS = [
        "last_trades",
        "top_buys",
        "top_sells",
        "qtr_contracts",
        "top_lobbying",
    ]

    CHOICES_COMMANDS_TICKER = [
        "congress",
        "raw_congress",
        "senate",
        "raw_senate",
        "house",
        "raw_house",
        "last_contracts",
        "raw_contracts",
        "contracts",
        "qtr_contracts_hist",
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
>>GOVERNMENT<<

What would you like to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program
    load          load a ticker

Explore:
    last_trades          last trades
    top_buys             show most purchased stocks
    top_sells            show most sold stocks
    last_contracts       show last government contracts given out
    qtr_contracts        quarterly government contracts analysis
    top_lobbying         top corporate lobbying tickers

Current Ticker: {self.ticker or None}{dim_no_ticker}
    raw_congress         raw congress trades on the ticker
    congress             plot congress trades on the ticker
    raw_senate           raw senate trades on the ticker
    senate               plot senate trades on the ticker
    raw_house            raw house trades on the tickers
    house                plot house trades on the ticker
    raw_contracts        raw contracts on the ticker
    contracts            plot sum of contracts on the ticker
    qtr_contracts_hist   quarterly government contracts historical
    lobbying             corporate lobbying details{reset_style}
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
            os.system("cls||clear")
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

    def call_last_trades(self, other_args: List[str]):
        """Process last trades command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="last_trades",
            description="Last government trading trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=["congress", "senate", "house"],
            type=str,
            default="senate",
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
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            quiverquant_view.display_last_government(
                gov_type=ns_parser.gov,
                past_days=ns_parser.past_transactions_days,
                representative=ns_parser.representative,
            )

        except Exception as e:
            print(e, "\n")

    def call_top_buys(self, other_args: List[str]):
        """Process top_buys command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="top_buys",
            description="Top buys for government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=["congress", "senate", "house"],
            type=str,
            default="senate",
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
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg", "csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file or export dataframe to csv,json,xlsx",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            quiverquant_view.display_government_buys(
                gov_type=ns_parser.gov,
                past_transactions_months=ns_parser.past_transactions_months,
                num=ns_parser.num,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_top_sells(self, other_args: List[str]):
        """Process top_sells command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="top_sells",
            description="Top sells for government trading. [Source: www.quiverquant.com]",
        )
        parser.add_argument(
            "-g",
            "--govtype",
            dest="gov",
            choices=["congress", "senate", "house"],
            type=str,
            default="senate",
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
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg", "csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file or export dataframe to csv,json,xlsx",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            quiverquant_view.display_government_sells(
                gov_type=ns_parser.gov,
                past_transactions_months=ns_parser.past_transactions_months,
                num=ns_parser.num,
                raw=ns_parser.raw,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_last_contracts(self, other_args: List[str]):
        """Process last_contracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="last_contracts",
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
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg", "csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file or export dataframe to csv,json,xlsx",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            quiverquant_view.display_last_contracts(
                past_transaction_days=ns_parser.past_transaction_days,
                num=ns_parser.num,
                sum_contracts=ns_parser.sum,
                export=ns_parser.export,
            )
        except Exception as e:
            print(e, "\n")

    def call_qtr_contracts(self, other_args: List[str]):
        """Process contracts command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="qtr_contracts",
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
            help="Analysis to look at contracts.",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            quiverquant_view.display_qtr_contracts(
                analysis=ns_parser.analysis, num=ns_parser.num
            )
        except Exception as e:
            print(e, "\n")

    def call_top_lobbying(self, other_args: List[str]):
        """Process top_lobbying command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="top_lobbying",
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
        parser.add_argument(
            "--export",
            choices=["png", "jpg", "pdf", "svg", "csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export plot to png,jpg,pdf,svg file or export dataframe to csv,json,xlsx",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            quiverquant_view.display_top_lobbying(
                num=ns_parser.num, raw=ns_parser.raw, export=ns_parser.export
            )
        except Exception as e:
            print(e, "\n")

    def call_raw_congress(self, other_args: List[str]):
        """Process raw_congress command"""
        quiverquant_view.raw_government(other_args, self.ticker, "congress")

    def call_congress(self, other_args: List[str]):
        """Process congress command"""
        quiverquant_view.government_trading(other_args, self.ticker, "congress")

    def call_senate(self, other_args: List[str]):
        """Process senate command"""
        quiverquant_view.government_trading(other_args, self.ticker, "senate")

    def call_house(self, other_args: List[str]):
        """Process house command"""
        quiverquant_view.government_trading(other_args, self.ticker, "house")

    def call_raw_senate(self, other_args: List[str]):
        """Process raw_senate command"""
        quiverquant_view.raw_government(other_args, self.ticker, "senate")

    def call_raw_house(self, other_args: List[str]):
        """Process raw_house command"""
        quiverquant_view.raw_government(other_args, self.ticker, "house")

    def call_raw_contracts(self, other_args: List[str]):
        """Process raw_contracts command"""
        quiverquant_view.raw_contracts(other_args, self.ticker)

    def call_contracts(self, other_args: List[str]):
        """Process contracts command"""
        quiverquant_view.contracts(other_args, self.ticker)

    def call_qtr_contracts_hist(self, other_args: List[str]):
        """Process qtr_contracts_hist command"""
        quiverquant_view.qtr_contracts_hist(other_args, self.ticker)

    def call_lobbying(self, other_args: List[str]):
        """Process lobbying command"""
        quiverquant_view.lobbying(other_args, self.ticker)


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
            continue
