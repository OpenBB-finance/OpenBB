""" Pricing Controller Module """
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional

import pandas as pd

from openbb_terminal import feature_flags as obbff
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console
from openbb_terminal.stocks.options import yfinance_view

logger = logging.getLogger(__name__)


class PricingController(BaseController):
    """Pricing Controller class"""

    CHOICES_COMMANDS = [
        "add",
        "rmv",
        "show",
        "rnval",
    ]
    PATH = "/stocks/options/pricing/"
    CHOICES_GENERATION = True

    def __init__(
        self,
        ticker: str,
        selected_date: str,
        prices: pd.DataFrame,
        queue: Optional[List[str]] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.ticker = ticker
        self.selected_date = selected_date
        self.prices = prices

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/options/pricing/")
        mt.add_param("_ticker", self.ticker or "")
        mt.add_param("_expiry", self.selected_date or "")
        mt.add_raw("\n")
        mt.add_cmd("add")
        mt.add_cmd("rmv")
        mt.add_raw("\n")
        mt.add_cmd("show")
        mt.add_cmd("rnval")
        console.print(text=mt.menu_text, menu="Stocks - Options - Pricing")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            if self.selected_date:
                return [
                    "stocks",
                    f"load {self.ticker}",
                    "options",
                    f"exp -d {self.selected_date}",
                    "pricing",
                ]
            return ["stocks", f"load {self.ticker}", "options", "payoff"]
        return []

    @log_start_end(log=logger)
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="Adds a price to the list",
        )
        parser.add_argument(
            "-p",
            "--price",
            type=float,
            required="-h" not in other_args,
            dest="price",
            help="Projected price of the stock at the expiration date",
        )
        parser.add_argument(
            "-c",
            "--chance",
            type=float,
            required="-h" not in other_args,
            dest="chance",
            help="Chance that the stock is at a given projected price",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.price in self.prices["Price"].to_list():
                df = self.prices[(self.prices["Price"] != ns_parser.price)]
            else:
                df = self.prices

            new = {"Price": ns_parser.price, "Chance": ns_parser.chance}
            df = df.append(new, ignore_index=True)
            self.prices = df.sort_values("Price")

    @log_start_end(log=logger)
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rmv",
            description="Removes a price from the list",
        )
        parser.add_argument(
            "-p",
            "--price",
            type=float,
            required="-h" not in other_args and "-a" not in other_args,
            dest="price",
            help="Price you want to remove from the list",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            default=False,
            dest="all",
            help="Remove all prices from the list",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.all:
                self.prices = pd.DataFrame(columns=["Price", "Chance"])
            else:
                self.prices = self.prices[(self.prices["Price"] != ns_parser.price)]

    @log_start_end(log=logger)
    def call_show(self, other_args):
        """Process show command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="show",
            description="Display prices",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            print_rich_table(
                self.prices,
                headers=list(self.prices.columns),
                show_index=False,
                title=f"Estimated price(s) of {self.ticker} at {self.selected_date}",
            )

    @log_start_end(log=logger)
    def call_rnval(self, other_args: List[str]):
        """Process rnval command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rnval",
            description="The risk neutral value of the options",
        )
        parser.add_argument(
            "-p",
            "--put",
            action="store_true",
            default=False,
            help="Show puts instead of calls",
        )
        parser.add_argument(
            "-m",
            "--min",
            type=float,
            default=None,
            dest="mini",
            help="Minimum strike price shown",
        )
        parser.add_argument(
            "-M",
            "--max",
            type=float,
            default=None,
            dest="maxi",
            help="Maximum strike price shown",
        )
        parser.add_argument(
            "-r",
            "--risk",
            type=float,
            default=None,
            dest="risk",
            help="The risk-free rate to use",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.ticker:
                if self.selected_date:
                    if sum(self.prices["Chance"]) == 1:
                        yfinance_view.risk_neutral_vals(
                            self.ticker,
                            self.selected_date,
                            self.prices,
                            ns_parser.put,
                            ns_parser.mini,
                            ns_parser.maxi,
                            ns_parser.risk,
                        )
                    else:
                        console.print("Total chances must equal one\n")
                else:
                    console.print("No expiry loaded. First use `exp {expiry date}`\n")
            else:
                console.print("No ticker loaded. First use `load <ticker>`\n")
