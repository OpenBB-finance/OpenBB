"""Cryptocurrency Due diligence Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622, C0201
import argparse
import difflib
from typing import List, Union
from datetime import datetime, timedelta
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.cryptocurrency.due_diligence import (
    coinglass_model,
    glassnode_model,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.crypto_controller import CRYPTO_SOURCES

from gamestonk_terminal.cryptocurrency.due_diligence import (
    coinglass_view,
    glassnode_view,
    pycoingecko_view,
    coinpaprika_view,
    binance_view,
    coinbase_model,
    binance_model,
    coinbase_view,
)
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    try_except,
    system_clear,
    valid_date,
)
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import (
    load,
)

FILTERS_VS_USD_BTC = ["usd", "btc"]


class DueDiligenceController:

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

    CHOICES_COMMANDS = ["load", "oi", "active", "change", "nonzero", "eb"]

    CHOICES += CHOICES_COMMANDS

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
    }

    DD_VIEWS_MAPPING = {
        "cg": pycoingecko_view,
        "cp": coinpaprika_view,
        "bin": binance_view,
    }

    def __init__(
        self,
        coin=None,
        source=None,
        symbol=None,
        coin_map_df: pd.DataFrame = None,
        queue: List[str] = None,
    ):
        """CONSTRUCTOR"""

        self.dd_parser = argparse.ArgumentParser(add_help=False, prog="dd")
        self.dd_parser.add_argument("cmd", choices=self.CHOICES)

        self.current_coin = coin
        self.current_df = pd.DataFrame()
        self.source = source
        self.symbol = symbol
        self.coin_map_df = coin_map_df

        for _, value in self.SPECIFIC_CHOICES.items():
            self.CHOICES.extend(value)

        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["load"]["--source"] = {c: None for c in CRYPTO_SOURCES.keys()}
            choices["active"]["-i"] = {c: None for c in glassnode_model.INTERVALS}
            choices["change"] = {
                c: None for c in glassnode_model.GLASSNODE_SUPPORTED_EXCHANGES
            }
            choices["change"]["-i"] = {c: None for c in glassnode_model.INTERVALS}
            choices["nonzero"]["-i"] = {c: None for c in glassnode_model.INTERVALS}
            choices["eb"] = {
                c: None for c in glassnode_model.GLASSNODE_SUPPORTED_EXCHANGES
            }
            choices["eb"]["-i"] = {c: None for c in glassnode_model.INTERVALS}
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
            choices["ps"]["--vs"] = {c: None for c in coinpaprika_view.CURRENCIES}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = "Due Diligence Menu:\n"
        help_text += """
    load        load a specific cryptocurrency for analysis
"""
        help_text += (
            f"\nCoin: {self.current_coin}" if self.current_coin != "" else "\nCoin: ?"
        )
        help_text += (
            f"\nSource: {CRYPTO_SOURCES.get(self.source, '?')}\n"
            if self.source != ""
            else "\nSource: ?\n"
        )
        help_text += """
Glassnode:
   active          active addresses
   nonzero         addresses with non-zero balances
   change          30d change of supply held on exchange wallets
   eb              total balance held on exchanges (in percentage and units)
Coinglass:
   oi              open interest per exchange
CoinPaprika:
   basic           basic information about loaded coin
   ps              price and supply related metrics for loaded coin
   mkt             all markets for loaded coin
   ex              all exchanges where loaded coin is listed
   twitter         tweets for loaded coin
   events          events related to loaded coin
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
Binance:
   binbook         show order book
   balance         show coin balance
Coinbase:
   cbbook          show order book
   trades          show last trades
   stats           show coin stats
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

        (known_args, other_args) = self.dd_parser.parse_known_args(an_input.split())

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
        self.queue.insert(0, "dd")
        if self.current_coin:
            self.queue.insert(0, f"load {self.current_coin} --source {self.source}")
        self.queue.insert(0, "crypto")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load crypto currency to perform analysis on. "
            "Available data sources are CoinGecko, CoinPaprika, Binance, Coinbase"
            "By default main source used for analysis is CoinGecko (cg). To change it use --source flag",
        )

        parser.add_argument(
            "-c",
            "--coin",
            help="Coin to get",
            dest="coin",
            type=str,
            required="-h" not in other_args,
        )

        parser.add_argument(
            "-s",
            "--source",
            help="Source of data",
            dest="source",
            choices=CRYPTO_SOURCES.keys(),
            default="cg",
            required=False,
        )
        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            source = ns_parser.source

            for arg in ["--source", source]:
                if arg in other_args:
                    other_args.remove(arg)

            self.current_coin, self.source, self.symbol, self.coin_map_df, _, _ = load(
                coin=ns_parser.coin, source=ns_parser.source
            )
            if self.symbol:
                print(f"\nLoaded {self.current_coin} from source {self.source}\n")

    @try_except
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
                choices=glassnode_model.INTERVALS,
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
            print("Glassnode source does not support this symbol\n")

    @try_except
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
                choices=glassnode_model.INTERVALS,
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
            print("Glassnode source does not support this symbol\n")

    @try_except
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
                choices=glassnode_model.INTERVALS,
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
            print("Glassnode source does not support this symbol\n")

    @try_except
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
                choices=glassnode_model.INTERVALS,
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
            print("Glassnode source does not support this symbol\n")

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
    def call_binbook(self, other_args):
        """Process binbook command"""
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

    @try_except
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
            print(f"Couldn't find any quoted coins for provided symbol {coin}")

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

    @try_except
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

    @try_except
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
            print(
                f"Couldn't find any quoted coins for provided symbol {self.current_coin}"
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

    @try_except
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

    # paprika
    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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

    @try_except
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


def menu(
    coin=None,
    source=None,
    symbol=None,
    coin_map_df: pd.DataFrame = None,
    queue: List[str] = None,
):
    """Due Dilligence Menu"""

    source = source if source else "cg"
    dd_controller = DueDiligenceController(
        coin=coin, source=source, symbol=symbol, queue=queue, coin_map_df=coin_map_df
    )
    an_input = "HELP_ME"
    while True:
        # There is a command in the queue
        if dd_controller.queue and len(dd_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if dd_controller.queue[0] in ("q", "..", "quit"):
                if len(dd_controller.queue) > 1:
                    return dd_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = dd_controller.queue[0]
            dd_controller.queue = dd_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in dd_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /crypto/dd/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                dd_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and dd_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /crypto/dd/ $ ",
                        completer=dd_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/dd/ $ ")

        try:
            # Process the input command
            dd_controller.queue = dd_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /crypto/dd menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                dd_controller.CHOICES,
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
                        dd_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                dd_controller.queue.insert(0, an_input)
            else:
                print("\n")
