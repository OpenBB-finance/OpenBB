"""Technical Analysis Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive_list,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.technical_analysis import (
    finviz_view,
    finbrain_view,
    finnhub_view,
    tradingview_view,
)
from gamestonk_terminal.common.technical_analysis import (
    custom_indicators_view,
    momentum_model,
    overlap_view,
    trend_indicators,
    volatility_model,
    volume_model,
)


class TechnicalAnalysisController:
    """Technical Analysis Controller class"""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "view",
        "summary",
        "recom",
        "pr",
        "ema",
        "sma",
        "vwap",
        "zlma",
        "cci",
        "macd",
        "rsi",
        "stoch",
        "fisher",
        "cg",
        "adx",
        "aroon",
        "bbands",
        "ad",
        "obv",
        "fib",
    ]

    def __init__(
        self,
        s_stock: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
    ):
        """Constructor"""
        self.s_stock = s_stock
        self.start = start
        self.interval = interval
        self.stock = stock

        self.ta_parser = argparse.ArgumentParser(add_help=False, prog="ta")
        self.ta_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        s_intraday = (f"Intraday {self.interval}", "Daily")[self.interval == "1440min"]
        if self.start:
            str1 = f"\n{s_intraday} Stock: {self.s_stock} (from {self.start.strftime('%Y-%m-%d')})"
        else:
            str1 = f"\n{s_intraday} Stock: {self.s_stock}"

        help_str = f"""https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/stocks/technical_analysis
{str1}

Technical Analysis:
    cls         clear screen
    help        show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon program

    view        view historical data and trendlines [Finviz]
    summary     technical summary report [FinBrain API]
    recom       recommendation based on Technical Indicators [Tradingview API]
    pr          pattern recognition [Finnhub]

overlap:
    ema         exponential moving average
    sma         simple moving average
    zlma        zero lag moving average"
    vwap        volume weighted average price
momentum:
    cci         commodity channel index
    macd        moving average convergence/divergence
    rsi         relative strength index
    stoch       stochastic oscillator
    fisher      fisher transform
    cg          centre of gravity
trend:
    adx         average directional movement index
    aroon       aroon indicator
volatility:
    bbands      bollinger bands
volume:
    ad          accumulation/distribution line values
    obv         on balance volume
custom:
    fib         fibonacci retracement
