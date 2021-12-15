"""Forex Controller"""
__docformat__ = "numpy"

import argparse
import difflib
from datetime import timedelta, datetime
from typing import List, Union

import pandas as pd
from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.forex import av_view, av_model

from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    valid_date,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session

# pylint: disable=R1710,import-outside-toplevel


class ForexController:
    """Forex Controller class"""

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
        """Construct Data"""
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
        """Print help"""
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
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """

        # Empty command
        if not an_input:
            print("")
            return self.queue if len(self.queue) > 0 else []

        if "/" in an_input:
            actions = an_input.split("/")
            an_input = actions[0]
            for cmd in actions[1:][::-1]:
                self.queue.insert(0, cmd)

        (known_args, other_args) = self.fx_parser.parse_known_args(an_input.split())

        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue if len(self.queue) > 0 else []

    def call_cd(self, other_args):
        """Process cd command"""
        if other_args:
            args = other_args[0].split("/")
            if len(args) > 0:
                for m in args[::-1]:
                    if m:
                        self.queue.insert(0, m)
            else:
                self.queue.insert(0, args[0])

        self.queue.insert(0, "q")

        return self.queue if len(self.queue) > 0 else []

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()
        return self.queue if len(self.queue) > 0 else []

    def call_quit(self, _):
        """Process quit menu command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            return self.queue
        return ["q"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            self.queue.insert(0, "q")
            return self.queue
        return ["q", "q"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "forex")
            self.queue.insert(0, "r")
            self.queue.insert(0, "q")
            return self.queue
        return ["q", "r", "forex"]

    # COMMANDS
    @try_except
    def call_to(self, other_args: List[str]):
        """Process 'to' command"""
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
        if not ns_parser:
            return self.queue if len(self.queue) > 0 else []

        self.to_symbol = ns_parser.to_symbol

        print(f"\nSelected pair\nFrom: {self.from_symbol}\nTo:   {self.to_symbol}\n\n")
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_from(self, other_args: List[str]):
        """Process 'from' command"""
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
        if not ns_parser:
            return self.queue if len(self.queue) > 0 else []

        self.from_symbol = ns_parser.from_symbol

        print(f"\nSelected pair\nFrom: {self.from_symbol}\nTo:   {self.to_symbol}\n\n")
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_load(self, other_args: List[str]):
        """Process select command"""
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

        # For the case where a user uses: 'load BB'
        if other_args and "-t" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return self.queue if len(self.queue) > 0 else []

        if not self.to_symbol or not self.from_symbol:
            print("\nMake sure both a to symbol and a from symbol are supplied\n")
            return self.queue if len(self.queue) > 0 else []

        self.data = av_model.get_historical(
            to_symbol=self.to_symbol,
            from_symbol=self.from_symbol,
            resolution=ns_parser.resolution,
            interval=ns_parser.interval,
            start_date=ns_parser.start_date.strftime("%Y-%m-%d"),
        )
        print(f"Loaded historic data from {self.from_symbol} to {self.to_symbol}")
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_candle(self, other_args: List[str]):
        """Process quote command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Show candle for loaded fx data",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return self.queue if len(self.queue) > 0 else []
        if self.data.empty:
            print("No forex historical data loaded.  Load first using <load>.")
            return self.queue if len(self.queue) > 0 else []

        av_view.display_candle(self.data, self.to_symbol, self.from_symbol)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="Get current exchange rate quote",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return self.queue if len(self.queue) > 0 else []

        if not self.to_symbol or not self.from_symbol:
            print('Make sure both a "to" symbol and a "from" symbol are selected\n')
            return self.queue if len(self.queue) > 0 else []

        av_view.display_quote(self.to_symbol, self.from_symbol)
        return self.queue if len(self.queue) > 0 else []

    # MENUS
    def call_oanda(self, _):
        from gamestonk_terminal.forex.oanda import oanda_controller

        return oanda_controller.menu(self.queue)

    # TODO: Add news and reddit commands back
    # def call_eda(self, _):
    #    try:
    #        df = fx_view.get_candles_dataframe(account, self.instrument, None)
    #        df = df.rename(columns={"Close": "Adj Close"})
    #        instrument = self.instrument
    #        s_start = pd.to_datetime(df.index.values[0])
    #        s_interval = "1440min"
    #        eda_controller.menu(df, instrument, s_start, s_interval)
    #    except AttributeError:
    #        print("No data found, do you have your oanda API keys set?")

    # def call_ba(self, _):
    #    instrument = fx_view.format_instrument(self.instrument, " ")
    #    try:
    #        df = fx_view.get_candles_dataframe(account, self.instrument, None)
    #        s_start = pd.to_datetime(df.index.values[0])
    #        ba_controller.menu(instrument, s_start)
    #    except AttributeError:
    #        print("No data found, do you have your oanda API keys set?")


def menu(queue: List[str] = None):
    """Forex Menu"""
    fx_controller = ForexController(queue)
    HELP_ME = True

    while True:
        # There is a command in the queue
        if fx_controller.queue and len(fx_controller.queue) > 0:
            if fx_controller.queue[0] in ("q", ".."):
                if len(fx_controller.queue) > 1:
                    return fx_controller.queue[1:]
                return []

            an_input = fx_controller.queue[0]
            fx_controller.queue = fx_controller.queue[1:]
            if an_input and an_input in fx_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /forex/ $ {an_input}")

        else:
            if HELP_ME:
                fx_controller.print_help()
                HELP_ME = False

            if session and gtff.USE_PROMPT_TOOLKIT and fx_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /forex/ $ ",
                    completer=fx_controller.completer,
                    search_ignore_case=True,
                )

            else:
                an_input = input(f"{get_flair()} /forex/ $ ")

        try:
            fx_controller.queue = fx_controller.switch(an_input)

        except SystemExit:
            print(f"\nThe command '{an_input}' doesn't exist.", end="")
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                fx_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )

            if similar_cmd:
                if " " in an_input:
                    an_input = f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                else:
                    an_input = similar_cmd[0]
                print(f" Replacing by '{an_input}'.")
                fx_controller.queue.insert(0, an_input)
            print("\n")
