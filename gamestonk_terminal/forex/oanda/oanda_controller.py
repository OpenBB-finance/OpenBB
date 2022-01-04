"""Oanda Controller."""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union

from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.forex import av_model
from gamestonk_terminal.forex.oanda import oanda_view

# from gamestonk_terminal.forex.exploratory_data_analysis import eda_controller
from gamestonk_terminal.helper_funcs import (
    get_flair,
    try_except,
    parse_known_args_and_warn,
    system_clear,
    check_non_negative_float,
)
from gamestonk_terminal.menu import session


account = cfg.OANDA_ACCOUNT


class OandaController:
    """Oanda menu controller."""

    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]

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
        # "news",
        # "reddit",
    ]
    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Construct Data."""
        self.fx_parser = argparse.ArgumentParser(add_help=False, prog="oanda")
        self.fx_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}

            # HELP WANTED!
            # TODO:
            # We currently use the Alpha Vantage currency list for autocompletion
            # This leads to messages like `USD_EUR is not a valid instrument.`
            # In Oanda they have their own list of available instruments. It would be
            # Great to fetch these lists and store them locally like it's done for
            # other currency codes (see ./av_forex_currencies.csv and how it's handled).
            choices["to"] = {c: None for c in av_model.CURRENCY_LIST}
            choices["from"] = {c: None for c in av_model.CURRENCY_LIST}

            self.completer = NestedCompleter.from_nested_dict(choices)

        self.from_symbol = ""
        self.to_symbol = ""

        self.instrument: Union[str, None] = None

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help."""
        dim_if_no_ticker = Style.DIM if not self.instrument else ""
        reset_style_if_no_ticker = Style.RESET_ALL if not self.instrument else ""

        help_text = f"""
    summary       shows account summary
    calendar      show calendar
    list          list order history
    pending       get information on pending orders
    cancel        cancel a pending order by ID -i order ID
    positions     get open positions
    trades        list open trades
    closetrade    close a trade by id

    Loaded instrument: {self.instrument if self.instrument else ""}

    from      select the "from" currency in a forex pair
    to        select the "to" currency in a forex pair
    {dim_if_no_ticker}
    candles       show candles
    price         shows price for selected instrument
    order         place limit order -u # of units -p price
    orderbook     print orderbook
    positionbook  print positionbook
    {reset_style_if_no_ticker}

    """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input.

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.fx_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command."""
        system_clear()

    def call_home(self, _):
        """Process home command."""
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command."""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command."""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command."""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command."""
        self.queue.insert(0, "oanda")
        self.queue.insert(0, "forex")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
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
            type=av_model.check_valid_forex_currency,
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
            self.to_symbol = ns_parser.to_symbol.upper()
            self.instrument = f"{self.from_symbol}_{self.to_symbol}"

            print(
                f"\nSelected pair\nFrom: {self.from_symbol}\nTo:   {self.to_symbol}\n\n"
            )

    @try_except
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
            type=av_model.check_valid_forex_currency,
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
            self.from_symbol = ns_parser.from_symbol.upper()
            self.instrument = f"{self.from_symbol}_{self.to_symbol}"

            print(
                f"\nSelected pair\nFrom: {self.from_symbol}\nTo:   {self.to_symbol}\n\n"
            )

    @try_except
    def call_price(self, other_args):
        """Process Price Command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="price",
            description="Get price for selected instrument.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_fx_price(account, self.instrument)

    @try_except
    def call_summary(self, other_args):
        """Process account summary command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="summary",
            description="Print some information about your account.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_account_summary(account)

    @try_except
    def call_orderbook(self, other_args):
        """Process Oanda Order Book."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="orderbook",
            description="Plot an orderbook for an instrument if Oanda provides one.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_order_book(account, self.instrument)

    @try_except
    def call_positionbook(self, other_args):
        """Process Oanda Position Book."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="positionbook",
            description="Plot a position book for an instrument if Oanda provides one.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_position_book(account, self.instrument)

    @try_except
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            order_state = ns_parser.state.upper()
            order_count = ns_parser.limit
            oanda_view.list_orders(account, order_state, order_count)

    @try_except
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            price = ns_parser.price
            units = ns_parser.units
            oanda_view.create_order(account, self.instrument, price, units)

    @try_except
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
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            orderID = ns_parser.orderID
            oanda_view.cancel_pending_order(account, orderID)

    @try_except
    def call_positions(self, other_args):
        """Get Open Positions."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="positions",
            description="Get information about open positions.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_open_positions(account)

    @try_except
    def call_pending(self, other_args):
        """See up to 25 pending orders."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pending",
            description="Get information about pending orders.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_pending_orders(account)

    @try_except
    def call_trades(self, other_args):
        """List open trades."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="trades",
            description="Get information about open trades.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            oanda_view.get_open_trades(account)

    @try_except
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
        if other_args:
            if "-i" not in other_args[0]:
                other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            orderID = ns_parser.orderID
            units = ns_parser.units
            oanda_view.close_trade(account, orderID, units)

    @try_except
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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

    @try_except
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            days = ns_parser.days
            oanda_view.calendar(self.instrument, days)


def menu(queue: List[str] = None):
    """Oanda Forex Menu."""
    oanda_controller = OandaController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if oanda_controller.queue and len(oanda_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if oanda_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(oanda_controller.queue) > 1:
                    return oanda_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = oanda_controller.queue[0]
            oanda_controller.queue = oanda_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in oanda_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /forex/oanda/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                oanda_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and oanda_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /forex/oanda/ $ ",
                        completer=oanda_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /forex/oanda/ $ ")

        try:
            # Process the input command
            oanda_controller.queue = oanda_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /forex/oanda menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                oanda_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        oanda_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                oanda_controller.queue.insert(0, an_input)
            else:
                print("\n")