"""
        print(help_str)

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

        (known_args, other_args) = self.ta_parser.parse_known_args(an_input.split())

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

    # SPECIFIC
    def call_view(self, other_args: List[str]):
        """Process view command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="view",
            description="""
            View historical price with trendlines. [Source: Finviz]
        """,
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finviz_view.view(self.s_stock)

        except Exception as e:
            print(e, "\n")

    def call_summary(self, other_args: List[str]):
        """Process summary command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="summary",
            description="""
            Technical summary report provided by FinBrain's API.
            FinBrain Technologies develops deep learning algorithms for financial analysis
            and prediction, which currently serves traders from more than 150 countries
            all around the world. [Source:  https://finbrain.tech]
        """,
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finbrain_view.technical_summary_report(self.s_stock)

        except Exception as e:
            print(e, "\n")

    def call_recom(self, other_args: List[str]):
        """Process recom command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="recom",
            description="""
            Print tradingview recommendation based on technical indicators.
            [Source: https://pypi.org/project/tradingview-ta/]
        """,
        )
        parser.add_argument(
            "-s",
            "--screener",
            action="store",
            dest="screener",
            type=str,
            default="america",
            choices=["crypto", "forex", "cfd"],
            help="Screener. See https://python-tradingview-ta.readthedocs.io/en/latest/usage.html",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            action="store",
            dest="exchange",
            type=str,
            default="",
            help="""Set exchange. For Forex use: 'FX_IDC', and for crypto use 'TVC'.
            See https://python-tradingview-ta.readthedocs.io/en/latest/usage.html.
            By default Alpha Vantage tries to get this data from the ticker. """,
        )
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=str,
            default="",
            choices=["1M", "1W", "1d", "4h", "1h", "15m", "5m", "1m"],
            help="""Interval, that corresponds to the recommendation given by tradingview based on technical indicators.
            See https://python-tradingview-ta.readthedocs.io/en/latest/usage.html""",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            tradingview_view.print_recommendation(
                ticker=self.s_stock,
                screener=ns_parser.screener,
                exchange=ns_parser.exchange,
                interval=ns_parser.interval,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_pr(self, other_args: List[str]):
        """Process pr command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pr",
            description="""
            Display pattern recognition signals on the data. [Source: https://finnhub.io]
        """,
        )
        parser.add_argument(
            "-r",
            "--resolution",
            action="store",
            dest="resolution",
            type=str,
            default="D",
            choices=["1", "5", "15", "30", "60", "D", "W", "M"],
            help="Plot resolution to look for pattern signals",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finnhub_view.plot_pattern_recognition(
                ticker=self.s_stock,
                resolution=ns_parser.resolution,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    # COMMON
    def call_ema(self, other_args: List[str]):
        """Process ema command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ema",
            description="""
            The Exponential Moving Average is a staple of technical
            analysis and is used in countless technical indicators. In a Simple Moving
            Average, each value in the time period carries equal weight, and values outside
            of the time period are not included in the average. However, the Exponential
            Moving Average is a cumulative calculation, including all data. Past values have
            a diminishing contribution to the average, while more recent values have a greater
            contribution. This method allows the moving average to be more responsive to changes
            in the data.
        """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive_list,
            default=[20, 50],
            help="length",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            overlap_view.view_ma(
                ma="EMA",
                s_ticker=self.s_stock,
                s_interval=self.interval,
                df_stock=self.stock,
                window_length=ns_parser.n_length,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_sma(self, other_args: List[str]):
        """Process sma command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sma",
            description="""
                Moving Averages are used to smooth the data in an array to
                help eliminate noise and identify trends. The Simple Moving Average is literally
                the simplest form of a moving average. Each output value is the average of the
                previous n values. In a Simple Moving Average, each value in the time period carries
                equal weight, and values outside of the time period are not included in the average.
                This makes it less responsive to recent changes in the data, which can be useful for
                filtering out those changes.
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive_list,
            default=[20, 50],
            help="length",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            overlap_view.view_ma(
                ma="SMA",
                s_ticker=self.s_stock,
                s_interval=self.interval,
                df_stock=self.stock,
                window_length=ns_parser.n_length,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_zlma(self, other_args: List[str]):
        """Process zlma command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="zlma",
            description="""
                The zero lag exponential moving average (ZLEMA) indicator
                was created by John Ehlers and Ric Way. The idea is do a
                regular exponential moving average (EMA) calculation but
                on a de-lagged data instead of doing it on the regular data.
                Data is de-lagged by removing the data from "lag" days ago
                thus removing (or attempting to) the cumulative effect of
                the moving average.
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive_list,
            default=[20],
            help="length",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            overlap_view.view_ma(
                ma="ZLMA",
                s_ticker=self.s_stock,
                s_interval=self.interval,
                df_stock=self.stock,
                window_length=ns_parser.n_length,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_vwap(self, other_args: List[str]):
        """Process vwap command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vwap",
            description="""
                The Volume Weighted Average Price that measures the average typical price
                by volume.  It is typically used with intraday charts to identify general direction.
            """,
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            # Daily
            if self.interval == "1440min":
                print("VWAP should be used with intraday data. \n")
                return

            overlap_view.view_vwap(
                s_ticker=self.s_stock,
                s_interval=self.interval,
                df_stock=self.stock,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_cci(self, other_args: List[str]):
        """Process cci command"""
        momentum_model.cci(other_args, self.s_stock, self.interval, self.stock)

    def call_macd(self, other_args: List[str]):
        """Process macd command"""
        momentum_model.macd(other_args, self.s_stock, self.interval, self.stock)

    def call_rsi(self, other_args: List[str]):
        """Process rsi command"""
        momentum_model.rsi(other_args, self.s_stock, self.interval, self.stock)

    def call_stoch(self, other_args: List[str]):
        """Process stoch command"""
        momentum_model.stoch(other_args, self.s_stock, self.interval, self.stock)

    def call_fisher(self, other_args: List[str]):
        """Process fisher command"""
        momentum_model.fisher(other_args, self.s_stock, self.interval, self.stock)

    def call_cg(self, other_args: List[str]):
        """Process cg command"""
        momentum_model.cg(other_args, self.s_stock, self.interval, self.stock)

    def call_adx(self, other_args: List[str]):
        """Process adx command"""
        trend_indicators.adx(other_args, self.s_stock, self.interval, self.stock)

    def call_aroon(self, other_args: List[str]):
        """Process aroon command"""
        trend_indicators.aroon(other_args, self.s_stock, self.interval, self.stock)

    def call_bbands(self, other_args: List[str]):
        """Process bbands command"""
        volatility_model.bbands(other_args, self.s_stock, self.interval, self.stock)

    def call_ad(self, other_args: List[str]):
        """Process ad command"""
        volume_model.ad(other_args, self.s_stock, self.interval, self.stock)

    def call_obv(self, other_args: List[str]):
        """Process obv command"""
        volume_model.obv(other_args, self.s_stock, self.interval, self.stock)

    def call_fib(self, other_args: List[str]):
        """Process fib command"""
        custom_indicators_view.fibinocci_retracement(
            other_args, self.stock, self.s_stock
        )


def menu(s_stock: str, start: datetime, interval: str, stock: pd.DataFrame):
    """Technical Analysis Menu"""

    ta_controller = TechnicalAnalysisController(s_stock, start, interval, stock)
    ta_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ta_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (stocks)>(ta)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(ta)> ")

        try:
            plt.close("all")

            process_input = ta_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
