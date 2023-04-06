"""Crypto Technical Analysis Controller Module"""
__docformat__ = "numpy"
# pylint: disable=C0302,R0904,C0201

import argparse
import logging
import webbrowser
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd

from openbb_terminal.common.technical_analysis import (
    custom_indicators_view,
    momentum_view,
    overlap_model,
    overlap_view,
    trend_indicators_view,
    volatility_model,
    volatility_view,
    volume_view,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    check_non_negative,
    check_positive,
    check_positive_float,
    check_positive_list,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import CryptoBaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


def no_ticker_message():
    """Print message when no ticker is loaded"""
    console.print("[red]No data loaded. Use 'load' command to load a symbol[/red]")


class TechnicalAnalysisController(CryptoBaseController):
    """Technical Analysis Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "ema",
        "sma",
        "wma",
        "hma",
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
        "donchian",
        "kc",
        "ad",
        "adosc",
        "obv",
        "fib",
        "tv",
        "atr",
        "demark",
        "cones",
    ]

    PATH = "/crypto/ta/"
    CHOICES_GENERATION = True

    def __init__(
        self,
        coin: str,
        start: datetime,
        interval: str,
        stock: pd.DataFrame,
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.coin = coin
        self.start = start
        self.interval = interval
        self.stock = stock
        self.stock["Adj Close"] = stock["Close"]

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            choices["load"] = {
                "--interval": {
                    c: {}
                    for c in [
                        "1",
                        "5",
                        "15",
                        "30",
                        "60",
                        "240",
                        "1440",
                        "10080",
                        "43200",
                    ]
                },
                "-i": "--interval",
                "--exchange": {c: {} for c in self.exchanges},
                "--source": {c: {} for c in ["CCXT", "YahooFinance", "CoingGecko"]},
                "--vs": {c: {} for c in ["usd", "eur"]},
                "--start": None,
                "-s": "--start",
                "--end": None,
                "-e": "--end",
            }

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        crypto_str = f" {self.coin} (from {self.start.strftime('%Y-%m-%d')})"
        mt = MenuText("crypto/ta/", 90)
        mt.add_param("_ticker", crypto_str)
        mt.add_raw("\n")
        mt.add_cmd("tv")
        mt.add_raw("\n")
        mt.add_info("_overlap_")
        mt.add_cmd("ema")
        mt.add_cmd("hma")
        mt.add_cmd("sma")
        mt.add_cmd("vwap")
        mt.add_cmd("wma")
        mt.add_cmd("zlma")
        mt.add_info("_momentum_")
        mt.add_cmd("cci")
        mt.add_cmd("cg")
        mt.add_cmd("demark")
        mt.add_cmd("fisher")
        mt.add_cmd("macd")
        mt.add_cmd("rsi")
        mt.add_cmd("stoch")
        mt.add_info("_trend_")
        mt.add_cmd("adx")
        mt.add_cmd("aroon")
        mt.add_info("_volatility_")
        mt.add_cmd("atr")
        mt.add_cmd("bbands")
        mt.add_cmd("cones")
        mt.add_cmd("donchian")
        mt.add_cmd("kc")
        mt.add_info("_volume_")
        mt.add_cmd("ad")
        mt.add_cmd("adosc")
        mt.add_cmd("obv")
        mt.add_info("_custom_")
        mt.add_cmd("fib")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Technical Analysis")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.coin:
            return ["crypto", f"load {self.coin}", "ta"]
        return []

    @log_start_end(log=logger)
    def call_tv(self, other_args):
        """Process tv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tv",
            description="""View TradingView for technical analysis. [Source: TradingView]""",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            # temp USDT before we make changes to crypto ta_controller
            webbrowser.open(
                f"https://www.tradingview.com/chart/?symbol={self.coin}usdt"
            )

    # COMMON
    # TODO: Go through all models and make sure all needed columns are in dfs

    @log_start_end(log=logger)
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
            default=overlap_model.WINDOW_LENGTHS,
            help="Window lengths.  Multiple values indicated as comma separated values.",
        )
        parser.add_argument(
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=check_non_negative,
            default=0,
            help="offset",
            choices=range(0, 100),
            metavar="N_OFFSET",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            overlap_view.view_ma(
                ma_type="EMA",
                symbol=self.coin,
                data=self.stock["Adj Close"],
                window=ns_parser.n_length,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            default=overlap_model.WINDOW_LENGTHS,
            help="Window lengths.  Multiple values indicated as comma separated values. ",
        )
        parser.add_argument(
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=check_non_negative,
            default=0,
            help="offset",
            choices=range(0, 100),
            metavar="N_OFFSET",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            overlap_view.view_ma(
                ma_type="SMA",
                symbol=self.coin,
                data=self.stock["Adj Close"],
                window=ns_parser.n_length,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_wma(self, other_args: List[str]):
        """Process wma command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="wma",
            description="""
                A Weighted Moving Average puts more weight on recent data and less on past data.
                This is done by multiplying each bar’s price by a weighting factor. Because of its
                unique calculation, WMA will follow prices more closely than a corresponding Simple
                Moving Average.
                        """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive_list,
            default=overlap_model.WINDOW_LENGTHS,
            help="Window lengths.  Multiple values indicated as comma separated values. ",
        )
        parser.add_argument(
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=check_non_negative,
            default=0,
            help="offset",
            choices=range(0, 100),
            metavar="N_OFFSET",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            overlap_view.view_ma(
                ma_type="WMA",
                symbol=self.coin,
                data=self.stock["Adj Close"],
                window=ns_parser.n_length,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_hma(self, other_args: List[str]):
        """Process hma command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hma",
            description="""
                The Hull Moving Average solves the age old dilemma of making a moving average
                more responsive to current price activity whilst maintaining curve smoothness.
                In fact the HMA almost eliminates lag altogether and manages to improve smoothing
                at the same time.
                        """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive_list,
            default=overlap_model.WINDOW_LENGTHS2,
            help="Window lengths.  Multiple values indicated as comma separated values. ",
        )
        parser.add_argument(
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=check_non_negative,
            default=0,
            help="offset",
            choices=range(0, 100),
            metavar="N_OFFSET",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            overlap_view.view_ma(
                ma_type="HMA",
                symbol=self.coin,
                data=self.stock["Adj Close"],
                window=ns_parser.n_length,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            help="Window lengths.  Multiple values indicated as comma separated values.",
        )
        parser.add_argument(
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=check_non_negative,
            default=0,
            help="offset",
            choices=range(0, 100),
            metavar="N_OFFSET",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            overlap_view.view_ma(
                ma_type="ZLMA",
                symbol=self.coin,
                data=self.stock["Adj Close"],
                window=ns_parser.n_length,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=check_non_negative,
            default=0,
            help="offset",
            choices=range(0, 100),
            metavar="N_OFFSET",
        )
        parser.add_argument(
            "--start",
            dest="start",
            type=valid_date,
            help="Starting date to select",
            required="--end" in other_args,
        )
        parser.add_argument(
            "--end",
            dest="end",
            type=valid_date,
            help="Ending date to select",
            required="--start" in other_args,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            # Daily
            if self.interval == "1440min":
                if not ns_parser.start:
                    console.print(
                        "If no date conditions, VWAP should be used with intraday data. \n"
                    )
                    return
                interval_text = "Daily"
            else:
                interval_text = self.interval

            overlap_view.view_vwap(
                symbol=self.coin,
                interval=interval_text,
                data=self.stock,
                start_date=ns_parser.start,
                end_date=ns_parser.end,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_cci(self, other_args: List[str]):
        """Process cci command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cci",
            description="""
                The CCI is designed to detect beginning and ending market trends.
                The range of 100 to -100 is the normal trading range. CCI values outside of this
                range indicate overbought or oversold conditions. You can also look for price
                divergence in the CCI. If the price is making new highs, and the CCI is not,
                then a price correction is likely.
            """,
        )

        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )
        parser.add_argument(
            "-s",
            "--scalar",
            action="store",
            dest="n_scalar",
            type=check_positive,
            default=0.015,
            help="scalar",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            momentum_view.display_cci(
                symbol=self.coin,
                data=self.stock,
                window=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_macd(self, other_args: List[str]):
        """Process macd command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="macd",
            description="""
                The Moving Average Convergence Divergence (MACD) is the difference
                between two Exponential Moving Averages. The Signal line is an Exponential Moving
                Average of the MACD. \n \n The MACD signals trend changes and indicates the start
                of new trend direction. High values indicate overbought conditions, low values
                indicate oversold conditions. Divergence with the price indicates an end to the
                current trend, especially if the MACD is at extreme high or low values. When the MACD
                line crosses above the signal line a buy signal is generated. When the MACD crosses
                below the signal line a sell signal is generated. To confirm the signal, the MACD
                should be above zero for a buy, and below zero for a sell.
            """,
        )
        parser.add_argument(
            "--fast",
            action="store",
            dest="n_fast",
            type=check_positive,
            default=12,
            help="The short period.",
            choices=range(1, 100),
            metavar="N_FAST",
        )
        parser.add_argument(
            "--slow",
            action="store",
            dest="n_slow",
            type=check_positive,
            default=26,
            help="The long period.",
        )
        parser.add_argument(
            "--signal",
            action="store",
            dest="n_signal",
            type=check_positive,
            default=9,
            help="The signal period.",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            momentum_view.display_macd(
                symbol=self.coin,
                data=self.stock["Adj Close"],
                n_fast=ns_parser.n_fast,
                n_slow=ns_parser.n_slow,
                n_signal=ns_parser.n_signal,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rsi(self, other_args: List[str]):
        """Process rsi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rsi",
            description="""
                The Relative Strength Index (RSI) calculates a ratio of the
                recent upward price movements to the absolute price movement. The RSI ranges
                from 0 to 100. The RSI is interpreted as an overbought/oversold indicator when
                the value is over 70/below 30. You can also look for divergence with price. If
                the price is making new highs/lows, and the RSI is not, it indicates a reversal.
            """,
        )

        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )
        parser.add_argument(
            "-s",
            "--scalar",
            action="store",
            dest="n_scalar",
            type=check_positive,
            default=100,
            help="scalar",
        )
        parser.add_argument(
            "-d",
            "--drift",
            action="store",
            dest="n_drift",
            type=check_positive,
            default=1,
            help="drift",
            choices=range(1, 100),
            metavar="N_DRIFT",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            momentum_view.display_rsi(
                symbol=self.coin,
                data=self.stock["Adj Close"],
                window=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                drift=ns_parser.n_drift,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_stoch(self, other_args: List[str]):
        """Process stoch command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stoch",
            description="""
                The Stochastic Oscillator measures where the close is in relation
                to the recent trading range. The values range from zero to 100. %D values over 75
                indicate an overbought condition; values under 25 indicate an oversold condition.
                When the Fast %D crosses above the Slow %D, it is a buy signal; when it crosses
                below, it is a sell signal. The Raw %K is generally considered too erratic to use
                for crossover signals.
            """,
        )
        parser.add_argument(
            "-k",
            "--fastkperiod",
            action="store",
            dest="n_fastkperiod",
            type=check_positive,
            default=14,
            help="The time period of the fastk moving average",
            choices=range(1, 100),
            metavar="N_FASTKPERIOD",
        )
        parser.add_argument(
            "-d",
            "--slowdperiod",
            action="store",
            dest="n_slowdperiod",
            type=check_positive,
            default=3,
            help="The time period of the slowd moving average",
            choices=range(1, 100),
            metavar="N_SLOWDPERIOD",
        )
        parser.add_argument(
            "--slowkperiod",
            action="store",
            dest="n_slowkperiod",
            type=check_positive,
            default=3,
            help="The time period of the slowk moving average",
            choices=range(1, 100),
            metavar="N_SLOWKPERIOD",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            momentum_view.display_stoch(
                symbol=self.coin,
                data=self.stock,
                fastkperiod=ns_parser.n_fastkperiod,
                slowdperiod=ns_parser.n_slowdperiod,
                slowkperiod=ns_parser.n_slowkperiod,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_fisher(self, other_args: List[str]):
        """Process fisher command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fisher",
            description="""
                The Fisher Transform is a technical indicator created by John F. Ehlers
                that converts prices into a Gaussian normal distribution.1 The indicator
                highlights when prices have   moved to an extreme, based on recent prices.
                This may help in spotting turning points in the price of an asset. It also
                helps show the trend and isolate the price waves within a trend.
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            momentum_view.display_fisher(
                symbol=self.coin,
                data=self.stock,
                window=ns_parser.n_length,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_cg(self, other_args: List[str]):
        """Process cg command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cg",
            description="""
                The Center of Gravity indicator, in short, is used to anticipate future price movements
                and to trade on price reversals as soon as they happen. However, just like other oscillators,
                the COG indicator returns the best results in range-bound markets and should be avoided when
                the price is trending. Traders who use it will be able to closely speculate the upcoming
                price change of the asset.
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            momentum_view.display_cg(
                symbol=self.coin,
                data=self.stock["Adj Close"],
                window=ns_parser.n_length,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_adx(self, other_args: List[str]):
        """Process adx command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="adx",
            description="""
            The ADX is a Welles Wilder style moving average of the Directional Movement Index (DX).
            The values range from 0 to 100, but rarely get above 60. To interpret the ADX, consider
            a high number to be a strong trend, and a low number, a weak trend.
        """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )
        parser.add_argument(
            "-s",
            "--scalar",
            action="store",
            dest="n_scalar",
            type=check_positive,
            default=100,
            help="scalar",
        )
        parser.add_argument(
            "-d",
            "--drift",
            action="store",
            dest="n_drift",
            type=check_positive,
            default=1,
            help="drift",
            choices=range(1, 100),
            metavar="N_DRIFT",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            trend_indicators_view.display_adx(
                symbol=self.coin,
                data=self.stock,
                window=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                drift=ns_parser.n_drift,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_aroon(self, other_args: List[str]):
        """Process aroon command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="aroon",
            description="""
                The word aroon is Sanskrit for "dawn's early light." The Aroon
                indicator attempts to show when a new trend is dawning. The indicator consists
                of two lines (Up and Down) that measure how long it has been since the highest
                high/lowest low has occurred within an n period range. \n \n When the Aroon Up is
                staying between 70 and 100 then it indicates an upward trend. When the Aroon Down
                is staying between 70 and 100 then it indicates an downward trend. A strong upward
                trend is indicated when the Aroon Up is above 70 while the Aroon Down is below 30.
                Likewise, a strong downward trend is indicated when the Aroon Down is above 70 while
                the Aroon Up is below 30. Also look for crossovers. When the Aroon Down crosses above
                the Aroon Up, it indicates a weakening of the upward trend (and vice versa).
            """,
        )

        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=25,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )
        parser.add_argument(
            "-s",
            "--scalar",
            action="store",
            dest="n_scalar",
            type=check_positive,
            default=100,
            help="scalar",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            trend_indicators_view.display_aroon(
                symbol=self.coin,
                data=self.stock,
                window=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_bbands(self, other_args: List[str]):
        """Process bbands command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bbands",
            description="""
                Bollinger Bands consist of three lines. The middle band is a simple
                moving average (generally 20 periods) of the typical price (TP). The upper and lower
                bands are F standard deviations (generally 2) above and below the middle band.
                The bands widen and narrow when the volatility of the price is higher or lower,
                respectively. \n \nBollinger Bands do not, in themselves, generate buy or sell signals;
                they are an indicator of overbought or oversold conditions. When the price is near the
                upper or lower band it indicates that a reversal may be imminent. The middle band
                becomes a support or resistance level. The upper and lower bands can also be
                interpreted as price targets. When the price bounces off of the lower band and crosses
                the middle band, then the upper band becomes the price target.
            """,
        )

        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=15,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )
        parser.add_argument(
            "-s",
            "--std",
            action="store",
            dest="n_std",
            type=check_positive_float,
            default=2,
            help="std",
            choices=np.arange(0.0, 10, 0.25).tolist(),
            metavar="N_STD",
        )
        parser.add_argument(
            "-m",
            "--mamode",
            action="store",
            dest="s_mamode",
            default="sma",
            choices=volatility_model.MAMODES,
            help="mamode",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            volatility_view.display_bbands(
                symbol=self.coin,
                data=self.stock,
                window=ns_parser.n_length,
                n_std=ns_parser.n_std,
                mamode=ns_parser.s_mamode,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_donchian(self, other_args: List[str]):
        """Process donchian command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="donchian",
            description="""
                Donchian Channels are three lines generated by moving average
                calculations that comprise an indicator formed by upper and lower
                bands around a midrange or median band. The upper band marks the
                highest price of a security over N periods while the lower band
                marks the lowest price of a security over N periods. The area
                between the upper and lower bands represents the Donchian Channel.
                """,
        )
        parser.add_argument(
            "-u",
            "--length_upper",
            action="store",
            dest="n_length_upper",
            type=check_positive,
            default=20,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH_UPPER",
        )
        parser.add_argument(
            "-l",
            "--length_lower",
            action="store",
            dest="n_length_lower",
            type=check_positive,
            default=20,
            help="length",
            choices=range(1, 100),
            metavar="N_LENGTH_LOWER",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            volatility_view.display_donchian(
                symbol=self.coin,
                data=self.stock,
                upper_length=ns_parser.n_length_upper,
                lower_length=ns_parser.n_length_lower,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_kc(self, other_args: List[str]):
        """Process kc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="kc",
            description="""
                 Keltner Channels are volatility-based bands that are placed
                 on either side of an asset's price and can aid in determining
                 the direction of a trend.The Keltner channel uses the average
                 true range (ATR) or volatility, with breaks above or below the top
                 and bottom barriers signaling a continuation.
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=20,
            help="Window length",
            choices=range(1, 100),
            metavar="N_LENGTH",
        )
        parser.add_argument(
            "-s",
            "--scalar",
            action="store",
            dest="n_scalar",
            type=check_positive,
            default=2,
            help="scalar",
        )
        parser.add_argument(
            "-m",
            "--mamode",
            action="store",
            dest="s_mamode",
            default="ema",
            choices=volatility_model.MAMODES,
            help="mamode",
        )
        parser.add_argument(
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=check_non_negative,
            default=0,
            help="offset",
            choices=range(0, 100),
            metavar="N_OFFSET",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            volatility_view.view_kc(
                symbol=self.coin,
                data=self.stock,
                window=ns_parser.n_length,
                scalar=ns_parser.n_scalar,
                mamode=ns_parser.s_mamode,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ad(self, other_args: List[str]):
        """Process ad command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ad",
            description="""
                The Accumulation/Distribution Line is similar to the On Balance
                Volume (OBV), which sums the volume times +1/-1 based on whether the close is
                higher than the previous close. The Accumulation/Distribution indicator, however
                multiplies the volume by the close location value (CLV). The CLV is based on the
                movement of the issue within a single bar and can be +1, -1 or zero. \n \n
                The Accumulation/Distribution Line is interpreted by looking for a divergence in
                the direction of the indicator relative to price. If the Accumulation/Distribution
                Line is trending upward it indicates that the price may follow. Also, if the
                Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
                then it signals an impending flattening of the price.
            """,
        )
        parser.add_argument(
            "--open",
            action="store_true",
            default=False,
            dest="b_use_open",
            help="uses open value of stock",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            volume_view.display_ad(
                symbol=self.coin,
                data=self.stock,
                use_open=ns_parser.b_use_open,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_adosc(self, other_args: List[str]):
        """Process adosc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="adosc",
            description="""
                 Accumulation/Distribution Oscillator, also known as the Chaikin Oscillator
                 is essentially a momentum indicator, but of the Accumulation-Distribution line
                 rather than merely price. It looks at both the strength of price moves and the
                 underlying buying and selling pressure during a given time period. The oscillator
                 reading above zero indicates net buying pressure, while one below zero registers
                 net selling pressure. Divergence between the indicator and pure price moves are
                 the most common signals from the indicator, and often flag market turning points.
            """,
        )
        parser.add_argument(
            "--open",
            action="store_true",
            default=False,
            dest="b_use_open",
            help="uses open value of stock",
        )
        parser.add_argument(
            "--fast",
            action="store",
            dest="n_length_fast",
            type=check_positive,
            default=3,
            help="fast length",
            choices=range(1, 100),
            metavar="N_LENGTH_FAST",
        )
        parser.add_argument(
            "--slow",
            action="store",
            dest="n_length_slow",
            type=check_positive,
            default=10,
            help="slow length",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            volume_view.display_adosc(
                symbol=self.coin,
                data=self.stock,
                use_open=ns_parser.b_use_open,
                fast=ns_parser.n_length_fast,
                slow=ns_parser.n_length_slow,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_obv(self, other_args: List[str]):
        """Process obv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="obv",
            description="""
                The On Balance Volume (OBV) is a cumulative total of the up and
                down volume. When the close is higher than the previous close, the volume is added
                to the running total, and when the close is lower than the previous close, the volume
                is subtracted from the running total. \n \n To interpret the OBV, look for the OBV
                to move with the price or precede price moves. If the price moves before the OBV,
                then it is a non-confirmed move. A series of rising peaks, or falling troughs, in the
                OBV indicates a strong trend. If the OBV is flat, then the market is not trending.
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            volume_view.display_obv(
                symbol=self.coin,
                data=self.stock,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_fib(self, other_args: List[str]):
        """Process fib command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fib",
            description="Calculates the fibonacci retracement levels",
        )
        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            type=int,
            help="Days to look back for retracement",
            default=120,
            choices=range(1, 960),
            metavar="PERIOD",
        )
        parser.add_argument(
            "--start",
            dest="start",
            type=valid_date,
            help="Starting date to select",
            required="--end" in other_args,
        )
        parser.add_argument(
            "--end",
            dest="end",
            type=valid_date,
            help="Ending date to select",
            required="--start" in other_args,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            custom_indicators_view.fibonacci_retracement(
                symbol=self.coin,
                data=self.stock,
                limit=ns_parser.period,
                start_date=ns_parser.start,
                end_date=ns_parser.end,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_demark(self, other_args: List[str]):
        """Process demark command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="demark",
            description="Calculates the Demark sequential indicator.",
        )
        parser.add_argument(
            "-m",
            "--min",
            help="Minimum value of indicator to show (declutters plot).",
            dest="min_to_show",
            type=check_positive,
            default=5,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if not self.coin:
                no_ticker_message()
                return
            momentum_view.display_demark(
                self.stock,
                self.coin.upper(),
                min_to_show=ns_parser.min_to_show,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_atr(self, other_args: List[str]):
        """Process atr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="atr",
            description="""
                Averge True Range is used to measure volatility, especially volatility caused by
                gaps or limit moves.
            """,
        )
        parser.add_argument(
            "-l",
            "--length",
            action="store",
            dest="n_length",
            type=check_positive,
            default=14,
            help="Window length",
        )
        parser.add_argument(
            "-m",
            "--mamode",
            action="store",
            dest="s_mamode",
            default="ema",
            choices=volatility_model.MAMODES,
            help="mamode",
        )
        parser.add_argument(
            "-o",
            "--offset",
            action="store",
            dest="n_offset",
            type=int,
            default=0,
            help="offset",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            if not self.coin:
                no_ticker_message()
                return
            volatility_view.display_atr(
                data=self.stock,
                symbol=self.coin.upper(),
                window=ns_parser.n_length,
                mamode=ns_parser.s_mamode,
                offset=ns_parser.n_offset,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_cones(self, other_args: List[str]):
        """Process cones command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cones",
            description="""
            Calculates the realized volatility quantiles over rolling windows of time.
            The model for calculating volatility is selectable.
            """,
        )
        parser.add_argument(
            "-l",
            "--lower_q",
            action="store",
            dest="lower_q",
            type=float,
            default=0.25,
            help="The lower quantile value for calculations.",
        )
        parser.add_argument(
            "-u",
            "--upper_q",
            action="store",
            dest="upper_q",
            type=float,
            default=0.75,
            help="The upper quantile value for calculations.",
        )
        parser.add_argument(
            "-m",
            "--model",
            action="store",
            dest="model",
            default="STD",
            choices=volatility_model.VOLATILITY_MODELS,
            type=str,
            help="The model used to calculate realized volatility.",
        )
        parser.add_argument(
            "--is_crypto",
            dest="is_crypto",
            action="store_false",
            default=True,
            help="If True, volatility is calculated for 365 days instead of 252.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if not self.coin:
                no_ticker_message()
                return

            volatility_view.display_cones(
                data=self.stock,
                symbol=self.coin.upper(),
                lower_q=ns_parser.lower_q,
                upper_q=ns_parser.upper_q,
                model=ns_parser.model,
                is_crypto=ns_parser.is_crypto,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
