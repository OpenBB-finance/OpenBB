"""Cryptocurrency Due diligence Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import os
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.due_diligence import (
    pycoingecko_view,
    coinpaprika_view,
    binance_view,
)


class DueDiligenceController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "chart",
    ]

    SPECIFIC_CHOICES = {
        "cp": [
            "events",
            "twitter",
            "ex",
            "mkt",
            "ps",
            "basic",
        ],
        "cg": [
            "info",
            "market",
            "ath",
            "atl",
            "score",
            "web",
            "social",
            "bc",
            "dev",
        ],
        "bin": [
            "book",
            "balance",
        ],
    }

    DD_VIEWS_MAPPING = {
        "cg": pycoingecko_view,
        "cp": coinpaprika_view,
        "bin": binance_view,
    }

    def __init__(self, coin=None, source=None):
        """CONSTRUCTOR"""

        self._dd_parser = argparse.ArgumentParser(add_help=False, prog="dd")

        self.current_coin = coin
        self.current_currency = None
        self.current_df = pd.DataFrame()
        self.source = source

        self.CHOICES.extend(self.SPECIFIC_CHOICES[self.source])

        self._dd_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Due Diligence:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program
"""
        if self.source == "cp":
            help_text += """
CoinPaprika:
   basic           basic information about loaded coin
   ps              price and supply related metrics for loaded coin
   mkt             all markets for loaded coin
   ex              all exchanges where loaded coin is listed
   twitter         tweets for loaded coin
   events          events related to loaded coin
"""
        if self.source == "cg":
            help_text += """
CoinGecko:
   info            basic information about loaded coin
   market          market stats about loaded coin
   ath             all time high related stats for loaded coin
   atl             all time low related stats for loaded coin
   web             found websites for loaded coin e.g forum, homepage
   social          social portals urls for loaded coin, e.g reddit, twitter
   score           different kind of scores for loaded coin, e.g developer score, sentiment score
   dev             github, bitbucket coin development statistics
   bc              links to blockchain explorers for loaded coin
"""
        if self.source == "bin":
            help_text += """
Binance:
   book            show order book
   balance         show coin balance
"""

        help_text += "   chart           display chart\n"
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

        (known_args, other_args) = self._dd_parser.parse_known_args(an_input.split())

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

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu."""
        print("Moving back to (crypto) menu")
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    def call_info(self, other_args):
        """Process info command"""
        if self.current_coin:
            pycoingecko_view.info(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_market(self, other_args):
        """Process market command"""
        if self.current_coin:
            pycoingecko_view.market(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_web(self, other_args):
        """Process web command"""
        if self.current_coin:
            pycoingecko_view.web(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_social(self, other_args):
        """Process social command"""
        if self.current_coin:
            pycoingecko_view.social(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_dev(self, other_args):
        """Process dev command"""
        if self.current_coin:
            pycoingecko_view.dev(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_ath(self, other_args):
        """Process ath command"""
        if self.current_coin:
            pycoingecko_view.ath(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_atl(self, other_args):
        """Process atl command"""
        if self.current_coin:
            pycoingecko_view.atl(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_score(self, other_args):
        """Process score command"""
        if self.current_coin:
            pycoingecko_view.score(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_bc(self, other_args):
        """Process bc command"""
        if self.current_coin:
            pycoingecko_view.bc(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    # binance
    def call_book(self, other_args):
        """Process book command"""
        binance_view.order_book(other_args, self.current_coin)

    def call_balance(self, other_args):
        """Process balance command"""
        binance_view.balance(other_args, self.current_coin)

    def call_chart(self, other_args):
        """Process chart command"""
        getattr(self.DD_VIEWS_MAPPING[self.source], "chart")(
            self.current_coin, other_args
        )

    # paprika
    def call_ps(self, other_args):
        """Process ps command"""
        if self.current_coin:
            coinpaprika_view.price_supply(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_basic(self, other_args):
        """Process basic command"""
        if self.current_coin:
            coinpaprika_view.basic(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_mkt(self, other_args):
        """Process mkt command"""
        if self.current_coin:
            coinpaprika_view.markets(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_ex(self, other_args):
        """Process ex command"""
        if self.current_coin:
            coinpaprika_view.exchanges(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_events(self, other_args):
        """Process events command"""
        if self.current_coin:
            coinpaprika_view.events(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_twitter(self, other_args):
        """Process twitter command"""
        if self.current_coin:
            coinpaprika_view.twitter(self.current_coin, other_args)
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )


def menu(coin=None, source=None):

    source = source if source else "cg"
    dd_controller = DueDiligenceController(coin=coin, source=source)
    dd_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in dd_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(dd)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(dd)> ")

        try:
            process_input = dd_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
