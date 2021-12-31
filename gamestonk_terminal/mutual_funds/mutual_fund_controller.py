"""Mutual Fund Controller"""
__docformat__ = "numpy"

import argparse
import difflib
from datetime import datetime, timedelta
from typing import List, Union

import investpy
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from rich import console

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    check_non_negative_float,
    check_positive,
    get_flair,
    parse_known_args_and_warn,
    system_clear,
    try_except,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.mutual_funds import investpy_model, investpy_view, yfinance_view

t_console = console.Console()


class FundController:
    """Fund Controller class"""

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
        "country",
        "search",
        "overview",
        "info",
        "load",
        "plot",
        "sector",
        "equity",
    ]

    CHOICES += CHOICES_COMMANDS
    fund_countries = investpy.funds.get_fund_countries()
    search_by_choices = ["name", "issuer", "isin", "symbol"]
    search_cols = [
        "country",
        "name",
        "symbol",
        "issuer",
        "isin",
        "asset_class",
        "currency",
        "underlying",
    ]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.fund_parser = argparse.ArgumentParser(add_help=False, prog="fund")
        self.fund_parser.add_argument("cmd", choices=self.CHOICES)
        self.country = "united states"
        self.completer: Union[None, NestedCompleter] = None
        self.data = pd.DataFrame()
        self.fund_name = ""
        self.fund_symbol = ""
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["country"] = {c: None for c in self.fund_countries}
            choices["search"]["-b"] = {c: None for c in self.search_by_choices}
            choices["search"]["--by"] = {c: None for c in self.search_by_choices}
            choices["search"]["-s"] = {c: None for c in self.search_cols}
            choices["search"]["--sortby"] = {c: None for c in self.search_cols}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        fund_string = f"{self.fund_name or None}"
        fund_string2 = f" ({self.fund_symbol})" if self.fund_symbol else ""
        fund_string += fund_string2
        help_str = f"""
[bold]Mutual Funds[/bold]:[italic]

Investing.com[/italic]:
    country       set a country for filtering

Current Country: [green]{self.country.title()}[/green][italic]

Investing.com[/italic]:
    overview      overview of top funds by country
    search        search for Mutual Funds
    load          load historical fund data

Current Fund: [cyan] {fund_string}[/cyan]
[italic]{'[dim]' if not self.fund_symbol else ''}
Investing.com[/italic]:
    info          get fund information
    plot          plot loaded historical fund data{'[/dim]' if not self.fund_symbol else ''}
[italic]{'[dim]' if not self.fund_symbol or self.country!='united states' else ''}
Yahoo Finance[/italic]:
    sector        sector weightings
    equity        equity holdings
    {'[/dim]' if not self.fund_symbol or self.country!='united states' else ''}
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

        (known_args, other_args) = self.fund_parser.parse_known_args(an_input.split())

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
        print("")
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

    def call_reset(self, _):
        """Process reset command"""
        if self.fund_name:
            self.queue.insert(0, f"load {self.fund_name} --name")
        self.queue.insert(0, f"country -n {self.country}")
        self.queue.insert(0, "funds")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")

    @try_except
    def call_country(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="country",
            description="Set a country for funds",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            nargs="+",
            help="country to select",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            country_candidate = " ".join(ns_parser.name)
            if country_candidate.lower() in self.fund_countries:
                self.country = " ".join(ns_parser.name)
            else:
                t_console.print(
                    f"{country_candidate.lower()} not a valid country to select."
                )
        t_console.print("")
        return self.queue

    @try_except
    def call_search(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="Search mutual funds in selected country based on selected field.",
        )
        parser.add_argument(
            "-b",
            "--by",
            choices=self.search_by_choices,
            default="name",
            dest="by",
            help="Field to search by",
        )
        parser.add_argument(
            "-f",
            "--fund",
            help="Fund string to search for",
            dest="fund",
            type=str,
            nargs="+",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            choices=self.search_cols,
            help="Column to sort by",
            default="name",
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Number of search results to show",
            type=check_positive,
            dest="limit",
            default=10,
        )
        parser.add_argument(
            "-a",
            "--ascend",
            dest="ascending",
            help="Sort in ascending order",
            action="store_true",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            search_string = " ".join(ns_parser.fund)
            investpy_view.display_search(
                by=ns_parser.by,
                value=search_string,
                country=self.country,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascending=ns_parser.ascending,
            )
        return self.queue

    @try_except
    def call_overview(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="overview",
            description="Show overview of funds from selected country.",
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Number of search results to show",
            type=check_positive,
            dest="limit",
            default=10,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            investpy_view.display_overview(
                self.country, limit=ns_parser.limit, export=ns_parser.export
            )
        return self.queue

    @try_except
    def call_info(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="Get fund information.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.fund_name:
                t_console.print(
                    "No fund loaded.  Please use `load` first to plot.\n", style="bold"
                )
                return self.queue
            investpy_view.display_fund_info(self.fund_name, country=self.country)
        return self.queue

    @try_except
    def call_load(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Get historical data.",
        )
        parser.add_argument(
            "-f",
            "--fund",
            help="Fund string to search for",
            dest="fund",
            type=str,
            nargs="+",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-n",
            "--name",
            action="store_true",
            default=False,
            dest="name",
            help="Flag to indicate name provided instead of symbol.",
        )
        # Keeping the date format constant for investpy even though it needs to be reformatted in model
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the fund",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the fund",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            parsed_fund = " ".join(ns_parser.fund)
            (
                self.data,
                self.fund_name,
                self.fund_symbol,
                self.country,
            ) = investpy_model.get_fund_historical(
                fund=parsed_fund,
                name=ns_parser.name,
                country=self.country,
                start_date=ns_parser.start,
                end_date=ns_parser.end,
            )
            if self.data.empty:
                t_console.print(
                    """No data found.
