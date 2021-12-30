""" Options Screener Controller Module """
__docformat__ = "numpy"

import argparse
import difflib
import os
from typing import List, Union

from colorama import Style
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    system_clear,
    try_except,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.stocks.comparison_analysis import ca_controller
from gamestonk_terminal.stocks.options import syncretism_view

# pylint: disable=E1121


class ScreenerController:
    """Screener Controller class"""

    # Command choices
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
    CHOICES_COMMANDS = ["view", "set", "scr"]
    CHOICES_MENUS = [
        "ca",
        "po",
    ]
    CHOICES += CHOICES_COMMANDS + CHOICES_MENUS

    presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")
    preset_choices = [
        f.split(".")[0] for f in os.listdir(presets_path) if f.endswith(".ini")
    ]

    def __init__(self, queue: List[str] = None):
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
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.preset = "high_IV"
        self.screen_tickers: List = list()

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = f"""
    view          view available presets (or one in particular)
    set           set one of the available presets

PRESET: {self.preset}

    scr            screen data from this preset
{Style.NORMAL if self.screen_tickers else Style.DIM}
Last screened tickers: {', '.join(self.screen_tickers)}
>   ca             take these to comparison analysis menu
>   po             take these to portoflio optimization menu{Style.RESET_ALL}
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
        # additional quit for when we come to this menu through a relative path
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "screen")
        self.queue.insert(0, "options")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
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
                syncretism_view.view_available_presets(
                    preset=ns_parser.preset, presets_path=self.presets_path
                )

            else:
                for preset in self.preset_choices:
                    print(preset)
                print("")

    @try_except
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="set",
            description="""Set preset from custom and default ones.""",
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
    def call_scr(self, other_args: List[str]):
        """Process scr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="scr",
            description="""Screener filter output from https://ops.syncretism.io/index.html.
        Where: CS: Contract Symbol; S: Symbol, T: Option Type; Str: Strike; Exp v: Expiration;
        IV: Implied Volatility; LP: Last Price; B: Bid; A: Ask; V: Volume; OI: Open Interest;
        Y: Yield; MY: Monthly Yield; SMP: Regular Market Price; SMDL: Regular Market Day Low;
        SMDH: Regular Market Day High; LU: Last Trade Date; LC: Last Crawl; ITM: In The Money;
        PC: Price Change; PB: Price-to-book. """,
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default=self.preset,
            help="Filter presets",
            choices=self.preset_choices,
        )
        parser.add_argument(
            "-l",
            "--limit",
            type=check_positive,
            default=10,
            help="Limit of random entries to display. Default shows all",
            dest="limit",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            self.screen_tickers = syncretism_view.view_screener_output(
                preset=ns_parser.preset,
                presets_path=self.presets_path,
                n_show=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_po(self, _):
        """Call the portfolio optimization menu with selected tickers"""
        if self.screen_tickers:
            self.queue = po_controller.menu(self.screen_tickers, from_submenu=True)
        else:
            print("Some tickers must be screened first through one of the presets!\n")

    @try_except
    def call_ca(self, _):
        """Call the comparison analysis menu with selected tickers"""
        if self.screen_tickers:
            self.queue = ca_controller.menu(
                self.screen_tickers, self.queue, from_submenu=True
            )
        else:
            print("Some tickers must be screened first through one of the presets!\n")


def menu(queue: List[str] = None):
    """Screener Menu"""
    scr_controller = ScreenerController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if scr_controller.queue and len(scr_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if scr_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(scr_controller.queue) > 1:
                    return scr_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = scr_controller.queue[0]
            scr_controller.queue = scr_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in scr_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/options/screen/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                scr_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and scr_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/options/screen/ $ ",
                    completer=scr_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/options/screen/ $ ")

        try:
            # Process the input command
            scr_controller.queue = scr_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options/screen menu.",
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
                    if candidate_input == an_input:
                        an_input = ""
                        scr_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                scr_controller.queue.insert(0, an_input)
            else:
                print("\n")
