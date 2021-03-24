"""Options Controller Module."""
__docformat__ = "numpy"

import argparse
from typing import List
import matplotlib.pyplot as plt

import yfinance as yf
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
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
        self.expiry_date = self.raw_data_options.options[0]
        self.op_parser = argparse.ArgumentParser(add_help=False, prog="op")
        self.op_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def expiry_dates(self, other_args: List[str]):
        """Print all available expiry dates."""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="exp",
            description="""See expiry dates.""",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="n_date",
            action="store",
            type=int,
            default=-1,
            choices=range(len(self.raw_data_options.options)),
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
                for i, d in enumerate(self.raw_data_options.options):
                    print(f"   {(2-len(str(i)))*' '}{i}.  {d}")

            # It means an expiry date was correctly selected
            else:
                self.expiry_date = self.raw_data_options.options[ns_parser.n_date]
                print(f"\nSelected expiry date : {self.expiry_date}")

        except Exception as e:
            print(e)

        print("")
        return

    @staticmethod
    def print_help(expiry_date):
        """Print help."""
        print("\nOptions insight Mode:")
        print("   help          show this  menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print(f"Selected expiry date: {expiry_date}")
        print("")
        print("   exp           see/set expiry date")
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
        print("")

    def call_exp(self, other_args: List[str]):
        """Process exp command."""
        self.expiry_dates(self, other_args)


def menu(ticker: str):
    """Options info Menu."""

    op_controller = OptionsController(ticker)
    op_controller.call_help(None)

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
