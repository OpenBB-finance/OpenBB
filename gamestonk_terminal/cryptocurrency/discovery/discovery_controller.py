"""Cryptocurrency Discovery Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622, C0201
import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_known_args_and_warn,
    check_positive,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.discovery import (
    coinmarketcap_model,
    coinpaprika_model,
    dappradar_view,
    pycoingecko_model,
    pycoingecko_view,
    coinpaprika_view,
    coinmarketcap_view,
)


class DiscoveryController(BaseController):
    """Discovery Controller class"""

    CHOICES_COMMANDS = [
        "cpsearch",
        "cmctop",
        "cgtrending",
        "cgvolume",
        "cggainers",
        "cglosers",
        "cgdefi",
        "cgtop",
        "drnft",
        "drgames",
        "drdapps",
        "drdex",
    ]

    PATH = "/crypto/disc/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["cggainers"]["-p"] = {c: {} for c in pycoingecko_model.API_PERIODS}
            choices["cglosers"]["-p"] = {c: {} for c in pycoingecko_model.API_PERIODS}
            choices["cgtrending"]["-s"] = {
                c: {} for c in pycoingecko_model.TRENDING_FILTERS
            }
            choices["cgtop"] = {
                c: None for c in pycoingecko_model.get_categories_keys()
            }
            choices["cgtop"]["--category"] = {
                c: None for c in pycoingecko_model.get_categories_keys()
            }
            choices["cgvolume"]["-s"] = {c: {} for c in pycoingecko_model.CAP_FILTERS}
            choices["cgdefi"]["-s"] = {c: {} for c in pycoingecko_model.CAP_FILTERS}
            choices["cmctop"]["-s"] = {c: {} for c in coinmarketcap_model.FILTERS}
            choices["cpsearch"]["-s"] = {c: {} for c in coinpaprika_model.FILTERS}
            choices["cpsearch"]["-c"] = {c: {} for c in coinpaprika_model.CATEGORIES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[cmds]
[src][CoinGecko][/src]
    cgtop             top coins (with or withoug category)
    cgtrending        trending coins
    cgvolume          coins with highest volume
    cggainers         top gainers - coins which price gained the most in given period
    cglosers          top losers - coins which price dropped the most in given period
    cgdefi            decentralized finance coins
[src][CoinPaprika][/src]
    cpsearch          search for coins
[src][CoinMarketCap][/src]
    cmctop            top coins
[src][DappRadar][/src]
    drnft             top non fungible tokens
    drgames           top blockchain games
    drdapps           top decentralized apps
    drdex             top decentralized exchanges
[/cmds]
"""
        console.print(text=help_text, menu="Cryptocurrency - Discovery")

    def call_cgtop(self, other_args):
        """Process cgtop command"""
        parser = argparse.ArgumentParser(
            prog="cgtop",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Check coins by category and market cap. [Source: CoinGecko]""",
        )

        parser.add_argument(
            "-c",
            "--category",
            default="",
            dest="category",
            help="Category (e.g., stablecoins). Empty for no category",
        )

        parser.add_argument(
            "-l",
            "--limit",
            default=10,
            dest="limit",
            help="Limit of records",
            type=check_positive,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_coins(
                category=ns_parser.category,
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_drdapps(self, other_args):
        """Process drdapps command"""
        parser = argparse.ArgumentParser(
            prog="drdapps",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
            You can look on only N number of records with --limit,
            You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag to set it
            to sort descending.
            There is --urls flag, which will display one additional column you all urls for coins.
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_dapps(
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_drgames(self, other_args):
        """Process drgames command"""
        parser = argparse.ArgumentParser(
            prog="drgames",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
            You can look on only N number of records with --limit,
            You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag to set it
            to sort descending.
            There is --urls flag, which will display one additional column you all urls for coins.
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_games(
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_drdex(self, other_args):
        """Process drdex command"""
        parser = argparse.ArgumentParser(
            prog="drdex",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
            You can look on only N number of records with --limit,
            You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag to set it
            to sort descending.
            There is --urls flag, which will display one additional column you all urls for coins.
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_dexes(
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_drnft(self, other_args):
        """Process drnft command"""
        parser = argparse.ArgumentParser(
            prog="drnft",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
            You can look on only N number of records with --limit,
            You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag to set it
            to sort descending.
            There is --urls flag, which will display one additional column you all urls for coins.
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_nfts(
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_cggainers(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="cggainers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
            You can look on only N number of records with --limit,
            You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag to set it
            to sort descending.
            There is --urls flag, which will display one additional column you all urls for coins.
            """,
        )

        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            type=str,
            help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
            default="1h",
            choices=pycoingecko_model.API_PERIODS,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_gainers(
                period=ns_parser.period,
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_cglosers(self, other_args):
        """Process losers command"""
        parser = argparse.ArgumentParser(
            prog="cglosers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
           Shows Largest Losers - coins which price dropped the most in given period
           You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
           You can look on only N number of records with --limit,
           You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag
           to sort descending.
           Flag --urls will display one additional column with all coingecko urls for listed coins.
            """,
        )

        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            type=str,
            help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
            default="1h",
            choices=pycoingecko_model.API_PERIODS,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_losers(
                period=ns_parser.period,
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    def call_cgtrending(self, other_args):
        """Process trending command"""
        parser = argparse.ArgumentParser(
            prog="cgtrending",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Discover trending coins.
                Use --limit parameter to display only N number of records,
                You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
                to sort descending.
                Flag --urls will display one additional column with all coingecko urls for listed coins.
                trending will display: Rank, Name, Price_BTC, Price_USD
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_trending(
                export=ns_parser.export,
            )

    def call_cgvolume(self, other_args):
        """Process volume command"""
        parser = argparse.ArgumentParser(
            prog="cgvolume",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top Coins by Trading Volume.
                You can display only N number of coins with --limit parameter.
                You can sort data by on of columns  Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d,
                Volume_24h, Market_Cap with --sort parameter and also with --descend flag to sort descending.
                Displays columns:  Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.CAP_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_top_volume_coins(
                top=ns_parser.limit,
                # sortby=ns_parser.sortby,
                # descend=ns_parser.descend,
                export=ns_parser.export,
            )

    def call_cgdefi(self, other_args):
        """Process defi command"""
        parser = argparse.ArgumentParser(
            prog="cgdefi",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top DeFi Coins by Market Capitalization
               DeFi or Decentralized Finance refers to financial services that are built
               on top of distributed networks with no central intermediaries.
               You can display only N number of coins with --limit parameter.
               You can sort data by Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d,
                Volume 24h, Market Cap, Url with --sort and also with --descend flag to sort descending.
               Flag --urls will display  urls""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=pycoingecko_model.CAP_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-u",
            "--urls",
            dest="urls",
            action="store_true",
            help="Flag to show urls",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_top_defi_coins(
                top=ns_parser.limit,
                # sortby=ns_parser.sortby,
                # descend=ns_parser.descend,
                # links=ns_parser.urls,
                export=ns_parser.export,
            )

    def call_cmctop(self, other_args):
        """Process cmctop command"""
        parser = argparse.ArgumentParser(
            prog="cmctop",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="This gets the top ranked coins from coinmarketcap.com",
        )

        parser.add_argument(
            "-l",
            "--limit",
            default=15,
            dest="limit",
            help="Limit of records",
            type=check_positive,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="column to sort data by.",
            default="CMC_Rank",
            choices=coinmarketcap_model.FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinmarketcap_view.display_cmc_top_coins(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    def call_cpsearch(self, other_args):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpsearch",
            description="""Search over CoinPaprika API
            You can display only N number of results with --limit parameter.
            You can sort data by id, name , category --sort parameter and also with --descend flag to sort descending.
            To choose category in which you are searching for use --cat/-c parameter. Available categories:
            currencies|exchanges|icos|people|tags|all
            Displays:
                id, name, category""",
        )

        parser.add_argument(
            "-q",
            "--query",
            help="phrase for search",
            dest="query",
            nargs="+",
            type=str,
            required="-h" not in other_args,
        )

        parser.add_argument(
            "-c",
            "--cat",
            help="Categories to search: currencies|exchanges|icos|people|tags|all. Default: all",
            dest="category",
            default="all",
            type=str,
            choices=coinpaprika_model.CATEGORIES,
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
            help="Sort by given column. Default: id",
            default="id",
            choices=coinpaprika_model.FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-q")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_search_results(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
                query=" ".join(ns_parser.query),
                category=ns_parser.category,
            )
