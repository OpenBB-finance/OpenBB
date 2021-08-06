"""Options Controller Module."""
__docformat__ = "numpy"

import argparse
import os
from typing import List
import matplotlib.pyplot as plt

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.options import (
    barchart_view,
    syncretism_view,
    calculator_model,
    op_helpers,
    yfinance_view,
    yfinance_model,
    tradier_view,
    tradier_model,
    fdscanner_view,
)

from gamestonk_terminal.config_terminal import TRADIER_TOKEN
from gamestonk_terminal.menu import session


class OptionsController:
    """Options Controller class."""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "disp",
        "scr",
        "calc",
        "yf",
        "tr",
        "info",
        "load",
        "exp",
        "vol",
        "voi",
        "oi",
        "hist",
        "chains",
        "grhist",
        "unu",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Construct data."""
        self.ticker = ""
        self.expiry_dates = []
        self.selected_date = ""

        self.op_parser = argparse.ArgumentParser(add_help=False, prog="options")
        self.op_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def print_help(self):
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
        print("   unu           show unusual options activity")
        print("")
        print(f"Current Ticker: {self.ticker or None}")
        print("   load          load new ticker")
        print("   info          display option information (volatility, IV rank etc)")
        print("")
        print("   calc          basic call/put PnL calculator")
        print("")
        print(f"Current Expiration: {self.selected_date or None}")
        print("   exp           see and set expiration dates")
        print("")
        if self.selected_date and self.ticker:
            print("   chains        display option chains with greeks [Tradier]]")
            print("   oi            plot open interest [Tradier/YF]")
            print("   vol           plot volume [Tradier/YF]")
            print("   voi           plot volume and open interest [Tradier/YF]")
            print("   hist          plot option history [Tradier")
            print("   grhist        plot option greek history [Syncretism]")
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
        """Process Help command."""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_calc(self, other_args: List[str]):
        """Process calc command"""
        calculator_model.pnl_calculator(other_args)

    def call_unu(self, other_args: List[str]):
        """Process act command"""

        parser = argparse.ArgumentParser(
            prog="unu",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="This command gets unusual options from fdscanner.com",
        )
        parser.add_argument(
            "-n",
            "--num",
            dest="num",
            type=int,
            default=20,
            help="Number of options to show.  Each scraped page gives 20 results.",
        )

        parser.add_argument(
            "--sortby",
            dest="sortby",
            default="Vol/OI",
            choices=["Option", "Vol/OI", "Vol", "OI", "Bid", "Ask"],
            help="Column to sort by.  Vol/OI is the default and typical variable to be considered unusual.",
        )
        parser.add_argument(
            "-a",
            "--ascending",
            dest="ascend",
            default=False,
            action="store_true",
            help="Flag to sort in ascending order",
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            fdscanner_view.display_options(
                num=ns_parser.num,
                sort_column=ns_parser.sortby,
                export=ns_parser.export,
                ascending=ns_parser.ascend,
            )

        except Exception as e:
            print(e, "\n")

    def call_info(self, other_args: List[str]):
        """Process info command"""
        barchart_view.print_options_data(self.ticker, other_args)

    def call_disp(self, other_args: List[str]):
        """Process disp command"""
        syncretism_view.view_available_presets(other_args)

    def call_scr(self, other_args: List[str]):
        """Process scr command"""
        syncretism_view.screener_output(other_args)

    def call_load(self, other_args: List[str]):
        """Process load command"""
        self.ticker = op_helpers.load(other_args)
        if TRADIER_TOKEN == "REPLACE_ME":
            self.expiry_dates = yfinance_model.option_expirations(self.ticker)
        else:
            self.expiry_dates = tradier_model.option_expirations(self.ticker)

    def call_exp(self, other_args: List[str]):
        """Process exp command"""
        if self.ticker:
            self.selected_date = op_helpers.select_option_date(
                self.expiry_dates, other_args
            )
        else:
            print("Please select a ticker using load {ticker}", "\n")

    def call_hist(self, other_args: List[str]):
        if TRADIER_TOKEN != "REPLACE_ME":
            tradier_view.display_historical(self.ticker, self.selected_date, other_args)
        else:
            print("TRADIER TOKEN not supplied. \n")

    def call_chains(self, other_args: List[str]):
        """Process chains command"""
        if TRADIER_TOKEN != "REPLACE_ME":
            tradier_view.display_chains(self.ticker, self.selected_date, other_args)
        else:
            print("TRADIER TOKEN not supplied. \n")

    def call_vol(self, other_args: List[str]):
        """Process vol command"""
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required.\n")
            return
        parsed = op_helpers.vol(other_args)
        if not parsed:
            return
        if parsed.source == "tr" and TRADIER_TOKEN != "REPLACE_ME":
            options = tradier_model.get_option_chains(self.ticker, self.selected_date)
            tradier_view.plot_vol(options, self.ticker, self.selected_date, parsed)
        else:
            options = yfinance_model.get_option_chain(self.ticker, self.selected_date)
            yfinance_view.plot_vol(
                options.calls, options.puts, self.ticker, self.selected_date, parsed
            )

    def call_voi(self, other_args: List[str]):
        """Process voi command"""
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required.")
            return
        parsed = op_helpers.voi(other_args)
        if not parsed:
            return
        if parsed.source == "tr" and TRADIER_TOKEN != "REPLACE_ME":
            options = tradier_model.get_option_chains(self.ticker, self.selected_date)
            tradier_view.plot_volume_open_interest(
                self.ticker, self.selected_date, options, parsed
            )
        else:
            options = yfinance_model.get_option_chain(self.ticker, self.selected_date)
            yfinance_view.plot_volume_open_interest(
                self.ticker, self.selected_date, options.calls, options.puts, parsed
            )

    def call_oi(self, other_args: List[str]):
        """Process oi command"""
        if not self.ticker and not self.selected_date:
            print("Ticker and expiration required.")
            return
        parsed = op_helpers.oi(other_args)
        if not parsed:
            return
        if parsed.source == "tr" and TRADIER_TOKEN != "REPLACE_ME":
            options = tradier_model.get_option_chains(self.ticker, self.selected_date)
            tradier_view.plot_oi(options, self.ticker, self.selected_date, parsed)
        else:
            options = yfinance_model.get_option_chain(self.ticker, self.selected_date)
            yfinance_view.plot_oi(
                options.calls, options.puts, self.ticker, self.selected_date, parsed
            )

    def call_grhist(self, other_args: List[str]):
        """Process grhist command"""
        syncretism_view.historical_greeks(self.ticker, self.selected_date, other_args)


def menu():
    """Options Menu."""
    op_controller = OptionsController()
    op_controller.call_help(None)
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in op_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (options)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (options)> ")

        try:
            plt.close("all")

            process_input = op_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
