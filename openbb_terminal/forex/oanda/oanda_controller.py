"""Oanda Controller."""
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional, Union

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forex import av_model, forex_helper
from openbb_terminal.forex.forex_helper import FOREX_SOURCES
from openbb_terminal.forex.oanda import oanda_view
from openbb_terminal.helper_funcs import check_non_negative_float
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)

account = get_current_user().credentials.OANDA_ACCOUNT


class OandaController(BaseController):
    """Oanda menu controller."""

    CHOICES_COMMANDS = [
        "from",
        "to",
        "price",
        "summary",
        "list",
        "orderbook",
        "positionbook",
        "order",
        "cancel",
        "positions",
        "closetrade",
        "trades",
        "candles",
        "pending",
        "calendar",
    ]
    PATH = "/forex/oanda/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct Data."""
        super().__init__(queue)

        self.from_symbol = ""
        self.to_symbol = ""
        self.source = "Oanda"
        self.instrument: Union[str, None] = None

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            # TODO: We currently use the Alpha Vantage currency list for autocompletion
            # This leads to messages like `USD_EUR is not a valid instrument.`
            # In Oanda they have their own list of available instruments. It would be
            # Great to fetch these lists and store them locally like it's done for
            # other currency codes (see ./av_forex_currencies.csv and how it's handled).

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        mt = MenuText("forex/oanda/")
        mt.add_cmd("summary")
        mt.add_cmd("calendar")
        mt.add_cmd("list")
        mt.add_cmd("pending")
        mt.add_cmd("cancel")
        mt.add_cmd("positions")
        mt.add_cmd("trades")
        mt.add_cmd("closetrade")
        mt.add_raw("\n")
        mt.add_cmd("from")
        mt.add_cmd("to")
        mt.add_raw("\n")
        mt.add_param("_loaded", self.instrument or "")
        mt.add_param("_from", self.from_symbol)
        mt.add_param("_to", self.to_symbol)
        mt.add_param("_source", FOREX_SOURCES[self.source])
        mt.add_raw("\n")
        mt.add_cmd("candles", self.instrument)
        mt.add_cmd("price", self.instrument)
        mt.add_cmd("order", self.instrument)
        mt.add_cmd("orderbook", self.instrument)
        mt.add_cmd("positionbook", self.instrument)
        console.print(text=mt.menu_text, menu="Forex - Oanda")

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
            required="-h" not in other_args,
            type=av_model.check_valid_forex_currency,
            dest="to_symbol",
            choices=forex_helper.YF_CURRENCY_LIST,
            metavar="TO_SYMBOL",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.to_symbol = ns_parser.to_symbol.upper()
            self.instrument = f"{self.from_symbol}_{self.to_symbol}"

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
            prog="from",
            description='Select the "from" currency symbol in a forex pair',
        )
        parser.add_argument(
            "-n",
            "--name",
            help="From currency",
            required="-h" not in other_args,
            type=av_model.check_valid_forex_currency,
            dest="from_symbol",
            choices=forex_helper.YF_CURRENCY_LIST,
            metavar="FROM_SYMBOL",
        )

        if (
            other_args
            and "-n" not in other_args[0]
            and "--name" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-n")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.from_symbol = ns_parser.from_symbol.upper()
            self.instrument = f"{self.from_symbol}_{self.to_symbol}"

            console.print(
                f"\nSelected pair\nFrom:   {self.from_symbol}\n"
                f"To:     {self.to_symbol}\n"
                f"Source: {FOREX_SOURCES[self.source]}\n\n"
            )

    @log_start_end(log=logger)
    def call_price(self, other_args):
        """Process Price Command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="price",
            description="Get price for selected instrument.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_fx_price(account, self.instrument)

    @log_start_end(log=logger)
    def call_summary(self, other_args):
        """Process account summary command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="summary",
            description="Print some information about your account.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_account_summary(account)

    @log_start_end(log=logger)
    def call_orderbook(self, other_args):
        """Process Oanda Order Book."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="orderbook",
            description="Plot an orderbook for an instrument if Oanda provides one.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_order_book(account, self.instrument)

    @log_start_end(log=logger)
    def call_positionbook(self, other_args):
        """Process Oanda Position Book."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="positionbook",
            description="Plot a position book for an instrument if Oanda provides one.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_position_book(account, self.instrument)

    @log_start_end(log=logger)
    def call_list(self, other_args: List[str]):
        """Process list orders command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="list",
            description="List order history",
        )
        parser.add_argument(
            "-s",
            "--state",
            dest="state",
            action="store",
            default="ALL",
            type=str,
            required=False,
            help="List orders that have a specific state.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            action="store",
            default=20,
            type=int,
            required=False,
            help="Limit the number of orders to retrieve.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            order_state = ns_parser.state.upper()
            order_count = ns_parser.limit
            oanda_view.list_orders(account, order_state, order_count)

    @log_start_end(log=logger)
    def call_order(self, other_args: List[str]):
        """Place limit order."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="order",
            description="Create order",
        )
        parser.add_argument(
            "-u",
            "--unit",
            dest="units",
            action="store",
            type=int,
            required="-h" not in other_args,
            help="The number of units to place in the order request. Positive for "
            + "a long position and negative for a short position.",
        )
        parser.add_argument(
            "-p",
            "--price",
            dest="price",
            action="store",
            type=check_non_negative_float,
            required="-h" not in other_args,
            help="The price to set for the limit order.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            price = ns_parser.price
            units = ns_parser.units
            oanda_view.create_order(account, self.instrument, price, units)

    @log_start_end(log=logger)
    def call_cancel(self, other_args: List[str]):
        """Cancel pending order by ID."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="cancel",
            description="Cancel a Pending Order.",
        )
        parser.add_argument(
            "-i",
            "--id",
            dest="orderID",
            action="store",
            required="-h" not in other_args,
            type=str,
            help="The pending order ID to cancel.",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-i")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            orderID = ns_parser.orderID
            oanda_view.cancel_pending_order(account, orderID)

    @log_start_end(log=logger)
    def call_positions(self, other_args):
        """Get Open Positions."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="positions",
            description="Get information about open positions.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_open_positions(account)

    @log_start_end(log=logger)
    def call_pending(self, other_args):
        """See up to 25 pending orders."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pending",
            description="Get information about pending orders.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_pending_orders(account)

    @log_start_end(log=logger)
    def call_trades(self, other_args):
        """List open trades."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="trades",
            description="Get information about open trades.",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_open_trades(account)

    @log_start_end(log=logger)
    def call_closetrade(self, other_args: List[str]):
        """Close a trade by id."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="closetrade",
            description="Close a trade by id.",
        )
        parser.add_argument(
            "-i",
            "--id",
            dest="orderID",
            action="store",
            type=str,
            required=False,
            help="The Trade ID to close. ",
        )
        parser.add_argument(
            "-u",
            "--units",
            dest="units",
            action="store",
            required=False,
            help="The number of units on the trade to close. If not set it "
            + "defaults to all units. ",
        )
        if other_args and "-i" not in other_args[0] and "-h" not in other_args[0]:
            other_args.insert(0, "-i")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            orderID = ns_parser.orderID
            units = ns_parser.units
            oanda_view.close_trade(account, orderID, units)

    @log_start_end(log=logger)
    def call_candles(self, other_args: List[str]):
        """Plot candle chart for a loaded currency pair."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="candles",
            description="Display Candle Data",
        )
        parser.add_argument(
            "-g",
            "--granularity",
            dest="granularity",
            action="store",
            type=str,
            default="D",
            required=False,
            help="The timeframe to get for the candle chart (Seconds: S5, S10, S15, S30 "
            + "Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12 "
            + "Day (default): D, Week: W Month: M",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="candlecount",
            action="store",
            default=180,
            type=int,
            required=False,
            help="The number of candles to retrieve. Default:180 ",
        )
        parser.add_argument(
            "-a",
            "--ad",
            dest="ad",
            action="store_true",
            help="Adds ad (Accumulation/Distribution Indicator) to the chart",
        )
        parser.add_argument(
            "-b",
            "--bbands",
            dest="bbands",
            action="store_true",
            help="Adds Bollinger Bands to the chart",
        )
        parser.add_argument(
            "-c",
            "--cci",
            dest="cci",
            action="store_true",
            help="Adds cci (Commodity Channel Index) to the chart",
        )
        parser.add_argument(
            "-e",
            "--ema",
            dest="ema",
            action="store_true",
            help="Adds ema (Exponential Moving Average) to the chart",
        )
        parser.add_argument(
            "-o",
            "--obv",
            dest="obv",
            action="store_true",
            help="Adds obv (On Balance Volume) to the chart",
        )
        parser.add_argument(
            "-r",
            "--rsi",
            dest="rsi",
            action="store_true",
            help="Adds rsi (Relative Strength Index) to the chart",
        )
        parser.add_argument(
            "-s",
            "--sma",
            dest="sma",
            action="store_true",
            help="Adds sma (Simple Moving Average) to the chart",
        )
        parser.add_argument(
            "-v",
            "--vwap",
            dest="vwap",
            action="store_true",
            help="Adds vwap (Volume Weighted Average Price) to the chart",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.show_candles(
                self.instrument,
                granularity=ns_parser.granularity.upper(),
                candlecount=ns_parser.candlecount,
                additional_charts={
                    "ad": ns_parser.ad,
                    "bbands": ns_parser.bbands,
                    "cci": ns_parser.cci,
                    "ema": ns_parser.ema,
                    "obv": ns_parser.obv,
                    "rsi": ns_parser.rsi,
                    "sma": ns_parser.sma,
                    "vwap": ns_parser.vwap,
                },
            )

    @log_start_end(log=logger)
    def call_calendar(self, other_args: List[str]):
        """Call calendar."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="calendar",
            description="Show Calendar Data",
        )
        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            action="store",
            type=int,
            default=7,
            required=False,
            help="The number of days to search for, up to 30 forward or backward "
            + "use negative numbers to search back. ",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            days = ns_parser.days
            oanda_view.calendar(self.instrument, days)
