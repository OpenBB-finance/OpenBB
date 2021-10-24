"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime, timedelta, date
import math

from prompt_toolkit.completion import NestedCompleter
import pandas as pd

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio.brokers import bro_controller
from gamestonk_terminal.portfolio.portfolio_analysis import pa_controller
from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.portfolio import portfolio_view, portfolio_model, yfinance_model
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

# pylint: disable=R1710
# pylint: disable=E1101


class PortfolioController:
    """Portfolio Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
    ]

    CHOICES_MENUS = [
        "bro",
        "pa",
        "po",
        "load",
        "save",
        "show",
        "add",
        "rmv",
        "ar",
    ]

    CHOICES += CHOICES_MENUS

    def __init__(self):
        """Constructor"""
        self.port_parser = argparse.ArgumentParser(add_help=False, prog="portfolio")
        self.port_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer = NestedCompleter.from_nested_dict(
            {c: None for c in self.CHOICES}
        )
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

    def print_help(self):
        """Print help"""
        help_text = """
>> PORTFOLIO <<

What do you want to do?
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

>   bro         brokers holdings, \t\t supports: robinhood, alpaca, ally, degiro
>   pa          portfolio analysis, \t\t analyses your custom portfolio
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt

Portfolio:
    load        instructions on how to load data
    save        updated your csv portfolio
    show        show existing portfolio
    add         add a security to your portfolio
    rmv         remove a security from your portfolio

