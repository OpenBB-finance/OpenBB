"""Forex Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd

from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.forex import av_view, forex_helper, fxempire_view
from openbb_terminal.forex.forex_helper import (
    FOREX_SOURCES,
    SOURCES_INTERVALS,
    parse_forex_symbol,
)
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    export_data,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console, get_ordered_list_sources
from openbb_terminal.stocks import stocks_helper

# pylint: disable=R1710,import-outside-toplevel

logger = logging.getLogger(__name__)


forex_data_path = os.path.join(
    os.path.dirname(__file__), os.path.join("data", "polygon_tickers.csv")
)
tickers = pd.read_csv(forex_data_path).iloc[:, 0].to_list()
FX_TICKERS = list(set(tickers + [t[-3:] + t[:3] for t in tickers if len(t) == 6]))


class ForexController(BaseController):
    """Forex Controller class."""

    CHOICES_COMMANDS = [
        "fwd",
        "candle",
        "load",
        "quote",
    ]
    CHOICES_MENUS = [
        "forecast",
        "qa",
        "oanda",
        "ta",
    ]
    RESOLUTION = ["i", "d", "w", "m"]

    PATH = "/forex/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct Data."""
        super().__init__(queue)

        self.fx_pair = ""
        self.from_symbol = ""
        self.to_symbol = ""
        self.source = get_ordered_list_sources(f"{self.PATH}load")[0]
        self.data = pd.DataFrame()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            choices["load"].update({c: {} for c in FX_TICKERS})

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("forex/", 80)
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_param("_ticker", self.fx_pair)
        mt.add_param("_source", FOREX_SOURCES[self.source])
        mt.add_raw("\n")
        mt.add_cmd("quote", self.fx_pair)
        mt.add_cmd("candle", self.fx_pair)
        mt.add_cmd("fwd", self.fx_pair)
        mt.add_raw("\n")
        mt.add_menu("ta", self.fx_pair)
        mt.add_menu("qa", self.fx_pair)
        mt.add_menu("forecast")
        mt.add_raw("\n")
        mt.add_info("forex")
        mt.add_menu("oanda")
        console.print(text=mt.menu_text, menu="Forex")

    def custom_reset(self):
        """Class specific component of reset command"""
        set_fx_pair = f"load {self.fx_pair}" if self.fx_pair else ""
        if set_fx_pair:
            return ["forex", set_fx_pair]
        return []

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process select command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load historical exchange rate data."
            "Available data sources are Alpha Advantage and YahooFinance"
            "By default main source used for analysis is YahooFinance (yf). To change it use --source av",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Currency pair to load.",
            type=parse_forex_symbol,
            metavar="TICKER",
            choices=FX_TICKERS,
        )
        parser.add_argument(
            "-r",
            "--resolution",
            choices=self.RESOLUTION,
            default="d",
            help="[Alphavantage only] Resolution of data. Can be intraday, daily, weekly or monthly",
            dest="resolution",
        )
        parser.add_argument(
            "-i",
            "--interval",
            choices=SOURCES_INTERVALS["YahooFinance"],
            default="1day",
            help="""Interval of intraday data. Options:
            [YahooFinance] 1min, 2min, 5min, 15min, 30min, 60min, 90min, 1hour, 1day, 5day, 1week, 1month, 3month.
            [AlphaVantage] 1min, 5min, 15min, 30min, 60min""",
            dest="interval",
        )
        parser.add_argument(
            "-s",
            "--start",
            default=(datetime.now() - timedelta(days=365)),
            type=valid_date,
            help="The starting date (format YYYY-MM-DD) of the forex pair",
            dest="start_date",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the forex pair",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.ticker not in FX_TICKERS:
                logger.error("Invalid forex pair")
                console.print(f"{ns_parser.ticker} not a valid forex pair.\n")
                return

            self.fx_pair = ns_parser.ticker
            self.from_symbol = ns_parser.ticker[:3]
            self.to_symbol = ns_parser.ticker[3:]

            if self.to_symbol and self.from_symbol:
                self.data = forex_helper.load(
                    to_symbol=self.to_symbol,
                    from_symbol=self.from_symbol,
                    resolution=ns_parser.resolution,
                    interval=ns_parser.interval,
                    start_date=ns_parser.start_date.strftime("%Y-%m-%d"),
                    end_date=ns_parser.end.strftime("%Y-%m-%d"),
                    source=ns_parser.source,
                )

                if self.data.empty:
                    console.print(
                        "\n[red]No historical data loaded.\n\n"
                        f"Make sure you have appropriate access for the '{ns_parser.source}' data source "
                        f"and that '{ns_parser.source}' supports the requested range.[/red]"
                    )
                else:
                    self.data.index.name = "date"
                    console.print(f"{self.from_symbol}-{self.to_symbol} loaded.")

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    "load",
                    self.data.copy(),
                    " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None,
                )
                self.source = ns_parser.source
            else:
                console.print("\n[red]Make sure to load.[/red]\n")

    @log_start_end(log=logger)
    def call_candle(self, other_args: List[str]):
        """Process candle command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Show candle for loaded fx data",
        )
        parser.add_argument(
            "--sort",
            choices=forex_helper.CANDLE_SORT,
            default="",
            type=str.lower,
            dest="sort",
            help="Choose a column to sort by. Only works when raw data is displayed.",
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            dest="raw",
            default=False,
            help="Shows raw data instead of chart.",
        )
        parser.add_argument(
            "-t",
            "--trend",
            action="store_true",
            default=False,
            help="Flag to add high and low trends to candle",
            dest="trendlines",
        )
        parser.add_argument(
            "--ma",
            dest="mov_avg",
            type=str,
            help=(
                "Add moving average in number of days to plot and separate by a comma. "
                "Value for ma (moving average) keyword needs to be greater than 1."
            ),
            default=None,
        )
        parser.add_argument(
            "--log",
            help="Plot with y axis on log scale",
            action="store_true",
            default=False,
            dest="logy",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=20,
        )

        if ns_parser:
            if not self.to_symbol:
                console.print("No ticker loaded. First use 'load <ticker>'")
                return

            data = stocks_helper.process_candle(self.data)
            if ns_parser.raw:
                if (
                    ns_parser.trendlines
                    and (data.index[1] - data.index[0]).total_seconds() >= 86400
                ):
                    data = stocks_helper.find_trendline(data, "OC_High", "high")
                    data = stocks_helper.find_trendline(data, "OC_Low", "low")

                qa_view.display_raw(
                    data=data,
                    sortby=ns_parser.sort,
                    ascend=ns_parser.reverse,
                    limit=ns_parser.limit,
                )

            else:
                mov_avgs = []

                if ns_parser.mov_avg:
                    mov_list = (num for num in ns_parser.mov_avg.split(","))

                    for num in mov_list:
                        try:
                            num = int(num)

                            if num <= 1:
                                raise ValueError

                            mov_avgs.append(num)
                        except ValueError:
                            console.print(
                                f"[red]{num} is not a valid moving average, must be an integer greater than 1."
                            )

                forex_helper.display_candle(
                    to_symbol=self.to_symbol,
                    from_symbol=self.from_symbol,
                    data=data,
                    add_trend=ns_parser.trendlines,
                    ma=mov_avgs,
                    yscale="log" if ns_parser.logy else "linear",
                )

            export_data(
                ns_parser.export,
                os.path.dirname(os.path.abspath(__file__)),
                f"{self.fx_pair}",
                self.data,
                " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None,
            )

    @log_start_end(log=logger)
    def call_quote(self, other_args: List[str]):
        """Process quote command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="Get current exchange rate quote",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.source == "YahooFinance":
                if self.to_symbol and self.from_symbol:
                    self.data = forex_helper.load(
                        to_symbol=self.to_symbol,
                        from_symbol=self.from_symbol,
                        resolution="i",
                        interval="1min",
                        start_date=(datetime.now() - timedelta(days=5)).strftime(
                            "%Y-%m-%d"
                        ),
                        source="YahooFinance",
                    )
                    console.print(f"\nQuote for {self.from_symbol}/{self.to_symbol}\n")
                    console.print(
                        f"Last refreshed : {self.data.index[-1].strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    console.print(f"Last value     : {self.data['Adj Close'][-1]}\n")
                else:
                    logger.error("No forex pair loaded.")
                    console.print("[red]Make sure a forex pair is loaded.[/red]\n")

            elif ns_parser.source == "AlphaVantage":
                if self.to_symbol and self.from_symbol:
                    av_view.display_quote(self.to_symbol, self.from_symbol)
                else:
                    logger.error("No forex pair loaded.")
                    console.print("[red]Make sure a forex pair is loaded.[/red]\n")

    @log_start_end(log=logger)
    def call_fwd(self, other_args: List[str]):
        """Process fwd command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fwd",
            description="Get forward rates for loaded pair.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.fx_pair:
                fxempire_view.display_forward_rates(
                    self.to_symbol,
                    self.from_symbol,
                    ns_parser.export,
                    ns_parser.sheet_name,
                )
            else:
                logger.error("Make sure ba currency pair is loaded.")
                console.print("[red]Make sure a currency pair is loaded.[/red]\n")

    # MENUS
    @log_start_end(log=logger)
    @check_api_key(["OANDA_ACCOUNT_TYPE", "OANDA_ACCOUNT", "OANDA_TOKEN"])
    def call_oanda(self, _):
        """Enter Oanda menu."""
        from openbb_terminal.forex.oanda.oanda_controller import OandaController

        self.queue = self.load_class(OandaController, queue=self.queue)

    @log_start_end(log=logger)
    def call_ta(self, _):
        """Process ta command"""
        from openbb_terminal.forex.technical_analysis.ta_controller import (
            TechnicalAnalysisController,
        )

        # TODO: Play with this to get correct usage
        if self.to_symbol and self.from_symbol and not self.data.empty:
            self.queue = self.load_class(
                TechnicalAnalysisController,
                ticker=f"{self.from_symbol}/{self.to_symbol}",
                source=self.source,
                data=self.data,
                start=self.data.index[0],
                interval="",
                queue=self.queue,
            )

        else:
            console.print("No currency pair data is loaded. Use 'load' to load data.\n")

    @log_start_end(log=logger)
    def call_qa(self, _):
        """Process qa command"""
        if self.from_symbol and self.to_symbol:
            if self.data.empty:
                console.print(
                    "No currency pair data is loaded. Use 'load' to load data.\n"
                )
            else:
                from openbb_terminal.forex.quantitative_analysis import qa_controller

                self.queue = self.load_class(
                    qa_controller.QaController,
                    self.from_symbol,
                    self.to_symbol,
                    self.data,
                    self.queue,
                )
        else:
            console.print("No pair selected.\n")

    @log_start_end(log=logger)
    def call_forecast(self, _):
        """Process forecast command"""
        from openbb_terminal.forecast import forecast_controller

        self.queue = self.load_class(
            forecast_controller.ForecastController,
            self.fx_pair,
            self.data,
            self.queue,
        )
