"""Cryptocurrency Context Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, R1710, W0622, C0201, C0301

import argparse
import logging
import os
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency import cryptocurrency_helpers, pyth_model, pyth_view
from openbb_terminal.cryptocurrency.crypto_views import find
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import (
    display_all_coins,
    plot_chart,
)
from openbb_terminal.cryptocurrency.due_diligence import (
    binance_view,
    coinpaprika_view,
    finbrain_crypto_view,
    pycoingecko_view,
)
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    export_data,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import CryptoBaseController
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=import-outside-toplevel


logger = logging.getLogger(__name__)

FIND_KEYS = ["id", "symbol", "name"]

CRYPTO_SOURCES = {
    "Binance": "Binance",
    "CoingGecko": "CoinGecko",
    "CoinPaprika": "CoinPaprika",
    "Coinbase": "Coinbase",
    "YahooFinance": "YahooFinance",
}


class CryptoController(CryptoBaseController):
    """Crypto Controller"""

    CHOICES_COMMANDS = [
        "headlines",
        "candle",
        "load",
        "find",
        "prt",
        "resources",
        "price",
    ]
    CHOICES_MENUS = [
        "ta",
        "dd",
        "ov",
        "disc",
        "onchain",
        "defi",
        "tools",
        "nft",
        "qa",
        "forecast",
    ]

    DD_VIEWS_MAPPING = {
        "CoingGecko": pycoingecko_view,
        "CoinPaprika": coinpaprika_view,
        "Binance": binance_view,
    }
    PATH = "/crypto/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            choices["load"] = {
                "--interval": {
                    c: {}
                    for c in [
                        "1",
                        "5",
                        "15",
                        "30",
                        "60",
                        "240",
                        "1440",
                        "10080",
                        "43200",
                    ]
                },
                "-i": "--interval",
                "--exchange": {c: {} for c in self.exchanges},
                "--source": {c: {} for c in ["CCXT", "YahooFinance", "CoinGecko"]},
                "--vs": {c: {} for c in ["usd", "eur"]},
                "--start": None,
                "-s": "--start",
                "--end": None,
                "-e": "--end",
            }

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/")
        mt.add_cmd("load")
        mt.add_cmd("find")
        mt.add_cmd("price", "Pyth")
        mt.add_raw("\n")
        mt.add_param(
            "_symbol", f"{self.symbol.upper()}/{self.vs.upper()}" if self.symbol else ""
        )
        if self.source == "CCXT":
            mt.add_param(
                "_exchange", self.exchange if self.symbol and self.exchange else ""
            )
        mt.add_param("_source", self.source if self.symbol and self.source else "")
        mt.add_param("_interval", self.current_interval)
        mt.add_raw("\n")
        mt.add_cmd("headlines")
        mt.add_cmd("candle", self.symbol)
        mt.add_cmd("prt", self.symbol)
        mt.add_raw("\n")
        mt.add_menu("disc")
        mt.add_menu("ov")
        mt.add_menu("onchain")
        mt.add_menu("defi")
        mt.add_menu("tools")
        mt.add_menu("nft")
        mt.add_menu("dd", self.symbol)
        mt.add_menu("ta", self.symbol)
        mt.add_menu("qa", self.symbol)
        mt.add_menu("forecast", self.symbol)
        console.print(text=mt.menu_text, menu="Cryptocurrency")

    @log_start_end(log=logger)
    def call_prt(self, other_args):
        """Process prt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="prt",
            description="Potential Returns Tool"
            "Tool to check returns if loaded coin reaches provided price or other crypto market cap"
            "Uses CoinGecko to grab coin data (price and market cap).",
        )
        parser.add_argument(
            "--vs",
            help="Coin to compare with",
            dest="vs",
            type=str,
            required="-h" not in other_args and "--help" not in other_args,
            default=None,
        )
        parser.add_argument(
            "-p",
            "--price",
            help="Desired price",
            dest="price",
            type=int,
            default=None,
        )
        parser.add_argument(
            "-t",
            "--top",
            help="Compare with top N coins",
            dest="top",
            type=int,
            default=None,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--vs")

        if ns_parser := self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        ):
            if self.symbol:
                num_args = 0
                for arg in vars(ns_parser):
                    if getattr(ns_parser, arg):
                        num_args = num_args + 1
                        if num_args > 1:
                            console.print("[red]Please chose only one flag[/red]\n")
                            return
                current_coin_id = cryptocurrency_helpers.get_coingecko_id(self.symbol)
                if ns_parser.vs is not None:
                    coin_found = cryptocurrency_helpers.get_coingecko_id(ns_parser.vs)
                    if not coin_found:
                        console.print(
                            f"VS Coin '{ns_parser.vs}' not found in CoinGecko\n"
                        )
                        return
                else:
                    coin_found = None
                if (
                    ns_parser.vs is None
                    and ns_parser.top is None
                    and ns_parser.price is None
                ):
                    console.print(
                        "[red]Please chose a flag: --top, --vs, or --price [/red]\n"
                    )
                    return
                pycoingecko_view.display_coin_potential_returns(
                    current_coin_id,
                    coin_found,
                    ns_parser.top,
                    ns_parser.price,
                )
            else:
                console.print("[red]Please load a coin first![/red]\n")

    @log_start_end(log=logger)
    def call_price(self, other_args):
        """Process price command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="price",
            description="""Display price and interval of confidence in real-time. [Source: Pyth]""",
        )
        parser.add_argument(
            "-s",
            "--symbol",
            required="-h" not in other_args and "--help" not in other_args,
            type=str,
            dest="symbol",
            help="Symbol of coin to load data for, ~100 symbols are available",
            choices=pyth_model.ASSETS.keys(),
            metavar="SYMBOL",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")

        if ns_parser := self.parse_known_args_and_warn(parser, other_args):
            upper_symbol = ns_parser.symbol.upper()
            if "-USD" not in ns_parser.symbol:
                upper_symbol += "-USD"
            if upper_symbol in pyth_model.ASSETS:
                console.print(
                    "[param]If it takes too long, you can use 'Ctrl + C' to cancel.\n[/param]"
                )
                pyth_view.display_price(upper_symbol)
            else:
                console.print("[red]The symbol selected does not exist.[/red]\n")

    @log_start_end(log=logger)
    def call_candle(self, other_args):
        """Process candle command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="""Display chart for loaded coin. You can specify currency vs which you want
            to show chart and also number of days to get data for.""",
        )
        parser.add_argument(
            "--log",
            help="Plot with y axis on log scale",
            action="store_true",
            default=False,
            dest="logy",
        )

        if ns_parser := self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        ):
            if not self.symbol:
                console.print("No coin loaded. First use `load {symbol}`\n")
                return
            figure = plot_chart(
                exchange=self.exchange,
                source=self.source,
                to_symbol=self.symbol,
                from_symbol=self.current_currency,
                prices_df=self.current_df,
                interval=self.current_interval,
                yscale="log" if ns_parser.logy else "linear",
                external_axes=ns_parser.is_image,
            )
            export_data(
                ns_parser.export,
                os.path.join(os.path.dirname(os.path.abspath(__file__))),
                f"{self.symbol}",
                self.current_df,
                " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None,
                figure=figure,
            )

    @log_start_end(log=logger)
    def call_ta(self, _):
        """Process ta command"""
        from openbb_terminal.cryptocurrency.technical_analysis.ta_controller import (
            TechnicalAnalysisController,
        )

        # TODO: Play with this to get correct usage
        if self.symbol:
            if self.current_currency != "" and not self.current_df.empty:
                self.queue = self.load_class(
                    TechnicalAnalysisController,
                    stock=self.current_df,
                    coin=self.symbol,
                    start=self.current_df.index[0],
                    interval="",
                    queue=self.queue,
                )

        else:
            console.print("No coin selected. Use 'load' to load a coin.\n")

    @log_start_end(log=logger)
    def call_tools(self, _):
        """Process tools command"""
        from openbb_terminal.cryptocurrency.tools.tools_controller import (
            ToolsController,
        )

        self.queue = self.load_class(ToolsController, self.queue)

    @log_start_end(log=logger)
    def call_disc(self, _):
        """Process disc command"""
        from openbb_terminal.cryptocurrency.discovery.discovery_controller import (
            DiscoveryController,
        )

        self.queue = self.load_class(DiscoveryController, self.queue)

    @log_start_end(log=logger)
    def call_ov(self, _):
        """Process ov command"""
        from openbb_terminal.cryptocurrency.overview.overview_controller import (
            OverviewController,
        )

        self.queue = self.load_class(OverviewController, self.queue)

    @log_start_end(log=logger)
    def call_defi(self, _):
        """Process defi command"""
        from openbb_terminal.cryptocurrency.defi.defi_controller import DefiController

        self.queue = self.load_class(DefiController, self.queue)

    @log_start_end(log=logger)
    def call_headlines(self, other_args):
        """Process sentiment command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="headlines",
            description="""Display sentiment analysis from FinBrain for chosen Cryptocurrencies""",
        )
        parser.add_argument(
            "-c",
            "--coin",
            default="BTC",
            type=str,
            dest="coin",
            help="Symbol of coin to load data for, ~100 symbols are available",
            choices=finbrain_crypto_view.COINS,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        if ns_parser := self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        ):
            finbrain_crypto_view.display_crypto_sentiment_analysis(
                symbol=ns_parser.coin, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_dd(self, _):
        """Process dd command"""
        if self.symbol:
            from openbb_terminal.cryptocurrency.due_diligence.dd_controller import (
                DueDiligenceController,
            )

            self.queue = self.load_class(
                DueDiligenceController,
                self.symbol,
                self.source,
                queue=self.queue,
            )
        else:
            console.print("No coin selected. Use 'load' to load a coin.\n")

    @log_start_end(log=logger)
    def call_qa(self, _):
        """Process qa command"""
        if self.symbol:
            from openbb_terminal.cryptocurrency.quantitative_analysis import (
                qa_controller,
            )

            self.queue = self.load_class(
                qa_controller.QaController,
                self.symbol,
                self.current_df,
                self.queue,
            )

    @log_start_end(log=logger)
    def call_onchain(self, _):
        """Process onchain command"""
        from openbb_terminal.cryptocurrency.onchain.onchain_controller import (
            OnchainController,
        )

        self.queue = self.load_class(OnchainController, self.queue)

    @log_start_end(log=logger)
    def call_nft(self, _):
        """Process nft command"""
        from openbb_terminal.cryptocurrency.nft.nft_controller import NFTController

        self.queue = self.load_class(NFTController, self.queue)

    # TODO: merge the two views that this command calls. (find + previously called coins)
    @log_start_end(log=logger)
    def call_find(self, other_args):
        """Process find command"""
        parser = argparse.ArgumentParser(
            prog="find",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Find similar coin by name, symbol, or id. If you don't remember exact name or id of the Coin at CoinGecko,
            Binance, Coinbase or CoinPaprika you can use this command to display coins with similar name, symbol or id
            to your search query.
            Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
            It will search for coin that has similar name to polka and display top 25 matches.
            -c, --coin stands for coin - you provide here your search query
            -k, --key it's a searching key. You can search by symbol, id or name of coin
            -l, --limit it displays top N number of records.
            coins: Shows list of coins available on CoinGecko, CoinPaprika and Binance.If you provide name of
            coin then in result you will see ids of coins with best match for all mentioned services.
            If you provide "ALL" in your coin search query, then all coins will be displayed. To move over coins you
            can use pagination mechanism with skip, top params. E.g. coins ALL --skip 100 --limit 30 then all coins
            from 100 to 130 will be displayed. By default skip = 0, limit = 10.
            If you won't provide source of the data everything will be displayed (CoinGecko, CoinPaprika, Binance).
            If you want to search only in given source then use --source flag. E.g. if you want to find coin with name
            uniswap on CoinPaprika then use: coins uniswap --source cp --limit 10
            """,
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Symbol Name or Id of Coin",
            dest="coin",
            required="-h" not in other_args and "--help" not in other_args,
            type=str,
        )
        parser.add_argument(
            "-k",
            "--key",
            dest="key",
            help="Specify by which column you would like to search: symbol, name, id",
            type=str,
            choices=FIND_KEYS,
            default="symbol",
        )
        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            help="Number of records to display",
            type=check_positive,
        )
        parser.add_argument(
            "-s",
            "--skip",
            default=0,
            dest="skip",
            help="Skip n of records",
            type=check_positive,
            choices=range(1, 300),
            metavar="SKIP",
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
        )
        # TODO: merge find + display_all_coins
        if ns_parser:
            if ns_parser.coin == "ALL":
                display_all_coins(
                    symbol=ns_parser.coin,
                    source=ns_parser.source,
                    limit=ns_parser.limit,
                    skip=ns_parser.skip,
                    show_all=True,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                find(
                    query=ns_parser.coin,
                    source=ns_parser.source,
                    key=ns_parser.key,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_forecast(self, _):
        """Process forecast command"""
        from openbb_terminal.forecast import forecast_controller

        console.print(self.symbol)
        self.queue = self.load_class(
            forecast_controller.ForecastController,
            self.symbol,
            self.current_df,
            self.queue,
        )
