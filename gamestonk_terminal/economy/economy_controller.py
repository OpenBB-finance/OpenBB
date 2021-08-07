""" Econ Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.economy import fred_view
from gamestonk_terminal.economy import finnhub_view
from gamestonk_terminal.economy import cnn_view
from gamestonk_terminal.economy import wsj_view
from gamestonk_terminal.economy.report import report_controller

# pylint: disable=R1710


class EconomyController:
    """Economy Controller"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "feargreed",
        "events",
        "custom",
        "disp",
        "overview",
        "indices",
        "futures",
        "usbonds",
        "glbonds",
        "futures",
        "currencies",
    ]

    CHOICES_SHORTCUTS = [
        "vixcls",
        "gdp",
        "unrate",
        "dgs1",
        "dgs5",
        "dgs10",
        "dgs30",
        "mortgage30us",
        "fedfunds",
        "aaa",
        "dexcaus",
    ]

    CHOICES_MENUS = [
        "report",
    ]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_SHORTCUTS
    CHOICES += CHOICES_MENUS

    def __init__(self):
        """Constructor"""
        self.econ_parser = argparse.ArgumentParser(add_help=False, prog="economy")
        self.econ_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/economy

>> ECONOMY <<

What do you want to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program
CNN:
    feargreed     CNN Fear and Greed Index
Finnhub:
    events        economic impact events
FRED:
    custom        customized FRED data from https://fred.stlouisfed.org
    disp          display FRED shortcuts commands
Wall St. Journal:
    overview      market data overview
    indices       us indices overview
    futures       futures overview
    usbonds       us bond overview
    glbonds       global bonds overview
    currencies    currency overview

>   report        generate automatic report
"""
        print(help_text)

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

        (known_args, other_args) = self.econ_parser.parse_known_args(an_input.split())

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

    def call_events(self, other_args: List[str]):
        """Process events command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="events",
            description="""
                Output economy impact calendar impact events. [Source: https://finnhub.io]
            """,
        )
        parser.add_argument(
            "-c",
            "--country",
            action="store",
            dest="country",
            type=str,
            default="US",
            choices=["NZ", "AU", "ERL", "CA", "EU", "US", "JP", "CN", "GB", "CH"],
            help="Country from where to get economy calendar impact events",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=10,
            help="Number economy calendar impact events to display",
        )
        parser.add_argument(
            "-i",
            "--impact",
            action="store",
            dest="impact",
            type=str,
            default="all",
            choices=["low", "medium", "high", "all"],
            help="Impact of the economy event",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-c")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finnhub_view.economy_calendar_events(
                country=ns_parser.country,
                num=ns_parser.num,
                impact=ns_parser.impact,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_custom(self, other_args: List[str]):
        """Process custom command"""
        fred_view.display_fred(other_args, "")

    def call_disp(self, _):
        """Process custom command"""
        fred_view.display_fred_shortcuts()

    def call_vixcls(self, other_args: List[str]):
        """Process vixcls command"""
        fred_view.display_fred(other_args, "VIXCLS")

    def call_gdp(self, other_args: List[str]):
        """Process gdp command"""
        fred_view.display_fred(other_args, "GDP")

    def call_unrate(self, other_args: List[str]):
        """Process unrate command"""
        fred_view.display_fred(other_args, "UNRATE")

    def call_dgs1(self, other_args: List[str]):
        """Process dgs1 command"""
        fred_view.display_fred(other_args, "DGS1")

    def call_dgs5(self, other_args: List[str]):
        """Process dgs5 command"""
        fred_view.display_fred(other_args, "DGS5")

    def call_dgs10(self, other_args: List[str]):
        """Process dgs10 command"""
        fred_view.display_fred(other_args, "DGS10")

    def call_dgs30(self, other_args: List[str]):
        """Process dgs30 command"""
        fred_view.display_fred(other_args, "DGS30")

    def call_mortgage30us(self, other_args: List[str]):
        """Process mortgage30us command"""
        fred_view.display_fred(other_args, "MORTGAGE30US")

    def call_fedfunds(self, other_args: List[str]):
        """Process fedfunds command"""
        fred_view.display_fred(other_args, "FEDFUNDS")

    def call_aaa(self, other_args: List[str]):
        """Process aaa command"""
        fred_view.display_fred(other_args, "AAA")

    def call_dexcaus(self, other_args: List[str]):
        """Process dexcaus command"""
        fred_view.display_fred(other_args, "DEXCAUS")

    def call_feargreed(self, other_args: List[str]):
        """Process feargreed command"""
        cnn_view.fear_and_greed_index(other_args)

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        wsj_view.display_overview(other_args)

    def call_indices(self, other_args: List[str]):
        """Process indices command"""
        wsj_view.display_indices(other_args)

    def call_futures(self, other_args: List[str]):
        """Process futures command"""
        wsj_view.display_futures(other_args)

    def call_usbonds(self, other_args: List[str]):
        """Process usbonds command"""
        wsj_view.display_usbonds(other_args)

    def call_glbonds(self, other_args: List[str]):
        """Process glbonds command"""
        wsj_view.display_glbonds(other_args)

    def call_currencies(self, other_args: List[str]):
        """Process curremcies command"""
        wsj_view.display_currencies(other_args)

    def call_report(self, _):
        """Process report command"""
        ret = report_controller.menu()

        if ret is False:
            self.print_help()
        else:
            return True


def menu():
    """Econ Menu"""

    econ_controller = EconomyController()
    econ_controller.print_help()

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in econ_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (economy)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (economy)> ")
        try:
            process_input = econ_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
