"""Cryptocurrency Context Controller"""
__docformat__ = "numpy"
# pylint: disable=R0904, C0302, R1710, W0622, C0201, C0301

import argparse
from datetime import datetime, timedelta
import difflib
from typing import List, Union
import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from rich import console
from binance.client import Client

from gamestonk_terminal.cryptocurrency.pycoingecko_helpers import calc_change
from gamestonk_terminal.cryptocurrency.due_diligence import pycoingecko_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    system_clear,
    try_except,
    valid_date_in_past,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.due_diligence import (
    coinpaprika_view,
    binance_view,
    pycoingecko_view,
    finbrain_crypto_view,
    binance_model,
    coinbase_model,
)
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import (
    FIND_KEYS,
    display_all_coins,
    load,
    find,
    plot_chart,
)
import gamestonk_terminal.config_terminal as cfg

# pylint: disable=import-outside-toplevel


CRYPTO_SOURCES = {
    "bin": "Binance",
    "cg": "CoinGecko",
    "cp": "CoinPaprika",
    "cb": "Coinbase",
}

t_console = console.Console()


class CryptoController:
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
        "headlines",
        "chart",
        "load",
        "coins",
        "find",
    ]

    CHOICES_MENUS = ["ta", "dd", "ov", "disc", "onchain", "defi", "nft", "pred"]

    DD_VIEWS_MAPPING = {
        "cg": pycoingecko_view,
        "cp": coinpaprika_view,
        "bin": binance_view,
    }

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(self, queue: List[str] = None):
        """CONSTRUCTOR"""

        self.crypto_parser = argparse.ArgumentParser(add_help=False, prog="crypto")
        self.crypto_parser.add_argument("cmd", choices=self.CHOICES)

        self.symbol = ""
        self.current_coin = ""
        self.current_df = pd.DataFrame()
        self.current_currency = ""
        self.source = ""
        self.coin_map_df = pd.DataFrame()
        self.current_interval = ""
        self.price_str = ""

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["coins"]["--source"] = {c: {} for c in CRYPTO_SOURCES.keys()}
            choices["load"]["--source"] = {c: {} for c in CRYPTO_SOURCES.keys()}
            choices["find"]["--source"] = {c: {} for c in CRYPTO_SOURCES.keys()}
            choices["find"]["-k"] = {c: {} for c in FIND_KEYS}
            choices["headlines"] = {c: {} for c in finbrain_crypto_view.COINS}
            # choices["prt"]["--vs"] = {c: {} for c in coingecko_coin_ids} # list is huge. makes typing buggy
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = """
     load        load a specific cryptocurrency for analysis
     find        find coins in a certain source
     coins       find coins and check map across multiple sources
"""
        help_text += (
            f"\nCoin: {self.current_coin}" if self.current_coin != "" else "\nCoin: ?"
        )
        help_text += (
            f"\nSource: {CRYPTO_SOURCES.get(self.source, '?')}\n"
            if self.source != ""
            else "\nSource: ?\n"
        )
        help_text += self.price_str + "\n"
        help_text += f"""
     headlines   crypto sentiment from 15+ major news headlines [Finbrain]{'[dim]' if not self.current_coin else ''}
     chart       view a candle chart for a specific cryptocurrency
     prt         potential returns tool                  e.g.: check how much upside if eth reaches btc market cap{'[/dim]' if not self.current_coin else ''}
    """  # noqa
        help_text += f"""
>    disc        discover trending cryptocurrencies,     e.g.: top gainers, losers, top sentiment
>    ov          overview of the cryptocurrencies,       e.g.: market cap, DeFi, latest news, top exchanges, stables
>    onchain     information on different blockchains,   e.g.: eth gas fees, whale alerts, DEXes info
>    defi        decentralized finance information,      e.g.: dpi, llama, tvl, lending, borrow, funding
>    nft         non-fungible tokens,                    e.g.: today drops{'[dim]' if not self.current_coin else ''}
>    dd          due-diligence for loaded coin,          e.g.: coin information, social media, market stats
>    ta          technical analysis for loaded coin,     e.g.: ema, macd, rsi, adx, bbands, obv
>    pred        prediction techniques                   e.g.: regression, arima, rnn, lstm, conv1d, monte carlo{'[/dim]' if not self.current_coin else ''}
"""  # noqa
        t_console.print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

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

        (known_args, other_args) = self.crypto_parser.parse_known_args(an_input.split())

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

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "crypto")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")

    @try_except
    def call_prt(self, other_args):
        """Process prt command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="prt",
                description="Potential Returns Tool"
                "Tool to check returns if loaded coin reaches provided price or other crypto market cap"
                "Uses CoinGecko to grab coin data (price and market cap).",
            )
            group = parser.add_mutually_exclusive_group(required=True)
            group.add_argument(
                "--vs", help="Coin to compare with", dest="vs", type=str, default=None
            )
            group.add_argument(
                "-p",
                "--price",
                help="Desired price",
                dest="price",
                type=int,
                default=None,
            )
            group.add_argument(
                "-t",
                "--top",
                help="Compare with top N coins",
                dest="top",
                type=int,
                default=None,
            )
            if other_args and "-" not in other_args[0][0]:
                other_args.insert(0, "--vs")

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if ns_parser:
                if ns_parser.vs:
                    coin_found = pycoingecko_model.check_coin(ns_parser.vs)
                    if not coin_found:
                        print(f"VS Coin '{ns_parser.vs}' not found in CoinGecko\n")
                        return
                pycoingecko_view.display_coin_potential_returns(
                    self.coin_map_df["CoinGecko"],
                    ns_parser.vs,
                    ns_parser.top,
                    ns_parser.price,
                )

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_coins(self, other_args):
        """Process coins command"""
        parser = argparse.ArgumentParser(
            prog="coins",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows list of coins available on CoinGecko, CoinPaprika and Binance.If you provide name of
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
            help="Coin you search for",
            dest="coin",
            required="-h" not in other_args,
            type=str,
        )

        parser.add_argument(
            "-s",
            "--skip",
            default=0,
            dest="skip",
            help="Skip n of records",
            type=check_positive,
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
            "--source",
            dest="source",
            help="Source of data.",
            type=str,
            choices=CRYPTO_SOURCES.keys(),
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            display_all_coins(
                coin=ns_parser.coin,
                source=ns_parser.source,
                top=ns_parser.limit,
                skip=ns_parser.skip,
                show_all=bool("ALL" in other_args),
                export=ns_parser.export,
            )

    @try_except
    def call_load(self, other_args):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load crypto currency to perform analysis on."
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
            "--source",
            help="Source of data",
            dest="source",
            choices=("cp", "cg", "bin", "cb"),
            default="cg",
            required=False,
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date_in_past,
            default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the crypto",
        )
        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs)",
            dest="vs",
            default="usd",
            type=str,
        )
        parser.add_argument(
            "-i",
            "--interval",
            help="Interval to get data (Only available on binance/coinbase)",
            dest="interval",
            default="1day",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        delta = (datetime.now() - ns_parser.start).days
        if ns_parser:
            source = ns_parser.source
            for arg in ["--source", source]:
                if arg in other_args:
                    other_args.remove(arg)

            # TODO: protections in case None is returned
            (
                self.current_coin,
                self.source,
                self.symbol,
                self.coin_map_df,
                self.current_df,
                self.current_currency,
            ) = load(
                coin=ns_parser.coin,
                source=ns_parser.source,
                should_load_ta_data=True,
                days=delta,
                interval=ns_parser.interval,
                vs=ns_parser.vs,
            )
            if self.symbol:
                self.current_interval = ns_parser.interval
                first_price = self.current_df["Close"].iloc[0]
                last_price = self.current_df["Close"].iloc[-1]
                second_last_price = self.current_df["Close"].iloc[-2]
                interval_change = calc_change(last_price, second_last_price)
                since_start_change = calc_change(last_price, first_price)
                if isinstance(self.current_currency, str):
                    self.price_str = f"""Current Price: {round(last_price,2)} {self.current_currency.upper()}