Reports:
    ar          annual report for performance of a given portfolio
        """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False, or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.port_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    # MENUS
    def call_bro(self, _):
        """Process bro command"""
        ret = bro_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_pa(self, _):
        """Process pa command"""
        ret = pa_controller.menu()
        if ret is False:
            self.print_help()
        else:
            return True

    def call_po(self, _):
        """Process po command"""
        ret = po_controller.menu([])
        if ret is False:
            self.print_help()
        else:
            return True

    def call_load(self, other_args: List[str]):
        """Process load command"""
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
            dest="name",
            required="-h" not in other_args,
            help="Name of file to be saved",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        try:
            self.portfolio = portfolio_model.load_df(ns_parser.name)
        except Exception as e:
            print(e, "\n")

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
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if (
            ".csv" not in ns_parser.name
            and ".xlsx" not in ns_parser.name
            and ".json" not in ns_parser.name
        ):
            print(
                "Please submit as 'filename.filetype' with filetype being csv, xlsx, or json\n"
            )

        try:
            portfolio_model.save_df(self.portfolio, ns_parser.name)
        except Exception as e:
            print(e, "\n")

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
            type=str,
            choices=["stock", "bond", "option", "crypto"],
            default="stock",
            help="Type of asset to add",
        )
        parser.add_argument(
            "-v",
            "--volume",
            dest="volume",
            type=float,
            default=1,
            help="Amounts of the asset owned",
        )
        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=str,
            default=datetime.now().strftime("%Y/%m/%d"),
            help="Date: yyyy/mm/dd",
        )
        parser.add_argument(
            "-p",
            "--price",
            dest="price",
            type=float,
            required="-h" not in other_args,
            help="Price purchased for asset",
        )
        parser.add_argument(
            "-f",
            "--fees",
            dest="fees",
            type=float,
            help="Fees paid for transaction",
        )
        parser.add_argument(
            "-r",
            "--premium",
            dest="premium",
            type=float,
            help="Premium paid/received for the option",
        )
        parser.add_argument(
            "--side",
            type=str,
            dest="side",
            choices=["buy", "sell", "interest"],
            default="buy",
            help="Choose to buy, sell, or record interest for an asset. Enter interest per item.",
        )
        if other_args:
            if "-n" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        data = {
            "Name": ns_parser.name,
            "Type": ns_parser.type,
            "Volume": ns_parser.volume,
            "Date": ns_parser.date.replace("_", " "),
            "Price": ns_parser.price,
            "Fees": ns_parser.fees,
            "Premium": ns_parser.premium,
            "Side": ns_parser.side,
        }
        self.portfolio = self.portfolio.append([data])
        self.portfolio.index = list(range(0, len(self.portfolio.values)))
        print(f"{ns_parser.name.upper()} successfully added\n")

    def call_rmv(self, _):
        """Process rmv command"""
        portfolio_view.show_df(self.portfolio, True)
        to_rmv = int(input("\nType the index number you want to remove:\n"))
        if 0 <= to_rmv < len(self.portfolio.index):
            self.portfolio = self.portfolio.drop(self.portfolio.index[to_rmv])
            self.portfolio.index = list(range(0, len(self.portfolio.values)))
        else:
            print(
                f"Invalid index please use an integer between 0 and {len(self.portfolio.index)-1}\n"
            )

    def call_ar(self, _):
        """Process ar command"""
        try:
            val = self.generate_performance()
            portfolio_view.annual_report(val)
        except Exception as e:
            print(e, "\n")

    def generate_performance(self) -> pd.DataFrame:
        """Creates a new df with performance results"""
        changes = self.portfolio.copy()
        # Transactions sorted for only stocks
        changes = changes[changes["Type"] == "stock"]
        uniques = list(set(changes["Name"].tolist()))
        # Stock price history for each stock
        hist = yfinance_model.get_stocks(uniques)
        # Dividends for each stock
        divs = yfinance_model.get_dividends(uniques)
        divs = divs.fillna(0)
        mini = min(changes["Date"])
        days = pd.date_range(mini, date.today() - timedelta(days=1), freq="d")
        zeros = [0 for _ in uniques]
        data = [zeros + zeros + zeros + [0] for _ in days]
        vals = ["Quantity", "Cost Basis", "Profit"]
        arrays = [[x for _ in uniques for x in vals] + ["Cash"], uniques * 3 + ["Cash"]]
        tuples = list(zip(*arrays))
        headers = pd.MultiIndex.from_tuples(tuples, names=["first", "second"])
        log = pd.DataFrame(data, columns=headers, index=days)

        for index, _ in log.iterrows():
            values = changes[changes["Date"] == index]
            if len(values.index) > 0:
                for _, sub_row in values.iterrows():
                    ticker = sub_row["Name"]
                    quantity = sub_row["Quantity"]
                    price = sub_row["Price"]
                    fees = sub_row["Fees"]
                    if math.isnan(fees):
                        fees = 0
                    sign = -1 if sub_row["Side"].lower() == "sell" else 1
                    pos1 = log.cumsum().at[index, ("Quantity", ticker)] > 0
                    pos2 = (quantity * sign) > 0

                    if sub_row["Side"].lower() == "interest":
                        log.at[index, ("Cost Basis", ticker)] = (
                            log.at[index, ("Cost Basis", ticker)] + quantity * price
                        )
                        print(-(quantity * price))
                        log.at[index, ("Cash", "Cash")] = log.at[
                            index, ("Cash", "Cash")
                        ] - (quantity * price)

                    elif (
                        pos1 == pos2
                        or log.cumsum().at[index, ("Quantity", ticker)] == 0
                        or (quantity * sign) == 0
                    ):
                        log.at[index, ("Quantity", ticker)] = (
                            log.at[index, ("Quantity", ticker)] + quantity * sign
                        )
                        log.at[index, ("Cost Basis", ticker)] = (
                            log.at[index, ("Cost Basis", ticker)]
                            + fees
                            + quantity * sign * price
                        )
                        print(-(fees + quantity * sign * price))
                        log.at[index, ("Cash", "Cash")] = log.at[
                            index, ("Cash", "Cash")
                        ] - (fees + quantity * sign * price)
                    else:
                        rev = (
                            log.at[index, ("Profit", ticker)]
                            + quantity * sign * price * -1
                        )
                        wa_cost = (
                            quantity / log.cumsum().at[index, ("Quantity", ticker)]
                        ) * log.cumsum().at[index, ("Cost Basis", ticker)]
                        log.at[index, ("Profit", ticker)] = rev - wa_cost - fees
                        print(rev - fees)
                        log.at[index, ("Cash", "Cash")] = (
                            log.at[index, ("Cash", "Cash")] + rev - fees
                        )
                        log.at[index, ("Quantity", ticker)] = (
                            log.at[index, ("Quantity", ticker)] + quantity * sign
                        )
                        log.at[index, ("Cost Basis", ticker)] = (
                            log.at[index, ("Cost Basis", ticker)] - wa_cost
                        )

        log[("Cash", "Cash")] = log[("Cash", "Cash")].cumsum()

        comb = pd.merge(log, hist, how="left", left_index=True, right_index=True)
        comb = comb.fillna(method="ffill")
        comb = pd.merge(comb, divs, how="left", left_index=True, right_index=True)
        comb = comb.fillna(0)

        for uni in uniques:
            comb[("Quantity", uni)] = comb[("Quantity", uni)].cumsum()
            comb[("Cost Basis", uni)] = comb[("Cost Basis", uni)].cumsum()
            comb[("Cash", "Cash")] = comb[("Cash", "Cash")] + (
                comb[("Quantity", uni)] * comb[("Dividend", uni)]
            )
            comb[("Holding", uni)] = comb[("Quantity", uni)] * comb[("Close", uni)]
            comb[("Profit", uni)] = comb[("Profit", uni)].cumsum()

        comb["holdings"] = comb.sum(level=0, axis=1)["Holding"]
        comb["profits"] = comb.sum(level=0, axis=1)["Profit"]
        comb["total_prof"] = comb["holdings"] + comb["profits"]
        comb["total_cost"] = comb.sum(level=0, axis=1)["Cost Basis"]
        return comb


def menu():
    """Portfolio Menu"""
    portfolio_controller = PortfolioController()
    portfolio_controller.call_help(None)
    while True:
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in portfolio_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (portfolio)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (portfolio)> ")

        try:
            process_input = portfolio_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exit\n")
            continue
