"""Backtesting Controller Module"""
__docformat__ = "numpy"

import argparse
import os
from typing import List, Union
from datetime import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session

# This code below aims to fix an issue with the fnn module, used by bt module
# which forces matplotlib backend to be 'agg' which doesn't allow to plot
# Save current matplotlib backend
default_backend = mpl.get_backend()
# pylint: disable=wrong-import-position
from gamestonk_terminal.backtesting import bt_view  # noqa: E402

# Restore backend matplotlib used
mpl.use(default_backend)


class BacktestingController:
    """Backtesting Class"""

    CHOICES = ["?", "cls", "help", "q", "quit", "ema", "ema_cross", "rsi"]

    def __init__(
        self,
        ticker: str,
        start: Union[datetime, str],
    ):
        self.ticker = ticker
        self.start = start
        self.bt_parser = argparse.ArgumentParser(add_help=False, prog="bt")
        self.bt_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/backtesting"
        )
        print("\nBacktesting:")
        print("   cls         clear screen")
        print("   ?/help      show this menu again")
        print("   q           quit this menu, and shows back to main menu")
        print("   quit        quit to abandon program")
        print("")
        print("   ema         buy when price exceeds EMA(l)")
        print("   ema_cross   buy when EMA(short) > EMA(long) ")
        print("   rsi         buy when RSI < low and sell when RSI > high")
        print("")

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

        (known_args, other_args) = self.bt_parser.parse_known_args(an_input.split())

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

    def call_ema(self, other_args: List[str]):
        """Call EMA strategy"""
        bt_view.simple_ema(self.ticker, self.start, other_args)

    def call_ema_cross(self, other_args: List[str]):
        """Call EMA Cross strategy"""
        bt_view.ema_cross(self.ticker, self.start, other_args)

    def call_rsi(self, other_args: List[str]):
        """Call RSI Strategy"""
        bt_view.rsi_strat(self.ticker, self.start, other_args)


def menu(ticker: str, start: Union[str, datetime]):
    """Backtesting Menu"""
    plt.close("all")
    bt_controller = BacktestingController(ticker, start)
    bt_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in bt_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (bt)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (bt)> ")

        try:
            plt.close("all")

            process_input = bt_controller.switch(an_input)
            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
