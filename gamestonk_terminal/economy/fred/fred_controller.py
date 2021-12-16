"""FRED Controller"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List

from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy.fred import fred_view, fred_model
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    valid_date,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session


class FredController:
    CHOICES = ["cls", "?", "help", "q", "quit"]

    CHOICES_COMMANDS = ["search", "add", "rmv", "plot"]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.fred_parser = argparse.ArgumentParser(add_help=False, prog="fred")
        self.fred_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.current_series = dict()
        self.current_long_id = 0

    def print_help(self):
        """Print help"""
        id_string = ""
        for s_id, sub_dict in self.current_series.items():
            id_string += f"    {s_id.upper()}{(self.current_long_id-len(s_id)) * ' '} : {sub_dict['title']}\n"
        help_text = f"""
What do you want to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program

    search        search FRED series notes
    add           add series ID to list
    rmv           remove series ID from list

Current Series IDs:
{id_string}{Style.DIM if not self.current_series else ""}
    plot          plot selected series {Style.RESET_ALL}
        """
        print(help_text)

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

        (known_args, other_args) = self.fred_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    @try_except
    def call_search(self, other_args: List[str]):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Print series notes when searching for series. [Source: FRED]",
        )
        parser.add_argument(
            "-s",
            "--series",
            action="store",
            dest="series_term",
            type=str,
            required="-h" not in other_args,
            help="Search for this series term.",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_positive,
            default=5,
            help="Maximum number of series notes to display.",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        fred_view.notes(
            series_term=ns_parser.series_term,
            num=ns_parser.num,
        )

    @try_except
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add",
            description="Add a FRED series to current selection",
        )
        parser.add_argument(
            "-i",
            "--id",
            dest="series_id",
            required="-h" not in other_args,
            type=str,
            help="FRED Series from https://fred.stlouisfed.org. For multiple series use: series1,series2,series3",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        # Loop through entries.  If it exists, save title in dictionary
        for s_id in ns_parser.series_id.split(","):
            exists, information = fred_model.check_series_id(s_id)
            if exists:
                self.current_series[s_id] = {
                    "title": information["seriess"][0]["title"],
                    "units": information["seriess"][0]["units_short"],
                }
                self.current_long_id = max(self.current_long_id, len(s_id))

        print(
            f"Current Series: {', '.join(self.current_series.keys()) .upper() or None}\n"
        )

    @try_except
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="Remove a FRED series from current selection",
        )
        parser.add_argument(
            "-a",
            "--all",
            help="Flag to remove all selections",
            dest="all",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-i",
            "--id",
            type=str,
            choices=self.current_series.keys(),
            required="-h" not in other_args
            and "-a" not in other_args
            and "--all" not in other_args,
            dest="series_id",
            help="Specific id's to remove",
        )

        if other_args:
            if (
                "-h" not in other_args
                and "-i" not in other_args
                and "--id" not in other_args
                and "-a" not in other_args
                and "--all" not in other_args
            ):
                other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.all:
            self.current_series = {}
            self.current_long_id = 0
            print("")
            return

        self.current_series.pop(ns_parser.series_id)
        print(f"Current Series Ids: {', '.join(self.current_series.keys()) or None}\n")

    @try_except
    def call_plot(self, other_args):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="plot",
            description="Plot selected FRED Series",
        )
        parser.add_argument(
            "-s",
            dest="start_date",
            type=valid_date,
            default="2020-01-01",
            help="Starting date (YYYY-MM-DD) of data",
        )
        parser.add_argument(
            "--raw",
            help="Flag to show raw data",
            dest="raw",
            action="store_true",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if not ns_parser:
            return

        fred_view.display_fred_series(
            self.current_series, ns_parser.start_date, ns_parser.raw, ns_parser.export
        )


def menu():
    """Fred Menu"""

    fred_controller = FredController()
    fred_controller.print_help()

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in fred_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (economy)(fred)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (economy)(fred)> ")
        try:
            process_input = fred_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, fred_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
