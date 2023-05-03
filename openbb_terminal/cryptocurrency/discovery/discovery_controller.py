"""Cryptocurrency Discovery Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622, C0201
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.discovery import (
    coinmarketcap_model,
    coinmarketcap_view,
    coinpaprika_model,
    coinpaprika_view,
    cryptostats_view,
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
    valid_date,
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
        "nft_mktp_chains",
        "nft_mktp",
        "dapps",
        "fees",
        "dapp_categories",
        "dapp_chains",
        "dapp_metrics",
        "defi_chains",
        "tokens",
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
        mt.add_cmd("nft_mktp_chains")
        mt.add_cmd("nft_mktp")
        mt.add_cmd("dapps")
        mt.add_cmd("fees")
        mt.add_cmd("dapp_categories")
        mt.add_cmd("dapp_chains")
        mt.add_cmd("dapp_metrics")
        mt.add_cmd("defi_chains")
        mt.add_cmd("tokens")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Discovery")

    @log_start_end(log=logger)
    def call_fees(self, other_args: List[str]):
        """Process fees command"""

        parser = argparse.ArgumentParser(
            prog="fees",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Cryptos where users pay most fees on [Source: CryptoStats]
            """,
        )

        parser.add_argument(
            "--mc",
            action="store_true",
            dest="marketcap",
            default=False,
            help="Include the market cap rank",
        )
        parser.add_argument(
            "--tvl",
            action="store_true",
            dest="tvl",
            default=False,
            help="Include the total value locked",
        )

        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=valid_date,
            help="Initial date. Default: yesterday",
            default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            nargs="+",
            help="Sort by given column. Default: One Day Fees",
            default="One Day Fees",
            choices=["One Day Fees", "Market Cap Rank"],
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
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )

        if ns_parser:
            cryptostats_view.display_fees(
                marketcap=ns_parser.marketcap,
                tvl=ns_parser.tvl,
                date=ns_parser.date,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
            )

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
            Shows available decentralized applications [Source: https://dappradar.com/]
            Accepts --chain argument to filter by blockchain
                    --page argument to show a specific page. Default: 1
                    --limit argument to limit the number of records per page. Default: 15
            """,
        )
        parser.add_argument(
            "-c",
            "--chain",
            dest="chain",
            help="Filter by blockchain",
            metavar="CHAIN",
        )
        parser.add_argument(
            "-p",
            "--page",
            dest="page",
            type=check_positive,
            help="Page number",
            default=1,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display per page",
            default=15,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_dapps(
                chain=ns_parser.chain,
                page=ns_parser.page,
                resultPerPage=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_dapp_categories(self, other_args):
        """Process dapp_categories command"""
        parser = argparse.ArgumentParser(
            prog="dapp_categories",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows available dapp categories [Source: https://dappradar.com/]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_dapp_categories(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_dapp_chains(self, other_args):
        """Process dapp_chains command"""
        parser = argparse.ArgumentParser(
            prog="dapp_chains",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows available dapp chains [Source: https://dappradar.com/]
            """,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_dapp_chains(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_dapp_metrics(self, other_args):
        """Process dapp_metrics command"""
        parser = argparse.ArgumentParser(
            prog="dapp_metrics",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows dapp metrics [Source: https://dappradar.com/]
            Accepts --dappId argument to specify the dapp
                    --chain argument to filter by blockchain for multi-chain dapps
                    --time_range argument to specify the time range. Default: 7d (can be 24h, 7d, 30d)
            """,
        )
        parser.add_argument(
            "-d",
            "--dappId",
            dest="dappId",
            help="Dapp ID",
            metavar="DAPP_ID",
        )
        parser.add_argument(
            "-c",
            "--chain",
            dest="chain",
            help="Filter by blockchain",
            metavar="CHAIN",
        )
        parser.add_argument(
            "-t",
            "--time_range",
            dest="time_range",
            help="Time range",
            metavar="TIME_RANGE",
            choices=["24h", "7d", "30d"],
            default="7d",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_dapp_metrics(
                dappId=ns_parser.dappId,
                chain=ns_parser.chain,
                time_range=ns_parser.time_range,
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

    @log_start_end(log=logger)
    def call_nft_mktp_chains(self, other_args):
        """Process nft_mktp_chains command"""
        parser = argparse.ArgumentParser(
            prog="nft_mktp_chains",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows NFT marketplace chains [Source: https://dappradar.com/]
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            dappradar_view.display_nft_marketplace_chains(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_defi_chains(self, other_args):
        """Process defi_chains command"""
        parser = argparse.ArgumentParser(
            prog="defi_chains",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows DeFi chains [Source: https://dappradar.com/]
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            dappradar_view.display_defi_chains(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_nft_mktp(self, other_args):
        """Process nft_mktp command"""
        parser = argparse.ArgumentParser(
            prog="nft_mktp",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows NFT marketplaces [Source: https://dappradar.com/]
            Accepts --chain  to filter by blockchain
                    --sortby {name, avgPrice, volume, traders...} to sort by column
                    --order {asc, desc} to sort ascending or descending
                    --limit to limit number of records
            """,
        )
        parser.add_argument(
            "-c",
            "--chain",
            dest="chain",
            help="Name of the blockchain to filter by.",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            nargs="+",
            help="Sort by given column.",
            choices=stocks_helper.format_parse_choices(dappradar_model.NFT_COLUMNS),
            metavar="SORTBY",
        )
        parser.add_argument(
            "-o",
            "--order",
            dest="order",
            help="Order of sorting. Default: desc",
            default="desc",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_nft_marketplaces(
                sortby=ns_parser.sortby,
                order=ns_parser.order,
                chain=ns_parser.chain,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_tokens(self, other_args):
        """Process tokens command"""
        parser = argparse.ArgumentParser(
            prog="tokens",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows chains that support tokens [Source: https://dappradar.com/]
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            dappradar_view.display_token_chains(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
