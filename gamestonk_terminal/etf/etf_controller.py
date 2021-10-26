"""ETF Controller"""
__docformat__ = "numpy"

import argparse
import os
from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from thepassiveinvestor import create_ETF_report

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.etf import screener_view, stockanalysis_view, wsj_view
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    MENU_GO_BACK,
    MENU_QUIT,
    MENU_RESET,
)
from gamestonk_terminal.menu import session


class ETFController:
    """ETF Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "reset",
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
        "pir",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.etf_parser = argparse.ArgumentParser(add_help=False, prog="etf")
        self.etf_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_str = """
>> ETF <<

What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program
    reset       reset terminal and reload configs

StockAnalysis.com:
    search        search ETFs matching name (i.e. BlackRock or Invesco)
    overview      get overview of ETF symbol
    holdings      get top holdings for ETF
    compare       compare overview of multiple ETF
    screener      screen etfs based on overview data

Wall St. Journal:
    gainers       show top gainers
    decliners     show top decliners
    active        show most active

The Passive Investor:
    pir           create ETF report of multiple tickers
"""
        print(help_str)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        MENU_GO_BACK, MENU_QUIT, MENU_RESET
            MENU_GO_BACK - Show main context menu again
            MENU_QUIT - Quit terminal
            MENU_RESET - Reset terminal and go back to same previous menu
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
        return MENU_GO_BACK

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return MENU_QUIT

    def call_reset(self, _):
        """Process Reset command - reset the program"""
        return MENU_RESET

    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Search all available etfs for matching input",
        )
        parser.add_argument(
            "-e",
            "--etf",
            type=str,
            dest="search_str",
            nargs="+",
            help="String to search for",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-e")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            search_string = " ".join(ns_parser.search_str)
            stockanalysis_view.view_search(
                to_match=search_string, export=ns_parser.export
            )

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
            "-e",
            "--etf",
            type=str,
            dest="name",
            help="Symbol to look for",
            required="-h" not in other_args,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-e")

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            stockanalysis_view.view_overview(
                symbol=ns_parser.name, export=ns_parser.export
            )

        except Exception as e:
            print(e, "\n")

    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="holdings",
            description="Look at ETF holdings",
        )
        parser.add_argument(
            "-e",
            "--etf",
            type=str,
            dest="name",
            help="ETF to get holdings for",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            dest="limit",
            help="Number of holdings to get",
            default=20,
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-e")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            stockanalysis_view.view_holdings(
                symbol=ns_parser.name,
                num_to_show=ns_parser.limit,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_compare(self, other_args):
        """Process compare command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="compare",
            description="Compare selected ETFs",
        )
        parser.add_argument(
            "-e",
            "--etfs",
            type=str,
            dest="names",
            help="Symbols to compare",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-e")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            etf_list = ns_parser.names.upper().split(",")
            stockanalysis_view.view_comparisons(etf_list, export=ns_parser.export)

        except Exception as e:
            print(e, "\n")

    def call_screener(self, other_args):
        """Process screener command"""
        # TODO: Change presets to use view/set like in stocks/options

        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="screener",
            add_help=False,
            description="Screens ETFS from a personal scraping github repository.  Data scraped from stockanalysis.com",
        )
        parser.add_argument(
            "-n",
            "--num",
            type=int,
            help="Number of etfs to show",
            dest="num",
            default=20,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        parser.add_argument(
            "--preset",
            choices=[
                file.strip(".ini")
                for file in os.listdir(
                    os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")
                )
            ],
            default="etf_config",
            help="Preset to use",
            dest="preset",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            screener_view.view_screener(
                num_to_show=ns_parser.num,
                preset=ns_parser.preset,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_gainers(self, other_args):
        """Process gainers command"""
        wsj_view.show_top_mover("gainers", other_args)

    def call_decliners(self, other_args):
        """Process decliners command"""
        wsj_view.show_top_mover("decliners", other_args)

    def call_active(self, other_args):
        """Process gainers command"""
        wsj_view.show_top_mover("active", other_args)

    def call_pir(self, other_args):
        """Process pir command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pir",
            description="Create a ETF Report of the selected ETFs",
        )
        parser.add_argument(
            "-e",
            "--etfs",
            type=str,
            dest="names",
            help="Symbols to create a report for",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "--filename",
            default=f"ETF_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            dest="filename",
            help="Filename of the ETF report",
        )
        parser.add_argument(
            "--folder",
            default=os.path.dirname(os.path.abspath(__file__)).replace(
                "gamestonk_terminal", "exports"
            ),
            dest="folder",
            help="Folder where the ETF report will be saved",
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-e")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            etf_list = ns_parser.names.upper().split(",")
            create_ETF_report(
                etf_list, filename=ns_parser.filename, folder=ns_parser.folder
            )
            print(
                f"Created ETF report as {ns_parser.filename} in folder {ns_parser.folder} \n"
            )

        except Exception as e:
            print(e, "\n")


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
