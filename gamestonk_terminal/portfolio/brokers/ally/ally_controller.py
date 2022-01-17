"""Ally Controller"""
__docformat__ = "numpy"

import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers.ally import ally_view
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)


class AllyController(BaseController):
    """Ally Controller class"""

    CHOICES_COMMANDS = ["holdings", "history", "balances", "quote", "movers"]

    list_choices = [
        "toplosers",
        "toppctlosers",
        "topvolume",
        "topactive",
        "topgainers",
        "toppctgainers",
    ]
    PATH = "/portfolio/bro/ally/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["movers"]["-t"] = {c: None for c in self.list_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[cmds]
    holdings    show account holdings
    history     show history of your account
    balances    show balance details of account

[info]Stock Information:[/info]
    quote       get stock quote
    movers      get ranked lists of movers[/cmds]
"""
        console.print(text=help_text, menu="Portfolio - Brokers")

    def call_holdings(self, other_args: List[str]):
        """Process holdings command"""
        parser = argparse.ArgumentParser(
            prog="holdings",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display info about your trading accounts on Ally",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_holdings(export=ns_parser.export)

    def call_history(self, other_args: List[str]):
        """Process history command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="history",
            description="""Account transaction history""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            default=15,
            type=int,
            help="Number of recent transactions to show",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_history(
                n_to_show=ns_parser.limit, export=ns_parser.export
            )

    def call_balances(self, other_args: List[str]):
        """Process balances command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balances",
            description="""Account balance details""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ally_view.display_balances(export=ns_parser.export)

    def call_quote(self, other_args: List[str]):
        """Process balances command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="""Get stock quote""",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        parser.add_argument(
            "-t",
            "--ticker",
            help="Ticker to get quote for. Can be in form of 'tick1,tick2...'",
            type=str,
            dest="ticker",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            ally_view.display_stock_quote(ns_parser.ticker)

    def call_movers(self, other_args: List[str]):
        """Process movers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="movers",
            description="""Get stock movers""",
        )
        parser.add_argument(
            "-t",
            "--type",
            help="List to get movers of",
            choices=self.list_choices,
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
            "-l", "--limit", help="Number to show", type=int, default=15, dest="limit"
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:

            ally_view.display_top_lists(
                list_type=ns_parser.list_type,
                exchange=ns_parser.exchange,
                num_to_show=ns_parser.limit,
                export=ns_parser.export,
            )
