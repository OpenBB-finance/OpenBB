"""Cryptocurrency Discovery Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622, C0201
import argparse
import logging
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
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
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console, get_ordered_list_sources
from openbb_terminal.stocks import stocks_helper

logger = logging.getLogger(__name__)


class DiscoveryController(BaseController):
    """Discovery Controller class"""

    CHOICES_COMMANDS = [
        "search",
        "top",
        "trending",
        "gainers",
        "losers",
        "nft",
        "games",
        "dapps",
        "dex",
    ]

    PATH = "/crypto/disc/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            ordered_list_sources_top = get_ordered_list_sources(f"{self.PATH}top")
            if ordered_list_sources_top and ordered_list_sources_top[0] == "CoinGecko":
                choices["top"]["--sort"] = {
                    c: {}
                    for c in stocks_helper.format_parse_choices(
                        pycoingecko_view.COINS_COLUMNS
                    )
                }
            else:
                choices["top"]["--sort"] = {
                    c: {}
                    for c in stocks_helper.format_parse_choices(
                        coinmarketcap_model.FILTERS
                    )
                }

            choices["top"]["-s"] = choices["top"]["--sort"]

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/disc/")
        mt.add_cmd("top")
        mt.add_cmd("trending")
        mt.add_cmd("gainers")
        mt.add_cmd("losers")
        mt.add_cmd("search")
        mt.add_cmd("nft")
        mt.add_cmd("games")
        mt.add_cmd("dapps")
        mt.add_cmd("dex")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Discovery")

    @log_start_end(log=logger)
    def call_top(self, other_args):
        """Process top command"""
        ordered_list_sources_top = get_ordered_list_sources(f"{self.PATH}top")

        if ordered_list_sources_top and ordered_list_sources_top[0] == "CoinGecko":
            argument_sort_default = "Market Cap Rank"
        else:
            argument_sort_default = "CMC_Rank"

        parser = argparse.ArgumentParser(
            prog="top",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Display N coins from the data source, if the data source is CoinGecko it
            can receive a category as argument (-c decentralized-finance-defi or -c stablecoins)
            and will show only the top coins in that category.
            can also receive sort arguments (these depend on the source), e.g., --sort Volume [$]
            You can sort by {Symbol,Name,Price [$],Market Cap,Market Cap Rank,Volume [$]} with CoinGecko
            Number of coins to show: -l 10
            """,
        )

        parser.add_argument(
            "-c",
            "--category",
            default="",
            dest="category",
            help="Category (e.g., stablecoins). Empty for no category. Only works for 'CoinGecko' source.",
            choices=pycoingecko_model.get_categories_keys(),
            metavar="CATEGORY",
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
            default=stocks_helper.format_parse_choices([argument_sort_default]),
            metavar="SORTBY",
        )

        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.source == "CoinGecko":
                pycoingecko_view.display_coins(
                    sortby=" ".join(ns_parser.sortby),
                    category=ns_parser.category,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    ascend=ns_parser.reverse,
                )
            elif ns_parser.source == "CoinMarketCap":
                coinmarketcap_view.display_cmc_top_coins(
                    limit=ns_parser.limit,
                    sortby=ns_parser.sortby,
                    ascend=ns_parser.reverse,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_dapps(self, other_args):
        """Process dapps command"""
        parser = argparse.ArgumentParser(
            prog="dapps",
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
            choices=stocks_helper.format_parse_choices(dappradar_model.DAPPS_COLUMNS),
            metavar="SORTBY",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_dapps(
                sortby=" ".join(ns_parser.sortby),
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_games(self, other_args):
        """Process games command"""
        parser = argparse.ArgumentParser(
            prog="games",
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
            choices=stocks_helper.format_parse_choices(dappradar_model.DEX_COLUMNS),
            metavar="SORTBY",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_games(
                sortby=" ".join(ns_parser.sortby),
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_dex(self, other_args):
        """Process dex command"""
        parser = argparse.ArgumentParser(
            prog="dex",
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
            choices=stocks_helper.format_parse_choices(dappradar_model.DEX_COLUMNS),
            metavar="SORTBY",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_dexes(
                sortby=" ".join(ns_parser.sortby),
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_nft(self, other_args):
        """Process nft command"""
        parser = argparse.ArgumentParser(
            prog="nft",
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
            choices=stocks_helper.format_parse_choices(dappradar_model.NFT_COLUMNS),
            metavar="SORTBY",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_top_nfts(
                sortby=" ".join(ns_parser.sortby),
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_gainers(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="gainers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --interval to set which timeframe are you interested in: {14d,1h,1y,200d,24h,30d,7d}
            You can look on only N number of records with --limit,
            You can sort by {Symbol,Name,Price [$],Market Cap,Market Cap Rank,Volume [$]} with --sort.
            """,
        )

        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
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
            default=["market_cap"],
            choices=stocks_helper.format_parse_choices(
                pycoingecko_model.GAINERS_LOSERS_COLUMNS
            ),
            metavar="SORTBY",
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_gainers(
                interval=ns_parser.interval,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=" ".join(ns_parser.sortby),
                ascend=ns_parser.reverse,
            )

    @log_start_end(log=logger)
    def call_losers(self, other_args):
        """Process losers command"""
        parser = argparse.ArgumentParser(
            prog="losers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
           Shows Largest Losers - coins which price dropped the most in given period
           You can use parameter --interval to set which timeframe are you interested in: {14d,1h,1y,200d,24h,30d,7d}
           You can look on only N number of records with --limit,
           You can sort by {Symbol,Name,Price [$],Market Cap,Market Cap Rank,Volume [$]} with --sort.
            """,
        )

        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
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
            choices=stocks_helper.format_parse_choices(
                pycoingecko_model.GAINERS_LOSERS_COLUMNS
            ),
            metavar="SORTBY",
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_losers(
                interval=ns_parser.interval,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=" ".join(ns_parser.sortby),
                ascend=ns_parser.reverse,
            )

    @log_start_end(log=logger)
    def call_trending(self, other_args):
        """Process trending command"""
        parser = argparse.ArgumentParser(
            prog="trending",
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
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_search(self, other_args):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="search",
            description="""Search over CoinPaprika API
            You can display only N number of results with --limit parameter.
            You can sort data by id, name , category --sort parameter and also with --reverse flag to sort descending.
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
            "--category",
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-q")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_search_results(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                query=" ".join(ns_parser.query),
                category=ns_parser.category,
            )
