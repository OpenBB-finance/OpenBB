"""Cryptocurrency Context Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, R1710, W0622, C0201, C0301

import argparse
import logging
import os
from typing import List
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal.cryptocurrency import cryptocurrency_helpers
from openbb_terminal import feature_flags as obbff
from openbb_terminal.cryptocurrency.cryptocurrency_helpers import (
    FIND_KEYS,
    display_all_coins,
    find,
    plot_chart,
)
from openbb_terminal.cryptocurrency.due_diligence import (
    binance_view,
    coinpaprika_view,
    finbrain_crypto_view,
    pycoingecko_view,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import CryptoBaseController
from openbb_terminal.rich_config import console, MenuText

# pylint: disable=import-outside-toplevel


logger = logging.getLogger(__name__)

CRYPTO_SOURCES = {
    "bin": "Binance",
    "cg": "CoinGecko",
    "cp": "CoinPaprika",
    "cb": "Coinbase",
    "yf": "YahooFinance",
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
        "pred",
        "qa",
    ]

    DD_VIEWS_MAPPING = {
        "cg": pycoingecko_view,
        "cp": coinpaprika_view,
        "bin": binance_view,
    }
    PATH = "/crypto/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"]["-d"] = {
                c: {} for c in ["1", "7", "14", "30", "90", "180", "365"]
            }
            choices["load"]["--vs"] = {c: {} for c in ["usd", "eur"]}
            choices["find"]["-k"] = {c: {} for c in FIND_KEYS}
            choices["headlines"] = {c: {} for c in finbrain_crypto_view.COINS}
            # choices["prt"]["--vs"] = {c: {} for c in coingecko_coin_ids} # list is huge. makes typing buggy

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/")
        mt.add_cmd("load")
        mt.add_cmd("find")
        mt.add_raw("\n")
        mt.add_param("_symbol", self.symbol.upper())
        mt.add_param(
            "_source", "CoinGecko (Price), YahooFinance (Volume)" if self.symbol else ""
        )
        mt.add_raw("\n")
        mt.add_cmd("headlines", "FinBrain")
        mt.add_cmd("chart", "", self.symbol)
        mt.add_cmd("prt", "", self.symbol)
        mt.add_raw("\n")
        mt.add_menu("disc")
        mt.add_menu("ov")
        mt.add_menu("onchain")
        mt.add_menu("defi")
        mt.add_menu("tools")
        mt.add_menu("nft")
        mt.add_menu("dd", self.symbol)
        mt.add_menu("ta", self.symbol)
        mt.add_menu("pred", self.symbol)
        mt.add_menu("qa", self.symbol)
        console.print(text=mt.menu_text, menu="Cryptocurrency")

    @log_start_end(log=logger)
    def call_prt(self, other_args):
        """Process prt command"""
        if self.symbol:
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
                required="-h" not in other_args,
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

            ns_parser = self.parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if ns_parser:
                if ns_parser.vs:
                    current_coin_id = cryptocurrency_helpers.get_coingecko_id(
                        self.symbol
                    )
                    coin_found = cryptocurrency_helpers.get_coingecko_id(ns_parser.vs)
                    if not coin_found:
                        console.print(
                            f"VS Coin '{ns_parser.vs}' not found in CoinGecko\n"
                        )
                        return
                    pycoingecko_view.display_coin_potential_returns(
                        current_coin_id,
                        coin_found,
                        ns_parser.top,
                        ns_parser.price,
                    )

                else:
                    console.print(
                        "No coin selected. Use 'load' to load the coin you want to look at.\n"
                    )

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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            if not self.symbol:
                console.print("No coin loaded. First use `load {symbol}`\n")
                return

            plot_chart(
                symbol=self.symbol,
                currency=self.current_currency,
                prices_df=self.current_df,
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            finbrain_crypto_view.display_crypto_sentiment_analysis(
                coin=ns_parser.coin, export=ns_parser.export
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
        """Process pred command"""
        if self.symbol:
            from openbb_terminal.cryptocurrency.quantitative_analysis import (
                qa_controller,
            )

            if self.current_interval != "1day":
                console.print("Only interval `1day` is possible for now.\n")
            else:
                self.queue = self.load_class(
                    qa_controller.QaController,
                    self.symbol,
                    self.current_df,
                    self.queue,
                )

    @log_start_end(log=logger)
    def call_pred(self, _):
        """Process pred command"""
        if obbff.ENABLE_PREDICT:
            if self.symbol:
                try:
                    from openbb_terminal.cryptocurrency.prediction_techniques import (
                        pred_controller,
                    )

                    if self.current_interval != "1day":
                        console.print("Only interval `1day` is possible for now.\n")
                    else:
                        self.queue = self.load_class(
                            pred_controller.PredictionTechniquesController,
                            self.symbol,
                            self.current_df,
                            self.queue,
                        )
                except ImportError:
                    logger.exception("Tensorflow not available")
                    console.print("[red]Run pip install tensorflow to continue[/red]\n")

            else:
                console.print(
                    "No coin selected. Use 'load' to load the coin you want to look at.\n"
                )
        else:
            console.print(
                "Predict is disabled. Check ENABLE_PREDICT flag on feature_flags.py",
                "\n",
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
            If you provide ALL keyword in your search query, then all coins will be displayed. To move over coins you
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
            required="-h" not in other_args,
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
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
        )
        # TODO: merge find + display_all_coins
        if ns_parser.coin:
            find(
                coin=ns_parser.coin,
                source=ns_parser.source,
                key=ns_parser.key,
                top=ns_parser.limit,
                export=ns_parser.export,
            )
            display_all_coins(
                coin=ns_parser.coin,
                source=ns_parser.source,
                top=ns_parser.limit,
                skip=ns_parser.skip,
                show_all=bool("ALL" in other_args),
                export=ns_parser.export,
            )
