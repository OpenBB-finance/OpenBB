"""Forex Controller."""
__docformat__ = "numpy"

import argparse
from datetime import timedelta, datetime
from typing import List, Union

import pandas as pd
from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.decorators import try_except, menu_decorator
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.forex import av_view, av_model

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    valid_date,
    system_clear,
)
from gamestonk_terminal.menu import session

# pylint: disable=R1710,import-outside-toplevel,W0613


class ForexController:
    """Forex Controller class."""

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

    CHOICES_COMMANDS = ["to", "from", "load", "quote", "candle"]

    CHOICES_MENUS = ["oanda"]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(self, queue: List[str] = None):
        """Construct Data."""
        self.fx_parser = argparse.ArgumentParser(add_help=False, prog="forex")
        self.fx_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}

            choices["to"] = {c: None for c in av_model.CURRENCY_LIST}
            choices["from"] = {c: None for c in av_model.CURRENCY_LIST}

            self.completer = NestedCompleter.from_nested_dict(choices)

        self.from_symbol = "USD"
        self.to_symbol = ""
        self.data = pd.DataFrame()

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help."""
        dim_bool = self.from_symbol and self.to_symbol
        help_text = f"""
    from      select the "from" currency in a forex pair
    to        select the "to" currency in a forex pair

From: {None or self.from_symbol}
To:   {None or self.to_symbol}
{Style.DIM if not dim_bool else ""}
AlphaVantage:
    quote         get last quote
    load          get historical data
    candle        show candle plot for loaded data
{Style.RESET_ALL}
Forex brokerages:
>   oanda         Oanda menu
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

    def call_reset(self, _):
        """Process reset command."""
        self.queue.insert(0, "forex")
        self.queue.insert(0, "reset")
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
            self.to_symbol = ns_parser.to_symbol

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
            self.from_symbol = ns_parser.from_symbol
            print(
                f"\nSelected pair\nFrom: {self.from_symbol}\nTo:   {self.to_symbol}\n\n"
            )

    @try_except
    def call_load(self, other_args: List[str]):
        """Process select command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load historical exchange rate data.",
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
            choices=[1, 5, 15, 30, 60],
            default="5",
            help="Interval of intraday data.  Can be 1, 5, 15, 30 or 60.",
            dest="interval",
        )
        parser.add_argument(
            "-s",
            "--start_date",
            default=(datetime.now() - timedelta(days=366)),
            type=valid_date,
            help="Start date of data.",
            dest="start_date",
        )
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.to_symbol and self.from_symbol:
                self.data = av_model.get_historical(
                    to_symbol=self.to_symbol,
                    from_symbol=self.from_symbol,
                    resolution=ns_parser.resolution,
                    interval=ns_parser.interval,
                    start_date=ns_parser.start_date.strftime("%Y-%m-%d"),
                )
                print(
                    f"Loaded historic data from {self.from_symbol} to {self.to_symbol}"
                )
            else:
                print("\nMake sure both a to symbol and a from symbol are supplied\n")

    @try_except
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
                av_view.display_candle(self.data, self.to_symbol, self.from_symbol)
            else:
                print("No forex historical data loaded.  Load first using <load>.\n")

    @try_except
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
                print('Make sure both a "to" symbol and a "from" symbol are selected\n')

    # MENUS
    def call_oanda(self, _):
        """Enter Oanda menu."""
        from gamestonk_terminal.forex.oanda import oanda_controller

        self.queue = oanda_controller.menu(self.queue)

    # HELP WANTED!
    # TODO: Add news and reddit commands back
    # behavioural analysis and exploratory data analysis would be useful in the
    # forex menu. The examples of integration of the common ba and eda components
    # into the stocks context can provide an insight on how this can be done.
    # The earlier implementation did not work and was deleted in commit
    # d0e51033f7d5d4da6386b9e0b787892979924dce


@menu_decorator("/forex/", ForexController)
def menu(queue: List[str] = None):
    """Forex Menu."""
