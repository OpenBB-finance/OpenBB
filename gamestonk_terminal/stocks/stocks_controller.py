import argparse
import os
from typing import List

import pandas as pd
from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common import newsapi_view
from gamestonk_terminal.helper_funcs import (
    b_is_stock_market_open,
    check_positive,
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.options import options_controller
from gamestonk_terminal.stocks.backtesting import bt_controller
from gamestonk_terminal.stocks.behavioural_analysis import ba_controller
from gamestonk_terminal.stocks.comparison_analysis import ca_controller
from gamestonk_terminal.stocks.dark_pool_shorts import dps_controller
from gamestonk_terminal.stocks.discovery import disc_controller
from gamestonk_terminal.stocks.due_diligence import dd_controller
from gamestonk_terminal.stocks.exploratory_data_analysis import eda_controller
from gamestonk_terminal.stocks.fundamental_analysis import fa_controller
from gamestonk_terminal.stocks.government import gov_controller
from gamestonk_terminal.stocks.insider import insider_controller
from gamestonk_terminal.stocks.report import report_controller
from gamestonk_terminal.stocks.research import res_controller
from gamestonk_terminal.stocks.residuals_analysis import ra_controller
from gamestonk_terminal.stocks.screener import screener_controller
from gamestonk_terminal.stocks.stocks_helper import candle, load, quote
from gamestonk_terminal.stocks.technical_analysis import ta_controller

# pylint: disable=R1710


class StocksController:
    """Stocks Controller class"""

    # To hold suffix for Yahoo Finance
    suffix = ""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "load",
        "quote",
        "candle",
        "news",
    ]

    CHOICES_MENUS = [
        "ta",
        "ba",
        "eda",
        "pred",
        "ra",
        "disc",
        "dps",
        "scr",
        "ins",
        "gov",
        "res",
        "fa",
        "bt",
        "dd",
        "ca",
        "report",
        "options",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(self, ticker):
        """Constructor"""
        self.stock = pd.DataFrame()
        self.ticker = ticker
        self.start = ""
        self.interval = "1440min"

        self.stocks_parser = argparse.ArgumentParser(add_help=False, prog="stocks")
        self.stocks_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer = NestedCompleter.from_nested_dict(
            {c: None for c in self.CHOICES}
        )

    def print_help(self):
        """Print help"""

        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.ticker and self.start:
            stock_text = f"{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})"
        else:
            stock_text = f"{s_intraday} Stock: {self.ticker}"

        help_text = f"""https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/stocks

>> STOCKS <<

What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

    load        load a specific stock ticker for analysis

{stock_text}
Market {('CLOSED', 'OPEN')[b_is_stock_market_open()]}
{Style.DIM if not self.ticker else ''}
    quote       view the current price for a specific stock ticker
    candle      view a candle chart for a specific stock ticker
    news        latest news of the company [News API]
{Style.RESET_ALL if not self.ticker else ''}
>>  options     go into options context {'with ' if self.ticker else ''}{self.ticker}

>   disc        discover trending stocks, \t e.g. map, sectors, high short interest
>   dps         dark pool and short data, \t e.g. darkpool, short interest, ftd
>   scr         screener stocks, \t\t e.g. overview/performance, using preset filters
>   ins         insider trading,         \t e.g.: latest penny stock buys, top officer purchases
>   gov         government menu, \t\t e.g. house trading, contracts, corporate lobbying
>   report      generate automatic report,   \t e.g.: dark pool, due diligence{Style.DIM if not self.ticker else ''}
>   fa          fundamental analysis,    \t e.g.: income, balance, cash, earnings
>   res         research web page,       \t e.g.: macroaxis, yahoo finance, fool
>   dd          in-depth due-diligence,  \t e.g.: news, analyst, shorts, insider, sec
>   ca          comparison analysis,     \t e.g.: historical, correlation, financials
>   bt          strategy backtester,      \t e.g.: simple ema, ema cross, rsi strategies
>   ta          technical analysis,      \t e.g.: ema, macd, rsi, adx, bbands, obv
>   ba          behavioural analysis,    \t from: reddit, stocktwits, twitter, google
>   eda         exploratory data analysis,\t e.g.: decompose, cusum, residuals analysis
>   ra          residuals analysis,      \t e.g.: model fit, qqplot, hypothesis test
>   pred        prediction techniques,   \t e.g.: regression, arima, rnn, lstm
{Style.RESET_ALL if not self.ticker else ''}"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False, or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.stocks_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    # COMMANDS
    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker, self.start, self.interval, self.stock = load(
            other_args, self.ticker, self.start, self.interval, self.stock
        )
        if "." in self.ticker:
            self.ticker, self.suffix = self.ticker.split(".")
        else:
            self.suffix = ""

    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        quote(
            other_args, self.ticker + "." + self.suffix if self.suffix else self.ticker
        )

    def call_candle(self, other_args: List[str]):
        """Process candle command"""
        candle(
            self.ticker + "." + self.suffix if self.suffix else self.ticker,
            other_args,
        )

    def call_news(self, other_args: List[str]):
        """Process news command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        parser = argparse.ArgumentParser(
            add_help=False,
            prog="news",
            description="""
                Prints latest news about company, including date, title and web link. [Source: News API]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=5,
            help="Number of latest news being printed.",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            newsapi_view.news(
                term=self.ticker,
                num=ns_parser.n_num,
            )

        except Exception as e:
            print(e, "\n")

    # MENUS
    def call_disc(self, _):
        """Process disc command"""
        ret = disc_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_dps(self, _):
        """Process dps command"""
        ret = dps_controller.menu(self.ticker, self.start, self.stock)
        if ret is False:
            self.print_help()
        else:
            return True

    def call_scr(self, _):
        """Process scr command"""
        ret = screener_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_ins(self, _):
        """Process ins command"""
        ret = insider_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )
        if ret is False:
            self.print_help()
        else:
            return True

    def call_gov(self, _):
        """Process gov command"""
        ret = gov_controller.menu(self.ticker)
        if ret is False:
            self.print_help()
        else:
            return True

    def call_report(self, _):
        """Process report command"""
        ret = report_controller.menu()

        if ret is False:
            self.print_help()
        else:
            return True

    def call_res(self, _):
        """Process res command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = res_controller.menu(
            self.ticker,
            self.start,
            self.interval,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_dd(self, _):
        """Process dd command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = dd_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_ca(self, _):
        """Process ca command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = ca_controller.menu(self.ticker, self.start, self.interval, self.stock)

        if ret is False:
            self.print_help()
        else:
            return True

    def call_fa(self, _):
        """Process fa command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = fa_controller.menu(
            self.ticker,
            self.start,
            self.interval,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_bt(self, _):
        """Process bt command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = bt_controller.menu(
            self.ticker,
            self.start,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_ta(self, _):
        """Process ta command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = ta_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_ba(self, _):
        """Process ba command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = ba_controller.menu(
            self.ticker,
            self.start,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_ra(self, _):
        """Process ra command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        ret = ra_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_eda(self, _):
        """Process eda command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        if self.interval != "1440min":
            # TODO: This menu should work regardless of data being daily or not!
            print("Load daily data to use this menu!", "\n")
            return

        ret = eda_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_pred(self, _):
        """Process pred command"""
        if not gtff.ENABLE_PREDICT:
            print(
                "Predict is disabled. Check ENABLE_PREDICT flag on feature_flags.py",
                "\n",
            )
            return

        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        if self.interval != "1440min":
            # TODO: This menu should work regardless of data being daily or not!
            print("Load daily data to use this menu!", "\n")
            return

        try:
            # pylint: disable=import-outside-toplevel
            from gamestonk_terminal.stocks.prediction_techniques import pred_controller
        except ModuleNotFoundError as e:
            print("One of the optional packages seems to be missing: ", e, "\n")
            return
        except Exception as e:
            print(e, "\n")
            return

        ret = pred_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_options(self, _):
        """Process options command"""
        return options_controller.menu(self.ticker)


def menu(ticker: str = ""):
    """Stocks Menu"""
    stocks_controller = StocksController(ticker)
    stocks_controller.call_help(None)
    while True:
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in stocks_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (stocks)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)> ")

        try:
            process_input = stocks_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exit\n")
            continue
