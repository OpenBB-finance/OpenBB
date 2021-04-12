""" Due Diligence Controller """
__docformat__ = "numpy"

import argparse
from typing import List
from pandas.core.frame import DataFrame
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.due_diligence import business_insider_view as bi_view
from gamestonk_terminal.due_diligence import financial_modeling_prep_api as fmp_api
from gamestonk_terminal.due_diligence import finviz_api as fvz_api
from gamestonk_terminal.due_diligence import market_watch_api as mw_api
from gamestonk_terminal.due_diligence import quandl_api as q_api
from gamestonk_terminal.due_diligence import reddit_api as r_api
from gamestonk_terminal.due_diligence import news_api
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session


class DueDiligenceController:
    """ Due Diligence Controller """

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "red",
        "short",
        "rating",
        "pt",
        "est",
        "ins",
        "insider",
        "news",
        "analyst",
        "warnings",
        "sec",
    ]

    def __init__(self, stock: DataFrame, ticker: str, start: str, interval: str):
        """Constructor

        Parameters
        ----------
        stock : DataFrame
            Due diligence stock dataframe
        ticker : str
            Due diligence ticker symbol
        start : str
            Start date of the stock data
        interval : str
            Stock data interval
        """
        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval
        self.dd_parser = argparse.ArgumentParser(add_help=False, prog="dd")
        self.dd_parser.add_argument(
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

        print("\nDue Diligence:")
        print("   help          show this fundamental analysis menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   news          latest news of the company [News API]")
        print("   red           gets due diligence from another user's post [Reddit]")
        print("   analyst       analyst prices and ratings of the company [Finviz]")
        print(
            "   rating        rating of the company from strong sell to strong buy [FMP]"
        )
        print("   pt            price targets over time [Business Insider]")
        print(
            "   est           quarter and year analysts earnings estimates [Business Insider]"
        )
        print("   ins           insider activity over time [Business Insider]")
        print("   insider       insider trading of the company [Finviz]")
        print("   sec           SEC filings [Market Watch]")
        print("   short         short interest [Quandl]")
        print(
            "   warnings      company warnings according to Sean Seah book [Market Watch]"
        )
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
        (known_args, other_args) = self.dd_parser.parse_known_args(an_input.split())

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

    def call_red(self, other_args: List[str]):
        """ Process red command """
        r_api.due_diligence(other_args, self.ticker)

    def call_insider(self, other_args: List[str]):
        """ Process insider command """
        fvz_api.insider(other_args, self.ticker)

    def call_news(self, other_args: List[str]):
        """ Process news command """
        news_api.news(other_args, self.ticker)

    def call_analyst(self, other_args: List[str]):
        """ Process analyst command """
        fvz_api.analyst(other_args, self.ticker)

    def call_pt(self, other_args: List[str]):
        """ Process pt command """
        bi_view.price_target_from_analysts(
            other_args, self.stock, self.ticker, self.start, self.interval
        )

    def call_est(self, other_args: List[str]):
        """ Process est command """
        bi_view.estimates(other_args, self.ticker)

    def call_ins(self, other_args: List[str]):
        """ Process ins command """
        bi_view.insider_activity(
            other_args, self.stock, self.ticker, self.start, self.interval
        )

    def call_rating(self, other_args: List[str]):
        """ Process rating command """
        fmp_api.rating(other_args, self.ticker)

    def call_warnings(self, other_args: List[str]):
        """ Process rating command """
        mw_api.sean_seah_warnings(other_args, self.ticker)

    def call_sec(self, other_args: List[str]):
        """ Process sec command """
        mw_api.sec_fillings(other_args, self.ticker)

    def call_short(self, other_args: List[str]):
        """ Process short command """
        q_api.short_interest(other_args, self.ticker, self.start)


def menu(stock: DataFrame, ticker: str, start: str, interval: str):
    """Due Diligence Menu

    Parameters
    ----------
    stock : DataFrame
        Due diligence stock dataframe
    ticker : str
        Due diligence ticker symbol
    start : str
        Start date of the stock data
    interval : str
        Stock data interval
    """

    dd_controller = DueDiligenceController(stock, ticker, start, interval)
    dd_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in dd_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (dd)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (dd)> ")

        try:
            process_input = dd_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