Performance in interval ({self.current_interval}): {'[green]' if interval_change > 0 else "[red]"}{round(interval_change,2)}%{'[/green]' if interval_change > 0 else "[/red]"}
Performance since {ns_parser.start.strftime('%Y-%m-%d')}: {'[green]' if since_start_change > 0 else "[red]"}{round(since_start_change,2)}%{'[/green]' if since_start_change > 0 else "[/red]"}"""  # noqa

                    t_console.print(
                        f"""
Loaded {self.current_coin} against {self.current_currency} from {CRYPTO_SOURCES[self.source]} source

{self.price_str}
"""
                    )  # noqa

    @try_except
    def call_chart(self, other_args):
        """Process chart command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="chart",
                description="""Display chart for loaded coin. You can specify currency vs which you want
                to show chart and also number of days to get data for.""",
            )

            if self.source == "cp":
                parser.add_argument(
                    "--vs",
                    default="usd",
                    dest="vs",
                    help="Currency to display vs coin",
                    choices=["usd", "btc", "BTC", "USD"],
                    type=str,
                )
                parser.add_argument(
                    "-d",
                    "--days",
                    default=30,
                    dest="days",
                    help="Number of days to get data for",
                    type=check_positive,
                )

            if self.source == "cg":
                parser.add_argument(
                    "--vs", default="usd", dest="vs", help="Currency to display vs coin"
                )
                parser.add_argument(
                    "-d",
                    "--days",
                    default=30,
                    dest="days",
                    help="Number of days to get data for",
                )

            if self.source == "bin":
                client = Client(cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET)
                interval_map = {
                    "1day": client.KLINE_INTERVAL_1DAY,
                    "3day": client.KLINE_INTERVAL_3DAY,
                    "1hour": client.KLINE_INTERVAL_1HOUR,
                    "2hour": client.KLINE_INTERVAL_2HOUR,
                    "4hour": client.KLINE_INTERVAL_4HOUR,
                    "6hour": client.KLINE_INTERVAL_6HOUR,
                    "8hour": client.KLINE_INTERVAL_8HOUR,
                    "12hour": client.KLINE_INTERVAL_12HOUR,
                    "1week": client.KLINE_INTERVAL_1WEEK,
                    "1min": client.KLINE_INTERVAL_1MINUTE,
                    "3min": client.KLINE_INTERVAL_3MINUTE,
                    "5min": client.KLINE_INTERVAL_5MINUTE,
                    "15min": client.KLINE_INTERVAL_15MINUTE,
                    "30min": client.KLINE_INTERVAL_30MINUTE,
                    "1month": client.KLINE_INTERVAL_1MONTH,
                }

                _, quotes = binance_model.show_available_pairs_for_given_symbol(
                    self.current_coin
                )

                parser.add_argument(
                    "--vs",
                    help="Quote currency (what to view coin vs)",
                    dest="vs",
                    type=str,
                    default="USDT",
                    choices=quotes,
                )
                parser.add_argument(
                    "-i",
                    "--interval",
                    help="Interval to get data",
                    choices=list(interval_map.keys()),
                    dest="interval",
                    default="1day",
                    type=str,
                )
                parser.add_argument(
                    "-l",
                    "--limit",
                    dest="limit",
                    default=100,
                    help="Number to get",
                    type=check_positive,
                )

            if self.source == "cb":
                interval_map = {
                    "1min": 60,
                    "5min": 300,
                    "15min": 900,
                    "1hour": 3600,
                    "6hour": 21600,
                    "24hour": 86400,
                    "1day": 86400,
                }

                _, quotes = coinbase_model.show_available_pairs_for_given_symbol(
                    self.current_coin
                )
                if len(quotes) < 0:
                    print(
                        f"Couldn't find any quoted coins for provided symbol {self.current_coin}"
                    )
                    return
                parser.add_argument(
                    "--vs",
                    help="Quote currency (what to view coin vs)",
                    dest="vs",
                    type=str,
                    default="USDT" if "USDT" in quotes else quotes[0],
                    choices=quotes,
                )
                parser.add_argument(
                    "-i",
                    "--interval",
                    help="Interval to get data",
                    choices=list(interval_map.keys()),
                    dest="interval",
                    default="1day",
                    type=str,
                )
                parser.add_argument(
                    "-l",
                    "--limit",
                    dest="limit",
                    default=100,
                    help="Number to get",
                    type=check_positive,
                )
            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
            )

            if ns_parser:
                if self.source in ["bin", "cb"]:
                    limit = ns_parser.limit
                    interval = ns_parser.interval
                    days = 0
                else:
                    limit = 0
                    interval = "1day"
                    days = ns_parser.days

                plot_chart(
                    coin_map_df=self.coin_map_df,
                    limit=limit,
                    interval=interval,
                    days=days,
                    currency=ns_parser.vs,
                    source=self.source,
                )

    @try_except
    def call_ta(self, _):
        """Process ta command"""
        from gamestonk_terminal.cryptocurrency.technical_analysis import ta_controller

        # TODO: Play with this to get correct usage
        if self.current_coin:
            if self.current_currency != "" and not self.current_df.empty:
                self.queue = ta_controller.menu(
                    stock=self.current_df,
                    ticker=self.current_coin,
                    start=self.current_df.index[0],
                    interval="",
                    queue=self.queue,
                )

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    @try_except
    def call_disc(self, _):
        """Process disc command"""
        from gamestonk_terminal.cryptocurrency.discovery import discovery_controller

        self.queue = discovery_controller.menu(queue=self.queue)

    @try_except
    def call_ov(self, _):
        """Process ov command"""
        from gamestonk_terminal.cryptocurrency.overview import overview_controller

        self.queue = overview_controller.menu(queue=self.queue)

    @try_except
    def call_defi(self, _):
        """Process defi command"""
        from gamestonk_terminal.cryptocurrency.defi import defi_controller

        self.queue = defi_controller.menu(queue=self.queue)

    @try_except
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            finbrain_crypto_view.display_crypto_sentiment_analysis(
                coin=ns_parser.coin, export=ns_parser.export
            )

    @try_except
    def call_dd(self, _):
        """Process dd command"""
        if self.current_coin:
            from gamestonk_terminal.cryptocurrency.due_diligence import dd_controller

            self.queue = dd_controller.menu(
                self.current_coin,
                self.source,
                self.symbol,
                self.coin_map_df,
                queue=self.queue,
            )
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    @try_except
    def call_pred(self, _):
        """Process pred command"""
        if self.current_coin:
            from gamestonk_terminal.cryptocurrency.prediction_techniques import (
                pred_controller,
            )

            if self.current_interval != "1day":
                print("Only interval `1day` is possible for now.\n")
            else:
                self.queue = pred_controller.menu(
                    self.current_coin,
                    self.current_df,
                    self.queue,
                )
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    @try_except
    def call_onchain(self, _):
        """Process onchain command"""
        from gamestonk_terminal.cryptocurrency.onchain import onchain_controller

        self.queue = onchain_controller.menu(queue=self.queue)

    @try_except
    def call_nft(self, _):
        """Process nft command"""
        from gamestonk_terminal.cryptocurrency.nft import nft_controller

        self.queue = nft_controller.menu(queue=self.queue)

    @try_except
    def call_find(self, other_args):
        """Process find command"""
        parser = argparse.ArgumentParser(
            prog="find",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at CoinGecko,
            Binance, Coinbase or CoinPaprika you can use this command to display coins with similar name, symbol or id
            to your search query.
            Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
            It will search for coin that has similar name to polka and display top 25 matches.
            -c, --coin stands for coin - you provide here your search query
            -k, --key it's a searching key. You can search by symbol, id or name of coin
            -l, --limit it displays top N number of records.""",
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
            "--source",
            dest="source",
            choices=CRYPTO_SOURCES.keys(),
            default="cg",
            help="Source of data.",
            type=str,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            find(
                coin=ns_parser.coin,
                source=ns_parser.source,
                key=ns_parser.key,
                top=ns_parser.limit,
                export=ns_parser.export,
            )


def menu(queue: List[str] = None):
    crypto_controller = CryptoController(queue)
    first = True

    while True:
        # There is a command in the queue
        if crypto_controller.queue and len(crypto_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if crypto_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(crypto_controller.queue) > 1:
                    return crypto_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = crypto_controller.queue[0]
            crypto_controller.queue = crypto_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in crypto_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /crypto/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if first:
                crypto_controller.print_help()
                first = False

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and crypto_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /crypto/ $ ",
                        completer=crypto_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"

            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/ $ ")

        try:
            # Process the input command
            crypto_controller.queue = crypto_controller.switch(an_input)
        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /crypto menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                crypto_controller.CHOICES,
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
                        crypto_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                crypto_controller.queue.insert(0, an_input)
            else:
                print("\n")
