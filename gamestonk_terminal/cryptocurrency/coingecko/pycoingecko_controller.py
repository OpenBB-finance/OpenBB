"""Cryptocurrency Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, W0622
import argparse
import os
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.coingecko import pycoingecko_view
from gamestonk_terminal.technical_analysis import ta_controller


class GeckoController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
        "global",
        "find",
        "coins",
        "defi",
        "news",
        "trending",
        "most_voted",
        "most_visited",
        "top_volume",
        "recently",
        "sentiment",
        "gainers",
        "losers",
        "stables",
        "yfarms",
        "top_defi",
        "top_dex",
        "top_nft",
        "nft_today",
        "nft_market",
        "exchanges",
        "ex_rates",
        "platforms",
        "products",
        "indexes",
        "derivatives",
        "categories",
        "hold",
        "hold_comp",
        "load",
        "clear",
        "chart",
        "ta",
        "info",
        "market",
        "ath",
        "atl",
        "score",
        "web",
        "social",
        "bc",
        "dev",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self._gecko_parser = argparse.ArgumentParser(add_help=False, prog="cg")
        self._gecko_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_currency = None
        self.current_df = pd.DataFrame()
        self.source = ""

    def print_help(self):
        """Print help"""
        print("\nCoinGecko:")
        print("   cls             clear screen")
        print("   ?/help          show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print("")
        print("Coin")
        print("   find            find coin by name, symbol or id")
        print("   load            load cryptocurrency data")
        print("   clear           remove loaded coin")
        print("")
        print(f"Loaded coin: {self.current_coin}")
        print("")
        print("   chart           price chart for loaded coin")
        print("   ta              yechnical analysis menu for loaded coin")
        print("   info            nasic information about loaded coin")
        print("   market          market stats about loaded coin")
        print("   ath             all time high related stats for loaded coin")
        print("   atl             all time low related stats for loaded coin")
        print("   web             found websites for loaded coin e.g forum, homepage")
        print(
            "   social          social portals urls for loaded coin, e.g reddit, twitter"
        )
        print(
            "   score           different kind of scores for loaded coin, e.g developer score, sentiment score"
        )
        print("   dev             github, bitbucket coin development statistics")
        print("   bc              links to blockchain explorers for loaded coin")
        print("")
        print("Overview:")
        print("   global          global crypto market info")
        print("   coins           coins available on CoinGecko")
        print("   defi            global DeFi market info")
        print("   trending        trending coins on CoinGecko")
        print("   most_voted      most voted coins on CoinGecko")
        print("   most_visited    most visited coins on CoinGecko")
        print("   top_volume      coins with highest volume on CoinGecko")
        print("   recently        recently added on CoinGecko")
        print("   sentiment       coins with most positive sentiment")
        print(
            "   gainers         top gainers - coins which price gained the most in given period "
        )
        print(
            "   losers          top losers - coins which price dropped the most in given period "
        )
        print("   stables         stablecoins")
        print("   yfarms          top yield farms")
        print("   top_defi        top defi protocols")
        print("   top_dex         top decentralized exchanges")
        print("   top_nft         top non fungible tokens")
        print("   nft_today       non fungible token of the day")
        print("   nft_market      non fungible token market status")
        print("   exchanges       top crypto exchanges")
        print("   ex_rates        coin exchange rates")
        print("   platforms       crypto financial platforms")
        print("   products        crypto financial products")
        print("   indexes         crypto indexes")
        print("   derivatives     crypto derivatives")
        print("   categories      crypto categories")
        print("   hold            ethereum, bitcoin holdings overview statistics")
        print("   hold_comp       ethereum, bitcoin holdings by public companies")
        print("")

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

        (known_args, other_args) = self._gecko_parser.parse_known_args(an_input.split())

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

    def call_find(self, other_args):
        """Process find command"""
        pycoingecko_view.find(other_args=other_args)

    def call_load(self, other_args):
        """Process load command"""
        self.current_coin = pycoingecko_view.load(other_args)

    def call_chart(self, other_args):
        """Process chart command"""
        if self.current_coin:
            pycoingecko_view.chart(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_info(self, other_args):
        """Process info command"""
        if self.current_coin:
            pycoingecko_view.info(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_market(self, other_args):
        """Process market command"""
        if self.current_coin:
            pycoingecko_view.market(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_web(self, other_args):
        """Process web command"""
        if self.current_coin:
            pycoingecko_view.web(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_social(self, other_args):
        """Process social command"""
        if self.current_coin:
            pycoingecko_view.social(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_dev(self, other_args):
        """Process dev command"""
        if self.current_coin:
            pycoingecko_view.dev(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_ath(self, other_args):
        """Process ath command"""
        if self.current_coin:
            pycoingecko_view.ath(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_atl(self, other_args):
        """Process atl command"""
        if self.current_coin:
            pycoingecko_view.atl(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_score(self, other_args):
        """Process score command"""
        if self.current_coin:
            pycoingecko_view.score(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_bc(self, other_args):
        """Process bc command"""
        if self.current_coin:
            pycoingecko_view.bc(self.current_coin, other_args)
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_clear(self, _):
        """Process clear command"""
        if self.current_coin:
            print(
                f"Current coin {self.current_coin.coin_symbol} was removed. You can load new coin with load -c <coin>"
            )
            self.current_coin = None
        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    # pylint: disable=inconsistent-return-statements
    def call_ta(self, other_args):
        """Process ta command"""
        if self.current_coin:
            self.current_df, self.current_currency = pycoingecko_view.ta(
                self.current_coin, other_args
            )
            if self.current_df is not None:
                try:
                    self.current_df = self.current_df[["price"]].rename(
                        columns={"price": "Close"}
                    )
                    self.current_df.index.name = "date"
                    quit = ta_controller.menu(
                        stock=self.current_df,
                        ticker=self.current_coin.coin_symbol,
                        start=self.current_df.index[0],
                        interval="",
                        context="(crypto)>(cg)",
                    )
                    print("")
                    if quit is not None:
                        if quit is True:
                            return quit

                except (ValueError, KeyError) as e:
                    print(e)
            else:
                return
        else:
            print("Please load a coin through either load - coin", "\n")
            return

    def call_hold(self, other_args):
        """Process hold command"""
        pycoingecko_view.holdings_overview(other_args)

    def call_hold_comp(self, other_args):
        """Process hold_comp command"""
        pycoingecko_view.holdings_companies_list(other_args)

    def call_gainers(self, other_args):
        """Process hold_comp command"""
        pycoingecko_view.gainers(other_args)

    def call_losers(self, other_args):
        """Process hold_comp command"""
        pycoingecko_view.losers(other_args)

    def call_trending(self, other_args):
        """Process trending command"""
        pycoingecko_view.discover(category="trending", other_args=other_args)

    def call_most_voted(self, other_args):
        """Process most_voted command"""
        pycoingecko_view.discover(category="most_voted", other_args=other_args)

    def call_recently(self, other_args):
        """Process recently command"""
        pycoingecko_view.recently_added(other_args=other_args)

    def call_most_visited(self, other_args):
        """Process most_voted command"""
        pycoingecko_view.discover(category="most_visited", other_args=other_args)

    def call_sentiment(self, other_args):
        """Process sentiment command"""
        pycoingecko_view.discover(category="positive_sentiment", other_args=other_args)

    def call_news(self, other_args):
        """Process news command"""
        pycoingecko_view.news(other_args=other_args)

    def call_categories(self, other_args):
        """Process top_categories command"""
        pycoingecko_view.categories(other_args=other_args)

    def call_stables(self, other_args):
        """Process stables command"""
        pycoingecko_view.stablecoins(other_args=other_args)

    def call_yfarms(self, other_args):
        """Process yield_farms command"""
        pycoingecko_view.yfarms(other_args=other_args)

    def call_top_volume(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_volume_coins(other_args=other_args)

    def call_top_defi(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_defi_coins(other_args=other_args)

    def call_top_dex(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_dex(other_args=other_args)

    def call_top_nft(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.top_dex(other_args=other_args)

    def call_nft_market(self, other_args):
        """Process top_volume command"""
        pycoingecko_view.nft_market_status(other_args=other_args)

    def call_nft_today(self, other_args):
        """Process nft_today command"""
        pycoingecko_view.nft_of_the_day(other_args=other_args)

    def call_products(self, other_args):
        """Process products command"""
        pycoingecko_view.products(other_args=other_args)

    def call_platforms(self, other_args):
        """Process platforms command"""
        pycoingecko_view.platforms(other_args=other_args)

    def call_exchanges(self, other_args):
        """Process exchanges command"""
        pycoingecko_view.exchanges(other_args=other_args)

    def call_ex_rates(self, other_args):
        """Process exchange_rates command"""
        pycoingecko_view.exchange_rates(other_args=other_args)

    def call_indexes(self, other_args):
        """Process indexes command"""
        pycoingecko_view.indexes(other_args=other_args)

    def call_derivatives(self, other_args):
        """Process derivatives command"""
        pycoingecko_view.derivatives(other_args=other_args)

    def call_global(self, other_args):
        """Process global command"""
        pycoingecko_view.global_market_info(other_args=other_args)

    def call_defi(self, other_args):
        """Process defi command"""
        pycoingecko_view.global_defi_info(other_args=other_args)

    def call_coins(self, other_args):
        """Process coins command"""
        pycoingecko_view.coin_list(other_args=other_args)


def menu():
    gecko_controller = GeckoController()
    gecko_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in gecko_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(cg)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(cg)> ")

        try:
            process_input = gecko_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
