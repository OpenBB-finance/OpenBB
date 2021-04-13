"""Portfolio Optimization Controller Module"""
__docformat__ = "numpy"


import argparse
from typing import List
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio_optimization import port_opt_api as po_api
from gamestonk_terminal.portfolio_optimization.port_opt_helper import display_weights


class PortfolioOptimization:

    CHOICES = [
        "help",
        "q",
        "quit",
        "select",
        "add",
        "equal_weight",
        "mkt_cap",
        "div_yield",
        "max_sharpe",
        "min_vol",
        "eff_risk",
        "eff_ret",
        "show_ef",
        "yolo",
    ]

    def __init__(self, tickers: List[str] = []):
        """
        Construct Portfolio Optimization
        """

        self.po_parser = argparse.ArgumentParser(add_help=False, prog="po")
        self.po_parser.add_argument("cmd", choices=self.CHOICES)
        self.tickers = list(set(tickers))
        # These will allow the ca menu to be re-access
        self.ca_ticker = None
        self.ca_similar = None

    @staticmethod
    def print_help(tickers: List[str]):
        """Print help"""
        print("\nPortfolio Optimization:")
        print("   help          show this menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print(f"\nCurrent Tickers: {('None', ', '.join(tickers))[bool(tickers)]}")
        print("")
        print("   add          add ticker to optimize")
        print("   select       overwrite current tickers with new tickers")
        print("")
        print("Optimization:")
        print("")
        print("   equal_weight   equally weighted portfolio")
        print("   mkt_cap        marketcap weighted portfolio")
        print("   div_yield      dividend weighted portfolio")
        print("   max_sharpe     portfolio with maximum sharpe ratio")
        print("   min_vol        portfolio with minimum volatility")
        print("   eff_risk       portfolio that maximizes returns at given risk")
        print("   eff_ret        portfolio that minimizes risk at given return")
        print("   show_ef        show the efficient frontier")
        print("")
        plt.close("all")

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """
        (known_args, other_args) = self.po_parser.parse_known_args(an_input.split())

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help(self.tickers)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_add(self, other_args: List[str]):
        self.add_stocks(self, other_args)

    def call_select(self, other_args: List[str]):
        self.tickers = []
        self.add_stocks(self, other_args)

    def call_equal_weight(self, other_args: List[str]):
        weights = po_api.equal_weight(self.tickers, other_args)
        print("Optimal Weights for Equal Weighting:")
        display_weights(weights)
        print("")

    def call_mkt_cap(self, other_args: List[str]):
        weights = po_api.property_weighting(self.tickers, "marketCap", other_args)
        print("Market Cap Weighting Weights:")
        display_weights(weights)
        print("")

    def call_div_yield(self, other_args: List[str]):
        weights = po_api.property_weighting(self.tickers, "dividendYield", other_args)
        print("Dividend Weighed Weights:")
        display_weights(weights)
        print("")

    def call_max_sharpe(self, other_args: List[str]):
        weights = po_api.ef_portfolio(self.tickers, "max_sharpe", other_args)
        print("Maximum Sharpe Weights:")
        display_weights(weights)
        print("")

    def call_min_vol(self, other_args: List[str]):
        weights = po_api.ef_portfolio(self.tickers, "min_volatility", other_args)
        print("Minimum volatility Weights:")
        display_weights(weights)
        print("")

    def call_eff_risk(self, other_args: List[str]):
        weights = po_api.ef_portfolio(self.tickers, "eff_risk", other_args)
        print("Weights for max returns at risk level")
        display_weights(weights)
        print("")

    def call_eff_ret(self, other_args: List[str]):
        weights = po_api.ef_portfolio(self.tickers, "eff_ret", other_args)
        print("Weights for min risk at target returns")
        display_weights(weights)
        print("")

    def call_show_ef(self, other_args):
        po_api.show_ef(self.tickers, other_args)
        print("")

    def call_yolo(self, _):
        # Easter egg :)
        print("DFV YOLO")
        print({"GME": 200})
        print("")

    @staticmethod
    def add_stocks(self, other_args: List[str]):
        """ Add ticker to current list for optimization"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add",
            description="""Add tickers for optimizing.""",
        )
        parser.add_argument(
            "-t",
            "--tickers",
            dest="add_tickers",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="add tickers to optimzation.",
        )
        try:

            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-t")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return
            tickers = set(self.tickers)
            for ticker in ns_parser.add_tickers:
                tickers.add(ticker)
            self.tickers = list(tickers)

            print(
                f"\nCurrent Tickers: {('None', ', '.join(self.tickers))[bool(self.tickers)]}"
            )
            print("")
        except Exception as e:
            print(e)

        print("")


def menu(tickers: List[str]):
    """Portfolio Optimization Menu"""
    if tickers == [""]:
        tickers = []
    po_controller = PortfolioOptimization(tickers)
    po_controller.call_help(tickers)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in po_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (po)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (po)> ")

        try:
            process_input = po_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
