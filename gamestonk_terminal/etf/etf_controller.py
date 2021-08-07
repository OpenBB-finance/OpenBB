"""ETF Controller"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal.menu import session
from gamestonk_terminal.etf import stockanalysis_view
from gamestonk_terminal.etf import stockanalysis_model
from gamestonk_terminal.etf.screener_model import etf_screener
from gamestonk_terminal.etf import wsj_view


class ETFController:
    """ETF Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "search",
        "overview",
        "compare",
        "holdings",
        "screener",
        "gainers",
        "decliners",
        "active",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.etf_parser = argparse.ArgumentParser(add_help=False, prog="etf")
        self.etf_parser.add_argument("cmd", choices=self.CHOICES)
        self.etf_symbols, self.etf_names = stockanalysis_model.get_all_names_symbols()

    def print_help(self):
        """Print help"""
        print(
            "https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/etf"
        )
        print("")
        print(">> ETF <<")
        print("")
        print("What do you want to do?")
        print("   cls           clear screen")
        print("   ?/help        show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("\nStockAnalysis.com")
        print("   search        search ETFs matching name (i.e. BlackRock or Invesco)")
        print("   overview      get overview of ETF symbol")
        print("   holdings      get top holdings for ETF")
        print("   compare       compare overview of multiple ETF")
        print("   screener      screen etfs based on overview data")
        print("\nWall St. Journal")
        print("   gainers       show top gainers")
        print("   decliners     show top decliners")
        print("   active        show most active")
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

        (known_args, other_args) = self.etf_parser.parse_known_args(an_input.split())

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

    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Search all available etfs for matching input",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            help="Name to search for",
            required=True,
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-n")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            matching_etfs = [
                self.etf_symbols[idx] + " - " + etf
                for idx, etf in enumerate(self.etf_names)
                if " ".join(other_args[1:]).lower() in etf.lower()
            ]

            print(*matching_etfs, sep="\n")
            if len(matching_etfs) == 0:
                print("No matches found")
            print("")

        except Exception as e:
            print(e, "\n")

    def call_overview(self, other_args: List[str]):
        """Process overview command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="Get overview data for selected etf",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            help="Symbol to look for",
            required="-h" not in other_args,
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-n")

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            if ns_parser.name.upper() not in self.etf_symbols:
                print("No matching ETFs found\n")
                return

            stockanalysis_view.view_overview(symbol=ns_parser.name)
        except Exception as e:
            print(e, "\n")

    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        etf_holdings(other_args)

    def call_compare(self, other_args):
        """Process compare command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="compare",
            description="Compare selected ETFs",
        )
        parser.add_argument(
            "-n",
            "--names",
            type=str,
            dest="names",
            help="Symbols to compare",
            required="-h" not in other_args,
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-n")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            etf_list = ns_parser.names.upper().split(",")
            for etf in etf_list:
                if etf not in self.etf_symbols:
                    print(f"{etf} not a known symbol. ")
                    etf_list.remove(etf)

            stockanalysis_view.view_comparisons(etf_list)

        except Exception as e:
            print(e, "\n")

    def call_screener(self, other_args):
        """Process screener command"""
        etf_screener(other_args)

    def call_gainers(self, other_args):
        """Process gainers command"""
        wsj_view.show_top_mover("gainers", other_args)

    def call_decliners(self, other_args):
        """Process decliners command"""
        wsj_view.show_top_mover("decliners", other_args)

    def call_active(self, other_args):
        """Process gainers command"""
        wsj_view.show_top_mover("active", other_args)


def menu():
    etf_controller = ETFController()
    etf_controller.print_help()
    plt.close("all")
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in etf_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (etf)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (etf)> ")

        try:
            process_input = etf_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
