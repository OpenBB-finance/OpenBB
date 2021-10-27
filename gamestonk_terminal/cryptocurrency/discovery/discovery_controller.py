"""Cryptocurrency Discovery Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import os
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    try_except,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.discovery import (
    pycoingecko_view,
    coinpaprika_view,
    coinmarketcap_view,
)
from gamestonk_terminal.cryptocurrency import cryptocurrency_helpers


class DiscoveryController:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
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

    def __init__(self):
        """CONSTRUCTOR"""

        self._discovery_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self._discovery_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Discovery:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program
    coins       search for coins on CoinGecko, Binance, CoinPaprika

CoinGecko:
    cgtrending        trending coins on CoinGecko
    cgvoted           most voted coins on CoinGecko
    cgvisited         most visited coins on CoinGecko
    cgvolume          coins with highest volume on CoinGecko
    cgrecently        recently added on CoinGecko
    cgsentiment       coins with most positive sentiment
    cggainers         top gainers - coins which price gained the most in given period
    cglosers          top losers - coins which price dropped the most in given period
    cgyfarms          top yield farms
    cgdefi            top defi protocols
    cgdex             top decentralized exchanges
    cgnft             top non fungible tokens
CoinPaprika:
    cpsearch          search on CoinPaprika
CoinMarketCap:
    cmctop            top coins from CoinMarketCap
"""
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

        (known_args, other_args) = self._discovery_parser.parse_known_args(
            an_input.split()
        )

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
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program."""
        return True

    @try_except
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
            dest="top",
            help="Limit of records",
            type=check_positive,
        )

        parser.add_argument(
            "--source",
            dest="source",
            required=False,
            help="Source of data.",
            type=str,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        cryptocurrency_helpers.display_all_coins(
            coin=ns_parser.coin,
            source=ns_parser.source,
            top=ns_parser.top,
            skip=ns_parser.skip,
            show_all=bool("ALL" in other_args),
            export=ns_parser.export,
        )

    @try_except
    def call_cggainers(self, other_args):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            prog="cggainers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Largest Gainers - coins which gain the most in given period.
            You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
            You can look on only top N number of records with --top,
            You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag to set it
            to sort descending.
            There is --links flag, which will display one additional column you all urls for coins.
            """,
        )

        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            type=str,
            help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
            default="1h",
            choices=["1h", "24h", "7d", "14d", "30d", "60d", "1y"],
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=["Rank", "Symbol", "Name", "Volume", "Price", "Change"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will additional column with urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_gainers(
            period=ns_parser.period,
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
    def call_cglosers(self, other_args):
        """Process losers command"""
        parser = argparse.ArgumentParser(
            prog="cglosers",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
           Shows Largest Losers - coins which price dropped the most in given period
           You can use parameter --period to set which timeframe are you interested in: 1h, 24h, 7d, 14d, 30d, 60d, 1y
           You can look on only top N number of records with --top,
           You can sort by Rank, Symbol, Name, Volume, Price, Change with --sort and also with --descend flag
           to sort descending.
           Flag --links will display one additional column with all coingecko urls for listed coins.
            """,
        )

        parser.add_argument(
            "-p",
            "--period",
            dest="period",
            type=str,
            help="time period, one from [1h, 24h, 7d, 14d, 30d, 60d, 1y]",
            default="1h",
            choices=["1h", "24h", "7d", "14d", "30d", "60d", "1y"],
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=["Rank", "Symbol", "Name", "Volume", "Price", "Change"],
        )
        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will additional column with urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        pycoingecko_view.display_losers(
            period=ns_parser.period,
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
    def call_cgtrending(self, other_args):
        """Process trending command"""
        parser = argparse.ArgumentParser(
            prog="cgtrending",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Discover trending coins.
                Use --top parameter to display only top N number of records,
                You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
                to sort descending.
                Flag --links will display one additional column with all coingecko urls for listed coins.
                trending will display: Rank, Name, Price_BTC, Price_USD
            """,
        )
        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Price_BTC",
                "Price_USD",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will additional column with urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_discover(
            category="trending",
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
    def call_cgvoted(self, other_args):
        """Process voted command"""
        parser = argparse.ArgumentParser(
            prog="cgvoted",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Discover most voted coins.
                Use --top parameter to display only top N number of records,
                You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
                to sort descending.
                Flag --links will display one additional column with all coingecko urls for listed coins.
                voted will display: Rank, Name, Price_BTC, Price_USD
                """,
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Price_BTC",
                "Price_USD",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will additional column with urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_discover(
            category="most_voted",
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
    def call_cgrecently(self, other_args):
        """Process recently command"""
        parser = argparse.ArgumentParser(
            prog="cgrecently",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
                Shows recently added coins on CoinGecko. You can display only top N number of coins with --top parameter.
                You can sort data by Rank, Name, Symbol, Price, Change_1h, Change_24h, Added with --sort
                and also with --descend flag to sort descending.
                Flag --links will display urls""",
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Symbol",
                "Price",
                "Change_1h",
                "Change_24h",
                "Added",
                "Url",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_recently_added(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
    def call_cgvisited(self, other_args):
        """Process most_visited command"""
        parser = argparse.ArgumentParser(
            prog="cgvisited",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Discover most visited coins.
            Use --top parameter to display only top N number of records,
            You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
            to sort descending.
            Flag --links will display one additional column with all coingecko urls for listed coins.
            visited will display: Rank, Name, Price_BTC, Price_USD
            """,
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Price_BTC",
                "Price_USD",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will additional column with urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_discover(
            category="most_visited",
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
    def call_cgsentiment(self, other_args):
        """Process sentiment command"""
        parser = argparse.ArgumentParser(
            prog="cgsentiment",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Discover coins with positive sentiment.
            Use --top parameter to display only top N number of records,
            You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
            to sort descending.
            Flag --links will display one additional column with all coingecko urls for listed coins.
            sentiment will display: Rank, Name, Price_BTC, Price_USD
            """,
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Price_BTC",
                "Price_USD",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will additional column with urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_discover(
            category="positive_sentiment",
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
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
            You can display only top N number of coins with --top parameter.
            You can sort data by Rank, Name,  Value_Locked, Return_Year with --sort parameter
            and also with --descend flag to sort descending.
                """,
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="Top N of records. Default 20",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Value_Locked",
                "Return_Year",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_yieldfarms(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

    @try_except
    def call_cgvolume(self, other_args):
        """Process volume command"""
        parser = argparse.ArgumentParser(
            prog="cgvolume",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top Coins by Trading Volume.
                You can display only top N number of coins with --top parameter.
                You can sort data by on of columns  Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d,
                Volume_24h, Market_Cap with --sort parameter and also with --descend flag to sort descending.
                Displays columns:  Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap""",
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="Top N of records. Default 15",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Symbol",
                "Price",
                "Change_1h",
                "Change_24h",
                "Change_7d",
                "Volume_24h",
                "Market_Cap",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_top_volume_coins(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

    @try_except
    def call_cgdefi(self, other_args):
        """Process defi command"""
        parser = argparse.ArgumentParser(
            prog="cgdefi",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top DeFi Coins by Market Capitalization
               DeFi or Decentralized Finance refers to financial services that are built
               on top of distributed networks with no central intermediaries.
               You can display only top N number of coins with --top parameter.
               You can sort data by Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d,
                Volume 24h, Market Cap, Url with --sort and also with --descend flag to sort descending.
               Flag --links will display  urls""",
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Symbol",
                "Price",
                "Change_1h",
                "Change_24h",
                "Change_7d",
                "Volume_24h",
                "Market_Cap",
                "Url",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_top_defi_coins(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            export=ns_parser.export,
        )

    @try_except
    def call_cgdex(self, other_args):
        """Process dex command"""
        parser = argparse.ArgumentParser(
            prog="cgdex",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
            Shows Top Decentralized Exchanges on CoinGecko by Trading Volume
            You can display only top N number of coins with --top parameter.
            You can sort data by  Name, Rank, Volume_24h, Coins, Pairs, Visits, Most_Traded, Market_Share by
            volume with --sort and also with --descend flag to sort descending.
            Display columns:
                  Name, Rank, Volume_24h, Coins, Pairs, Visits, Most_Traded, Market_Share""",
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=[
                "Name",
                "Rank",
                "Volume_24h",
                "Coins",
                "Pairs",
                "Visits",
                "Most_Traded",
                "Market_Share",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_top_dex(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

    @try_except
    def call_cgnft(self, other_args):
        """Process nft command"""
        parser = argparse.ArgumentParser(
            prog="cgnft",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top NFT Coins by Market Capitalization
                NFT (Non-fungible Token) refers to digital assets with unique characteristics.
                Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
                You can display only top N number of coins with --top parameter.
                You can sort data by Rank, Name, Symbol, Price, Change_1d, Change_24h, Change_7d, Market_Cap
                with --sort and also with --descend flag to sort descending.
                Flag --links will display urls
                Displays : Rank, Name, Symbol, Price, Change_1d, Change_24h, Change_7d, Market_Cap, Url""",
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=[
                "Rank",
                "Name",
                "Symbol",
                "Price",
                "Change_1h",
                "Change_24h",
                "Change_7d",
                "Volume_24h",
                "Market_Cap",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        pycoingecko_view.display_top_nft(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
            links=ns_parser.links,
        )

    @try_except
    def call_cmctop(self, other_args):
        """Process cmctop command"""
        parser = argparse.ArgumentParser(
            prog="cmctop",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="This gets the top ranked coins from coinmarketcap.com",
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
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="column to sort data by.",
            default="CMC_Rank",
            choices=["Symbol", "CMC_Rank", "LastPrice", "DayPctChange", "MarketCap"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        coinmarketcap_view.display_cmc_top_coins(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

    @try_except
    def call_cpsearch(self, other_args):
        """Process search command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpsearch",
            description="""Search over CoinPaprika API
            You can display only top N number of results with --top parameter.
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
            choices=[
                "currencies",
                "exchanges",
                "icos",
                "people",
                "tags",
                "all",
            ],
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
            help="Sort by given column. Default: id",
            default="id",
            choices=["category", "id", "name"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-q")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        coinpaprika_view.display_search_results(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
            query=ns_parser.query,
            category=ns_parser.category,
        )


def menu():
    disc_controller = DiscoveryController()
    disc_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in disc_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(disc)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(disc)> ")

        try:
            process_input = disc_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
