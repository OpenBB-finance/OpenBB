"""Ally Controller"""
__docformat__ = "numpy"

import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.ally import ally_view
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
)


class AllyController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
    ]

    ALLY_CHOICES = ["holdings", "history", "balances"]
    ALLY_STOCK_CHOICES = ["quote", "movers"]

    def __init__(self):
        """CONSTRUCTOR"""

        self._ally_parser = argparse.ArgumentParser(add_help=False, prog="ally")
        self.CHOICES.extend(self.ALLY_CHOICES)
        self.CHOICES.extend(self.ALLY_STOCK_CHOICES)
        self._ally_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Ally:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

    holdings    show account holdings
    history     show history of your account
    balances    show balance details of account

Stock Information:
    quote       get stock quote
    movers      get ranked lists of movers
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

        (known_args, other_args) = self._ally_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu."""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    @try_except
    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            prog="holdings",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Ally",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        ally_view.display_holdings(export=ns_parser.export)

    @try_except
    def call_history(self, other_args: List[str]):
        """Process history command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="history",
            description="""Account transaction history""",
        )
        parser.add_argument(
            "-n",
            "--num",
            dest="num",
            default=15,
            type=int,
            help="Number of recent transactions to show",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        ally_view.display_history(n_to_show=ns_parser.num, export=ns_parser.export)

    @try_except
    def call_balances(self, other_args: List[str]):
        """Process balances command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balances",
            description="""Account balance details""",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        ally_view.display_balances(export=ns_parser.export)

    @try_except
    def call_quote(self, other_args: List[str]):
        """Process balances command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="""Get stock quote""",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-t")
        parser.add_argument(
            "-t",
            "--ticker",
            help="Ticker to get quote for. Can be in form of 'tick1,tick2...'",
            type=str,
            dest="ticker",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        ally_view.display_stock_quote(ns_parser.ticker)

    @try_except
    def call_movers(self, other_args: List[str]):
        """Process movers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="movers",
            description="""Get stock movers""",
        )
        parser.add_argument(
            "-l",
            "--list",
            help="List to get movers of",
            choices=[
                "toplosers",
                "toppctlosers",
                "topvolume",
                "topactive",
                "topgainers",
                "toppctgainers",
            ],
            default="topactive",
            dest="list_type",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            help="""Exchange to look at.  Can be
            A:American Stock Exchange.
            N:New York Stock Exchange.
            Q:NASDAQ
            U:NASDAQ Bulletin Board
            V:NASDAQ OTC Other""",
            choices=["A", "N", "Q", "U", "V"],
            default="N",
            dest="exchange",
        )
        parser.add_argument(
            "-n", "--num", help="Number to show", type=int, default=15, dest="num"
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        ally_view.display_top_lists(
            list_type=ns_parser.list_type,
            exchange=ns_parser.exchange,
            num_to_show=ns_parser.num,
            export=ns_parser.export,
        )


def menu():

    ally_controller = AllyController()
    ally_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in ally_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (bro)>(ally)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (bro)>(ally)> ")

        try:
            process_input = ally_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
