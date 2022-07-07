"""Cryptocurrency Discovery Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622, C0201
import argparse
import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter


from openbb_terminal import feature_flags as obbff
from openbb_terminal.cryptocurrency.discovery import (
    coinmarketcap_model,
    coinmarketcap_view,
    coinpaprika_model,
    coinpaprika_view,
    dappradar_model,
    dappradar_view,
    pycoingecko_model,
    pycoingecko_view,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class DiscoveryController(BaseController):
    """Discovery Controller class"""

    CHOICES_COMMANDS = [
        "cpsearch",
        "cmctop",
        "cgtrending",
        "cggainers",
        "cglosers",
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

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["cggainers"]["-p"] = {c: {} for c in pycoingecko_model.API_PERIODS}
            choices["cggainers"]["--sort"] = {
                c: {} for c in pycoingecko_model.GAINERS_LOSERS_COLUMNS
            }
            choices["cglosers"]["--sort"] = {
                c: {} for c in pycoingecko_model.GAINERS_LOSERS_COLUMNS
            }
            choices["cglosers"]["-p"] = {c: {} for c in pycoingecko_model.API_PERIODS}
            choices["cgtop"] = {
                c: None for c in pycoingecko_model.get_categories_keys()
            }
            choices["cgtop"]["--category"] = {
                c: None for c in pycoingecko_model.get_categories_keys()
            }
            choices["cgtop"]["--sort"] = {
                c: None for c in pycoingecko_view.COINS_COLUMNS
            }
            choices["cmctop"]["-s"] = {c: {} for c in coinmarketcap_model.FILTERS}
            choices["cpsearch"]["-s"] = {c: {} for c in coinpaprika_model.FILTERS}
            choices["cpsearch"]["-c"] = {c: {} for c in coinpaprika_model.CATEGORIES}
            choices["drnft"]["--sort"] = {c: {} for c in dappradar_model.NFT_COLUMNS}
            choices["drgames"]["--sort"] = {c: {} for c in dappradar_model.DEX_COLUMNS}
            choices["drdex"]["--sort"] = {c: {} for c in dappradar_model.DEX_COLUMNS}
            choices["drdapps"]["--sort"] = {
                c: {} for c in dappradar_model.DAPPS_COLUMNS
            }

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/disc/")
        mt.add_cmd("cgtop", "CoinGecko")
        mt.add_cmd("cgtrending", "CoinGecko")
        mt.add_cmd("cggainers", "CoinGecko")
        mt.add_cmd("cglosers", "CoinGecko")
        mt.add_cmd("cpsearch", "CoinPaprika")
        mt.add_cmd("cmctop", "CoinMarketCap")
        mt.add_cmd("drnft", "DappRadar")
        mt.add_cmd("drgames", "DappRadar")
        mt.add_cmd("drdapps", "DappRadar")
        mt.add_cmd("drdex", "DappRadar")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Discovery")

    @log_start_end(log=logger)
    def call_cgtop(self, other_args):
        """Process cgtop command"""
        parser = argparse.ArgumentParser(
            prog="cgtop",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Display N coins from CoinGecko [Source: CoinGecko]
            can receive a category as argument (-c decentralized-finance-defi or -c stablecoins)
            and will show only the top coins in that category.
            can also receive sort arguments, e.g., --sort Volume [$]
            You can sort by {Symbol,Name,Price [$],Market Cap,Market Cap Rank,Volume [$]}
            Number of coins to show: -l 10
            """,
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
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: Market Cap Rank",
            default="Market Cap Rank",
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_coins(
                sortby=" ".join(ns_parser.sortby),
                category=ns_parser.category,
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_drdapps(self, other_args):
        """Process drdapps command"""
        parser = argparse.ArgumentParser(
            prog="drdapps",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows top decentralized applications [Source: https://dappradar.com/]
            Accepts --sort {Name,Category,Protocols,Daily Users,Daily Volume [$]}
            to sort by column
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
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: Daily Volume [$]",
            default="Daily Volume [$]",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_dapps(
                sortby=" ".join(ns_parser.sortby),
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_drgames(self, other_args):
        """Process drgames command"""
        parser = argparse.ArgumentParser(
            prog="drgames",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows top blockchain games [Source: https://dappradar.com/]
            Accepts --sort {Name,Daily Users,Daily Volume [$]}
            to sort by column
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
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: Daily Volume [$]",
            default="Daily Volume [$]",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_games(
                sortby=" ".join(ns_parser.sortby),
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_drdex(self, other_args):
        """Process drdex command"""
        parser = argparse.ArgumentParser(
            prog="drdex",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows top decentralized exchanges [Source: https://dappradar.com/]
            Accepts --sort {Name,Daily Users,Daily Volume [$]}
            to sort by column
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
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: Daily Volume [$]",
            default="Daily Volume [$]",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_dexes(
                sortby=" ".join(ns_parser.sortby),
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_drnft(self, other_args):
        """Process drnft command"""
        parser = argparse.ArgumentParser(
            prog="drnft",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows top NFT collections [Source: https://dappradar.com/]
            Accepts --sort {Name,Protocols,Floor Price [$],Avg Price [$],Market Cap,Volume [$]}
            to sort by column
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
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: Market Cap",
            default="Market Cap",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_nfts(
                sortby=" ".join(ns_parser.sortby),
                top=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_cggainers(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="cggainers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --period to set which timeframe are you interested in: {14d,1h,1y,200d,24h,30d,7d}
            You can look on only N number of records with --limit,
            You can sort by {Symbol,Name,Price [$],Market Cap,Market Cap Rank,Volume [$]} with --sort.
            """,
        )

        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            type=str,
            help="time period, one from {14d,1h,1y,200d,24h,30d,7d}",
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

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: Market Cap Rank",
            default=["Market Cap"],
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_gainers(
                period=ns_parser.period,
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=" ".join(ns_parser.sortby),
            )

    @log_start_end(log=logger)
    def call_cglosers(self, other_args):
        """Process losers command"""
        parser = argparse.ArgumentParser(
            prog="cglosers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
           Shows Largest Losers - coins which price dropped the most in given period
           You can use parameter --period to set which timeframe are you interested in: {14d,1h,1y,200d,24h,30d,7d}
           You can look on only N number of records with --limit,
           You can sort by {Symbol,Name,Price [$],Market Cap,Market Cap Rank,Volume [$]} with --sort.
            """,
        )

        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            type=str,
            help="time period, one from {14d,1h,1y,200d,24h,30d,7d}",
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

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: Market Cap Rank",
            default=["Market Cap"],
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_losers(
                period=ns_parser.period,
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=" ".join(ns_parser.sortby),
            )

    @log_start_end(log=logger)
    def call_cgtrending(self, other_args):
        """Process trending command"""
        parser = argparse.ArgumentParser(
            prog="cgtrending",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Discover trending coins (Top-7) on CoinGecko in the last 24 hours
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
        )
        if ns_parser:
            pycoingecko_view.display_trending(
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinmarketcap_view.display_cmc_top_coins(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
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
