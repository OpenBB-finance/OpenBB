"""Cryptocurrency Discovery Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622, C0201
import argparse
import difflib
from typing import List, Union
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    try_except,
    system_clear,
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
from gamestonk_terminal.cryptocurrency.crypto_controller import CRYPTO_SOURCES
from gamestonk_terminal.cryptocurrency import cryptocurrency_helpers


class DiscoveryController:
    """Discovery Controller class"""

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

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """CONSTRUCTOR"""

        self.discovery_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self.discovery_parser.add_argument("cmd", choices=self.CHOICES)
        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["coins"]["--source"] = {c: {} for c in CRYPTO_SOURCES.keys()}
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
        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = """
Discovery Menu:

Overview:
    coins             search for coins on CoinGecko, Binance, CoinPaprika
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

        (known_args, other_args) = self.discovery_parser.parse_known_args(
            an_input.split()
        )

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

        return self.queue

    def call_help(self, _):
        """Process help command"""
        self.print_help()
        return self.queue

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "quit"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "disc")
            self.queue.insert(0, "crypto")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "reset", "crypto", "disc"]

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

        if other_args:
            if not other_args[0][0] == "-":
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            cryptocurrency_helpers.display_all_coins(
                coin=ns_parser.coin,
                source=ns_parser.source,
                top=ns_parser.limit,
                skip=ns_parser.skip,
                show_all=bool("ALL" in other_args),
                export=ns_parser.export,
            )
        return self.queue

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
        return self.queue

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
        return self.queue

    @try_except
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

        return self.queue

    @try_except
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

        return self.queue

    @try_except
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
        return self.queue

    @try_except
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
        return self.queue

    @try_except
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
        return self.queue

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
        return self.queue

    @try_except
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
        return self.queue

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
        return self.queue

    @try_except
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
        return self.queue

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
        return self.queue

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
        return self.queue

    @try_except
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
        return self.queue


def menu(queue: List[str] = None):
    """Discovery Menu"""
    disc_controller = DiscoveryController(queue=queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if disc_controller.queue and len(disc_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if disc_controller.queue[0] in ("q", "..", "quit"):
                if len(disc_controller.queue) > 1:
                    return disc_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = disc_controller.queue[0]
            disc_controller.queue = disc_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in disc_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /crypto/disc/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                disc_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and disc_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /crypto/disc/ $ ",
                    completer=disc_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/disc/ $ ")

        try:
            # Process the input command
            disc_controller.queue = disc_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                disc_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                else:
                    candidate_input = similar_cmd[0]

                if candidate_input == an_input:
                    an_input = ""
                    disc_controller.queue = []
                    print("\n")
                    continue

                print(f" Replacing by '{an_input}'.")
                disc_controller.queue.insert(0, an_input)
            else:
                print("\n")
                an_input = ""
                disc_controller.queue = []
