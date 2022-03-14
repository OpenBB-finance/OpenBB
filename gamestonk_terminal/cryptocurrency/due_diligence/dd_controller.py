"""Cryptocurrency Due diligence Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622, C0201
import argparse
import logging
from datetime import datetime, timedelta
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.cryptocurrency.crypto_controller import CRYPTO_SOURCES
from gamestonk_terminal.cryptocurrency.due_diligence import (
    binance_model,
    binance_view,
    coinbase_model,
    coinbase_view,
    coinglass_model,
    coinglass_view,
    coinpaprika_view,
    glassnode_model,
    glassnode_view,
    pycoingecko_view,
    messari_model,
    messari_view,
)
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    parse_known_args_and_warn,
    valid_date,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import CryptoBaseController
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

FILTERS_VS_USD_BTC = ["usd", "btc"]


class DueDiligenceController(CryptoBaseController):
    """Due Diligence Controller class"""

    CHOICES_COMMANDS = ["load", "oi", "active", "change", "nonzero", "eb"]

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
            "binbook",
            "balance",
        ],
        "cb": ["cbbook", "trades", "stats"],
        "mes": ["mcapdom"],
    }

    DD_VIEWS_MAPPING = {
        "cg": pycoingecko_view,
        "cp": coinpaprika_view,
        "bin": binance_view,
        "mes": messari_view,
    }

    PATH = "/crypto/dd/"

    def __init__(
        self,
        coin=None,
        source=None,
        symbol=None,
        coin_map_df: pd.DataFrame = None,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)

        for _, value in self.SPECIFIC_CHOICES.items():
            self.controller_choices.extend(value)

        self.coin = coin
        self.source = source
        self.symbol = symbol
        self.coin_map_df = coin_map_df

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["load"]["--source"] = {c: None for c in CRYPTO_SOURCES.keys()}
            choices["active"]["-i"] = {
                c: None for c in glassnode_model.INTERVALS_ACTIVE_ADDRESSES
            }
            choices["change"] = {
                c: None for c in glassnode_model.GLASSNODE_SUPPORTED_EXCHANGES
            }
            choices["change"]["-i"] = {
                c: None
                for c in glassnode_model.INTERVALS_DISPLAY_EXCHANGE_NET_POSITION_CHANGE
            }
            choices["nonzero"]["-i"] = {
                c: None for c in glassnode_model.INTERVALS_NON_ZERO_ADDRESSES
            }
            choices["eb"] = {
                c: None for c in glassnode_model.GLASSNODE_SUPPORTED_EXCHANGES
            }
            choices["eb"]["-i"] = {
                c: None for c in glassnode_model.INTERVALS_EXCHANGE_BALANCES
            }
            choices["oi"]["-i"] = {c: None for c in coinglass_model.INTERVALS}
            choices["atl"]["--vs"] = {c: None for c in FILTERS_VS_USD_BTC}
            choices["ath"]["--vs"] = {c: None for c in FILTERS_VS_USD_BTC}
            choices["mkt"]["--vs"] = {c: None for c in coinpaprika_view.CURRENCIES}
            choices["mkt"]["-s"] = {c: None for c in coinpaprika_view.MARKET_FILTERS}
            choices["ex"]["-s"] = {c: None for c in coinpaprika_view.EX_FILTERS}
            choices["events"]["-s"] = {c: None for c in coinpaprika_view.EVENTS_FILTERS}
            choices["twitter"]["-s"] = {
                c: None for c in coinpaprika_view.TWEETS_FILTERS
            }
            choices["mcapdom"]["-i"] = {
                c: None for c in messari_model.INTERVALS_TIMESERIES
            }
            choices["ps"]["--vs"] = {c: None for c in coinpaprika_view.CURRENCIES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        source_txt = CRYPTO_SOURCES.get(self.source, "?") if self.source != "" else ""
        help_text = f"""[cmds]
    load        load a specific cryptocurrency for analysis

[param]Coin: [/param]{self.coin}
[param]Source: [/param]{source_txt}

