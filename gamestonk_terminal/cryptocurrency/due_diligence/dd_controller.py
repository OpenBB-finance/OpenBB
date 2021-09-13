"""Cryptocurrency Due diligence Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import os
import pandas as pd
from binance.client import Client
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.due_diligence import (
    pycoingecko_view,
    coinpaprika_view,
    binance_view,
    coinbase_model,
    binance_model,
    coinbase_view,
)
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
)

from gamestonk_terminal.cryptocurrency.due_diligence.coinpaprika_view import CURRENCIES
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import plot_chart
import gamestonk_terminal.config_terminal as cfg


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
        "cb": ["book", "trades", "stats"],
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
        if self.source == "cb":
            help_text += """
Coinbase:
   book            show order book
   trades          show last trades
   stats           show coin stats
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
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="info",
                description="""
                     Shows basic information about loaded coin like:
                     Name, Symbol, Description, Market Cap, Public Interest, Supply, and Price related metrics
                     """,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_info(
                    coin=self.current_coin, export=ns_parser.export
                )

            except Exception as e:
                print(e, "\n")

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_market(self, other_args):
        """Process market command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="market",
                description="""
                Market data for loaded coin. There you find metrics like:
                Market Cap, Supply, Circulating Supply, Price, Volume and many others.
                                    """,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_market(self.current_coin, ns_parser.export)

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_web(self, other_args):
        """Process web command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="web",
                description="""Websites found for given Coin. You can find there urls to
                                   homepage, forum, announcement site and others.""",
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_web(self.current_coin, export=ns_parser.export)

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_social(self, other_args):
        """Process social command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="social",
                description="""Shows social media corresponding to loaded coin. You can find there name of
                telegram channel, urls to twitter, reddit, bitcointalk, facebook and discord.""",
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_social(
                    self.current_coin, export=ns_parser.export
                )

            except Exception as e:
                print(e, "\n")

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_dev(self, other_args):
        """Process dev command"""
        if self.current_coin:
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

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_dev(self.current_coin, ns_parser.export)

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_ath(self, other_args):
        """Process ath command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="ath",
                description="""All time high data for loaded coin""",
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            parser.add_argument(
                "--vs",
                dest="vs",
                help="currency",
                default="usd",
                choices=["usd", "btc"],
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return
                pycoingecko_view.display_ath(
                    self.current_coin, ns_parser.vs, ns_parser.export
                )

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_atl(self, other_args):
        """Process atl command"""
        if self.current_coin:
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
                choices=["usd", "btc"],
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_atl(
                    self.current_coin, ns_parser.vs, ns_parser.export
                )

            except Exception as e:
                print(e, "\n")

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_score(self, other_args):
        """Process score command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="score",
                description="""
                In this view you can find different kind of scores for loaded coin.
                Those scores represents different rankings, sentiment metrics, some user stats and others.
                You will see CoinGecko scores, Developer Scores, Community Scores, Sentiment, Reddit scores
                and many others.
                                    """,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_score(self.current_coin, ns_parser.export)

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_bc(self, other_args):
        """Process bc command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="bc",
                description="""
                Blockchain explorers URLs for loaded coin. Those are sites like etherescan.io or polkascan.io
                in which you can see all blockchain data e.g. all txs, all tokens, all contracts...
                                    """,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                pycoingecko_view.display_bc(self.current_coin, ns_parser.export)

            except Exception as e:
                print(e, "\n")

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    # binance
    def call_book(self, other_args):
        """Process book command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                prog="book",
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="Get the order book for selected coin",
            )

            if self.source == "bin":

                limit_list = [5, 10, 20, 50, 100, 500, 1000, 5000]
                _, quotes = binance_model.show_available_pairs_for_given_symbol(
                    self.current_coin
                )

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

            if self.source == "cb":
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
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:

                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return

                if self.source == "bin":
                    binance_view.display_order_book(
                        coin=self.current_coin,
                        limit=ns_parser.limit,
                        currency=ns_parser.vs,
                        export=ns_parser.export,
                    )

                elif self.source == "cb":
                    pair = f"{self.current_coin.upper()}-{ns_parser.vs.upper()}"
                    coinbase_view.display_order_book(
                        product_id=pair,
                        export=ns_parser.export,
                    )

            except Exception as e:
                print(e, "\n")

    def call_balance(self, other_args):
        """Process balance command"""
        _, quotes = binance_model.show_available_pairs_for_given_symbol(
            self.current_coin
        )

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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return
            binance_view.display_balance(
                coin=self.current_coin, currency=ns_parser.vs, export=ns_parser.export
            )

        except Exception as e:
            print(e, "\n")

    def call_trades(self, other_args):
        """Process trades command"""
        parser = argparse.ArgumentParser(
            prog="trades",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Show last trades on Coinbase",
        )

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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            pair = f"{self.current_coin.upper()}-{ns_parser.vs.upper()}"
            if ns_parser.side.upper() == "all":
                side = None
            else:
                side = ns_parser.side

            coinbase_view.display_trades(
                product_id=pair, limit=ns_parser.top, side=side, export=ns_parser.export
            )

        except Exception as e:
            print(e, "\n")

    def call_stats(self, other_args):
        """Process stats command"""
        _, quotes = coinbase_model.show_available_pairs_for_given_symbol(
            self.current_coin
        )

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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            pair = f"{self.current_coin.upper()}-{ns_parser.vs.upper()}"
            coinbase_view.display_stats(pair, ns_parser.export)

        except Exception as e:
            print(e, "\n")

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

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)

                if not ns_parser:
                    return

                if self.source in ["bin", "cb"]:
                    limit = ns_parser.limit
                    interval = ns_parser.interval
                    days = 0
                else:
                    limit = 0
                    interval = "1day"
                    days = ns_parser.days

                plot_chart(
                    coin=self.current_coin,
                    limit=limit,
                    interval=interval,
                    days=days,
                    currency=ns_parser.vs,
                    source=self.source,
                )

            except Exception as e:
                print(e, "\n")

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    # paprika
    def call_ps(self, other_args):
        """Process ps command"""
        if self.current_coin:
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
                choices=CURRENCIES,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return

                coinpaprika_view.display_price_supply(
                    self.current_coin, ns_parser.vs, ns_parser.export
                )

            except Exception as e:
                print(e, "\n")

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_basic(self, other_args):
        """Process basic command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                prog="basic",
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="""Get basic information for coin. Like:
                    name, symbol, rank, type, description, platform, proof_type,
                    contract, tags, parent""",
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return

                coinpaprika_view.display_basic(self.current_coin, ns_parser.export)

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_mkt(self, other_args):
        """Process mkt command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                prog="mkt",
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="""Get all markets found for given coin.
                    You can display only top N number of markets with --top parameter.
                    You can sort data by pct_volume_share, exchange, pair, trust_score, volume, price --sort parameter
                    and also with --descend flag to sort descending.
                    You can use additional flag --links to see urls for each market
                    Displays:
                        exchange, pair, trust_score, volume, price, pct_volume_share,""",
            )

            parser.add_argument(
                "--vs",
                help="Quoted currency. Default USD",
                dest="vs",
                default="USD",
                type=str,
                choices=CURRENCIES,
            )

            parser.add_argument(
                "-t",
                "--top",
                default=20,
                dest="top",
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
                choices=[
                    "pct_volume_share",
                    "exchange",
                    "pair",
                    "trust_score",
                    "volume",
                    "price",
                ],
            )

            parser.add_argument(
                "--descend",
                action="store_false",
                help="Flag to sort in descending order (lowest first)",
                dest="descend",
                default=False,
            )

            parser.add_argument(
                "-l",
                "--links",
                dest="links",
                action="store_true",
                help="""Flag to show urls. If you will use that flag you will see only:
                    exchange, pair, trust_score, market_url columns""",
                default=False,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return

                coinpaprika_view.display_markets(
                    coin_id=self.current_coin,
                    currency=ns_parser.vs,
                    top=ns_parser.top,
                    sortby=ns_parser.sortby,
                    descend=ns_parser.descend,
                    links=ns_parser.links,
                    export=ns_parser.export,
                )

            except Exception as e:
                print(e, "\n")

        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_ex(self, other_args):
        """Process ex command"""
        if self.current_coin:
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
                "-t",
                "--top",
                default=10,
                dest="top",
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
                choices=["id", "name", "adjusted_volume_24h_share", "fiats"],
            )

            parser.add_argument(
                "--descend",
                action="store_false",
                help="Flag to sort in descending order (lowest first)",
                dest="descend",
                default=False,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return

                coinpaprika_view.display_exchanges(
                    coin_id=self.current_coin,
                    top=ns_parser.top,
                    sortby=ns_parser.sortby,
                    descend=ns_parser.descend,
                    export=ns_parser.export,
                )

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_events(self, other_args):
        """Process events command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                prog="events",
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="""
                Show information about most important coins events. Most of coins doesn't have any events.
                You can display only top N number of events with --top parameter.
                You can sort data by id, date , date_to, name, description, is_conference --sort parameter
                and also with --descend flag to sort descending.
                You can use additional flag --links to see urls for each event
                Displays:
                    date , date_to, name, description, is_conference, link, proof_image_link""",
            )

            parser.add_argument(
                "-t",
                "--top",
                default=10,
                dest="top",
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
                choices=["date", "date_to", "name", "description", "is_conference"],
            )

            parser.add_argument(
                "--descend",
                action="store_false",
                help="Flag to sort in descending order (lowest first)",
                dest="descend",
                default=False,
            )

            parser.add_argument(
                "-l",
                "--links",
                dest="links",
                action="store_true",
                help="Flag to show urls. If you will use that flag you will see only date, name, link columns",
                default=False,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return
                coinpaprika_view.display_events(
                    coin_id=self.current_coin,
                    top=ns_parser.top,
                    sortby=ns_parser.sortby,
                    descend=ns_parser.descend,
                    links=ns_parser.links,
                    export=ns_parser.export,
                )

            except Exception as e:
                print(e, "\n")
        else:
            print(
                "No coin selected. Use 'load' to load the coin you want to look at.\n"
            )

    def call_twitter(self, other_args):
        """Process twitter command"""
        if self.current_coin:
            parser = argparse.ArgumentParser(
                add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog="twitter",
                description="""Show last 10 tweets for given coin.
                    You can display only top N number of tweets with --top parameter.
                    You can sort data by date, user_name, status, retweet_count, like_count --sort parameter
                    and also with --descend flag to sort descending.
                    Displays:
                        date, user_name, status, retweet_count, like_count
                    """,
            )

            parser.add_argument(
                "-t",
                "--top",
                default=10,
                dest="top",
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
                choices=["date", "user_name", "status", "retweet_count", "like_count"],
            )

            parser.add_argument(
                "--descend",
                action="store_false",
                help="Flag to sort in descending order (lowest first)",
                dest="descend",
                default=False,
            )

            parser.add_argument(
                "--export",
                choices=["csv", "json", "xlsx"],
                default="",
                type=str,
                dest="export",
                help="Export dataframe data to csv,json,xlsx file",
            )

            try:
                ns_parser = parse_known_args_and_warn(parser, other_args)
                if not ns_parser:
                    return

                coinpaprika_view.display_twitter(
                    coin_id=self.current_coin,
                    top=ns_parser.top,
                    sortby=ns_parser.sortby,
                    descend=ns_parser.descend,
                    export=ns_parser.export,
                )

            except Exception as e:
                print(e, "\n")
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