Potential errors
    -- Incorrect country specified
    -- ISIN supplied instead of symbol
    -- Name used, but --name flag not passed"""
                )
        t_console.print("")
        return self.queue

    @try_except
    def call_plot(self, other_args: List[str]):
        """Process country command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="Plot historical data.",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if not self.fund_symbol:
                t_console.print(
                    "No fund loaded.  Please use `load` first to plot.\n", style="bold"
                )
                return self.queue
            investpy_view.display_historical(
                self.data, fund=self.fund_name, export=ns_parser.export
            )
        return self.queue

    @try_except
    def call_sector(self, other_args: List[str]):
        """Process sector command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sector",
            description="Show fund sector weighting.",
        )
        parser.add_argument(
            "-m",
            "--min",
            type=check_non_negative_float,
            dest="min",
            help="Minimum positive float to display sector",
            default=5,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if self.country != "united states":
                t_console.print(
                    "YFinance implementation currently only supports funds from united states"
                )
                return self.queue
            if not self.fund_symbol or not self.fund_name:
                t_console.print(
                    "No fund loaded.  Please use `load` first to plot.\n", style="bold"
                )
                return self.queue
            yfinance_view.display_sector(
                self.fund_symbol,
                min_pct_to_display=ns_parser.min,
                export=ns_parser.export,
            )

        return self.queue

    @try_except
    def call_equity(self, other_args: List[str]):
        """Process sector command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="equity",
            description="Show fund equity holdings.",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.country != "united states":
                t_console.print(
                    "YFinance implementation currently only supports funds from united states"
                )
                return self.queue
            if not self.fund_symbol or not self.fund_name:
                t_console.print(
                    "No fund loaded.  Please use `load` first to plot.\n", style="bold"
                )
                return self.queue
            yfinance_view.display_equity(self.fund_symbol)

        return self.queue


def menu(queue: List[str] = None):
    fund_controller = FundController(queue)
    first = True

    while True:
        # There is a command in the queue
        if fund_controller.queue and len(fund_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if fund_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(fund_controller.queue) > 1:
                    return fund_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = fund_controller.queue[0]
            fund_controller.queue = fund_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in fund_controller.CHOICES_COMMANDS:
                t_console.print(f"{get_flair()} /funds/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if first:
                fund_controller.print_help()
                first = False

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and fund_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /funds/ $ ",
                        completer=fund_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /funds/ $ ")

        try:
            # Process the input command
            fund_controller.queue = fund_controller.switch(an_input)

        except SystemExit:
            t_console.print(
                f"\nThe command '{an_input}' doesn't exist on the /funds/ menu."
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                fund_controller.CHOICES,
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
                        fund_controller.queue = []
                        t_console.print("")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.\n")
                fund_controller.queue.insert(0, an_input)
            else:
                t_console.print("")
