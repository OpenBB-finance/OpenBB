"""Options Controller Module."""
__docformat__ = "numpy"

import argparse
import os
from typing import List
import matplotlib.pyplot as plt
import pandas as pd

import yfinance as yf
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.options import (
    yahoo_view,
    tradier_view,
    barchart_view,
    syncretism_view,
)
from gamestonk_terminal.menu import session


class OptionsController:
    """Options Controller class."""

    # Command choices
    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "disp",
        "scr",
    ]

    CHOICES_TICKER_DEPENDENT = [
        "exp",
        "voi",
        "vcalls",
        "vputs",
        "chains",
        "info",
    ]

    def __init__(self, ticker: str, stock: pd.DataFrame):
        """Construct data."""
        if ticker:
            self.ticker = ticker
            self.yf_ticker_data = yf.Ticker(self.ticker)
            self.expiry_date = self.yf_ticker_data.options[0]
            self.options = self.yf_ticker_data.option_chain(self.expiry_date)
            self.last_adj_close_price = stock["Adj Close"].values[-1]

            self.op_parser = argparse.ArgumentParser(add_help=False, prog="op")
            self.op_parser.add_argument(
                "cmd",
                choices=self.CHOICES + self.CHOICES_TICKER_DEPENDENT,
            )
        else:
            self.expiry_date = ""
            self.op_parser = argparse.ArgumentParser(add_help=False, prog="op")
            self.op_parser.add_argument(
                "cmd",
                choices=self.CHOICES,
            )

    def expiry_dates(self, other_args: List[str]):
        """Print all available expiry dates."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="exp",
            description="""See/set expiry dates. [Source: Yahoo Finance]""",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="n_date",
            action="store",
            type=int,
            default=-1,
            choices=range(len(self.yf_ticker_data.options)),
            help=f"Expiry date index for {self.ticker}.",
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-d")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            # Print possible expiry dates
            if ns_parser.n_date == -1:
                print("\nAvailable expiry dates:")
                for i, d in enumerate(self.yf_ticker_data.options):
                    print(f"   {(2-len(str(i)))*' '}{i}.  {d}")

            # It means an expiry date was correctly selected
            else:
                self.expiry_date = self.yf_ticker_data.options[ns_parser.n_date]
                self.options = self.yf_ticker_data.option_chain(self.expiry_date)
                print(f"\nSelected expiry date : {self.expiry_date}")

        except Exception as e:
            print(e)

        print("")
        return

    @staticmethod
    def print_help(expiry_date):
        """Print help."""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/options"
        )
        print("\nOptions:")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   disp          display all preset screeners filters")
        print("   scr           output screener options")
        print("")
        if expiry_date:
            print(f"Selected expiry date: {expiry_date}")
            print("")
            print("   exp           see/set expiry date")
            print("   voi           volume + open interest options trading plot")
            print("   vcalls        calls volume + open interest plot")
            print("   vputs         puts volume + open interest plot")
            print("")
            print("   chains        display option chains")
            print(
                "   info          display option information (volatility, IV rank etc)"
            )
            print("")

    def switch(self, an_input: str):
        """Process and dispatch input.

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

        (known_args, other_args) = self.op_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help(self.expiry_date)
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command."""
        self.print_help(self.expiry_date)

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_exp(self, other_args: List[str]):
        """Process exp command."""
        self.expiry_dates(other_args)

    def call_voi(self, other_args: List[str]):
        """Process voi command."""
        yahoo_view.plot_volume_open_interest(
            other_args,
            self.ticker,
            self.expiry_date,
            self.last_adj_close_price,
            self.options.calls,
            self.options.puts,
        )

    def call_vcalls(self, other_args: List[str]):
        """Process vcalls command."""
        yahoo_view.plot_calls_volume_open_interest(
            other_args,
            self.ticker,
            self.expiry_date,
            self.last_adj_close_price,
            self.options.calls,
        )

    def call_vputs(self, other_args: List[str]):
        """Process vcalls command."""
        yahoo_view.plot_puts_volume_open_interest(
            other_args,
            self.ticker,
            self.expiry_date,
            self.last_adj_close_price,
            self.options.puts,
        )

    def call_chains(self, other_args):
        tradier_view.display_chains(self.ticker, self.expiry_date, other_args)

    def call_info(self, other_args):
        barchart_view.print_options_data(self.ticker, other_args)

    def call_disp(self, other_args):
        syncretism_view.view_available_presets(other_args)

    def call_scr(self, other_args):
        syncretism_view.screener_output(other_args)


def menu(ticker: str, stock: pd.DataFrame):
    """Options Menu."""

    try:
        op_controller = OptionsController(ticker, stock)
        op_controller.call_help(None)
    except IndexError:
        print("No options found for " + ticker)
        print("")
        process_input = False
        return process_input

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in op_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (op)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (op)> ")

        try:
            plt.close("all")

            process_input = op_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
