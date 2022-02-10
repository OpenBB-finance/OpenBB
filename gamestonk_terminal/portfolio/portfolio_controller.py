"""Portfolio Controller"""
__docformat__ = "numpy"

import argparse
import os
from os import listdir
from os.path import isfile, join
from typing import List, Dict, Union

from prompt_toolkit.completion import NestedCompleter
import pandas as pd
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    valid_date,
    check_positive_float,
    check_positive,
    EXPORT_ONLY_FIGURES_ALLOWED,
    print_rich_table,
)
from gamestonk_terminal.menu import session

from gamestonk_terminal.portfolio.portfolio_optimization import po_controller
from gamestonk_terminal.portfolio import (
    portfolio_view,
    portfolio_model,
)
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

# pylint: disable=R1710,E1101,C0415

portfolios_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "portfolios")


class PortfolioController(BaseController):
    """Portfolio Controller class"""

    CHOICES_COMMANDS = [
        "load",
        "save",
        "init",
        "show",
        "add",
        "build",
        "ar",
        "rmr",
        "al",
        "dd",
        "rolling",
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

        self.portfolio_name = ""
        self.portlist: List[str] = os.listdir(portfolios_path)
        self.portfolio = portfolio_model.Portfolio()

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"] = {c: None for c in self.portlist}
            choices["save"] = {c: None for c in self.portlist}
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        # NOTE: See comment at `call_pa` definition
        # >   pa          portfolio analysis, \t\t analyse portfolios
        help_text = f"""[menu]
>   bro         brokers holdings, \t\t supports: robinhood, ally, degiro, coinbase
>   po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt[/menu]

[info]Portfolio:[/info][cmds]
    load        load data into the portfolio
    save        save your portfolio for future use
    show        show existing transactions
    add         add a security to your portfolio
    init        initialize empty portfolio
    build       build portfolio from list of tickers and weights[/cmds]
[info]
Loaded:[/info] {self.portfolio_name or None}

[info]Graphs:[/info][cmds]
    rolling     display rolling metrics of portfolio and benchmark
    rmr         graph your returns versus the market's returns
    dd          display portfolio drawdown
    al          display allocation to given assets over period[/cmds]
        """
        # TODO: Clean up the reports inputs
        # TODO: Edit the allocation to allow the different asset classes
        # [info]Reports:[/info]
        #    ar          annual report for performance of a given portfolio
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

    # BUG: The commands in pa menu throw errors. First one says that it's related to
    #      string formatting and the second one has something to do with None being used
    #      instead of [] in the queue (assumption) what throws errors on the logger.
    # TODO: This submenu is disabled until the bug is fixed.
    # def call_pa(self, _):
    #     """Process pa command"""
    #     from gamestonk_terminal.portfolio.portfolio_analysis import pa_controller
    #
    #     self.queue = self.queue = self.load_class(
    #         pa_controller.PortfolioAnalysis, self.queue
    #     )

    def call_init(self, other_args: List[str]):
        """Process reset command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="init",
            description="Re-initialize with empty portfolio.",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.portfolio = portfolio_model.Portfolio()
        console.print()

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
            self.portfolio = portfolio_model.Portfolio.from_csv(
                os.path.join(portfolios_path, ns_parser.name)
            )
            self.portfolio_name = ns_parser.name
            console.print()

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
                portfolio_model.save_df(self.portfolio.trades, ns_parser.name)
            else:
                console.print(
                    "Please submit as 'filename.filetype' with filetype being csv, xlsx, or json\n"
                )

    def call_show(self, _):
        """Process show command"""
        if self.portfolio.empty:
            console.print("[red]No portfolio loaded.[/red]\n")
            return
        print_rich_table(self.portfolio.trades, show_index=False)
        console.print()

    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="add",
            description="Adds an item to your portfolio",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        console.print()
        inputs: Dict[str, Union[str, float, int]] = {}
        type_ = input("Type (stock, cash): \n")
        if type_ not in ["stock", "cash"]:
            console.print("[red]Currently only stocks or cash supported.[/red]\n")
            type_ = input("Type (stock, cash): \n")
            if type_ not in ["stock", "cash"]:
                console.print("[red]Two unsuccessful attempts.  Exiting add.[/red]\n")
                return

        inputs["Type"] = type_.lower()
        action = input("Action: (buy, sell, deposit, withdraw): \n").lower()

        if type_ == "cash":
            if action not in ["deposit", "withdraw"]:
                console.print("Cash can only be deposit or withdraw\n")
                action = input("Action: (buy, sell, deposit, withdraw): \n").lower()
                if action not in ["deposit", "withdraw"]:
                    console.print(
                        "[red]Two unsuccessful attempts.  Exiting add.[/red]\n"
                    )
                    return

        elif type_ == "stock":
            if action not in ["buy", "sell"]:
                console.print("Stock can only be buy or sell\n")
                if action not in ["buy", "sell"]:
                    console.print(
                        "[red]Two unsuccessful attempts.  Exiting add.[/red]\n"
                    )
                    return

        inputs["Side"] = action.lower()
        inputs["Name"] = input("Name (ticker or cash [if depositing cash]):\n")
        inputs["Date"] = valid_date(input("Purchase date (YYYY-MM-DD): \n")).strftime(
            "%Y-%m-%d"
        )
        inputs["Quantity"] = float(input("Quantity: \n"))
        inputs["Price"] = float(input("Price per share: \n"))
        inputs["Fees"] = float(input("Fees: \n"))
        inputs["Premium"] = ""
        if self.portfolio.empty:
            self.portfolio = portfolio_model.Portfolio(
                pd.DataFrame.from_dict(inputs, orient="index").T
            )
            console.print(
                f"Portfolio successfully initiialized with {inputs['Name']}.\n"
            )
            return
        self.portfolio.add_trade(inputs)

        console.print(f"{inputs['Name']} successfully added\n")

    def call_build(self, other_args: List[str]):
        """Process build command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="build",
            description="Build portfolio from list of tickers and weights",
        )
        parser.add_argument(
            "-s",
            "--start",
            help="Start date.",
            dest="start",
            default="2021-01-04",
            type=valid_date,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-t",
            "--tickers",
            type=str,
            help="List of symbols separated by commas (i.e AAPL,BTC,DOGE,SPY....)",
            dest="tickers",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-c",
            "--class",
            help="Asset class (stock, crypto, etf), separated by commas.",
            dest="classes",
            type=str,
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-w",
            "--weights",
            help="List of weights, separated by comma",
            type=str,
            dest="weights",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-a",
            "--amount",
            help="Amount to allocate initially.",
            dest="amount",
            default=100_000,
            type=check_positive,
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            list_of_tickers = ns_parser.tickers.split(",")
            types = ns_parser.classes.split(",")
            weights = [float(w) for w in ns_parser.weights.split(",")]
            self.portfolio = portfolio_model.Portfolio.from_custom_inputs_and_weights(
                start_date=ns_parser.start.strftime("%Y-%m-%d"),
                list_of_symbols=list_of_tickers,
                list_of_weights=weights,
                list_of_types=types,
                amount=ns_parser.amount,
            )
        console.print()

    def call_al(self, other_args: List[str]):
        """Process al command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="al",
            description="Display allocation",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            portfolio_view.display_allocation(self.portfolio, ns_parser.export)
        console.print()

    # def call_ar(self, other_args: List[str]):
    #     """Process ar command"""
    #     parser = argparse.ArgumentParser(
    #         add_help=False,
    #         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    #         prog="ar",
    #         description="Create an annual report based on given portfolio",
    #     )
    #     parser.add_argument(
    #         "-m",
    #         "--market",
    #         type=str,
    #         dest="market",
    #         default="SPY",
    #         help="Choose a ticker to be the market asset",
    #     )
    #     ns_parser = parse_known_args_and_warn(parser, other_args)
    #     if ns_parser:
    #         if not self.portfolio.empty:
    #             self.portfolio.generate_holdings_from_trades()
    #             self.portfolio.add_benchmark(ns_parser.market)
    #             portfolio_view.Report(
    #                 val, hist, ns_parser.market, 365
    #             ).generate_report()
    #         else:
    #             console.print("Please add items to the portfolio\n")

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
                portfolio_view.display_returns_vs_bench(
                    self.portfolio, ns_parser.market
                )
            else:
                console.print("[red]No portfolio loaded.[/red]")
        console.print()

    def call_dd(self, other_args: List[str]):
        """Process dd command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dd",
            description="Show portfolio drawdown",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if not self.portfolio.empty:
                self.portfolio.generate_holdings_from_trades()
                self.portfolio.add_benchmark("SPY")
                portfolio_view.display_drawdown(self.portfolio.portfolio_value)
            else:
                console.print("[red]No portfolio loaded.\n[/red]")

    def call_rolling(self, other_args: List[str]):
        """Process rolling command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rolling",
            description="Show rolling portfolio metrics vs benchmark",
        )
        parser.add_argument(
            "-b",
            "--benchmark",
            type=str,
            dest="benchmark",
            default="SPY",
            help="Choose a ticker to be the benchmark",
        )
        parser.add_argument(
            "-l",
            "--length",
            type=check_positive,
            dest="length",
            default=60,
            help="Length of rolling window",
        )
        parser.add_argument(
            "-r",
            "--rf",
            type=check_positive_float,
            dest="rf",
            default=0.001,
            help="Set risk free rate for calculations.",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            if self.portfolio.empty:
                console.print("[red]No portfolio loaded[/red].\n")
                return
            portfolio_view.display_rolling_stats(
                self.portfolio,
                length=ns_parser.length,
                benchmark=ns_parser.benchmark,
                risk_free_rate=ns_parser.rf,
            )
        console.print()
