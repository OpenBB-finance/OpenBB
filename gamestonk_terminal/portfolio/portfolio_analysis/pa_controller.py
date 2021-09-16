"""Portffolio Analysis Controller"""
__docformat__ = "numpy"

import argparse
import os
from pathlib import Path

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.portfolio_analysis import (
    portfolio_model,
    portfolio_view,
)

portfolios_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "portfolios")
possible_paths = [
    Path(port).stem for port in os.listdir(portfolios_path) if port.endswith(".csv")
]


class PortfolioController:
    """Portfolio Controller"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]
    CHOICES_COMMANDS = [
        "view",
        "load",
        "group",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        self.pa_parser = argparse.ArgumentParser(add_help=False, prog="pa")
        self.pa_parser.add_argument("cmd", choices=self.CHOICES)
        self.portfolio_name = ""
        self.portfolio = pd.DataFrame()

    def print_help(self):
        """Print help"""
        help_string = f"""https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/portfolio_analysis

>>PORTFOLIO ANALYSIS<<

What would you like to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

    view          view available portfolios
    load          load portfolio from csv file

Portfolio: {self.portfolio_name or None}

    group         view holdings grouped by parameter
            """
        print(help_string)

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

        (known_args, other_args) = self.pa_parser.parse_known_args(an_input.split())

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

    # TODO: allow loading other files than csv
    def call_load(self, other_args):
        """Process load command"""
        parser = argparse.ArgumentParser(
            prog="load",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Function to get portfolio from predefined csv file inside portfolios folder",
        )
        parser.add_argument(
            "-s",
            "--sector",
            action="store_true",
            default=False,
            help="Add sector to dataframe",
            dest="sector",
        )
        parser.add_argument(
            "--no_last_price",
            action="store_false",
            default=True,
            help="Don't add last price from yfinance",
            dest="last_price",
        )
        parser.add_argument(
            "--nan",
            action="store_true",
            default=False,
            help="Show nan entries from csv",
            dest="show_nan",
        )
        parser.add_argument(
            "-p",
            "--path",
            default="my_portfolio",
            choices=possible_paths,
            help="Path to csv file",
            dest="path",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            self.portfolio_name = ns_parser.path
            self.portfolio = portfolio_model.load_csv_portfolio(
                full_path=os.path.join(portfolios_path, ns_parser.path) + ".csv",
                sector=ns_parser.sector,
                last_price=ns_parser.last_price,
                show_nan=ns_parser.show_nan,
            )
            if not self.portfolio.empty:
                print(f"Successfully loaded: {self.portfolio_name}\n")

        except Exception as e:
            print(e)

    def call_group(self, other_args):
        """Process group command"""
        parser = argparse.ArgumentParser(
            prog="group",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Displays portfolio grouped by a given column",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-g")
        parser.add_argument(
            "-g",
            "--group",
            type=str,
            dest="group",
            default="Ticker",
            choices=self.portfolio.columns,
            help="Column to group by",
        )

        # The following arguments will be used in a later PR for customizable 'reports'

        # The --func flag will need to be tested that it exists for pandas groupby
        # parser.add_argument("-f",
        #                     "--func",
        #                     type=str,
        #                     dest="function",
        #                     help="Aggregate function to apply to groups"
        #                     )
        # parser.add_argument("-d",
        #                     "--display",
        #                     default = None,
        #                     help = "Columns to display",
        #                     dest="cols")

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if "value" not in self.portfolio.columns:
                print(
                    "'value' column not in portfolio.  Either add manually or load without --no_last_price flag\n"
                )
                return

            portfolio_view.display_group_holdings(
                portfolio=self.portfolio, group_column=ns_parser.group
            )

        except Exception as e:
            print(e, "\n")

    def call_view(self, other_args):
        parser = argparse.ArgumentParser(
            prog="view",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Show available portfolios to load.",
        )
        parser.add_argument(
            "-f",
            "-format",
            choices=["csv", "all"],
            help="Format of portfolios to view.  'csv' will show all csv files available, etc.",
            default="all",
            dest="file_format",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            available_ports = os.listdir(portfolios_path)
            if ns_parser.file_format != "all":
                available_ports = [
                    port
                    for port in available_ports
                    if port.endswith(ns_parser.file_format)
                ]

            print("\nAvailable Portfolios:\n")
            for port in available_ports:
                print(Path(port).stem)
            print("")

        except Exception as e:
            print(e, "\n")


def menu():
    """Portfolio Analysis Menu"""
    pa_controller = PortfolioController()
    pa_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in pa_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (portfolio)>(pa)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (portfolio)>(pa)> ")

        try:
            process_input = pa_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
