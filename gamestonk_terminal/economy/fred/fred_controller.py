"""FRED Controller"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union, Dict

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
    """FRED Controller Class"""

    CHOICES = [
        "cls",
        "cd",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
        "home",
    ]

    CHOICES_COMMANDS = ["search", "add", "rmv", "plot"]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.fred_parser = argparse.ArgumentParser(add_help=False, prog="fred")
        self.fred_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.current_series: Dict = dict()
        self.current_long_id = 0

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}

            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        id_string = ""
        for s_id, sub_dict in self.current_series.items():
            id_string += f"    {s_id.upper()}{(self.current_long_id-len(s_id)) * ' '} : {sub_dict['title']}\n"
        help_text = f"""
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
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.fred_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

        return ["quit"]

    def call_exit(self, _):
        print("")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "fred")
        self.queue.insert(0, "economy")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:

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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
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
        if ns_parser:
            if ns_parser.all:
                self.current_series = {}
                self.current_long_id = 0
                print("")

            self.current_series.pop(ns_parser.series_id)
            print(
                f"Current Series Ids: {', '.join(self.current_series.keys()) or None}\n"
            )

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
        if ns_parser:
            fred_view.display_fred_series(
                self.current_series,
                ns_parser.start_date,
                ns_parser.raw,
                ns_parser.export,
            )


def menu(queue: List[str] = None):
    """Fred Menu"""
    fred_controller = FredController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if fred_controller.queue and len(fred_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if fred_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(fred_controller.queue) > 1:
                    return fred_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = fred_controller.queue[0]
            fred_controller.queue = fred_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in fred_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /economy/fred/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                fred_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and fred_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /economy/fred/ $ ",
                    completer=fred_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /economy/fred/ $ ")

        try:
            # Process the input command
            fred_controller.queue = fred_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /economy/fred menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                fred_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        fred_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                fred_controller.queue.insert(0, an_input)
            else:
                print("\n")
