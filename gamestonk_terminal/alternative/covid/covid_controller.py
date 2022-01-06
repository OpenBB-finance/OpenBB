"""COVID Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
import logging
import pathlib
from typing import List, Union

import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from rich.console import Console

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.alternative.covid import covid_view
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    system_clear,
    try_except,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from gamestonk_terminal.menu import session

logger = logging.getLogger(__name__)
t_console = Console()

country_file = pathlib.Path(__file__).parent.joinpath("countries.txt")


class CovidController:
    """Covid Controller class"""

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

    CHOICES_COMMANDS = ["country", "ov", "deaths", "cases", "rates", "slopes"]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.covid_parser = argparse.ArgumentParser(add_help=False, prog="covid")
        self.covid_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.queue = queue if queue else list()
        self.completer: Union[None, NestedCompleter] = None
        self.country = "US"
        self.COUNTRY_LIST = pd.read_csv(country_file, sep="\n", index_col=None)[
            "Countries"
        ].to_list()
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["country"] = {c: None for c in self.COUNTRY_LIST}

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_str = f"""
        slopes      get countries with highest slope in cases
        country     select country for data

Country: [cyan]{self.country}[/cyan]

        ov          get overview (cases and deaths) for selected country
        deaths      get deaths for selected country
        cases       get cases for selected country
        rates       get death/cases rate for selected country
        """
        t_console.print(help_str)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            t_console.print("")
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

        logger.info(an_input)
        (known_args, other_args) = self.covid_parser.parse_known_args(an_input.split())

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
        t_console.print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, f"country {self.country}")
        self.queue.insert(0, "covid")
        self.queue.insert(0, "alternative")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_country(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="country",
            description="Select a country to look at data for.",
        )
        parser.add_argument(
            "-c",
            "--country",
            nargs="+",
            type=str,
            dest="country",
            help="Country to get data for.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.country:
                country = " ".join(ns_parser.country)
                if country not in self.COUNTRY_LIST:
                    t_console.print(f"[red]{country} not a valid selection.[/red]\n")
                    return
                self.country = country
                t_console.print(f"[cyan]{country}[/cyan] loaded\n")
            else:
                t_console.print("[red]Please input a country.[/red]\n")

    @try_except
    def call_ov(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ov",
            description="Show historical cases and deaths by country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_ov(
                self.country,
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_rates(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rates",
            description="Show historical rates country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="rates",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_deaths(self, other_args: List[str]):
        """Process deaths command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="deaths",
            description="Show historical deaths by country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="deaths",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_cases(self, other_args: List[str]):
        """Process cases command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cases",
            description="Show historical cases for country.",
        )
        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            covid_view.display_covid_stat(
                self.country,
                stat="cases",
                raw=ns_parser.raw,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
    def call_slopes(self, other_args: List[str]):
        """Process cases command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="slopes",
            description="Show countries with highest slopes.",
        )
        parser.add_argument(
            "-d",
            "--days",
            type=check_positive,
            help="Number of days back to look",
            dest="days",
            default=30,
        )
        parser.add_argument(
            "-a",
            "--ascend",
            action="store_true",
            default=False,
            help="Show in ascending order",
        )
        parser.add_argument(
            "-t",
            "--threshold",
            default=10000,
            dest="threshold",
            help="Threshold for total cases over period",
            type=check_positive,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )
        if ns_parser:
            covid_view.display_country_slopes(
                days_back=ns_parser.days,
                limit=ns_parser.limit,
                ascend=ns_parser.ascend,
                threshold=ns_parser.threshold,
            )


def menu(queue: List[str] = None):
    """Covid Menu"""
    covid_controller = CovidController(queue)
    an_input = "HELP_ME"
    logger.info("CovidMenu")
    while True:
        # There is a command in the queue
        if covid_controller.queue and len(covid_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if covid_controller.queue[0] in ("q", "..", "quit"):
                t_console.print("")
                if len(covid_controller.queue) > 1:
                    return covid_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = covid_controller.queue[0]
            covid_controller.queue = covid_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in covid_controller.CHOICES_COMMANDS:
                t_console.print(f"{get_flair()} /alternative/covid/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                covid_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and covid_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /alternative/covid/ $ ",
                        completer=covid_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /alternative/covid/ $ ")

        try:
            # Process the input command
            covid_controller.queue = covid_controller.switch(an_input)

        except SystemExit:
            t_console.print(
                f"\nThe command '{an_input}' doesn't exist on the /alternative/covid menu."
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                covid_controller.CHOICES,
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
                        covid_controller.queue = []
                        t_console.print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                t_console.print(f" Replacing by '{an_input}'.")
                covid_controller.queue.insert(0, an_input)
            else:
                t_console.print("")
