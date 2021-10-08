""" Payoff Controller Module """
__docformat__ = "numpy"

import argparse
import os
from typing import List
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.options.yfinance_model import get_option_chain


class Payoff:

    CHOICES = ["cls", "?", "help", "q", "quit", "list"]
    CHOICES_COMMANDS = [
        "select",
        "add",
        "rmv",
        "long",
        "short",
        "none",
        "plot",
    ]
    CHOICES += CHOICES_COMMANDS

    # pylint: disable=dangerous-default-value
    def __init__(self, ticker: str, expiration: str):
        """Construct Payoff"""

        self.po_parser = argparse.ArgumentParser(add_help=False, prog="po")
        self.po_parser.add_argument("cmd", choices=self.CHOICES)
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
        self.expiration = expiration
        self.options: List[dict[str, str]] = []
        self.underlying = 0

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """
>>OPTION PAYOFF DIAGRAM<<

What would you like to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program
    list          list available strike prices for calls and puts

Options:
    add           add tickers to the list of the tickers to be optimized
    rmv           remove tickers from the list of the tickers to be optimized

Underlying Asset:
    long          long the underlying asset
    short         short the underlying asset
    none          do not hold the underlying asset

Show:
    plot          show the efficient frontier
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

        (known_args, other_args) = self.po_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_list(self, _):
        """Lists available calls and puts"""
        length = max(len(self.calls), len(self.puts)) - 1
        print("#\tcall\tput")
        for i in range(length):
            call = self.calls[i][0] if i < len(self.calls) else "NA"
            put = self.puts[i][0] if i < len(self.puts) else "NA"
            print(f"{i}\t{call}\t{put}")

    def call_add(self, other_args: List[str]):
        """Process add command"""
        self.add_option(other_args)

    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        self.rmv_option(other_args)

    def call_long(self):
        """Process call command"""
        self.underlying = 1
        self.show_setup(True)

    def call_short(self):
        """Process short command"""
        self.underlying = -1
        self.show_setup(True)

    def call_none(self):
        """Process none command"""
        self.underlying = 0
        self.show_setup(True)

    def call_plot(self, other_args):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="""This function plots random portfolios based
                        on their risk and returns and shows the efficient frontier.""",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            print("Graph should show")

        except Exception as e:
            print(e, "\n")

    def show_setup(self, nl: bool = False):
        if self.underlying == -1:
            text = "Shorting"
        elif self.underlying == 0:
            text = "Not holding"
        else:
            text = "Longing"
        print(f"{text} the underlying asset")
        print("#\tType\tHold\tStrike\tCost")
        for i, o in enumerate(self.options):
            sign = "Long" if o["sign"] == 1 else "Short"
            print(f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['cost']}")
        if nl:
            print("")

    def add_option(self, other_args: List[str]):
        """Add an option to the diagram"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add/select",
            description="""Add/Select tickers for portfolio to be optimized.""",
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
            "-k",
            "--strike",
            dest="strike",
            type=int,
            help="strike price for option",
            required=True,
        )
        try:

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            opt_type = "put" if ns_parser.put else "call"
            sign = -1 if ns_parser.short else 1
            if ns_parser.put:
                strike = self.puts[ns_parser.strike][0]
                cost = self.puts[ns_parser.strike][1]
            else:
                strike = self.calls[ns_parser.strike][0]
                cost = self.calls[ns_parser.strike][1]

            option = {"type": opt_type, "sign": sign, "strike": strike, "cost": cost}
            self.options.append(option)
            self.show_setup(True)

        except Exception as e:
            print(e, "\n")

    def rmv_option(self, other_args: List[str]):
        """Remove one of the options from the diagram"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="""Remove one of the options to be shown in the payoff.""",
        )

        parser.add_argument(
            "-k",
            "--strike",
            dest="strike",
            type=int,
            help="strike price for option",
            required=True,
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-k")
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            del self.options[ns_parser.strike]
            self.show_setup(True)

        except Exception as e:
            print(e, "\n")


def menu(ticker: str, expiration: str):
    """Portfolio Optimization Menu"""
    plt.close("all")
    po_controller = Payoff(ticker, expiration)
    po_controller.call_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in po_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (options)>(payoff)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (options)>(payoff)> ")

        try:
            plt.close("all")

            process_input = po_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue


# pylint: disable=W0105
"""
type portItem = {
  id: number,
  type: "stock" | "call" | "put",
  sign: -1 | 0 | 1,
  strike: number,
  cost: number
}

  dataFunction(base: number, price: number) {
      var main = this.props.portfolio.find(item => item.id == 1);
      var optionsChange: number = 0;
      var change: number = price - base;
      this.props.portfolio.filter(item => item.id != 1).forEach(item => {
        if (item.type == "call") {
          let absChange: number = price > item.strike ? price - item.strike : 0;
          optionsChange += item.sign * absChange;
        } else if (item.type == "put") {
          let absChange: number = price < item.strike ? item.strike - price : 0;
          optionsChange += item.sign * absChange;
        }
      })
      return  (change * main.sign) + optionsChange;
    }

    getXValues() {
      var xList: number[] = Array.from(Array(101).keys())
      var min: number = this.props.data.price;
      var max: number = this.props.data.price;
      if (this.props.portfolio.length == 1) {
        min *= 0.5;
        max *= 1.5;
      } else if (this.props.portfolio.length > 1) {
        this.props.portfolio.forEach(item => {
          if (item.strike > max) {
            max = item.strike;
          }
          if (item.strike < min) {
            min = item.strike;
          }
          min *= 0.8;
          max *= 1.2;
        })
      }
      var range: number = max - min;
      return xList.map(item => min + ((item/100)*range));

     generateData() {
        var xVals: number[] = this.getXValues();
        var base: number = this.props.data.price;
        var totalCost: number = 0;
        this.props.portfolio.forEach(item => {
          totalCost += item.cost
        })
        var beforeFees = [];
        var afterFees = [];
        xVals.forEach(item => {
          beforeFees.push({"x" : item, "y": this.dataFunction(base, item)});
          if (totalCost != 0) {
            afterFees.push({"x" : item, "y": this.dataFunction(base, item) - totalCost});
          }
        })
        var returnDict = [{id: "Before Costs", data: beforeFees},]
        if (totalCost != 0){returnDict.push({id: "After Costs", data: afterFees})}
        return returnDict;
    }
"""
