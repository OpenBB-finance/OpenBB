#!/usr/bin/env python
"""Main Terminal Module"""
__docformat__ = "numpy"

import argparse
import os
import sys
from datetime import datetime
from typing import List
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.helper_funcs import (
    b_is_stock_market_open,
    get_flair,
)
from gamestonk_terminal.main_helper import (
    clear,
    load,
    view,
    candle,
    print_goodbye,
    quote,
    update_terminal,
    about_us,
    bootup,
    reset,
    check_api_keys,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.discovery import disc_controller
from gamestonk_terminal.due_diligence import dd_controller
from gamestonk_terminal.fundamental_analysis import fa_controller
from gamestonk_terminal.papermill import papermill_controller as mill
from gamestonk_terminal.behavioural_analysis import ba_controller
from gamestonk_terminal.technical_analysis import ta_controller
from gamestonk_terminal.comparison_analysis import ca_controller
from gamestonk_terminal.exploratory_data_analysis import eda_controller
from gamestonk_terminal.options import op_controller
from gamestonk_terminal.economy import econ_controller
from gamestonk_terminal.residuals_analysis import ra_controller
from gamestonk_terminal.portfolio_analysis import pa_controller
from gamestonk_terminal.brokers import bro_controller
from gamestonk_terminal.cryptocurrency import crypto_controller
from gamestonk_terminal.screener import screener_controller
from gamestonk_terminal.portfolio_optimization import po_controller
from gamestonk_terminal.forex import fx_controller
from gamestonk_terminal.backtesting import bt_controller
from gamestonk_terminal.resource_collection import rc_controller
from gamestonk_terminal.research import res_controller
from gamestonk_terminal.government import gov_controller
from gamestonk_terminal.etf import etf_controller
from gamestonk_terminal.insider import insider_controller


# pylint: disable=too-many-public-methods
class TerminalController:
    """Terminal Controller class"""

    # To hold suffix for Yahoo Finance
    suffix = ""

    # Command choices
    CHOICES_TICKER_DEPENDENT = [
        "ba",
        "res",
        "fa",
        "ta",
        "bt",
        "dd",
        "eda",
        "pred",
        "ca",
        "ra",
    ]

    CHOICES = [
        "cls",
        "?",
        "help",
        "quit",
        "q",
        "reset",
        "update",
        "clear",
        "load",
        "quote",
        "candle",
        "view",
        "disc",
        "scr",
        "mill",
        "econ",
        "pa",
        "crypto",
        "po",
        "ins",
        "fx",
        "rc",
        "op",
        "gov",
        "etf",
        "about",
        "bro",
        "ins",
        "keys",
    ]
    CHOICES += CHOICES_TICKER_DEPENDENT

    def __init__(
        self,
        stock: pd.DataFrame,
        ticker: str,
        start: datetime,
        interval: str,
    ):
        """Constructor"""
        self.stock = stock
        self.ticker = ticker
        self.start = start
        self.interval = interval

        self.update_succcess = False
        self.t_parser = argparse.ArgumentParser(add_help=False, prog="terminal")
        self.t_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer = NestedCompleter.from_nested_dict(
            {c: None for c in self.CHOICES}
        )

    def print_help(self):
        """Print help"""
        help_text = """
What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    update      update terminal from remote
    keys        check for defined api keys
    reset       reset terminal and reload configs
    about       about us
    q(uit)      to abandon the program

Contexts:
>   mill        papermill menu, \t\t menu to generate notebook reports
>   econ        economic data, \t\t\t e.g.: events, FRED data, GDP, VIXCLS
>   pa          portfolio analysis, \t\t analyses your custom portfolio
>   bro         brokers holdings, \t\t supports: robinhood, alpaca, ally
>   crypto      cryptocurrencies, \t\t from: coingecko, coinmarketcap, binance
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt
>   gov         government menu, \t\t house trading, contracts, corporate lobbying
>   etf         etf menu, \t\t\t from: StockAnalysis.com
>   fx          forex menu, \t\t\t forex support through Oanda
>   rc          resource collection, \t\t e.g. hf letters, arXiv, EDGAR, FINRA
>   op          options info,            \t e.g.: volume, open interest, chains, volatility
>   ins         insider trading,         \t e.g.: latest penny stock buys, insider sales
            """

        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.ticker and self.start:
            help_text += f"\n{s_intraday} Stock: {self.ticker} (from {self.start.strftime('%Y-%m-%d')})\n"
        elif self.ticker:
            help_text += f"\n{s_intraday} Stock: {self.ticker}\n"
        else:
            help_text += "\nStock: ?\n"

        help_text += f"Market {('CLOSED', 'OPEN')[b_is_stock_market_open()]}.\n"

        help_text += """
    clear       clear a specific stock ticker from analysis
    load        load a specific stock ticker for analysis
    """

        if self.ticker:
            help_text += """quote       view the current price for a specific stock ticker
    candle      view a candle chart for a specific stock ticker
    view        view and load a specific stock ticker for technical analysis

>   dd          in-depth due-diligence,  \t e.g.: news, analyst, shorts, insider, sec
>   ba          behavioural analysis,    \t from: reddit, stocktwits, twitter, google
>   ta          technical analysis,      \t e.g.: ema, macd, rsi, adx, bbands, obv
>   fa          fundamental analysis,    \t e.g.: income, balance, cash, earnings
>   res         research web page,       \t e.g.: macroaxis, yahoo finance, fool
>   ca          comparison analysis,     \t e.g.: historical, correlation, financials
>   eda         exploratory data analysis,\t e.g.: decompose, cusum, residuals analysis
>   ra          residuals analysis,      \t e.g.: model fit, qqplot, hypothesis test
>   bt          strategy backtester,      \t e.g.: simple ema, ema cross, rsi strategies
>   pred        prediction techniques,   \t e.g.: regression, arima, rnn, lstm"""

        help_text += """\n>   disc        discover trending stocks, \t e.g. map, sectors, high short interest
>   scr         screener stocks, \t\t e.g. overview/performance, using preset filters
        """

        print(help_text)

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

        if not self.ticker and an_input in self.CHOICES_TICKER_DEPENDENT:
            print("No ticker selected. Use 'load <ticker>'.\n")
            return None

        (known_args, other_args) = self.t_parser.parse_known_args(an_input.split())

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

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_q(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_reset(self, _):
        """Process reset command"""
        return True

    def call_clear(self, other_args: List[str]):
        """Process clear command"""
        self.ticker, self.start, self.interval, self.stock = clear(
            other_args, self.ticker, self.start, self.interval, self.stock
        )

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

    def call_view(self, other_args: List[str]):
        """Process view command"""
        view(other_args, self.ticker, self.interval, self.stock)

    def call_disc(self, _):
        """Process disc command"""
        return disc_controller.menu()

    def call_mill(self, _):
        """Process mill command"""
        return mill.papermill_menu()

    def call_fx(self, _):
        """Process fx command"""
        return fx_controller.menu()

    def call_econ(self, _):
        """Process econ command"""
        return econ_controller.menu()

    def call_pa(self, _):
        """Process pa command"""
        return pa_controller.menu()

    def call_bro(self, _):
        """Process bro command"""
        return bro_controller.menu()

    def call_crypto(self, _):
        """Process crypto command"""
        return crypto_controller.menu()

    def call_scr(self, _):
        """Process scr command"""
        return screener_controller.menu()

    def call_rc(self, _):
        """Process rc command"""
        return rc_controller.menu()

    def call_etf(self, _):
        """Process etf command"""
        return etf_controller.menu()

    def call_ins(self, _):
        """Process ins command"""
        return insider_controller.menu()

    def call_gov(self, _):
        """Process gov command"""
        return gov_controller.menu(self.ticker)

    def call_po(self, _):
        """Process po command"""
        return po_controller.menu([self.ticker])

    def call_update(self, _):
        """Process update command"""
        self.update_succcess = not update_terminal()
        return True

    def call_keys(self, _):
        """Process keys command"""
        check_api_keys()

    def call_about(self, _):
        """Process about command"""
        about_us()

    def call_ba(self, _):
        """Process ba command"""
        return ba_controller.menu(
            self.ticker,
            self.start,
        )

    def call_res(self, _):
        """Process res command"""
        return res_controller.menu(
            self.ticker,
            self.start,
            self.interval,
        )

    def call_ca(self, _):
        """Process ca command"""
        return ca_controller.menu(self.ticker, self.start, self.interval, self.stock)

    def call_fa(self, _):
        """Process fa command"""
        return fa_controller.menu(
            self.ticker,
            self.start,
            self.interval,
        )

    def call_ta(self, _):
        """Process ta command"""
        return ta_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

    def call_dd(self, _):
        """Process dd command"""
        return dd_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

    def call_ra(self, _):
        """Process ra command"""
        return ra_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

    def call_bt(self, _):
        """Process bt command"""
        return bt_controller.menu(
            self.ticker,
            self.start,
        )

    def call_eda(self, _):
        """Process eda command"""
        if self.interval == "1440min":
            return eda_controller.menu(
                self.ticker,
                self.start,
                self.interval,
                self.stock,
            )

        df_stock = yf.download(self.ticker, start=self.start, progress=False)
        df_stock.index.name = "date"
        s_interval = "1440min"

        return eda_controller.menu(
            self.ticker,
            self.start,
            s_interval,
            df_stock,
        )

    def call_op(self, _):
        """Process op command"""
        if self.interval == "1440min":
            return op_controller.menu(
                self.ticker,
                self.stock,
            )

        df_stock = yf.download(self.ticker, start=self.start, progress=False)

        return op_controller.menu(
            self.ticker,
            df_stock,
        )

    def call_pred(self, _):
        """Process pred command"""
        if not gtff.ENABLE_PREDICT:
            print(
                "Predict is disabled. Check ENABLE_PREDICT flag on feature_flags.py",
                "\n",
            )
            return None

        try:
            # pylint: disable=import-outside-toplevel
            from gamestonk_terminal.prediction_techniques import pred_controller
        except ModuleNotFoundError as e:
            print("One of the optional packages seems to be missing: ", e, "\n")
            return None
        except Exception as e:
            print(e, "\n")
            return None

        if self.interval == "1440min":
            return pred_controller.menu(
                self.ticker,
                self.start,
                self.interval,
                self.stock,
            )

        # If stock data is intradaily, we need to get data again as prediction
        # techniques work on daily adjusted data. By default we load data from
        # Alpha Vantage because the historical data loaded gives a larger
        # dataset than the one provided by quandl
        try:
            ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
            # pylint: disable=unbalanced-tuple-unpacking
            df_stock_pred, _ = ts.get_daily_adjusted(
                symbol=self.ticker, outputsize="full"
            )

            # pylint: disable=no-member
            df_stock_pred = df_stock_pred.sort_index(ascending=True)
            df_stock_pred = df_stock_pred[self.start :]
            return pred_controller.menu(
                self.ticker,
                self.start,
                "1440min",
                df_stock_pred,
            )
        except Exception as e:
            print(e)
            print("Either the ticker or the API_KEY are invalids. Try again!")
            return None


def terminal():
    """Terminal Menu"""

    bootup()

    ticker = ""  # "GME"
    start = ""  # "2021-01-01"
    stock = pd.DataFrame()  # yf.download(ticker, start, progress=False)
    interval = "1440min"

    t_controller = TerminalController(stock, ticker, start, interval)
    t_controller.print_help()

    parsed_stdin = False

    while True:

        if gtff.ENABLE_QUICK_EXIT:
            print("Quick exit enabled")
            break

        # Get input command from stdin or user
        if not parsed_stdin and len(sys.argv) > 1:
            an_input = " ".join(sys.argv[1:])
            print(f"{get_flair()}> {an_input}")
            parsed_stdin = True

        elif session and gtff.USE_PROMPT_TOOLKIT:
            an_input = session.prompt(
                f"{get_flair()}> ", completer=t_controller.completer
            )

        else:
            an_input = input(f"{get_flair()}> ")

        # Is command empty
        if not an_input:
            print("")
            continue

        # Process list of commands selected by user
        try:
            process_input = t_controller.switch(an_input)
            # None - Keep loop
            # True - Quit or Reset based on flag
            # False - Keep loop and show help menu

            if process_input is not None:
                # Quit terminal
                if process_input:
                    break

                t_controller.print_help()

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

    if not gtff.ENABLE_QUICK_EXIT:
        # Check if the user wants to reset application
        if an_input == "reset" or t_controller.update_succcess:
            ret_code = reset()
            if ret_code != 0:
                print_goodbye()
        else:
            print_goodbye()


if __name__ == "__main__":
    terminal()
