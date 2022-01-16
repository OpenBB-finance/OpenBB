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
    pycoingecko_model,
    pycoingecko_view,
    coinpaprika_view,
    coinmarketcap_view,
)


class DiscoveryController(BaseController):
    """Discovery Controller class"""

    CHOICES_COMMANDS = [
        "coins",
        "cpsearch",
        "cmctop",
        "cgtrending",
        "cgvoted",
        "cgvisited",
        "cgvolume",
        "cgrecently",
        "cgsentiment",
        "cggainers",
        "cglosers",
        "cgyfarms",
        "cgdefi",
        "cgdex",
        "cgnft",
    ]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__("/crypto/disc/", queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["cggainers"]["-p"] = {
                c: {} for c in pycoingecko_model.PERIODS.keys()
            }
            choices["cggainers"]["-s"] = {
                c: {} for c in pycoingecko_model.GAINERS_FILTERS
            }
            choices["cglosers"]["-p"] = {
                c: {} for c in pycoingecko_model.PERIODS.keys()
            }
            choices["cglosers"]["-s"] = {
                c: {} for c in pycoingecko_model.GAINERS_FILTERS
            }
            choices["cgtrending"]["-s"] = {
                c: {} for c in pycoingecko_model.TRENDING_FILTERS
            }
            choices["cgvoted"]["-s"] = {
                c: {} for c in pycoingecko_model.TRENDING_FILTERS
            }
            choices["cgvisited"]["-s"] = {
                c: {} for c in pycoingecko_model.TRENDING_FILTERS
            }
            choices["cgsentiment"]["-s"] = {
                c: {} for c in pycoingecko_model.TRENDING_FILTERS
            }
            choices["cgrecently"]["-s"] = {
                c: {} for c in pycoingecko_model.RECENTLY_FILTERS
            }
            choices["cgyfarms"]["-s"] = {
                c: {} for c in pycoingecko_model.YFARMS_FILTERS
            }
            choices["cgvolume"]["-s"] = {c: {} for c in pycoingecko_model.CAP_FILTERS}
            choices["cgdefi"]["-s"] = {c: {} for c in pycoingecko_model.CAP_FILTERS}
            choices["cgnft"]["-s"] = {c: {} for c in pycoingecko_model.CAP_FILTERS}
            choices["cgdex"]["-s"] = {c: {} for c in pycoingecko_model.DEX_FILTERS}
            choices["cmctop"]["-s"] = {c: {} for c in coinmarketcap_model.FILTERS}
            choices["cpsearch"]["-s"] = {c: {} for c in coinpaprika_model.FILTERS}
            choices["cpsearch"]["-c"] = {c: {} for c in coinpaprika_model.CATEGORIES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[cmds]
[src][CoinGecko][/src]
    cgtrending        trending coins
    cgvoted           most voted coins
    cgvisited         most visited coins
    cgvolume          coins with highest volume
    cgrecently        recently added
    cgsentiment       coins with most positive sentiment
    cggainers         top gainers - coins which price gained the most in given period
    cglosers          top losers - coins which price dropped the most in given period
    cgyfarms          top yield farms
    cgdefi            top defi protocols
    cgdex             top decentralized exchanges
    cgnft             top non fungible tokens
[src][CoinPaprika][/src]
    cpsearch          search for coins
[src][CoinMarketCap][/src]
    cmctop            top coins[/cmds]
"""
        console.print(text=help_text, menu="Cryptocurrency - Discovery")

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
            choices=pycoingecko_model.PERIODS.keys(),
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
            choices=pycoingecko_model.GAINERS_FILTERS,
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
            help="Flag to show urls. If you will use that flag you will additional column with urls",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_gainers(
                period=ns_parser.period,
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
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
            choices=pycoingecko_model.PERIODS.keys(),
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
            choices=pycoingecko_model.GAINERS_FILTERS,
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
            help="Flag to show urls. If you will use that flag you will additional column with urls",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            pycoingecko_view.display_losers(
                period=ns_parser.period,
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
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
            choices=pycoingecko_model.TRENDING_FILTERS,
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
            help="Flag to show urls. If you will use that flag you will additional column with urls",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_discover(
                category="trending",
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    def call_cgvoted(self, other_args):
        """Process voted command"""
        parser = argparse.ArgumentParser(
            prog="cgvoted",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Discover most voted coins.
                Use --limit parameter to display only N number of records,
                You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
                to sort descending.
                Flag --urls will display one additional column with all coingecko urls for listed coins.
                voted will display: Rank, Name, Price_BTC, Price_USD
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
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=pycoingecko_model.TRENDING_FILTERS,
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
            help="Flag to show urls. If you will use that flag you will additional column with urls",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_discover(
                category="most_voted",
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    def call_cgrecently(self, other_args):
        """Process recently command"""
        parser = argparse.ArgumentParser(
            prog="cgrecently",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
                Shows recently added coins on CoinGecko. You can display only N number of coins with --limit parameter.
                You can sort data by Rank, Name, Symbol, Price, Change_1h, Change_24h, Added with --sort
                and also with --descend flag to sort descending.
                Flag --urls will display urls""",
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
            choices=pycoingecko_model.RECENTLY_FILTERS,
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
            pycoingecko_view.display_recently_added(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    def call_cgvisited(self, other_args):
        """Process most_visited command"""
        parser = argparse.ArgumentParser(
            prog="cgvisited",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Discover most visited coins.
            Use --limit parameter to display only N number of records,
            You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
            to sort descending.
            Flag --urls will display one additional column with all coingecko urls for listed coins.
            visited will display: Rank, Name, Price_BTC, Price_USD
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
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=pycoingecko_model.TRENDING_FILTERS,
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
            help="Flag to show urls. If you will use that flag you will additional column with urls",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_discover(
                category="most_visited",
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    def call_cgsentiment(self, other_args):
        """Process sentiment command"""
        parser = argparse.ArgumentParser(
            prog="cgsentiment",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Discover coins with positive sentiment.
            Use --limit parameter to display only N number of records,
            You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
            to sort descending.
            Flag --urls will display one additional column with all coingecko urls for listed coins.
            sentiment will display: Rank, Name, Price_BTC, Price_USD
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
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=pycoingecko_model.TRENDING_FILTERS,
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
            help="Flag to show urls. If you will use that flag you will additional column with urls",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_discover(
                category="positive_sentiment",
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    def call_cgyfarms(self, other_args):
        """Process yfarms command"""
        parser = argparse.ArgumentParser(
            prog="cgyfarms",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Top Yield Farming Pools by Value Locked. Yield farming, also referred to as liquidity mining,
            is a way to generate rewards with cryptocurrency holdings.
            In simple terms, it means locking up cryptocurrencies and getting rewards.
            You can display only N number of coins with --limit parameter.
            You can sort data by Rank, Name,  Value_Locked, Return_Year with --sort parameter
            and also with --descend flag to sort descending.
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
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.YFARMS_FILTERS,
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
            pycoingecko_view.display_yieldfarms(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
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
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
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
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                export=ns_parser.export,
            )

    def call_cgdex(self, other_args):
        """Process dex command"""
        parser = argparse.ArgumentParser(
            prog="cgdex",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Top Decentralized Exchanges on CoinGecko by Trading Volume
            You can display only N number of coins with --limit parameter.
            You can sort data by  Name, Rank, Volume_24h, Coins, Pairs, Visits, Most_Traded, Market_Share by
            volume with --sort and also with --descend flag to sort descending.
            Display columns:
                  Name, Rank, Volume_24h, Coins, Pairs, Visits, Most_Traded, Market_Share""",
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
            choices=pycoingecko_model.DEX_FILTERS,
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
            pycoingecko_view.display_top_dex(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    def call_cgnft(self, other_args):
        """Process nft command"""
        parser = argparse.ArgumentParser(
            prog="cgnft",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top NFT Coins by Market Capitalization
                NFT (Non-fungible Token) refers to digital assets with unique characteristics.
                Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
                You can display only N number of coins with --limit parameter.
                You can sort data by Rank, Name, Symbol, Price, Change_1d, Change_24h, Change_7d, Market_Cap
                with --sort and also with --descend flag to sort descending.
                Flag --urls will display urls
                Displays : Rank, Name, Symbol, Price, Change_1d, Change_24h, Change_7d, Market_Cap, Url""",
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
            pycoingecko_view.display_top_nft(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
                links=ns_parser.urls,
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
