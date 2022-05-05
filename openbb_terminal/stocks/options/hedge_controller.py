""" Hedge Controller Module """
__docformat__ = "numpy"

import argparse
import logging
from typing import Dict, List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import yfinance_model
from openbb_terminal.helper_funcs import (
    check_non_negative,
    parse_known_args_and_warn,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options.hedge_model import(
    add_hedge_option,
    add_portfolio_option, 
    calc_hedge,
    rmv_hedge_option,
)

from openbb_terminal.stocks.options.yfinance_model import (
    get_option_chain,
    get_price,
)
from openbb_terminal.stocks.options.yfinance_view import show_greeks
from openbb_terminal.stocks.options import op_helpers
from datetime import datetime

# pylint: disable=R0902


logger = logging.getLogger(__name__)


class HedgeController(BaseController):
    """Hedge Controller class"""

    CHOICES_COMMANDS = [
        "list",
        "add",
        "rmv",
        "pick",
        "sop",
    ]

    underlying_asset_choices = ["long", "short", "none"]
    PATH = "/stocks/options/hedge/"

    def __init__(self, ticker: str, expiration: str, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.chain = get_option_chain(ticker, expiration)
        self.calls = list(
            zip(
                self.chain.calls["strike"].tolist(),
                self.chain.calls["impliedVolatility"].tolist(),
                
            )
        )
        self.puts = list(
            zip(
                self.chain.puts["strike"].tolist(),
                self.chain.puts["impliedVolatility"].tolist(),
            )
        )
        self.ticker = ticker
        self.current_price = get_price(ticker)
        self.expiration = expiration
        self.implied_volatility = self.chain.calls["impliedVolatility"]
        self.options: List[Dict[str, str]] = []
        self.underlying = 0
        self.side = 0
        self.amount = 0
        self.strike = 0
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
    pick          long, short, or none (default) / call or put / amount of position / strike price
[/cmds][param]
Underlying Asset Position: [/param]{('Short', 'None', 'Long')[self.underlying+1]} {self.side} {self.amount} @ {self.strike}
[cmds]
    list          list available strike prices for calls and puts

    add           add option to the list of the options{has_option_start}
    rmv           remove option from the list of the options{has_option_end}

    sop           selected options[/cmds]
        """
        console.print(text=help_text, menu="Stocks - Options - Hedge")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            if self.expiration:
                return [
                    "stocks",
                    f"load {self.ticker}",
                    "options",
                    f"exp -d {self.expiration}",
                    "hedge",
                ]
            return ["stocks", f"load {self.ticker}", "options", "hedge"]
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
                implied_volatility = options_list[ns_parser.index][1]
                
                option = {
                    "type": opt_type,
                    "sign": sign,
                    "strike": strike,
                    "implied_volatility": implied_volatility,
                }

                if opt_type == "call":
                    side = 1
                elif opt_type == "put":
                    side = -1
                self.options.append(option)
                date_obj = datetime.strptime(self.expiration, "%Y-%m-%d")
                days = (date_obj - datetime.now()).days + 1
                if days == 0: 
                    days = 0.01
                if (len(self.options)) <= 2:
                    add_hedge_option(self.current_price, implied_volatility, strike, days/365, side)

                if (len(self.options)) == 2:
                    calc_hedge(self.amount, self.side, sign)

                self.update_runtime_choices()

                console.print("#\tType\tHold\tStrike\tImplied Volatility")
                for i, o in enumerate(self.options):
                    asset: str = "Long" if o["sign"] == 1 else "Short"
                    console.print(
                        f"{i}\t{o['type']}\t{asset}\t{o['strike']}\t{o['implied_volatility']}"
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
            description="""Remove one of the options to be shown in the hedge.""",
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
                        
                        rmv_hedge_option(ns_parser.index)
                        self.update_runtime_choices()
                    else:
                        console.print("Please use a valid index.\n")

                console.print("#\tType\tHold\tStrike\tImplied Volatility")

                for i, o in enumerate(self.options):
                    sign = "Long" if o["sign"] == 1 else "Short"
                    console.print(
                        f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['implied_volatility']}"
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
            description="This function plots option hedge diagrams",
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
        parser.add_argument(
            "-s",
            "--side",
            dest="sidetype",
            type=str,
            help="Choose what you would like to do with the underlying asset",
            required="-h" not in other_args,
            choices=["call", "put"],
        )
        parser.add_argument(
            "-a",
            "--amount",
            help="Amount of underlying asset in position.",
            dest="amounttype",
            default=0,
            type=check_non_negative,
        )
        parser.add_argument(
            "-p",
            "--strikeprice",
            help="Strike price of option in position.",
            dest="striketype",
            default=0,
            type=check_non_negative,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            type = 0
            if ns_parser.underlyingtype == "long":
                self.underlying = 1
                type = 1
            elif ns_parser.underlyingtype == "none":
                self.underlying = 0
                type = 0
            elif ns_parser.underlyingtype == "short":
                self.underlying = -1
                type = -1

            side = 0
            if ns_parser.sidetype == "call":
                self.side = "call"
                side = 1
            elif ns_parser.sidetype == "put":
                self.side = "put"
                side = -1

            self.amount = ns_parser.amounttype
            self.strike = ns_parser.striketype

            index = -1
            strike = self.strike

            

            amount = self.amount
            price = self.current_price
            
            date_obj = datetime.strptime(self.expiration, "%Y-%m-%d")
            days = (date_obj - datetime.now()).days + 1
            if days == 0: 
                days = 0.01

            if side == 1:
                for i in range(len(self.chain.calls["strike"])):
                    if self.chain.calls["strike"][i] == strike:
                        index = i
                        break
                implied_volatility = self.chain.calls["impliedVolatility"][index]

            elif side == -1:
                for i in range(len(self.chain.puts["strike"])):
                    if self.chain.puts["strike"][i] == strike:
                        index = i
                        break
                implied_volatility = self.chain.puts["impliedVolatility"][index]
            
            add_portfolio_option(price, strike, type, side, days/365, implied_volatility)
            
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
            console.print("#\tType\tHold\tStrike\tImplied Volatility")
            for i, o in enumerate(self.options):
                sign = "Long" if o["sign"] == 1 else "Short"
                console.print(f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['implied_volatility']}")
            console.print("")

    