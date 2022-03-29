""" Payoff Controller Module """
__docformat__ = "numpy"

import argparse
import logging
from typing import Dict, List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    check_non_negative,
    parse_known_args_and_warn,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.yfinance_model import get_option_chain, get_price
from openbb_terminal.stocks.options.yfinance_view import plot_payoff

# pylint: disable=R0902


logger = logging.getLogger(__name__)


class PayoffController(BaseController):
    """Payoff Controller class"""

    CHOICES_COMMANDS = [
        "list",
        "add",
        "rmv",
        "pick",
        "plot",
        "sop",
    ]

    underlying_asset_choices = ["long", "short", "none"]
    PATH = "/stocks/options/payoff/"

    def __init__(self, ticker: str, expiration: str, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.chain = get_option_chain(ticker, expiration)
        self.calls = list(
            zip(
                self.chain.calls["strike"].tolist(),
                self.chain.calls["lastPrice"].tolist(),
            )
        )
        self.puts = list(
            zip(
                self.chain.puts["strike"].tolist(),
                self.chain.puts["lastPrice"].tolist(),
            )
        )
        self.ticker = ticker
        self.current_price = get_price(ticker)
        self.expiration = expiration
        self.options: List[Dict[str, str]] = []
        self.underlying = 0
        self.call_index_choices = range(len(self.calls))
        self.put_index_choices = range(len(self.puts))

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["pick"] = {c: {} for c in self.underlying_asset_choices}
            choices["add"] = {
                str(c): {} for c in list(range(max(len(self.puts), len(self.calls))))
            }
            # This menu contains dynamic choices that may change during runtime
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        """Update runtime choices"""
        if self.options and session and obbff.USE_PROMPT_TOOLKIT:
            self.choices["rmv"] = {str(c): {} for c in range(len(self.options))}
            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        has_option_start = "" if self.options else "[unvl]"
        has_option_end = "" if self.options else "[/unvl]"
        help_text = f"""
[param]Ticker: [/param]{self.ticker or None}
[param]Expiry: [/param]{self.expiration or None}
[cmds]
    pick          long, short, or none (default) underlying asset
[/cmds][param]
Underlying Asset: [/param]{('Short', 'None', 'Long')[self.underlying+1]}
[cmds]
    list          list available strike prices for calls and puts

    add           add option to the list of the options to be plotted{has_option_start}
    rmv           remove option from the list of the options to be plotted{has_option_end}

    sop           selected options
    plot          show the option payoff diagram[/cmds]
        """
        console.print(text=help_text, menu="Stocks - Options - Payoff")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            if self.expiration:
                return [
                    "stocks",
                    f"load {self.ticker}",
                    "options",
                    f"exp -d {self.expiration}",
                    "payoff",
                ]
            return ["stocks", f"load {self.ticker}", "options", "payoff"]
        return []

    @log_start_end(log=logger)
    def call_list(self, other_args):
        """Lists available calls and puts"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="list",
            description="""Lists available calls and puts.""",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            length = max(len(self.calls), len(self.puts)) - 1
            console.print("#\tcall\tput")
            for i in range(length):
                call = self.calls[i][0] if i < len(self.calls) else ""
                put = self.puts[i][0] if i < len(self.puts) else ""
                console.print(f"{i}\t{call}\t{put}")
            console.print("")

    @log_start_end(log=logger)
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add",
            description="""Add options to the diagram.""",
        )
        parser.add_argument(
            "-p",
            "--put",
            dest="put",
            action="store_true",
            help="buy a put instead of a call",
            default=False,
        )
        parser.add_argument(
            "-s",
            "--short",
            dest="short",
            action="store_true",
            help="short the option instead of buying it",
            default=False,
        )
        parser.add_argument(
            "-i",
            "--index",
            dest="index",
            type=check_non_negative,
            help="list index of the option",
            required="-h" not in other_args and "-k" not in other_args,
            choices=self.put_index_choices
            if "-p" in other_args
            else self.call_index_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            opt_type = "put" if ns_parser.put else "call"
            sign = -1 if ns_parser.short else 1
            options_list = self.puts if ns_parser.put else self.calls

            if ns_parser.index < len(options_list):
                strike = options_list[ns_parser.index][0]
                cost = options_list[ns_parser.index][1]

                option = {
                    "type": opt_type,
                    "sign": sign,
                    "strike": strike,
                    "cost": cost,
                }
                self.options.append(option)
                self.update_runtime_choices()

                console.print("#\tType\tHold\tStrike\tCost")
                for i, o in enumerate(self.options):
                    asset: str = "Long" if o["sign"] == 1 else "Short"
                    console.print(
                        f"{i}\t{o['type']}\t{asset}\t{o['strike']}\t{o['cost']}"
                    )
                console.print("")

            else:
                console.print("Please use a valid index\n")

    @log_start_end(log=logger)
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="""Remove one of the options to be shown in the payoff.""",
        )
        parser.add_argument(
            "-i",
            "--index",
            dest="index",
            type=check_non_negative,
            help="index of the option to remove",
            required=bool("-h" not in other_args and len(self.options) > 0),
            choices=range(len(self.options)),
        )
        parser.add_argument(
            "-a",
            "--all",
            dest="all",
            action="store_true",
            help="remove all of the options",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.options:
                if ns_parser.all:
                    self.options = []
                else:
                    if ns_parser.index < len(self.options):
                        del self.options[ns_parser.index]
                        self.update_runtime_choices()
                    else:
                        console.print("Please use a valid index.\n")

                console.print("#\tType\tHold\tStrike\tCost")
                for i, o in enumerate(self.options):
                    sign = "Long" if o["sign"] == 1 else "Short"
                    console.print(
                        f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['cost']}"
                    )
                console.print("")
        else:
            console.print(
                "No options have been selected, removing them is not possible\n"
            )

    @log_start_end(log=logger)
    def call_pick(self, other_args: List[str]):
        """Process pick command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="long",
            description="This function plots option payoff diagrams",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="underlyingtype",
            type=str,
            help="Choose what you would like to do with the underlying asset",
            required="-h" not in other_args,
            choices=self.underlying_asset_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.underlyingtype == "long":
                self.underlying = 1
            elif ns_parser.underlyingtype == "none":
                self.underlying = 0
            elif ns_parser.underlyingtype == "short":
                self.underlying = -1

        console.print("")

    @log_start_end(log=logger)
    def call_sop(self, other_args):
        """Process sop command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sop",
            description="Displays selected option",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            console.print("#\tType\tHold\tStrike\tCost")
            for i, o in enumerate(self.options):
                sign = "Long" if o["sign"] == 1 else "Short"
                console.print(f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['cost']}")
            console.print("")

    @log_start_end(log=logger)
    def call_plot(self, other_args):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="This function plots option payoff diagrams",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            plot_payoff(
                self.current_price,
                self.options,
                self.underlying,
                self.ticker,
                self.expiration,
            )
