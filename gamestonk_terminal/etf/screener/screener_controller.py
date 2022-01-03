"""Screener Controller Module"""
__docformat__ = "numpy"
# pylint:disable=too-many-lines
# pylint:disable=R0904,C0201

import os
import argparse
import configparser
import difflib
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
    check_positive,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.etf.screener import screener_view
from gamestonk_terminal.etf import financedatabase_view, financedatabase_model

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")


class ScreenerController:
    """Screener Controller class"""

    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]

    CHOICES_COMMANDS = [
        "view",
        "set",
        "screen",
        "sbc",
    ]

    CHOICES += CHOICES_COMMANDS

    presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")
    preset_choices = [
        f.split(".")[0] for f in os.listdir(presets_path) if f.endswith(".ini")
    ]

    sortby_screen_choices = [
        "Assets",
        "NAV",
        "Expense",
        "PE",
        "SharesOut",
        "Div",
        "DivYield",
        "Volume",
        "Open",
        "PrevClose",
        "YrLow",
        "YrHigh",
        "Beta",
        "N_Hold",
    ]

    def __init__(
        self,
        queue: List[str] = None,
    ):
        """Constructor"""
        self.scr_parser = argparse.ArgumentParser(add_help=False, prog="scr")
        self.scr_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["view"] = {c: None for c in self.preset_choices}
            choices["set"] = {c: None for c in self.preset_choices}
            choices["sbc"] = {
                c: None for c in financedatabase_model.get_etfs_categories()
            }
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.preset = "etf_config"
        self.screen_tickers: List = list()

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_str = f"""
    view        view available presets
    set         set one of the available presets

PRESET: {self.preset}

    screen      screen ETF using preset selected [StockAnalysis]

    sbc         screen by category [FinanceDatabase]
"""
        print(help_str)

    def switch(self, an_input: str):
        """Process and dispatch input
        Parameters
        -------
        an_input : str
            string with input arguments
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

        (known_args, other_args) = self.scr_parser.parse_known_args(an_input.split())

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

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "scr")
        self.queue.insert(0, "etf")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_view(self, other_args: List[str]):
        """Process view command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="view",
            description="""View available presets under presets folder.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            help="View specific custom preset",
            default="",
            choices=self.preset_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.preset:
                preset_filter = configparser.RawConfigParser()
                preset_filter.optionxform = str  # type: ignore
                preset_filter.read(presets_path + ns_parser.preset + ".ini")

                headers = [
                    "Price",
                    "Assets",
                    "NAV",
                    "Expense",
                    "PE",
                    "DivYield",
                    "Volume",
                    "Beta",
                    "N_Hold",
                    "Open",
                    "PrevClose",
                    "YrLow",
                    "YrHigh",
                ]

                print("")
                for filter_header in headers:
                    print(f" - {filter_header} -")
                    d_filters = {**preset_filter[filter_header]}
                    d_filters = {k: v for k, v in d_filters.items() if v}
                    if d_filters:
                        max_len = len(max(d_filters, key=len))
                        for key, value in d_filters.items():
                            print(f"{key}{(max_len-len(key))*' '}: {value}")
                    print("")

            else:
                print("\nPresets:")
                for preset in self.preset_choices:
                    with open(
                        presets_path + preset + ".ini",
                        encoding="utf8",
                    ) as f:
                        description = ""
                        for line in f:
                            if line.strip() == "[Price]":
                                break
                            description += line.strip()
                    print(
                        f"   {preset}{(30-len(preset)) * ' '}{description.split('Description: ')[1].replace('#', '')}"
                    )
                print("")

    @try_except
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="set",
            description="""Set preset.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default="template",
            help="Filter presets",
            choices=self.preset_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.preset = ns_parser.preset
        print("")

    @try_except
    def call_screen(self, other_args):
        """Process screen command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="screen",
            add_help=False,
            description="Screens ETFS from a personal scraping github repository.  Data scraped from stockanalysis.com",
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            help="Limit of etfs to display",
            dest="limit",
            default=10,
        )
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Assets",
            default="Assets",
            choices=self.sortby_screen_choices,
        )
        parser.add_argument(
            "-a",
            "--ascend",
            action="store_true",
            help="Flag to sort in ascending order (lowest on top)",
            dest="ascend",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            screener_view.view_screener(
                preset=self.preset,
                num_to_show=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.ascend,
                export=ns_parser.export,
            )

    @try_except
    def call_sbc(self, other_args: List[str]):
        """Process sbc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sbc",
            description="Search by category [Source: FinanceDatabase/StockAnalysis.com]",
        )
        parser.add_argument(
            "-c",
            "--category",
            type=str,
            dest="category",
            nargs="+",
            help="Category to look for",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            dest="limit",
            help="Limit of ETFs to display",
            default=5,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            category = " ".join(ns_parser.category)
            if category in financedatabase_model.get_etfs_categories():
                financedatabase_view.display_etf_by_category(
                    category=category,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                )
            else:
                print(
                    "The category selected does not exist, choose one from:"
                    f" {', '.join(financedatabase_model.get_etfs_categories())}\n"
                )


def menu(
    queue: List[str] = None,
):
    """Screener Menu"""

    scr_controller = ScreenerController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if scr_controller.queue and len(scr_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if scr_controller.queue[0] in ("q", "..", "quit"):
                if len(scr_controller.queue) > 1:
                    return scr_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = scr_controller.queue[0]
            scr_controller.queue = scr_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in scr_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /etf/scr/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                scr_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and scr_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /etf/scr/ $ ",
                        completer=scr_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /etf/scr/ $ ")

        try:
            # Process the input command
            scr_controller.queue = scr_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /etf/scr menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                scr_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                else:
                    candidate_input = similar_cmd[0]

                if candidate_input == an_input:
                    an_input = ""
                    scr_controller.queue = []
                    print("\n")
                    continue

                print(f" Replacing by '{an_input}'.")
                scr_controller.queue.insert(0, an_input)
            else:
                print("\n")
                an_input = ""
                scr_controller.queue = []