[src]Glassnode[/src]
   active          active addresses
   nonzero         addresses with non-zero balances
   change          30d change of supply held on exchange wallets
   eb              total balance held on exchanges (in percentage and units)
[src]Coinglass[/src]
   oi              open interest per exchange
[src]CoinPaprika[/src]
   basic           basic information about loaded coin
   ps              price and supply related metrics for loaded coin
   mkt             all markets for loaded coin
   ex              all exchanges where loaded coin is listed
   twitter         tweets for loaded coin
   events          events related to loaded coin
[src]CoinGecko[/src]
   info            basic information about loaded coin
   market          market stats about loaded coin
   ath             all time high related stats for loaded coin
   atl             all time low related stats for loaded coin
   web             found websites for loaded coin e.g forum, homepage
   social          social portals urls for loaded coin, e.g reddit, twitter
   score           different kind of scores for loaded coin, e.g developer score, sentiment score
   dev             github, bitbucket coin development statistics
   bc              links to blockchain explorers for loaded coin
[src]Binance[/src]
   binbook         show order book
   balance         show coin balance
[src]Coinbase[/src]
   cbbook          show order book
   trades          show last trades
   stats           show coin stats
[src]Messari[/src]
   mcapdom         show market cap dominance[/cmds]
"""
        console.print(text=help_text, menu="Stocks - Due Diligence")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.coin:
            return ["crypto", f"load {self.coin} --source {self.source}"]
        return []

    @log_start_end(log=logger)
    def call_nonzero(self, other_args: List[str]):
        """Process nonzero command"""

        if self.symbol.upper() in glassnode_model.GLASSNODE_SUPPORTED_ASSETS:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="nonzero",
                description="""
                    Display addresses with nonzero assets in a certain blockchain
                    [Source: https://glassnode.org]
                """,
            )

            parser.add_argument(
                "-i",
                "--interval",
                dest="interval",
                type=str,
                help="Frequency interval. Default: 24h",
                default="24h",
                choices=glassnode_model.INTERVALS_NON_ZERO_ADDRESSES,
            )

            # TODO: tell users that free api key only data with 1y lag
            parser.add_argument(
                "-s",
                "--since",
                dest="since",
                type=valid_date,
                help="Initial date. Default: 2020-01-01",
                default=(datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d"),
            )

            parser.add_argument(
                "-u",
                "--until",
                dest="until",
                type=valid_date,
                help="Final date. Default: 2021-01-01",
                default=(datetime.now() - timedelta(days=367)).strftime("%Y-%m-%d"),
            )

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
            )

            if ns_parser:
                glassnode_view.display_non_zero_addresses(
                    asset=self.symbol.upper(),
                    interval=ns_parser.interval,
                    since=int(datetime.timestamp(ns_parser.since)),
                    until=int(datetime.timestamp(ns_parser.until)),
                    export=ns_parser.export,
                )

        else:
            console.print("Glassnode source does not support this symbol\n")

    @log_start_end(log=logger)
    def call_active(self, other_args: List[str]):
        """Process active command"""

        if self.symbol.upper() in glassnode_model.GLASSNODE_SUPPORTED_ASSETS:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="active",
                description="""
                    Display active blockchain addresses over time
                    [Source: https://glassnode.org]
                """,
            )

            parser.add_argument(
                "-i",
                "--interval",
                dest="interval",
                type=str,
                help="Frequency interval. Default: 24h",
                default="24h",
                choices=glassnode_model.INTERVALS_ACTIVE_ADDRESSES,
            )

            parser.add_argument(
                "-s",
                "--since",
                dest="since",
                type=valid_date,
                help="Initial date. Default: 2020-01-01",
                default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            )

            parser.add_argument(
                "-u",
                "--until",
                dest="until",
                type=valid_date,
                help="Final date. Default: 2021-01-01",
                default=(datetime.now()).strftime("%Y-%m-%d"),
            )

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
            )

            if ns_parser:
                glassnode_view.display_active_addresses(
                    asset=self.symbol.upper(),
                    interval=ns_parser.interval,
                    since=int(datetime.timestamp(ns_parser.since)),
                    until=int(datetime.timestamp(ns_parser.until)),
                    export=ns_parser.export,
                )

        else:
            console.print("Glassnode source does not support this symbol\n")

    @log_start_end(log=logger)
    def call_change(self, other_args: List[str]):
        """Process change command"""

        if self.symbol.upper() in glassnode_model.GLASSNODE_SUPPORTED_ASSETS:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="change",
                description="""
                    Display active blockchain addresses over time
                    [Source: https://glassnode.org]
                """,
            )

            parser.add_argument(
                "-e",
                "--exchange",
                dest="exchange",
                type=str,
                help="Exchange to check change. Default: aggregated",
                default="aggregated",
                choices=glassnode_model.GLASSNODE_SUPPORTED_EXCHANGES,
            )

            parser.add_argument(
                "-i",
                "--interval",
                dest="interval",
                type=str,
                help="Frequency interval. Default: 24h",
                default="24h",
                choices=glassnode_model.INTERVALS_DISPLAY_EXCHANGE_NET_POSITION_CHANGE,
            )

            parser.add_argument(
                "-s",
                "--since",
                dest="since",
                type=valid_date,
                help="Initial date. Default: 2019-01-01",
                default="2019-01-01",
            )

            parser.add_argument(
                "-u",
                "--until",
                dest="until",
                type=valid_date,
                help="Final date. Default: 2020-01-01",
                default="2020-01-01",
            )

            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "-e")

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
            )

            if ns_parser:
                glassnode_view.display_exchange_net_position_change(
                    asset=self.symbol.upper(),
                    interval=ns_parser.interval,
                    exchange=ns_parser.exchange,
                    since=int(datetime.timestamp(ns_parser.since)),
                    until=int(datetime.timestamp(ns_parser.until)),
                    export=ns_parser.export,
                )
        else:
            console.print("Glassnode source does not support this symbol\n")

    @log_start_end(log=logger)
    def call_eb(self, other_args: List[str]):
        """Process eb command"""

        if self.symbol.upper() in glassnode_model.GLASSNODE_SUPPORTED_ASSETS:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="eb",
                description="""
                    Display active blockchain addresses over time
                    [Source: https://glassnode.org]
                """,
            )

            parser.add_argument(
                "-p",
                "--pct",
                dest="percentage",
                type=bool,
                help="Show percentage instead of stacked value. Default: False",
            )

            parser.add_argument(
                "-e",
                "--exchange",
                dest="exchange",
                type=str,
                help="Exchange to check change. Default: aggregated",
                default="aggregated",
                choices=glassnode_model.GLASSNODE_SUPPORTED_EXCHANGES,
            )

            parser.add_argument(
                "-i",
                "--interval",
                dest="interval",
                type=str,
                help="Frequency interval. Default: 24h",
                default="24h",
                choices=glassnode_model.INTERVALS_EXCHANGE_BALANCES,
            )

            parser.add_argument(
                "-s",
                "--since",
                dest="since",
                type=valid_date,
                help="Initial date. Default: 2019-01-01",
                default="2019-01-01",
            )

            parser.add_argument(
                "-u",
                "--until",
                dest="until",
                type=valid_date,
                help="Final date. Default: 2020-01-01",
                default="2020-01-01",
            )

            if other_args and not other_args[0][0] == "-":
                other_args.insert(0, "-e")

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
            )

            if ns_parser:
                glassnode_view.display_exchange_balances(
                    asset=self.symbol.upper(),
                    interval=ns_parser.interval,
                    exchange=ns_parser.exchange,
                    since=int(datetime.timestamp(ns_parser.since)),
                    until=int(datetime.timestamp(ns_parser.until)),
                    percentage=ns_parser.percentage,
                    export=ns_parser.export,
                )

        else:
            console.print("Glassnode source does not support this symbol\n")

    @log_start_end(log=logger)
    def call_oi(self, other_args):
        """Process oi command"""
        assert isinstance(self.symbol, str)
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="oi",
            description="""
                Displays open interest by exchange for a certain asset
                [Source: https://coinglass.github.io/API-Reference/]
            """,
        )

        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
            type=int,
            help="Frequency interval. Default: 0",
            default=0,
            choices=coinglass_model.INTERVALS,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            coinglass_view.display_open_interest(
                symbol=self.symbol.upper(),
                interval=ns_parser.interval,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_info(self, other_args):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="""
                    Shows basic information about loaded coin like:
                    Name, Symbol, Description, Market Cap, Public Interest, Supply, and Price related metrics
                    """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_info(
                symbol=self.coin_map_df["CoinGecko"], export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_market(self, other_args):
        """Process market command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="market",
            description="""
            Market data for loaded coin. There you find metrics like:
            Market Cap, Supply, Circulating Supply, Price, Volume and many others.""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_market(
                self.coin_map_df["CoinGecko"], ns_parser.export
            )

    @log_start_end(log=logger)
    def call_web(self, other_args):
        """Process web command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="web",
            description="""Websites found for given Coin. You can find there urls to
                                homepage, forum, announcement site and others.""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_web(
                self.coin_map_df["CoinGecko"], export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_social(self, other_args):
        """Process social command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="social",
            description="""Shows social media corresponding to loaded coin. You can find there name of
            telegram channel, urls to twitter, reddit, bitcointalk, facebook and discord.""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_social(
                self.coin_map_df["CoinGecko"], export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_dev(self, other_args):
        """Process dev command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dev",
            description="""
            Developers data for loaded coin. If the development data is available you can see
            how the code development of given coin is going on.
            There are some statistics that shows number of stars, forks, subscribers, pull requests,
            commits, merges, contributors on github.""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_dev(
                self.coin_map_df["CoinGecko"], ns_parser.export
            )

    @log_start_end(log=logger)
    def call_ath(self, other_args):
        """Process ath command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ath",
            description="""All time high data for loaded coin""",
        )

        parser.add_argument(
            "--vs",
            dest="vs",
            help="currency",
            default="usd",
            choices=FILTERS_VS_USD_BTC,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_ath(
                self.coin_map_df["CoinGecko"], ns_parser.vs, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_atl(self, other_args):
        """Process atl command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="atl",
            description="""All time low data for loaded coin""",
        )

        parser.add_argument(
            "--vs",
            dest="vs",
            help="currency",
            default="usd",
            choices=FILTERS_VS_USD_BTC,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_atl(
                self.coin_map_df["CoinGecko"], ns_parser.vs, ns_parser.export
            )

    @log_start_end(log=logger)
    def call_score(self, other_args):
        """Process score command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="score",
            description="""
            In this view you can find different kind of scores for loaded coin.
            Those scores represents different rankings, sentiment metrics, some user stats and others.
            You will see CoinGecko scores, Developer Scores, Community Scores, Sentiment, Reddit scores
            and many others.""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_score(
                self.coin_map_df["CoinGecko"], ns_parser.export
            )

    @log_start_end(log=logger)
    def call_bc(self, other_args):
        """Process bc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="bc",
            description="""
            Blockchain explorers URLs for loaded coin. Those are sites like etherescan.io or polkascan.io
            in which you can see all blockchain data e.g. all txs, all tokens, all contracts...
                                """,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_bc(self.coin_map_df["CoinGecko"], ns_parser.export)

    @log_start_end(log=logger)
    def call_binbook(self, other_args):
        """Process book command"""
        parser = argparse.ArgumentParser(
            prog="binbook",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Get the order book for selected coin",
        )

        limit_list = [5, 10, 20, 50, 100, 500, 1000, 5000]
        coin = self.coin_map_df["Binance"]
        _, quotes = binance_model.show_available_pairs_for_given_symbol(coin)
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            help="Limit parameter.  Adjusts the weight",
            default=100,
            type=int,
            choices=limit_list,
        )

        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs)",
            dest="vs",
            type=str,
            default="USDT",
            choices=quotes,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            binance_view.display_order_book(
                coin=coin,
                limit=ns_parser.limit,
                currency=ns_parser.vs,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_cbbook(self, other_args):
        """Process cbbook command"""
        coin = self.coin_map_df["Coinbase"]
        parser = argparse.ArgumentParser(
            prog="cbbook",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Get the order book for selected coin",
        )

        _, quotes = coinbase_model.show_available_pairs_for_given_symbol(coin)
        if len(quotes) < 0:
            console.print(f"Couldn't find any quoted coins for provided symbol {coin}")

        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs)",
            dest="vs",
            type=str,
            default="USDT" if "USDT" in quotes else quotes[0],
            choices=quotes,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            pair = f"{coin}-{ns_parser.vs.upper()}"
            coinbase_view.display_order_book(
                product_id=pair,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_balance(self, other_args):
        """Process balance command"""
        coin = self.coin_map_df["Binance"]
        _, quotes = binance_model.show_available_pairs_for_given_symbol(coin)

        parser = argparse.ArgumentParser(
            prog="balance",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display balance",
        )

        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs)",
            dest="vs",
            type=str,
            default="USDT",
            choices=quotes,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            binance_view.display_balance(
                coin=coin, currency=ns_parser.vs, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_trades(self, other_args):
        """Process trades command"""
        parser = argparse.ArgumentParser(
            prog="trades",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Show last trades on Coinbase",
        )
        coin = self.coin_map_df["Coinbase"]
        _, quotes = coinbase_model.show_available_pairs_for_given_symbol(coin)
        if len(quotes) < 0:
            console.print(
                f"Couldn't find any quoted coins for provided symbol {self.coin}"
            )

        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs)",
            dest="vs",
            type=str,
            default="USDT" if "USDT" in quotes else quotes[0],
            choices=quotes,
        )

        parser.add_argument(
            "--side",
            help="Side of trade: buy, sell, all",
            dest="side",
            type=str,
            default="all",
            choices=["all", "buy", "sell"],
        )

        parser.add_argument(
            "-t",
            "--top",
            default=15,
            dest="top",
            help="Limit of records",
            type=check_positive,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pair = f"{coin}-{ns_parser.vs.upper()}"
            if ns_parser.side.upper() == "all":
                side = None
            else:
                side = ns_parser.side

            coinbase_view.display_trades(
                product_id=pair, limit=ns_parser.top, side=side, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_stats(self, other_args):
        """Process stats command"""
        coin = self.coin_map_df["Binance"]
        _, quotes = coinbase_model.show_available_pairs_for_given_symbol(coin)

        parser = argparse.ArgumentParser(
            prog="stats",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display coin stats",
        )

        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs)",
            dest="vs",
            type=str,
            default="USDT" if "USDT" in quotes else quotes[0],
            choices=quotes,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pair = f"{coin}-{ns_parser.vs.upper()}"
            coinbase_view.display_stats(pair, ns_parser.export)

    @log_start_end(log=logger)
    def call_ps(self, other_args):
        """Process ps command"""
        parser = argparse.ArgumentParser(
            prog="ps",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Get price and supply related metrics for given coin.""",
        )

        parser.add_argument(
            "--vs",
            help="Quoted currency. Default USD",
            dest="vs",
            default="USD",
            type=str,
            choices=coinpaprika_view.CURRENCIES,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_price_supply(
                self.coin_map_df["CoinPaprika"],
                ns_parser.vs,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_basic(self, other_args):
        """Process basic command"""
        parser = argparse.ArgumentParser(
            prog="basic",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Get basic information for coin. Like:
                name, symbol, rank, type, description, platform, proof_type,
                contract, tags, parent""",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_basic(
                self.coin_map_df["CoinPaprika"],
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_mkt(self, other_args):
        """Process mkt command"""
        parser = argparse.ArgumentParser(
            prog="mkt",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Get all markets found for given coin.
                You can display only N number of markets with --limt parameter.
                You can sort data by pct_volume_share, exchange, pair, trust_score, volume, price --sort parameter
                and also with --descend flag to sort descending.
                You can use additional flag --urls to see urls for each market
                Displays:
                    exchange, pair, trust_score, volume, price, pct_volume_share,""",
        )

        parser.add_argument(
            "--vs",
            help="Quoted currency. Default USD",
            dest="vs",
            default="USD",
            type=str,
            choices=coinpaprika_view.CURRENCIES,
        )

        parser.add_argument(
            "-l",
            "--limit",
            default=20,
            dest="limit",
            help="Limit of records",
            type=check_positive,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: pct_volume_share",
            default="pct_volume_share",
            choices=coinpaprika_view.MARKET_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        parser.add_argument(
            "-u",
            "--urls",
            dest="urls",
            action="store_true",
            help="""Flag to show urls. If you will use that flag you will see only:
                exchange, pair, trust_score, market_url columns""",
            default=False,
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_markets(
                coin_id=self.coin_map_df["CoinPaprika"],
                currency=ns_parser.vs,
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ex(self, other_args):
        """Process ex command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ex",
            description="""Get all exchanges found for given coin.
                You can display only top N number of exchanges with --top parameter.
                You can sort data by  id, name, adjusted_volume_24h_share, fiats --sort parameter
                and also with --descend flag to sort descending.
                Displays:
                    id, name, adjusted_volume_24h_share, fiats""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            help="Limit of records",
            type=check_positive,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: date",
            default="adjusted_volume_24h_share",
            choices=coinpaprika_view.EX_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_exchanges(
                coin_id=self.coin_map_df["CoinPaprika"],
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_events(self, other_args):
        """Process events command"""
        parser = argparse.ArgumentParser(
            prog="events",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Show information about most important coins events. Most of coins doesn't have any events.
            You can display only top N number of events with --limit parameter.
            You can sort data by id, date , date_to, name, description, is_conference --sort parameter
            and also with --descend flag to sort descending.
            You can use additional flag --urls to see urls for each event
            Displays:
                date , date_to, name, description, is_conference, link, proof_image_link""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            help="Limit of records",
            type=check_positive,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: date",
            default="date",
            choices=coinpaprika_view.EVENTS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        parser.add_argument(
            "-u",
            "--urls",
            dest="urls",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will see only date, name, link columns",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_events(
                coin_id=self.coin_map_df["CoinPaprika"],
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_twitter(self, other_args):
        """Process twitter command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="twitter",
            description="""Show last 10 tweets for given coin.
                You can display only N number of tweets with --limit parameter.
                You can sort data by date, user_name, status, retweet_count, like_count --sort parameter
                and also with --descend flag to sort descending.
                Displays:
                    date, user_name, status, retweet_count, like_count
                """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            help="Limit of records",
            type=check_positive,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: date",
            default="date",
            choices=coinpaprika_view.TWEETS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_twitter(
                coin_id=self.coin_map_df["CoinPaprika"],
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_mcapdom(self, other_args: List[str]):
        """Process mcapdom command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mcapdom",
            description="""
                Display asset's percentage share of total crypto circulating market cap
                [Source: https://messari.io]
            """,
        )

        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
            type=str,
            help="Frequency interval. Default: 1d",
            default="1d",
            choices=messari_model.INTERVALS_TIMESERIES,
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start",
            type=valid_date,
            help="Initial date. Default: A year ago",
            default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-end",
            "--end",
            dest="end",
            type=valid_date,
            help="End date. Default: Today",
            default=datetime.now().strftime("%Y-%m-%d"),
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            messari_view.display_marketcap_dominance(
                coin=self.symbol.upper(),
                interval=ns_parser.interval,
                start=ns_parser.start,
                end=ns_parser.end,
                export=ns_parser.export,
            )
