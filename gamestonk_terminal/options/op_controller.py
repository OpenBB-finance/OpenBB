"""Options Controller Module."""
__docformat__ = "numpy"

import argparse
import matplotlib.pyplot as plt

import yfinance as yf
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.options import volume
from gamestonk_terminal.menu import session


class OptionsController:
    """Options Controller class."""

    # Command choices
    CHOICES = ["help", "q", "quit", "exp", "volume"]

    def __init__(
        self,
        ticker: str,
    ):
        """Construct data."""
        self.ticker = ticker
        self.raw_data_options = yf.Ticker(self.ticker)
        self.expiry_date = ""

        self.__set_exp_date()

        self.op_parser = argparse.ArgumentParser(add_help=False, prog="ca")
        self.op_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def __set_exp_date(self, date_index=0):
        self.expiry_date = self.raw_data_options.options[date_index]
        return

    @staticmethod
    def print_exp_dates(expiry_date, all_dates):
        """Print all available expiry dates."""
        print(f"current selected expiry date :[{expiry_date}]")
        print("\nAvailable dates:")
        for i, d in enumerate(all_dates):
            print(f"[{i}]   {d}")
        print(f"\nPlease select date: input a number between 0 and {len(all_dates)-1}")
        return

    @staticmethod
    def print_help(expiry_date):
        """Print help."""
        print("\nOptions insight Mode:")
        print("   help          show this  menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")

        print(
            f"   exp           set expiry date, current selected date : [{expiry_date}]"
        )
        print("   volume        plot options trading volume / open interest")
        print("")
        return

    def switch(self, an_input: str):
        """Process and dispatch input.

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """
        (known_args, other_args) = self.op_parser.parse_known_args(an_input.split())

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

    def call_volume(self, _):
        """Process volume command."""
        volume.volume_graph(
            self.raw_data_options,
            self.ticker,
            self.expiry_date,
            volume_percentile_threshold=60,
        )

    def call_exp(self, _):
        """Process exp command."""
        self.print_exp_dates(self.expiry_date, self.raw_data_options.options)

        date_index_choices = list(range(len(self.raw_data_options.options) - 1))
        while True:
            # Get input command from user
            if session and gtff.USE_PROMPT_TOOLKIT:
                completer = NestedCompleter.from_nested_dict(
                    {c: None for c in date_index_choices}
                )
                an_input = session.prompt(
                    f"{get_flair()} (exp)> ",
                    completer=completer,
                )
            else:
                an_input = input(f"{get_flair()} (exp)> ")

            try:
                plt.close("all")

                process_input = an_input

                if process_input is not None:
                    try:
                        self.__set_exp_date(int(an_input))
                        print(f"\nNew selected expiry date : [{self.expiry_date}]\n")
                        return
                        # menu(self.ticker, self)
                    except IndexError:
                        print(
                            f"\nSelection must be between [0 - {len(self.raw_data_options.options) - 1}]\n"
                        )

            except SystemExit:
                print("The command selected doesn't exist\n")
                continue


def menu(ticker: str, op_con=None):
    """Options info Menu."""
    if op_con is None:
        op_controller = OptionsController(ticker)
    else:
        op_controller = op_con
    op_controller.call_help("")

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
