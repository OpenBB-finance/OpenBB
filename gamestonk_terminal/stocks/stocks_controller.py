"""Stock Context Controller"""
__docformat__ = "numpy"

import argparse
import difflib
import os
from typing import List

from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common import newsapi_view
from gamestonk_terminal.helper_funcs import (
    b_is_stock_market_open,
    check_positive,
    export_data,
    get_flair,
    parse_known_args_and_warn,
    valid_date,
    MENU_GO_BACK,
    MENU_QUIT,
    MENU_RESET,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.stocks_helper import (
    display_candle,
    search,
    load,
    quote,
    process_candle,
)

from gamestonk_terminal.common.quantitative_analysis import qa_view

# pylint: disable=R1710,import-outside-toplevel


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
        "reset",
    ]

    CHOICES_COMMANDS = [
        "search",
        "load",
        "quote",
        "candle",
        "news",
    ]

    CHOICES_MENUS = [
        "ta",
        "ba",
        "qa",
        "pred",
        "disc",
        "dps",
        "scr",
        "sia",
        "ins",
        "gov",
        "res",
        "fa",
        "bt",
        "dd",
        "ca",
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
        dim_if_no_ticker = Style.DIM if not self.ticker else ""
        reset_style_if_no_ticker = Style.RESET_ALL if not self.ticker else ""
        help_text = f"""
What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program
    reset       reset terminal and reload configs

    search      search a specific stock ticker for analysis
    load        load a specific stock ticker for analysis

{stock_text}
Market {('CLOSED', 'OPEN')[b_is_stock_market_open()]}
{dim_if_no_ticker}
    quote       view the current price for a specific stock ticker
    candle      view a candle chart for a specific stock ticker
    news        latest news of the company [News API]
{reset_style_if_no_ticker}
>   options     options menu,  \t\t\t e.g.: chains, open interest, greeks, parity
>   disc        discover trending stocks, \t e.g. map, sectors, high short interest
>   sia         sector and industry analysis, \t e.g. companies per sector, quick ratio per industry and country
>   dps         dark pool and short data, \t e.g. darkpool, short interest, ftd
>   scr         screener stocks, \t\t e.g. overview/performance, using preset filters
>   ins         insider trading,         \t e.g.: latest penny stock buys, top officer purchases
>   gov         government menu, \t\t e.g. house trading, contracts, corporate lobbying
>   ba          behavioural analysis,    \t from: reddit, stocktwits, twitter, google
>   ca          comparison analysis,     \t e.g.: get similar, historical, correlation, financials{dim_if_no_ticker}
>   fa          fundamental analysis,    \t e.g.: income, balance, cash, earnings
>   res         research web page,       \t e.g.: macroaxis, yahoo finance, fool
>   dd          in-depth due-diligence,  \t e.g.: news, analyst, shorts, insider, sec
>   bt          strategy backtester,      \t e.g.: simple ema, ema cross, rsi strategies
>   ta          technical analysis,      \t e.g.: ema, macd, rsi, adx, bbands, obv
>   qa          quantitative analysis,   \t e.g.: decompose, cusum, residuals analysis
>   pred        prediction techniques,   \t e.g.: regression, arima, rnn, lstm
{reset_style_if_no_ticker}"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        MENU_GO_BACK, MENU_QUIT, MENU_RESET
            MENU_GO_BACK - Show main context menu again
            MENU_QUIT - Quit terminal
            MENU_RESET - Reset terminal and go back to same previous menu
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
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return MENU_GO_BACK

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return MENU_QUIT

    def call_reset(self, _):
        """Process Reset command - reset the program"""
        return MENU_RESET

    # COMMANDS
    @try_except
    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Show companies matching the search query.",
        )
        parser.add_argument(
            "-q",
            "--query",
            action="store",
            dest="query",
            type=str.lower,
            required="-h" not in other_args,
            help="The search term used to find company tickers.",
        )
        parser.add_argument(
            "-a",
            "--amount",
            default=10,
            type=int,
            dest="amount",
            help="Enter the number of Equities you wish to see in the Tabulate window.",
        )

        if other_args and "-q" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-q")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        search(query=ns_parser.query, amount=ns_parser.amount)

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
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=int,
            default=1440,
            choices=[1, 5, 15, 30, 60],
            help="Intraday stock minutes",
        )
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=["yf", "av", "iex"],
            default="yf",
            help="Source of historical data.",
        )
        parser.add_argument(
            "-p",
            "--prepost",
            action="store_true",
            default=False,
            dest="prepost",
            help="Pre/After market hours. Only works for 'yf' source, and intraday data",
        )

        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df_stock_candidate = load(
            ns_parser.ticker,
            ns_parser.start,
            ns_parser.interval,
            ns_parser.end,
            ns_parser.prepost,
            ns_parser.source,
        )

        if not df_stock_candidate.empty:
            self.stock = df_stock_candidate
            if "." in ns_parser.ticker:
                self.ticker, self.suffix = ns_parser.ticker.upper().split(".")
            else:
                self.ticker = ns_parser.ticker.upper()
                self.suffix = ""

            self.start = ns_parser.start
            self.interval = f"{ns_parser.interval}min"

    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        quote(
            other_args, self.ticker + "." + self.suffix if self.suffix else self.ticker
        )

    @try_except
    def call_candle(self, other_args: List[str]):
        """Process candle command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Shows historic data for a stock",
        )
        parser.add_argument(
            "-m",
            "--matplotlib",
            dest="matplotlib",
            action="store_true",
            default=False,
            help="Flag to show matplotlib instead of interactive plot using plotly.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        parser.add_argument(
            "--sort",
            choices=[
                "AdjClose",
                "Open",
                "Close",
                "High",
                "Low",
                "Volume",
                "Returns",
                "LogRet",
            ],
            default="",
            type=str,
            dest="sort",
            help="Choose a column to sort by",
        )
        parser.add_argument(
            "-d",
            "--descending",
            action="store_false",
            dest="descending",
            default=True,
            help="Sort selected column descending",
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Shows raw data instead of chart",
        )
        parser.add_argument(
            "-n",
            "--num",
            type=check_positive,
            help="Number to show if raw selected",
            dest="num",
            default=20,
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not self.ticker:
            print("No ticker loaded. First use `load {ticker}`\n")
            return

        export_data(
            ns_parser.export,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_data"),
            f"{self.ticker}",
            self.stock,
        )

        if ns_parser.raw:
            qa_view.display_raw(
                df=self.stock,
                sort=ns_parser.sort,
                des=ns_parser.descending,
                num=ns_parser.num,
            )

        else:
            data = process_candle(self.stock)

            display_candle(
                s_ticker=self.ticker,
                df_stock=data,
                use_matplotlib=ns_parser.matplotlib,
                intraday=self.interval != "1440min",
            )

    @try_except
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
        parser.add_argument(
            "-d",
            "--date",
            action="store",
            dest="n_start_date",
            type=valid_date,
            default=datetime.now() - timedelta(days=7),
            help="The starting date (format YYYY-MM-DD) to search articles from",
        )
        parser.add_argument(
            "-o",
            "--oldest",
            action="store_false",
            dest="n_oldest",
            default=True,
            help="Show oldest articles first",
        )
        parser.add_argument(
            "-s",
            "--sources",
            default=[],
            nargs="+",
            help="Show news only from the sources specified (e.g bbc yahoo.com)",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        sources = ns_parser.sources
        for idx, source in enumerate(sources):
            if source.find(".") == -1:
                sources[idx] += ".com"

        d_stock = yf.Ticker(self.ticker).info

        newsapi_view.news(
            term=d_stock["shortName"].replace(" ", "+")
            if "shortName" in d_stock
            else self.ticker,
            num=ns_parser.n_num,
            s_from=ns_parser.n_start_date.strftime("%Y-%m-%d"),
            show_newest=ns_parser.n_oldest,
            sources=",".join(sources),
        )

    # MENUS
    def call_disc(self, _):
        """Process disc command"""
        from gamestonk_terminal.stocks.discovery import disc_controller

        ret = disc_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_dps(self, _):
        """Process dps command"""
        from gamestonk_terminal.stocks.dark_pool_shorts import dps_controller

        ret = dps_controller.menu(self.ticker, self.start, self.stock)
        if ret is False:
            self.print_help()
        else:
            return True

    def call_scr(self, _):
        """Process scr command"""
        from gamestonk_terminal.stocks.screener import screener_controller

        ret = screener_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_sia(self, _):
        """Process ins command"""
        from gamestonk_terminal.stocks.sector_industry_analysis import sia_controller

        ret = sia_controller.menu(self.ticker)
        if ret is False:
            self.print_help()
        else:
            return True

    def call_ins(self, _):
        """Process ins command"""
        from gamestonk_terminal.stocks.insider import insider_controller

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
        from gamestonk_terminal.stocks.government import gov_controller

        ret = gov_controller.menu(self.ticker)
        if ret is False:
            self.print_help()
        else:
            return True

    def call_options(self, _):
        """Process options command"""
        from gamestonk_terminal.stocks.options import options_controller

        ret = options_controller.menu(self.ticker)
        if ret is False:
            self.print_help()
        else:
            return True

    def call_res(self, _):
        """Process res command"""
        from gamestonk_terminal.stocks.research import res_controller

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
        from gamestonk_terminal.stocks.due_diligence import dd_controller

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

        from gamestonk_terminal.stocks.comparison_analysis import ca_controller

        ret = ca_controller.menu([self.ticker] if self.ticker else "")

        if ret is False:
            self.print_help()
        else:
            return True

    def call_fa(self, _):
        """Process fa command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        from gamestonk_terminal.stocks.fundamental_analysis import fa_controller

        ret = fa_controller.menu(self.ticker, self.start, self.interval, self.suffix)

        if ret is False:
            self.print_help()
        else:
            return True

    def call_bt(self, _):
        """Process bt command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        from gamestonk_terminal.stocks.backtesting import bt_controller

        ret = bt_controller.menu(self.ticker, self.stock)

        if ret is False:
            self.print_help()
        else:
            return True

    def call_ta(self, _):
        """Process ta command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        from gamestonk_terminal.stocks.technical_analysis import ta_controller

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
        from gamestonk_terminal.stocks.behavioural_analysis import ba_controller

        ret = ba_controller.menu(
            self.ticker,
            self.start,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    def call_qa(self, _):
        """Process qa command"""
        if not self.ticker:
            print("Use 'load <ticker>' prior to this command!", "\n")
            return

        if self.interval != "1440min":
            # TODO: This menu should work regardless of data being daily or not!
            print("Load daily data to use this menu!", "\n")
            return

        from gamestonk_terminal.stocks.quantitative_analysis import qa_controller

        ret = qa_controller.menu(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
        )

        if ret is False:
            self.print_help()
        else:
            return True

    @try_except
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
            similar_cmd = difflib.get_close_matches(
                an_input, stocks_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")

            continue
