"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import os
from os import listdir
from os.path import isfile, join
from typing import List
from datetime import datetime

from prompt_toolkit.completion import NestedCompleter
import pandas as pd
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    valid_date,
    check_positive_float,
    check_positive,
)
from gamestonk_terminal.menu import session

from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.portfolio import (
    portfolio_view,
    portfolio_model,
    yfinance_model,
    portfolio_helper,
)
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

# pylint: disable=R1710,E1101,C0415


class PortfolioController(BaseController):
    """Portfolio Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "save",
        "show",
        "add",
        "rmv",
        "ar",
        "rmr",
        "al",
    ]
    CHOICES_MENUS = [
        "bro",
        "po",
        "pa",
    ]
    PATH = "/portfolio/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.portfolio = pd.DataFrame(
            columns=[
                "Name",
                "Type",
                "Quantity",
                "Date",
                "Price",
                "Fees",
                "Premium",
                "Side",
            ]
        )

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[menu]
>   bro         brokers holdings, \t\t supports: robinhood, ally, degiro, coinbase
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt
>   pa          portfolio analysis, \t\t analyse portfolios[/menu]

[info]Portfolio:[/info][cmds]
    load        load data into the portfolio
    save        save your portfolio for future use
    show        show existing transactions
    add         add a security to your portfolio
    rmv         remove a security from your portfolio[/cmds]

[info]Reports:[/info][cmds]
    ar          annual report for performance of a given portfolio

[info]Graphs:[/info][cmds]
    rmr         graph your returns versus the market's returns
    al          displays the allocation of the portfolio
        """
        console.print(text=help_text, menu="Portfolio")

    def call_bro(self, _):
        """Process bro command"""
        from gamestonk_terminal.portfolio.brokers.bro_controller import (
            BrokersController,
        )

        self.queue = self.load_class(BrokersController, self.queue)

    def call_po(self, _):
        """Process po command"""
        self.queue = self.load_class(
            po_controller.PortfolioOptimization, [], self.queue
        )

    def call_pa(self, _):
        """Process pa command"""
        from gamestonk_terminal.portfolio.portfolio_analysis import pa_controller

        self.queue = self.queue = self.load_class(
            pa_controller.PortfolioAnalysis, self.queue
        )

    def call_load(self, other_args: List[str]):
        """Process load command"""
        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(path, "portfolios"))
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            choices=[f for f in listdir(path) if isfile(join(path, f))],
            dest="name",
            required="-h" not in other_args,
            help="Name of file to be saved",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.portfolio = portfolio_model.load_df(ns_parser.name)
            console.print("")

    def call_save(self, other_args: List[str]):
        """Process save command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="save",
            description="Save your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            required="-h" not in other_args,
            help="Name of file to be saved",
        )
        if other_args and "-n" not in other_args and "-h" not in other_args:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if (
                ".csv" in ns_parser.name
                or ".xlsx" in ns_parser.name
                or ".json" in ns_parser.name
            ):
                portfolio_model.save_df(self.portfolio, ns_parser.name)
            else:
                console.print(
                    "Please submit as 'filename.filetype' with filetype being csv, xlsx, or json\n"
                )

    def call_show(self, _):
        """Process show command"""
        portfolio_view.show_df(self.portfolio, False)

    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="Adds an item to your portfolio",
        )
        parser.add_argument(
            "-n",
            "--name",
            type=str,
            dest="name",
            required="-h" not in other_args,
            help="Name of item to be added (for example a ticker for a stock)",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            type=lambda s: s.lower(),
            choices=["stock", "cash", "etf"],  # "bond", "option", "crypto",
            default="stock",
            help="Type of asset to add",
        )
        parser.add_argument(
            "-q",
            "--quantity",
            dest="quantity",
            type=check_positive_float,
            default=1,
            help="Amounts of the asset owned",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=valid_date,
            default=datetime.now(),
            help="Date: yyyy/mm/dd",
        )
        parser.add_argument(
            "-p",
            "--price",
            dest="price",
            type=check_positive_float,
            required="-h" not in other_args,
            help="Price purchased for asset",
        )
        parser.add_argument(
            "-f",
            "--fees",
            dest="fees",
            type=check_positive_float,
            help="Fees paid for transaction",
        )

        parser.add_argument(
            "-a",
            "--action",
            type=lambda s: s.lower(),
            dest="action",
            choices=["buy", "sell", "interest", "deposit", "withdrawal"],
            default="deposit" if "cash" in other_args else "buy",
            help="Select what you did in the transaction",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if ns_parser.type == "cash" and ns_parser.action not in [
            "deposit",
            "withdrawal",
        ]:
            console.print("Cash can only be deposited or withdrew\n")
            return
        if ns_parser.type != "cash" and ns_parser.action in ["deposit", "withdrawal"]:
            console.print("Only cash can be deposited or withdrew\n")
            return

        if ns_parser.type == "stock":
            if not portfolio_helper.is_ticker(ns_parser.name):
                console.print("Invalid ticker\n")
                return

        data = {
            "Name": ns_parser.name,
            "Type": ns_parser.type,
            "Quantity": ns_parser.quantity,
            "Date": ns_parser.date,
            "Price": ns_parser.price,
            "Fees": ns_parser.fees,
            "Premium": None,  # ns_parser.premium
            "Side": ns_parser.action,
        }
        self.portfolio = self.portfolio.append([data])
        self.portfolio.index = list(range(0, len(self.portfolio.values)))
        console.print(f"{ns_parser.name.upper()} successfully added\n")

    def call_rmv(self, _):
        """Process rmv command"""
        portfolio_view.show_df(self.portfolio, True)
        to_rmv = int(input("\nType the index number you want to remove:\n"))
        if 0 <= to_rmv < len(self.portfolio.index):
            self.portfolio = self.portfolio.drop(self.portfolio.index[to_rmv])
            self.portfolio.index = list(range(0, len(self.portfolio.values)))
        else:
            console.print(
                f"Invalid index please use an integer between 0 and {len(self.portfolio.index)-1}\n"
            )

    def call_ar(self, other_args: List[str]):
        """Process ar command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ar",
            description="Create an annual report based on given portfolio",
        )
        parser.add_argument(
            "-m",
            "--market",
            type=str,
            dest="market",
            default="SPY",
            help="Choose a ticker to be the market asset",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.portfolio.empty:
                val, hist = portfolio_model.convert_df(self.portfolio)
                if not val.empty:
                    portfolio_view.Report(
                        val, hist, ns_parser.market, 365
                    ).generate_report()
                else:
                    console.print("Cannot generate a graph from an empty dataframe\n")
            else:
                console.print("Please add items to the portfolio\n")

    def call_rmr(self, other_args: List[str]):
        """Process rmr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rmr",
            description="Graph of portfolio returns versus market returns",
        )
        parser.add_argument(
            "-m",
            "--market",
            type=str,
            dest="market",
            default="SPY",
            help="Choose a ticker to be the market asset",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.portfolio.empty:
                val, _ = portfolio_model.convert_df(self.portfolio)
                if not val.empty:
                    df_m = yfinance_model.get_market(val.index[0], ns_parser.market)
                    returns, _ = portfolio_model.get_return(val, df_m, 365)
                    portfolio_view.plot_overall_return(returns, ns_parser.market, True)
                else:
                    console.print("Cannot generate a graph from an empty dataframe\n")
            else:
                console.print("Please add items to the portfolio\n")

    def call_al(self, other_args: List[str]):
        """Process al command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="al",
            description="Gives allocation",
        )
        parser.add_argument(
            "-l",
            "--limit",
            help="Number to show",
            type=check_positive,
            default=20,
            dest="limit",
        )
        parser.add_argument(
            "-n",
            "--noetf",
            action="store_true",
            default=False,
            dest="no_etf_positions",
            help="If etf positions should not be added to the portfolio",
        )
        parser.add_argument(
            "-g",
            "--graph",
            action="store_true",
            default=False,
            dest="graph",
            help="Display table or pi chart of holdings",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not self.portfolio.empty:
            val, hist = portfolio_model.convert_df(self.portfolio)
            if not val.empty:
                df = portfolio_model.get_allocation(
                    val,
                    hist,
                    self.portfolio,
                    ns_parser.limit,
                    ns_parser.no_etf_positions,
                )
                portfolio_view.display_allocation(df, ns_parser.graph)
            else:
                console.print("Cannot generate a graph from an empty dataframe\n")
        else:
            console.print("Please add items to the portfolio\n")
