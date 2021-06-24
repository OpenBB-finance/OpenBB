"""Cryptocurrency Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency import (
    binance_model,
    pycoingecko_view,
    coinmarketcap_view as cmc_view,
)
from gamestonk_terminal.technical_analysis import ta_controller


class CryptoController:

    CHOICES = [
        "help",
        "q",
        "quit",
        "load",
        "view",
        "top",
        "global",
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
        "trend",
        "book",
        "trades",
        "candle",
        "balance",
        "select",
        "ta",
    ]

    def __init__(self):
        """CONSTRUCTOR"""

        self.crypto_parser = argparse.ArgumentParser(add_help=False, prog="crypto")
        self.crypto_parser.add_argument("cmd", choices=self.CHOICES)
        self.current_coin = None
        self.current_currency = None
        self.current_df = pd.DataFrame()
        self.source = ""

    def print_help(self):
        """Print help"""
        print("\nCryptocurrency:")
        print("   help            show this menu again")
        print("   q               quit this menu, and shows back to main menu")
        print("   quit            quit to abandon program")
        print(f"\nCurrent Coin: {self.current_coin}")
        print("")
        print("Coingecko:")
        print("   load            load cryptocurrency data")
        print("   view            load and view cryptocurrency data")
        print("   trend           show top 7 trending coins")
        print("   global          show global crypto market info")
        print("   coins           show coins available on CoinGecko")
        print("   defi            show global DeFi market info")
        print("   trending        show trending coins on CoinGecko")
        print("   most_voted      show most voted coins on CoinGecko")
        print("   top_volume      show coins with highest volume on CoinGecko")
        print("   recently        show recently added on CoinGecko")
        print("   sentiment       show coins with most positive sentiment")
        print(
            "   gainers         show top gainers - coins which price gained the most in given period "
        )
        print(
            "   losers          show top losers - coins which price dropped the most in given period "
        )
        print("   stables         show Stable Coins")
        print("   yfarms          show top Yield Farms")
        print("   top_defi        show top DeFi Protocols")
        print("   top_dex         show top Decentralized Exchanges")
        print("   top_nft         show top Non Fungible Tokens")
        print("   nft_today       show NFT Of The Day")
        print("   nft_market      show NFT Market Status")
        print("   exchanges       show Top Crypto Exchanges")
        print("   ex_rates        show Coin Exchange Rates")
        print("   platforms       show Crypto Financial Platforms")
        print("   products        show Crypto Financial Products")
        print("   indexes         show Crypto Indexes")
        print("   derivatives     show Crypto Derivatives")
        print("   categories      show Crypto Categories")
        print("   derivatives     show Crypto Derivatives")
        print("   hold            show eth, btc holdings overview statistics")
        print("   hold_comp       show eth, btc holdings by public companies")

        print("")
        print("CoinMarketCap:")
        print("   top           view top coins from coinmarketcap")
        print("")
        print("Binance:")
        print("   select        select coin/currency to use and load candle data")
        print("   book          show order book")
        print("   candle        show candles")
        print("   balance       show coin balance")
        print("")
        print(">  ta           technical analysis menu for")
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
        (known_args, other_args) = self.crypto_parser.parse_known_args(an_input.split())

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_load(self, other_args):
        """Process load command"""
        self.current_coin, self.current_df = pycoingecko_view.load(other_args)
        self.source = "CG"

    def call_view(self, other_args):
        """Process view command"""
        if self.current_coin:
            pycoingecko_view.view(self.current_coin, self.current_df, other_args)

        else:
            print("No coin selected. Use 'load' to load the coin you want to look at.")
            print("")

    def call_trend(self, _):
        """Process trend command"""
        pycoingecko_view.trend()

    def call_top(self, other_args):
        """Process top command"""
        cmc_view.get_cmc_top_n(other_args)

    def call_book(self, other_args):
        """Process book command"""
        binance_model.order_book(other_args, self.current_coin, self.current_currency)

    def call_candle(self, _):
        """Process candle command"""
        binance_model.show_candles(
            self.current_df, self.current_coin, self.current_currency
        )

    def call_balance(self, _):
        """Process balance command"""
        binance_model.balance(self.current_coin)

    def call_select(self, other_args):
        """Process select command"""
        (
            self.current_coin,
            self.current_currency,
            self.current_df,
        ) = binance_model.select_binance_coin(other_args)
        self.source = "BIN"
        print("")

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
        pycoingecko_view.top_categories(other_args=other_args)

    def call_stables(self, other_args):
        """Process stables command"""
        pycoingecko_view.stablecoins(other_args=other_args)

    def call_yfarms(self, other_args):
        """Process yield_farms command"""
        pycoingecko_view.yield_farms(other_args=other_args)

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

    # pylint: disable=inconsistent-return-statements
    def call_ta(self, _):
        """Process ta command"""
        if not self.current_coin:
            print("Please load a coin through either load or select", "\n")
        if self.current_df.empty:
            print("Price dataframe is empty")
        else:
            # Need to make the columns in df be compatible.  Also since there are no splits or dividends, there is no
            # adj close.  To tell ta to use Close, we can just set the interval to anything but 1440.
            # Binance provides candles so we just need to rename:
            if self.source == "BIN":
                self.current_df = self.current_df.rename(
                    columns={
                        "Open": "1. open",
                        "High": "2. high",
                        "Low": "3. low",
                        "Close": "4. close",
                        "Volume": "6. volume",
                    }
                )
                self.current_df.index.name = "date"

            # Coingecko does not provide candles so we can only provide close data.
            elif self.source == "CG":

                self.current_df = self.current_df[["Price"]].rename(
                    columns={"Price": "4. close"}
                )
                self.current_df.index.name = "date"

            return ta_controller.menu(
                self.current_df,
                self.current_coin,
                self.current_df.index[0],
                "",
            )


def menu():
    crypto_controller = CryptoController()
    crypto_controller.print_help()
    plt.close("all")
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in crypto_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)> ")

        try:
            process_input = crypto_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
