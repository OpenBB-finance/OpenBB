"""Research Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib
import webbrowser
from typing import List, Union
from datetime import datetime
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair, system_clear, try_except
from gamestonk_terminal.menu import session


class ResearchController:
    """Research Controller class"""

    CHOICES = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
    ]
    CHOICES_COMMANDS = [
        "macroaxis",
        "yahoo",
        "finviz",
        "marketwatch",
        "fool",
        "businessinsider",
        "fmp",
        "fidelity",
        "tradingview",
        "marketchameleon",
        "stockrow",
        "barchart",
        "grufity",
        "fintel",
        "zacks",
        "macrotrends",
        "newsfilter",
        "stockanalysis",
    ]
    CHOICES += CHOICES_COMMANDS

    def __init__(
        self, ticker: str, start: datetime, interval: str, queue: List[str] = None
    ):
        """Constructor"""
        self.res_parser = argparse.ArgumentParser(add_help=False, prog="res")
        self.res_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:

            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.ticker = ticker
        self.start = start
        self.interval = interval

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = f"""
Ticker: {self.ticker}

    macroaxis            www.macroaxis.com
    yahoo                www.finance.yahoo.com
    finviz               www.finviz.com
    marketwatch          www.marketwatch.com
    fool                 www.fool.com
    businessinsider      www.markets.businessinsider.com
    fmp                  www.financialmodelingprep.com
    fidelity             www.eresearch.fidelity.com
    tradingview          www.tradingview.com
    marketchameleon      www.marketchameleon.com
    stockrow             www.stockrow.com
    barchart             www.barchart.com
    grufity              www.grufity.com
    fintel               www.fintel.com
    zacks                www.zacks.com
    macrotrends          www.macrotrends.net
    newsfilter           www.newsfilter.io
    stockanalysis        www.stockanalysis.com
"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Parameters
        -------
        an_input : str
            string with input arguments

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """

        # Empty command
        if not an_input:
            print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.res_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "res")
        if self.ticker:
            self.queue.insert(0, f"load {self.ticker}")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_macroaxis(self, _):
        """Process macroaxis command"""
        webbrowser.open(f"https://www.macroaxis.com/invest/market/{self.ticker}")
        print("")

    @try_except
    def call_yahoo(self, _):
        """Process yahoo command"""
        webbrowser.open(f"https://finance.yahoo.com/quote/{self.ticker}")
        print("")

    @try_except
    def call_finviz(self, _):
        """Process finviz command"""
        webbrowser.open(f"https://finviz.com/quote.ashx?t={self.ticker}")
        print("")

    @try_except
    def call_marketwatch(self, _):
        """Process marketwatch command"""
        webbrowser.open(f"https://www.marketwatch.com/investing/stock/{self.ticker}")
        print("")

    @try_except
    def call_fool(self, _):
        """Process fool command"""
        webbrowser.open(f"https://www.fool.com/quote/{self.ticker}")
        print("")

    @try_except
    def call_businessinsider(self, _):
        """Process businessinsider command"""
        webbrowser.open(
            f"https://markets.businessinsider.com/stocks/{self.ticker}-stock/"
        )
        print("")

    @try_except
    def call_fmp(self, _):
        """Process fmp command"""
        webbrowser.open(
            f"https://financialmodelingprep.com/financial-summary/{self.ticker}"
        )
        print("")

    @try_except
    def call_fidelity(self, _):
        """Process fidelity command"""
        webbrowser.open(
            f"https://eresearch.fidelity.com/eresearch/goto/evaluate/snapshot.jhtml?symbols={self.ticker}"
        )
        print("")

    @try_except
    def call_tradingview(self, _):
        """Process tradingview command"""
        webbrowser.open(f"https://www.tradingview.com/symbols/{self.ticker}")
        print("")

    @try_except
    def call_marketchameleon(self, _):
        """Process marketchameleon command"""
        webbrowser.open(f"https://marketchameleon.com/Overview/{self.ticker}")
        print("")

    @try_except
    def call_stockrow(self, _):
        """Process stockrow command"""
        webbrowser.open(f"https://stockrow.com/{self.ticker}")
        print("")

    @try_except
    def call_barchart(self, _):
        """Process barchart command"""
        webbrowser.open(
            f"https://www.barchart.com/stocks/quotes/{self.ticker}/overview"
        )
        print("")

    @try_except
    def call_grufity(self, _):
        """Process grufity command"""
        webbrowser.open(f"https://grufity.com/stock/{self.ticker}")
        print("")

    @try_except
    def call_fintel(self, _):
        """Process fintel command"""
        webbrowser.open(f"https://fintel.io/s/us/{self.ticker}")
        print("")

    @try_except
    def call_zacks(self, _):
        """Process zacks command"""
        webbrowser.open(f"https://www.zacks.com/stock/quote/{self.ticker}")
        print("")

    @try_except
    def call_macrotrends(self, _):
        """Process macrotrends command"""
        webbrowser.open(
            f"https://www.macrotrends.net/stocks/charts/{self.ticker}/{self.ticker}/market-cap"
        )
        print("")

    @try_except
    def call_newsfilter(self, _):
        """Process newsfilter command"""
        webbrowser.open(f"https://newsfilter.io/search?query={self.ticker}")
        print("")

    @try_except
    def call_stockanalysis(self, _):
        """Process stockanalysis command"""
        webbrowser.open(f"https://stockanalysis.com/stocks/{self.ticker}/")
        print("")


def menu(ticker: str, start: datetime, interval: str, queue: List[str] = None):
    """Research Menu"""
    res_controller = ResearchController(ticker, start, interval, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if res_controller.queue and len(res_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if res_controller.queue[0] in ("q", "..", "quit"):
                if len(res_controller.queue) > 1:
                    return res_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = res_controller.queue[0]
            res_controller.queue = res_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in res_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/res/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                res_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and res_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /stocks/res/ $ ",
                        completer=res_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/res/ $ ")

        try:
            # Process the input command
            res_controller.queue = res_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/res menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                res_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        res_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                res_controller.queue.insert(0, an_input)
            else:
                print("\n")
