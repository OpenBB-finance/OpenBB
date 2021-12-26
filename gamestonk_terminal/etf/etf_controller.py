"""ETF Controller"""
__docformat__ = "numpy"

import argparse
import difflib
import os
from datetime import datetime
from typing import List, Union

from prompt_toolkit.completion import NestedCompleter
from thepassiveinvestor import create_ETF_report

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.etf import (
    screener_view,
    stockanalysis_view,
    wsj_view,
    financedatabase_view,
)
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session


class ETFController:
    """ETF Controller class"""

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
        "search",
        "overview",
        "compare",
        "holdings",
        "screener",
        "gainers",
        "decliners",
        "active",
        "pir",
        "fds",
    ]

    CHOICES += CHOICES_COMMANDS
    preset_options = [
        file.strip(".ini")
        for file in os.listdir(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")
        )
    ]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.etf_parser = argparse.ArgumentParser(add_help=False, prog="etf")
        self.etf_parser.add_argument("cmd", choices=self.CHOICES)

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["screener"]["--preset"] = {c: None for c in self.preset_options}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_str = """
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
Finance Database:
    fds           advanced ETF search based on category, name and/or description
"""
        print(help_str)

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

        (known_args, other_args) = self.etf_parser.parse_known_args(an_input.split())

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
        print("")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "etf")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")

    @try_except
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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            search_string = " ".join(ns_parser.search_str)
            stockanalysis_view.view_search(
                to_match=search_string, export=ns_parser.export
            )

    @try_except
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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            stockanalysis_view.view_overview(
                symbol=ns_parser.name, export=ns_parser.export
            )

    @try_except
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            stockanalysis_view.view_holdings(
                symbol=ns_parser.name,
                num_to_show=ns_parser.limit,
                export=ns_parser.export,
            )

    @try_except
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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            etf_list = ns_parser.names.upper().split(",")
            stockanalysis_view.view_comparisons(etf_list, export=ns_parser.export)

    @try_except
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
            "-l",
            "--limit",
            type=int,
            help="Number of etfs to show",
            dest="limit",
            default=20,
        )

        parser.add_argument(
            "--preset",
            choices=self.preset_options,
            default="etf_config",
            help="Preset to use",
            dest="preset",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:

            screener_view.view_screener(
                num_to_show=ns_parser.limit,
                preset=ns_parser.preset,
                export=ns_parser.export,
            )

    @try_except
    def call_gainers(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="gainers",
            description="Displays top ETF/Mutual fund gainers from wsj.com/market-data",
            add_help=False,
        )
        parser.add_argument(
            "-l", "--limit", help="Number to show", type=int, default=25, dest="limit"
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.show_top_mover("gainers", ns_parser.limit, ns_parser.export)

    def call_decliners(self, other_args):
        """Process decliners command"""
        parser = argparse.ArgumentParser(
            prog="decliners",
            description="Displays top ETF/Mutual fund decliners from wsj.com/market-data",
            add_help=False,
        )
        parser.add_argument(
            "-l", "--limit", help="Number to show", type=int, default=25, dest="limit"
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.show_top_mover("decliners", ns_parser.limit, ns_parser.export)

    def call_active(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="active",
            description="Displays most active ETF/Mutual funds from wsj.com/market-data",
            add_help=False,
        )
        parser.add_argument(
            "-l", "--limit", help="Number to show", type=int, default=25, dest="limit"
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            wsj_view.show_top_mover("active", ns_parser.limit, ns_parser.export)

    @try_except
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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            etf_list = ns_parser.names.upper().split(",")
            create_ETF_report(
                etf_list, filename=ns_parser.filename, folder=ns_parser.folder
            )
            print(
                f"Created ETF report as {ns_parser.filename} in folder {ns_parser.folder} \n"
            )

    @try_except
    def call_fds(self, other_args):
        """Process fds command"""
        parser = argparse.ArgumentParser(
            description="Display a selection of ETFs based on category, name and/or description filtered by total "
            "assets. Returns the top ETFs when no argument is given. [Source: Finance Database]",
            add_help=False,
        )
        parser.add_argument(
            "-c",
            "--category",
            default=None,
            nargs="+",
            dest="category",
            help="Specify the ETF selection based on a category",
        )
        parser.add_argument(
            "-n",
            "--name",
            default=None,
            nargs="+",
            dest="name",
            help="Specify the ETF selection based on the name",
        )
        parser.add_argument(
            "-d",
            "--description",
            default=None,
            nargs="+",
            dest="description",
            help="Specify the ETF selection based on the description (not shown in table)",
        )
        parser.add_argument(
            "-ie",
            "--include_exchanges",
            action="store_false",
            help="When used, data from different exchanges is also included. This leads to a much larger "
            "pool of data due to the same ETF being listed on multiple exchanges",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            type=int,
            dest="limit",
            help="Enter the number of ETFs you wish to see in the Tabulate window",
        )
        parser.add_argument(
            "-o",
            "--options",
            action="store_true",
            help="Obtain the available categories",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            financedatabase_view.show_etfs(
                category=ns_parser.category,
                name=ns_parser.name,
                description=ns_parser.description,
                include_exchanges=ns_parser.include_exchanges,
                amount=ns_parser.limit,
                options=ns_parser.options,
            )


def menu(queue: List[str] = None):
    etf_controller = ETFController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if etf_controller.queue and len(etf_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if etf_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(etf_controller.queue) > 1:
                    return etf_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = etf_controller.queue[0]
            etf_controller.queue = etf_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in etf_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /etf/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                etf_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and etf_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /etf/ $ ",
                    completer=etf_controller.completer,
                    search_ignore_case=True,
                )

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /etf/ $ ")

        try:
            # Process the input command
            etf_controller.queue = etf_controller.switch(an_input)

        except SystemExit:
            print(f"\nThe command '{an_input}' doesn't exist on the /etf menu.", end="")
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                etf_controller.CHOICES,
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
                        etf_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                etf_controller.queue.insert(0, an_input)
            else:
                print("\n")
