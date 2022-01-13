"""Stock Context Controller"""
__docformat__ = "numpy"

import argparse
import logging
import os
from typing import List

from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common import newsapi_view
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    export_data,
    parse_known_args_and_warn,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks import stocks_helper

from gamestonk_terminal.common.quantitative_analysis import qa_view

# pylint: disable=R1710,import-outside-toplevel

logger = logging.getLogger(__name__)


class StocksController(BaseController):
    """Stocks Controller class"""

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

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/stocks/", queue)

        self.stock = pd.DataFrame()
        self.ticker = ""
        self.suffix = ""  # To hold suffix for Yahoo Finance
        self.start = ""
        self.interval = "1440min"
        self.add_info = stocks_helper.additional_info_about_ticker("")

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

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
    search      search a specific stock ticker for analysis
    load        load a specific stock ticker and additional info for analysis
{dim_if_no_ticker}
{stock_text}
{self.add_info}

    quote       view the current price for a specific stock ticker
    candle      view a candle chart for a specific stock ticker
    news        latest news of the company [News API]
{reset_style_if_no_ticker}
Stocks Menus:
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

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return [
                "stocks",
                f"load {self.ticker}.{self.suffix}"
                if self.suffix
                else f"load {self.ticker}",
            ]
        return []

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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-q")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            stocks_helper.search(query=ns_parser.query, amount=ns_parser.amount)

    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source"
            + " is syf', an Indian ticker can be"
            + " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            + " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
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
            default=(datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d"),
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
            choices=["yf", "av", "iex"] if "-i" not in other_args else ["yf"],
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
        parser.add_argument(
            "-r",
            "--iexrange",
            dest="iexrange",
            help="Range for using the iexcloud api.  Note that longer range requires more tokens in account",
            choices=["ytd", "1y", "2y", "5y", "6m"],
            type=str,
            default="ytd",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            df_stock_candidate = stocks_helper.load(
                ns_parser.ticker,
                ns_parser.start,
                ns_parser.interval,
                ns_parser.end,
                ns_parser.prepost,
                ns_parser.source,
            )
            if not df_stock_candidate.empty:
                self.stock = df_stock_candidate
                self.add_info = stocks_helper.additional_info_about_ticker(
                    ns_parser.ticker
                )
                print(self.add_info)
                if "." in ns_parser.ticker:
                    self.ticker, self.suffix = ns_parser.ticker.upper().split(".")
                else:
                    self.ticker = ns_parser.ticker.upper()
                    self.suffix = ""

                if ns_parser.source == "iex":
                    self.start = self.stock.index[0].strftime("%Y-%m-%d")
                else:
                    self.start = ns_parser.start
                self.interval = f"{ns_parser.interval}min"
                print("")

    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        stocks_helper.quote(
            other_args, self.ticker + "." + self.suffix if self.suffix else self.ticker
        )

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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.ticker:
                export_data(
                    ns_parser.export,
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "raw_data"
                    ),
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
                    data = stocks_helper.process_candle(self.stock)

                    stocks_helper.display_candle(
                        s_ticker=self.ticker,
                        df_stock=data,
                        use_matplotlib=ns_parser.matplotlib,
                        intraday=self.interval != "1440min",
                    )
            else:
                print("No ticker loaded. First use `load {ticker}`\n")

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
        if ns_parser:
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

    def call_disc(self, _):
        """Process disc command"""
        from gamestonk_terminal.stocks.discovery.disc_controller import (
            DiscoveryController,
        )

        self.queue = DiscoveryController(self.queue).menu()

    def call_dps(self, _):
        """Process dps command"""
        from gamestonk_terminal.stocks.dark_pool_shorts.dps_controller import (
            DarkPoolShortsController,
        )

        self.queue = DarkPoolShortsController(
            self.ticker, self.start, self.stock, self.queue
        ).menu()

    def call_scr(self, _):
        """Process scr command"""
        from gamestonk_terminal.stocks.screener.screener_controller import (
            ScreenerController,
        )

        self.queue = ScreenerController(self.queue).menu()

    def call_sia(self, _):
        """Process ins command"""
        from gamestonk_terminal.stocks.sector_industry_analysis.sia_controller import (
            SectorIndustryAnalysisController,
        )

        self.queue = SectorIndustryAnalysisController(self.ticker, self.queue).menu()

    def call_ins(self, _):
        """Process ins command"""
        from gamestonk_terminal.stocks.insider.insider_controller import (
            InsiderController,
        )

        self.queue = InsiderController(
            self.ticker,
            self.start,
            self.interval,
            self.stock,
            self.queue,
        ).menu()

    def call_gov(self, _):
        """Process gov command"""
        from gamestonk_terminal.stocks.government.gov_controller import GovController

        self.queue = GovController(self.ticker, self.queue).menu()

    def call_options(self, _):
        """Process options command"""
        from gamestonk_terminal.stocks.options.options_controller import (
            OptionsController,
        )

        self.queue = OptionsController(self.ticker, self.queue).menu()

    def call_res(self, _):
        """Process res command"""
        if self.ticker:
            from gamestonk_terminal.stocks.research.res_controller import (
                ResearchController,
            )

            self.queue = ResearchController(
                self.ticker,
                self.start,
                self.interval,
                self.queue,
            ).menu()
        else:
            print("Use 'load <ticker>' prior to this command!", "\n")

    def call_dd(self, _):
        """Process dd command"""
        if self.ticker:
            from gamestonk_terminal.stocks.due_diligence import dd_controller

            self.queue = dd_controller.DueDiligenceController(
                self.ticker, self.start, self.interval, self.stock, self.queue
            ).menu()
        else:
            print("Use 'load <ticker>' prior to this command!", "\n")

    def call_ca(self, _):
        """Process ca command"""

        from gamestonk_terminal.stocks.comparison_analysis import ca_controller

        self.queue = ca_controller.ComparisonAnalysisController(
            [self.ticker] if self.ticker else "", self.queue
        ).menu()

    def call_fa(self, _):
        """Process fa command"""
        if self.ticker:
            from gamestonk_terminal.stocks.fundamental_analysis import fa_controller

            self.queue = fa_controller.FundamentalAnalysisController(
                self.ticker, self.start, self.interval, self.suffix, self.queue
            ).menu()
        else:
            print("Use 'load <ticker>' prior to this command!", "\n")

    def call_bt(self, _):
        """Process bt command"""
        if self.ticker:
            from gamestonk_terminal.stocks.backtesting import bt_controller

            self.queue = bt_controller.BacktestingController(
                self.ticker, self.stock, self.queue
            ).menu()
        else:
            print("Use 'load <ticker>' prior to this command!", "\n")

    def call_ta(self, _):
        """Process ta command"""
        if self.ticker:
            from gamestonk_terminal.stocks.technical_analysis import ta_controller

            self.queue = ta_controller.TechnicalAnalysisController(
                self.ticker, self.start, self.interval, self.stock, self.queue
            ).menu()
        else:
            print("Use 'load <ticker>' prior to this command!", "\n")

    def call_ba(self, _):
        """Process ba command"""
        from gamestonk_terminal.stocks.behavioural_analysis import ba_controller

        self.queue = ba_controller.BehaviouralAnalysisController(
            self.ticker, self.start, self.queue
        ).menu()

    def call_qa(self, _):
        """Process qa command"""
        if self.ticker:
            if self.interval == "1440min":
                from gamestonk_terminal.stocks.quantitative_analysis import (
                    qa_controller,
                )

                self.queue = qa_controller.QaController(
                    self.ticker, self.start, self.interval, self.stock, self.queue
                ).menu()
            # TODO: This menu should work regardless of data being daily or not!
            print("Load daily data to use this menu!", "\n")
        else:
            print("Use 'load <ticker>' prior to this command!", "\n")

    def call_pred(self, _):
        """Process pred command"""
        if gtff.ENABLE_PREDICT:
            if self.ticker:
                if self.interval == "1440min":
                    try:
                        from gamestonk_terminal.stocks.prediction_techniques import (
                            pred_controller,
                        )

                        self.queue = pred_controller.PredictionTechniquesController(
                            self.ticker,
                            self.start,
                            self.interval,
                            self.stock,
                            self.queue,
                        ).menu()
                    except ModuleNotFoundError as e:
                        print(
                            "One of the optional packages seems to be missing: ",
                            e,
                            "\n",
                        )

                # TODO: This menu should work regardless of data being daily or not!
                print("Load daily data to use this menu!", "\n")
            else:
                print("Use 'load <ticker>' prior to this command!", "\n")
        else:
            print(
                "Predict is disabled. Check ENABLE_PREDICT flag on feature_flags.py",
                "\n",
            )
