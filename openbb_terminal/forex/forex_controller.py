"""Forex Controller."""
__docformat__ = "numpy"

import argparse
import logging
import os
from datetime import datetime, timedelta
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forex import av_view, forex_helper, fxempire_view
from openbb_terminal.forex.forex_helper import FOREX_SOURCES, SOURCES_INTERVALS
from openbb_terminal.helper_funcs import (
    parse_known_args_and_warn,
    valid_date,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console
from openbb_terminal.decorators import check_api_key

# pylint: disable=R1710,import-outside-toplevel

logger = logging.getLogger(__name__)


class ForexController(BaseController):
    """Forex Controller class."""

    CHOICES_COMMANDS = ["to", "from", "load", "quote", "candle", "resources", "fwd"]
    CHOICES_MENUS = ["ta", "qa", "oanda", "pred"]
    PATH = "/forex/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Construct Data."""
        super().__init__(queue)

        self.from_symbol = "USD"
        self.to_symbol = ""
        self.source = "yf"
        self.data = pd.DataFrame()

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["to"] = {c: None for c in forex_helper.YF_CURRENCY_LIST}
            choices["from"] = {c: None for c in forex_helper.YF_CURRENCY_LIST}
            choices["load"]["--source"] = {c: None for c in FOREX_SOURCES}

            choices["support"] = self.SUPPORT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        has_symbols_start = "" if self.from_symbol and self.to_symbol else "[dim]"
        has_symbols_end = "" if self.from_symbol and self.to_symbol else "[/dim]"
        help_text = f"""[cmds]
    from             select the "from" currency in a forex pair
    to               select the "to" currency in a forex pair[/cmds]

[param]From:   [/param]{None or self.from_symbol}
[param]To:     [/param]{None or self.to_symbol}
[param]Source: [/param]{None or FOREX_SOURCES[self.source]}[cmds]{has_symbols_start}
[cmds]
    quote            get last quote [src][AlphaVantage][/src]
    load             get historical data
    candle           show candle plot for loaded pair
    fwd              get forward rates for loaded pair [src][FXEmpire][/src][/cmds]
[menu]
>   ta               technical analysis,                   e.g.: ema, macd, rsi, adx, bbands, obv
>   qa               quantitative analysis,                e.g.: decompose, cusum, residuals analysis
>   pred             prediction techniques                 e.g.: regression, arima, rnn, lstm, conv1d, monte carlo
[/menu]{has_symbols_end}
[info]Forex brokerages:[/info][menu]
>   oanda            Oanda menu[/menu][/cmds]
 """
        console.print(text=help_text, menu="Forex")

    def custom_reset(self):
        """Class specific component of reset command"""
        set_from_symbol = f"from {self.from_symbol}" if self.from_symbol else ""
        set_to_symbol = f"to {self.to_symbol}" if self.to_symbol else ""
        if set_from_symbol and set_to_symbol:
            return ["forex", set_from_symbol, set_to_symbol]
        return []

    @log_start_end(log=logger)
    def call_to(self, other_args: List[str]):
        """Process 'to' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="to",
            description='Select the "to" currency symbol in a forex pair',
        )
        parser.add_argument(
            "-n",
            "--name",
            help="To currency",
            type=forex_helper.check_valid_yf_forex_currency,
            dest="to_symbol",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.to_symbol = ns_parser.to_symbol

            console.print(
                f"\nSelected pair\nFrom:   {self.from_symbol}\n"
                f"To:     {self.to_symbol}\n"
                f"Source: {FOREX_SOURCES[self.source]}\n\n"
            )

    @log_start_end(log=logger)
    def call_from(self, other_args: List[str]):
        """Process 'from' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="to",
            description='Select the "from" currency symbol in a forex pair',
        )
        parser.add_argument(
            "-n",
            "--name",
            help="From currency",
            type=forex_helper.check_valid_yf_forex_currency,
            dest="from_symbol",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.from_symbol = ns_parser.from_symbol
            console.print(
                f"\nSelected pair\nFrom:   {self.from_symbol}\n"
                f"To:     {self.to_symbol}\n"
                f"Source: {FOREX_SOURCES[self.source]}\n\n"
            )

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
            "--source",
            help="Source of historical data",
            dest="source",
            choices=("yf", "av"),
            default="yf",
            required=False,
        )

        parser.add_argument(
            "-r",
            "--resolution",
            choices=["i", "d", "w", "m"],
            default="d",
            help="Resolution of data.  Can be intraday, daily, weekly or monthly",
            dest="resolution",
        )
        parser.add_argument(
            "-i",
            "--interval",
            choices=SOURCES_INTERVALS["yf"],
            default="5min",
            help="""Interval of intraday data. Options:
            [YahooFinance] 1min, 2min, 5min, 15min, 30min, 60min, 90min, 1hour, 1day, 5day, 1week, 1month, 3month.
            [AlphaAdvantage] 1min, 5min, 15min, 30min, 60min""",
            dest="interval",
        )
        parser.add_argument(
            "-s",
            "--start_date",
            default=(datetime.now() - timedelta(days=59)),
            type=valid_date,
            help="Start date of data.",
            dest="start_date",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:

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
                        "\n[red]"
                        + "No historical data loaded.\n"
                        + f"Make sure you have appropriate access for the '{ns_parser.source}' data source "
                        + f"and that '{ns_parser.source}' supports the requested range."
                        + "[/red]\n"
                    )
                else:
                    self.data.index.name = "date"

                self.source = ns_parser.source

                console.print(
                    f"\nSelected pair\nFrom:   {self.from_symbol}\n"
                    f"To:     {self.to_symbol}\n"
                    f"Source: {FOREX_SOURCES[self.source]}\n\n"
                )
            else:
                logger.error(
                    "Make sure both a to symbol and a from symbol are supplied."
                )
                console.print(
                    "\n[red]Make sure both a to symbol and a from symbol are supplied.[/red]\n"
                )

    @log_start_end(log=logger)
    def call_candle(self, other_args: List[str]):
        """Process quote command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Show candle for loaded fx data",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.data.empty:
                forex_helper.display_candle(self.data, self.to_symbol, self.from_symbol)
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.to_symbol and self.from_symbol:
                av_view.display_quote(self.to_symbol, self.from_symbol)
            else:
                logger.error(
                    "Make sure both a 'to' symbol and a 'from' symbol are selected."
                )
                console.print(
                    "[red]Make sure both a 'to' symbol and a 'from' symbol are selected.[/red]\n"
                )

    @log_start_end(log=logger)
    def call_fwd(self, other_args: List[str]):
        """Process fwd command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fwd",
            description="Get forward rates for loaded pair.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.to_symbol and self.from_symbol:
                fxempire_view.display_forward_rates(
                    self.to_symbol, self.from_symbol, ns_parser.export
                )
            else:
                logger.error(
                    "Make sure both a 'to' symbol and a 'from' symbol are selected."
                )
                console.print(
                    "[red]Make sure both a 'to' symbol and a 'from' symbol are selected.[/red]\n"
                )

    # MENUS
    @log_start_end(log=logger)
    @check_api_key(["OANDA_ACCOUNT_TYPE", "OANDA_ACCOUNT", "OANDA_TOKEN"])
    def call_oanda(self, _):
        """Enter Oanda menu."""
        from openbb_terminal.forex.oanda.oanda_controller import OandaController

        # if self.to_symbol and self.from_symbol:

        self.queue = self.load_class(
            OandaController,
            queue=self.queue,
        )
        # else:
        #     console.print("No currency pair data is loaded. Use 'load' to load data.\n")

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
    def call_pred(self, _):
        """Process pred command"""
        if obbff.ENABLE_PREDICT:
            if self.from_symbol and self.to_symbol:
                if self.data.empty:
                    console.print(
                        "No currency pair data is loaded. Use 'load' to load data.\n"
                    )
                else:
                    try:
                        from openbb_terminal.forex.prediction_techniques import (
                            pred_controller,
                        )

                        self.queue = self.load_class(
                            pred_controller.PredictionTechniquesController,
                            self.from_symbol,
                            self.to_symbol,
                            self.data.index[0],
                            "1440min",
                            self.data,
                            self.queue,
                        )
                    except ImportError:
                        logger.exception("Tensorflow not available")
                        console.print(
                            "[red]Run pip install tensorflow to continue[/red]\n"
                        )
            else:
                console.print("No pair selected.\n")
        else:
            console.print(
                "Predict is disabled. Check ENABLE_PREDICT flag on feature_flags.py",
                "\n",
            )

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

    # HELP WANTED!
    # TODO: Add news and reddit commands back
    # behavioural analysis and exploratory data analysis would be useful in the
    # forex menu. The examples of integration of the common ba and eda components
    # into the stocks context can provide an insight on how this can be done.
    # The earlier implementation did not work and was deleted in commit
    # d0e51033f7d5d4da6386b9e0b787892979924dce
