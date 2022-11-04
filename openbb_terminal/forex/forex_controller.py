"""Forex Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List

import pandas as pd

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forex import forex_helper, fxempire_view, av_view
from openbb_terminal.forex.forex_helper import FOREX_SOURCES, SOURCES_INTERVALS
from openbb_terminal.helper_funcs import (
    valid_date,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    export_data,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import (
    console,
    MenuText,
    translate,
    get_ordered_list_sources,
)
from openbb_terminal.decorators import check_api_key
from openbb_terminal.forex.forex_helper import parse_forex_symbol

# pylint: disable=R1710,import-outside-toplevel

logger = logging.getLogger(__name__)


forex_data_path = os.path.join(
    os.path.dirname(__file__), os.path.join("data", "polygon_tickers.csv")
)
FX_TICKERS = pd.read_csv(forex_data_path).iloc[:, 0].to_list()


class ForexController(BaseController):
    """Forex Controller class."""

    CHOICES_COMMANDS = [
        "load",
        "quote",
        "candle",
        "resources",
        "fwd",
        "forecast",
        "oanda",
    ]
    CHOICES_MENUS = ["ta", "qa", "Oanda"]
    RESOLUTION = ["i", "d", "w", "m"]

    PATH = "/forex/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Construct Data."""
        super().__init__(queue)

        self.fx_pair = ""
        self.from_symbol = ""
        self.to_symbol = ""
        self.source = get_ordered_list_sources(f"{self.PATH}load")[0]
        self.data = pd.DataFrame()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: {} for c in FX_TICKERS}
            choices["load"]["--ticker"] = {c: {} for c in FX_TICKERS}
            choices["load"]["-t"] = "--ticker"
            choices["load"]["--resolution"] = {c: {} for c in self.RESOLUTION}
            choices["load"]["-r"] = "--resolution"
            choices["load"]["--interval"] = {
                c: {} for c in SOURCES_INTERVALS["YahooFinance"]
            }
            choices["load"]["--start"] = None
            choices["load"]["-s"] = "--start"
            choices["load"]["--source"] = {c: {} for c in FOREX_SOURCES}
            choices["quote"]["--source"] = {
                c: {} for c in get_ordered_list_sources(f"{self.PATH}quote")
            }
            choices["candle"]["--ma"] = None

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

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
            help="Start date of data.",
            dest="start_date",
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
                    source=ns_parser.source,
                )

                if self.data.empty:
                    console.print(
                        "\n[red]No historical data loaded.\n\n"
                        f"Make sure you have appropriate access for the '{ns_parser.source}' data source "
                        f"and that '{ns_parser.source}' supports the requested range.[/red]\n"
                    )
                else:
                    self.data.index.name = "date"

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    "load",
                    self.data.copy(),
                )

                self.source = ns_parser.source
                if self.source != "YahooFinance":
                    console.print(f"{self.from_symbol}-{self.to_symbol} loaded.\n")
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
            "--ma",
            dest="mov_avg",
            type=str,
            help=translate(
                "Add moving average in number of days to plot and separate by a comma. "
                "Value for ma (moving average) keyword needs to be greater than 1."
            ),
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            mov_avgs = []
            if not self.data.empty:
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
                    self.data, self.to_symbol, self.from_symbol, mov_avgs
                )
            else:
                logger.error(
                    "No forex historical data loaded.  Load first using <load>."
                )
                console.print(
                    "[red]No forex historical data loaded.  Load first using <load>.[/red]\n"
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
                    self.to_symbol, self.from_symbol, ns_parser.export
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
