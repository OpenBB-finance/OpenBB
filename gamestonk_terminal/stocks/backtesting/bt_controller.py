"""Backtesting Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union

import matplotlib as mpl
import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    system_clear,
)
from gamestonk_terminal.menu import session

# This code below aims to fix an issue with the fnn module, used by bt module
# which forces matplotlib backend to be 'agg' which doesn't allow to plot
# Save current matplotlib backend
default_backend = mpl.get_backend()
# pylint: disable=wrong-import-position
from gamestonk_terminal.stocks.backtesting import bt_view  # noqa: E402

# Restore backend matplotlib used
mpl.use(default_backend)


class BacktestingController:
    """Backtesting Class"""

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
    CHOICES_COMMANDS = ["ema", "ema_cross", "rsi"]
    CHOICES += CHOICES_COMMANDS

    def __init__(self, ticker: str, stock: pd.DataFrame, queue: List[str] = None):
        self.ticker = ticker
        self.stock = stock
        self.bt_parser = argparse.ArgumentParser(add_help=False, prog="bt")
        self.bt_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.queue = queue if queue else list()

    def print_help(self):
        """Print help"""
        help_text = f"""
Backtesting:
Ticker: {self.ticker.upper()}

    ema         buy when price exceeds EMA(l)
    ema_cross   buy when EMA(short) > EMA(long)
    rsi         buy when RSI < low and sell when RSI > high
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

        (known_args, other_args) = self.bt_parser.parse_known_args(an_input.split())

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
        """Process cls command"""
        system_clear()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "bt")
        if self.ticker:
            self.queue.insert(0, f"load {self.ticker}")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_ema(self, other_args: List[str]):
        """Call EMA strategy"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ema",
            description="Strategy where stock is bought when Price > EMA(l)",
        )
        parser.add_argument(
            "-l",
            default=20,
            dest="length",
            type=check_positive,
            help="EMA period to consider",
        )
        parser.add_argument(
            "--spy",
            action="store_true",
            default=False,
            help="Flag to add spy hold comparison",
            dest="spy",
        )
        parser.add_argument(
            "--no_bench",
            action="store_true",
            default=False,
            help="Flag to not show buy and hold comparison",
            dest="no_bench",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:

            bt_view.display_simple_ema(
                ticker=self.ticker,
                df_stock=self.stock,
                ema_length=ns_parser.length,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                export=ns_parser.export,
            )

    @try_except
    def call_ema_cross(self, other_args: List[str]):
        """Call EMA Cross strategy"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ema_cross",
            description="Cross between a long and a short Exponential Moving Average.",
        )
        parser.add_argument(
            "-l",
            "--long",
            default=50,
            dest="long",
            type=check_positive,
            help="Long EMA period",
        )
        parser.add_argument(
            "-s",
            "--short",
            default=20,
            dest="short",
            type=check_positive,
            help="Short EMA period",
        )
        parser.add_argument(
            "--spy",
            action="store_true",
            default=False,
            help="Flag to add spy hold comparison",
            dest="spy",
        )
        parser.add_argument(
            "--no_bench",
            action="store_true",
            default=False,
            help="Flag to not show buy and hold comparison",
            dest="no_bench",
        )
        parser.add_argument(
            "--no_short",
            action="store_false",
            default=True,
            dest="shortable",
            help="Flag that disables the short sell",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:

            if ns_parser.long < ns_parser.short:
                print("Short EMA period is longer than Long EMA period\n")

            bt_view.display_ema_cross(
                ticker=self.ticker,
                df_stock=self.stock,
                short_ema=ns_parser.short,
                long_ema=ns_parser.long,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                shortable=ns_parser.shortable,
                export=ns_parser.export,
            )

    @try_except
    def call_rsi(self, other_args: List[str]):
        """Call RSI Strategy"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rsi",
            description="""Strategy that buys when the stock is less than a threshold
            and shorts when it exceeds a threshold.""",
        )
        parser.add_argument(
            "-p",
            "--periods",
            dest="periods",
            help="Number of periods for RSI calculation",
            type=check_positive,
            default=14,
        )
        parser.add_argument(
            "-u",
            "--high",
            default=70,
            dest="high",
            type=check_positive,
            help="High (upper) RSI Level",
        )
        parser.add_argument(
            "-l",
            "--low",
            default=30,
            dest="low",
            type=check_positive,
            help="Low RSI Level",
        )
        parser.add_argument(
            "--spy",
            action="store_true",
            default=False,
            help="Flag to add spy hold comparison",
            dest="spy",
        )
        parser.add_argument(
            "--no_bench",
            action="store_true",
            default=False,
            help="Flag to not show buy and hold comparison",
            dest="no_bench",
        )
        parser.add_argument(
            "--no_short",
            action="store_false",
            default=True,
            dest="shortable",
            help="Flag that disables the short sell",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.high < ns_parser.low:
                print("Low RSI value is higher than Low RSI value\n")

            bt_view.display_rsi_strategy(
                ticker=self.ticker,
                df_stock=self.stock,
                periods=ns_parser.periods,
                low_rsi=ns_parser.low,
                high_rsi=ns_parser.high,
                spy_bt=ns_parser.spy,
                no_bench=ns_parser.no_bench,
                shortable=ns_parser.shortable,
                export=ns_parser.export,
            )


def menu(ticker: str, stock: pd.DataFrame, queue: List[str] = None):
    """Backtesting Menu"""
    bt_controller = BacktestingController(ticker, stock, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if bt_controller.queue and len(bt_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if bt_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(bt_controller.queue) > 1:
                    return bt_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = bt_controller.queue[0]
            bt_controller.queue = bt_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in bt_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/bt/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                bt_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and bt_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/bt/ $ ",
                    completer=bt_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/bt/ $ ")

        try:
            # Process the input command
            bt_controller.queue = bt_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/bt menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                bt_controller.CHOICES,
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
                        bt_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                bt_controller.queue.insert(0, an_input)
            else:
                print("\n")
