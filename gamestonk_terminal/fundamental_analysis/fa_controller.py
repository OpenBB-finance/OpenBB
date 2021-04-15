""" Fundamental Analysis Controller """
__docformat__ = "numpy"

import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.fundamental_analysis import alpha_vantage_api as av_api
from gamestonk_terminal.fundamental_analysis import business_insider_api as bi_api
from gamestonk_terminal.fundamental_analysis import (
    financial_modeling_prep_api as fmp_api,
)
from gamestonk_terminal.fundamental_analysis import finviz_api as fvz_api
from gamestonk_terminal.fundamental_analysis import market_watch_api as mw_api
from gamestonk_terminal.fundamental_analysis import yahoo_finance_api as yf_api
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session


class FundamentalAnalysisController:
    """ Fundamental Analysis Controller """

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "screener",
        "income",
        "balance",
        "cash",
        "mgmt",
        "info",
        "shrs",
        "sust",
        "cal",
        "av",
        "fmp",
    ]

    def __init__(self, ticker: str, start: str, interval: str):
        """Constructor

        Parameters
        ----------
        ticker : str
            Fundamental analysis ticker symbol
        start : str
            Stat date of the stock data
        interval : str
            Stock data interval
        """

        self.ticker = ticker
        self.start = start
        self.interval = interval

        self.fa_parser = argparse.ArgumentParser(add_help=False, prog="fa")
        self.fa_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """ Print help """

        intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]

        if self.start:
            print(
                f"\n{intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
            )
        else:
            print(f"\n{intraday} Stock: {self.ticker}")

        print(
            "\nFundamental Analysis:"
        )  # https://github.com/JerBouma/FundamentalAnalysis
        print("   help          show this fundamental analysis menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   screener      screen info about the company [Finviz]")
        print("   mgmt          management team of the company [Business Insider]")
        print("")
        print("Market Watch API")
        print("   income        income statement of the company")
        print("   balance       balance sheet of the company")
        print("   cash          cash flow statement of the company")
        print("")
        print("Yahoo Finance API")
        print("   info          information scope of the company")
        print("   shrs          shareholders of the company")
        print("   sust          sustainability values of the company")
        print("   cal           calendar earnings and estimates of the company")
        print("")
        print("Other Sources:")
        print(">  av            Alpha Vantage MENU")
        print(">  fmp           Financial Modeling Prep MENU")
        print("")

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        (known_args, other_args) = self.fa_parser.parse_known_args(an_input.split())

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

    def call_mgmt(self, other_args: List[str]):
        """ Process mgmt command """
        bi_api.management(other_args, self.ticker)

    def call_screener(self, other_args: List[str]):
        """ Process screener command """
        fvz_api.screener(other_args, self.ticker)

    def call_income(self, other_args: List[str]):
        """ Process income command """
        mw_api.income(other_args, self.ticker)

    def call_balance(self, other_args: List[str]):
        """ Process balance command """
        mw_api.balance(other_args, self.ticker)

    def call_cash(self, other_args: List[str]):
        """ Process cash command """
        mw_api.cash(other_args, self.ticker)

    def call_info(self, other_args: List[str]):
        """ Process info command """
        yf_api.info(other_args, self.ticker)

    def call_shrs(self, other_args: List[str]):
        """ Process shrs command """
        yf_api.shareholders(other_args, self.ticker)

    def call_sust(self, other_args: List[str]):
        """ Process sust command """
        yf_api.sustainability(other_args, self.ticker)

    def call_cal(self, other_args: List[str]):
        """ Process cal command """
        yf_api.calendar_earnings(other_args, self.ticker)

    # pylint: disable=unused-argument
    def call_av(self, other_args: List[str]):
        """ Process av command """
        ret = av_api.menu(self.ticker, self.start, self.interval)

        if ret is not True:
            self.print_help()

    # pylint: disable=unused-argument
    def call_fmp(self, other_args: List[str]):
        """ Process fmp command """
        ret = fmp_api.menu(self.ticker, self.start, self.interval)

        if ret is not True:
            self.print_help()


def key_metrics_explained(other_args: List[str]):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="info",
        description="""
            Provides information about main key metrics. Namely: EBITDA,
            EPS, P/E, PEG, FCF, P/B, ROE, DPR, P/S, Dividend Yield Ratio, D/E, and Beta.
        """,
    )

    try:
        (_, l_unknown_args) = parser.parse_known_args(other_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        filepath = "fundamental_analysis/key_metrics_explained.txt"
        with open(filepath) as fp:
            line = fp.readline()
            while line:
                print(f"{line.strip()}")
                line = fp.readline()
            print("")

    except Exception as e:
        print(e)
        print("ERROR!\n")
        return


def menu(ticker: str, start: str, interval: str):
    """Fundamental Analysis menu

    Parameters
    ----------
    ticker : str
        Fundamental analysis ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """

    fa_controller = FundamentalAnalysisController(ticker, start, interval)
    fa_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in fa_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (fa)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (fa)> ")

        try:
            process_input = fa_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
