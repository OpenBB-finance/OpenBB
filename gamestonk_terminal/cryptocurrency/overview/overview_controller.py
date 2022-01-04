"""Cryptocurrency Overview Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import difflib
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    try_except,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.cryptocurrency.overview import (
    cryptopanic_model,
    pycoingecko_model,
    pycoingecko_view,
    coinpaprika_view,
    cryptopanic_view,
    withdrawalfees_model,
    withdrawalfees_view,
    coinpaprika_model,
    coinbase_model,
    coinbase_view,
)
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_view import CURRENCIES
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_all_contract_platforms,
)


class OverviewController:

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
        "cgglobal",
        "cgdefi",
        "cgnews",
        "cgstables",
        "cgnft",
        "cgnftday",
        "cgexchanges",
        "cgexrates",
        "cgplatforms",
        "cgproducts",
        "cgindexes",
        "cgderivatives",
        "cgcategories",
        "cghold",
        "cpglobal",
        "cpmarkets",
        "cpexmarkets",
        "cpinfo",
        "cpexchanges",
        "cpplatforms",
        "cpcontracts",
        "cbpairs",
        "news",
        "wf",
        "ewf",
        "wfpe",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """CONSTRUCTOR"""

        self.overview_parser = argparse.ArgumentParser(add_help=False, prog="ov")
        self.overview_parser.add_argument("cmd", choices=self.CHOICES)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = """
Overview Menu:

CoinGecko:
    cgglobal          global crypto market info
    cgnews            last news available on CoinGecko
    cgdefi            global DeFi market info
    cgstables         stablecoins
    cgnft             non fungible token market status
    cgnftday          non fungible token of the day
    cgexchanges       top crypto exchanges
    cgexrates         coin exchange rates
    cgplatforms       crypto financial platforms
    cgproducts        crypto financial products
    cgindexes         crypto indexes
    cgderivatives     crypto derivatives
    cgcategories      crypto categories
    cghold            ethereum, bitcoin holdings overview statistics
CoinPaprika:
    cpglobal          global crypto market info
    cpinfo            basic info about all coins available on CoinPaprika
    cpmarkets         market related info about all coins available on CoinPaprika
    cpexchanges       list all exchanges
    cpexmarkets       all available markets on given exchange
    cpplatforms       list blockchain platforms eg. ethereum, solana, kusama, terra
    cpcontracts       all smart contracts for given platform
Coinbase:
    cbpairs           info about available trading pairs on Coinbase
CryptoPanic:
    news              recent crypto news from CryptoPanic aggregator
WithdrawalFees:
    wf                overall withdrawal fees
    ewf               overall exchange withdrawal fees
    wfpe              crypto withdrawal fees per exchange
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

        (known_args, other_args) = self.overview_parser.parse_known_args(
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
        self.queue.insert(0, "ov")
        self.queue.insert(0, "crypto")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_wf(self, other_args: List[str]):
        """Process wf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="wf",
            description="""
                Display top coins withdrawal fees
                [Source: https://withdrawalfees.com/]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            help="Limit number of coins to display withdrawal fees. Default 10",
            dest="limit",
            default=10,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            withdrawalfees_view.display_overall_withdrawal_fees(
                top=ns_parser.limit, export=ns_parser.export
            )

    @try_except
    def call_ewf(self, other_args: List[str]):
        """Process ewf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ewf",
            description="""
                Display exchange withdrawal fees
                [Source: https://withdrawalfees.com/]
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            withdrawalfees_view.display_overall_exchange_withdrawal_fees(
                export=ns_parser.export
            )

    @try_except
    def call_wfpe(self, other_args: List[str]):
        """Process wfpe command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="wfpe",
            description="""
                Coin withdrawal fees per exchange
                [Source: https://withdrawalfees.com/]
            """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            default="bitcoin",
            type=str,
            dest="coin",
            help="Coin to check withdrawal fees in long format (e.g., bitcoin, ethereum)",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.coin:
                if ns_parser.coin in withdrawalfees_model.POSSIBLE_CRYPTOS:
                    withdrawalfees_view.display_crypto_withdrawal_fees(
                        symbol=ns_parser.coin, export=ns_parser.export
                    )
                else:
                    print(f"Coin '{ns_parser.coin}' does not exist.")

                    similar_cmd = difflib.get_close_matches(
                        ns_parser.coin,
                        withdrawalfees_model.POSSIBLE_CRYPTOS,
                        n=1,
                        cutoff=0.75,
                    )
                    if similar_cmd:
                        print(f"Replacing by '{similar_cmd[0]}'")
                        withdrawalfees_view.display_crypto_withdrawal_fees(
                            symbol=similar_cmd[0], export=ns_parser.export
                        )
                    else:
                        similar_cmd = difflib.get_close_matches(
                            ns_parser.coin,
                            withdrawalfees_model.POSSIBLE_CRYPTOS,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            print(f"Did you mean '{similar_cmd[0]}'?")
            else:
                print(
                    f"Couldn't find any coin with provided name: {ns_parser.coin}. "
                    f"Please choose one from list: {withdrawalfees_model.POSSIBLE_CRYPTOS}\n"
                )

    @try_except
    def call_cghold(self, other_args):
        """Process hold command"""
        parser = argparse.ArgumentParser(
            prog="cghold",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
                Shows overview of public companies that holds ethereum or bitcoin.
                You can find there most important metrics like:
                Total Bitcoin Holdings, Total Value (USD), Public Companies Bitcoin Dominance, Companies
                """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            dest="coin",
            type=str,
            help="companies with ethereum or bitcoin",
            default="bitcoin",
            choices=pycoingecko_model.HOLD_COINS,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_holdings_overview(
                coin=ns_parser.coin, export=ns_parser.export
            )

    @try_except
    def call_cgnews(self, other_args):
        """Process news command"""
        parser = argparse.ArgumentParser(
            prog="cgnews",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Shows latest crypto news from CoinGecko. "
            "You will see Index, Title, Author, Posted columns. "
            "You can sort by each of column above, using --sort parameter and also do it descending with --descend flag"
            "To display urls to news use --urls flag.",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            help="display N number of news >=10",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: index",
            default="Index",
            choices=pycoingecko_model.NEWS_FILTERS,
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
            pycoingecko_view.display_news(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
            )

    @try_except
    def call_cgcategories(self, other_args):
        """Process top_categories command"""
        parser = argparse.ArgumentParser(
            prog="cgcategories",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows top cryptocurrency categories by market capitalization. It includes categories like:
            stablecoins, defi, solana ecosystem, polkadot ecosystem and many others.
            "You can sort by each of column above, using --sort parameter and also do it descending with --descend flag"
            "To display urls use --urls flag.",
            Displays: Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h, Coins,""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number of records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.CATEGORIES_FILTERS,
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
            pycoingecko_view.display_categories(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
            )

    @try_except
    def call_cgstables(self, other_args):
        """Process stables command"""
        parser = argparse.ArgumentParser(
            prog="cgstables",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows stablecoins by market capitalization.
                Stablecoins are cryptocurrencies that attempt to peg their market value to some external reference
                like the U.S. dollar or to a commodity's price such as gold.
                You can display only N number of coins with --limit parameter.
                You can sort data by Rank, Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d with --sort
                and also with --descend flag to sort descending.
                Flag --urls will display stablecoins urls""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.STABLES_FILTERS,
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
            pycoingecko_view.display_stablecoins(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
            )

    @try_except
    def call_cgnft(self, other_args):
        """Process nft command"""

        parser = argparse.ArgumentParser(
            prog="cgnft",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows NFT market status
                NFT (Non-fungible Token) refers to digital assets with unique characteristics.
                Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
                Displays: NFT Market Cap, 24h Trading Volume, NFT Dominance vs Global market, Theta Network NFT Dominance
                """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_nft_market_status(export=ns_parser.export)

    @try_except
    def call_cgnftday(self, other_args):
        """Process nftday command"""
        parser = argparse.ArgumentParser(
            prog="cgnftday",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows NFT of the day
                NFT (Non-fungible Token) refers to digital assets with unique characteristics.
                Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
                With nft_today command you will display:
                    author, description, url, img url for NFT which was chosen on CoinGecko as a nft of the day.""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_nft_of_the_day(export=ns_parser.export)

    @try_except
    def call_cgproducts(self, other_args):
        """Process products command"""
        parser = argparse.ArgumentParser(
            prog="cgproducts",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top Crypto Financial Products with which you can earn yield, borrow or lend your crypto.
                You can display only N number of platforms with --limit parameter.
                You can sort data by Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate with --sort
                and also with --descend flag to sort descending.
                Displays: Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.PRODUCTS_FILTERS,
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
            pycoingecko_view.display_products(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
            )

    @try_except
    def call_cgplatforms(self, other_args):
        """Process platforms command"""
        parser = argparse.ArgumentParser(
            prog="cgplatforms",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top Crypto Financial Platforms in which you can borrow or lend your crypto.
                e.g Celsius, Nexo, Crypto.com, Aave and others.
                You can display only N number of platforms with --limit parameter.
                You can sort data by Rank, Name, Category, Centralized with --sort
                and also with --descend flag to sort descending.
                Displays: Rank, Name, Category, Centralized, Url""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.PLATFORMS_FILTERS,
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
            pycoingecko_view.display_platforms(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
            )

    @try_except
    def call_cgexchanges(self, other_args):
        """Process exchanges command"""
        parser = argparse.ArgumentParser(
            prog="cgexchanges",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top Crypto Exchanges
                You can display only N number exchanges with --limit parameter.
                You can sort data by Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC with --sort
                and also with --descend flag to sort descending.
                Flag --urls will display urls.
                Displays: Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.EXCHANGES_FILTERS,
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
            pycoingecko_view.display_exchanges(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
            )

    @try_except
    def call_cgexrates(self, other_args):
        """Process exchange_rates command"""
        parser = argparse.ArgumentParser(
            prog="cgexrates",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
                Shows list of crypto, fiats, commodity exchange rates from CoinGecko
                You can look on only N number of records with --limit,
                You can sort by Index, Name, Unit, Value, Type, and also use --descend flag to sort descending.""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Index",
            default="Index",
            choices=pycoingecko_model.EXRATES_FILTERS,
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
            pycoingecko_view.display_exchange_rates(
                sortby=ns_parser.sortby,
                top=ns_parser.limit,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_cgindexes(self, other_args):
        """Process indexes command"""
        parser = argparse.ArgumentParser(
            prog="cgindexes",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows list of crypto indexes from CoinGecko.
            Each crypto index is made up of a selection of cryptocurrencies, grouped together and weighted by market cap.
            You can display only N number of indexes with --limit parameter.
            You can sort data by Rank, Name, Id, Market, Last, MultiAsset with --sort
            and also with --descend flag to sort descending.
            Displays: Rank, Name, Id, Market, Last, MultiAsset
                """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.INDEXES_FILTERS,
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
            pycoingecko_view.display_indexes(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_cgderivatives(self, other_args):
        """Process derivatives command"""
        parser = argparse.ArgumentParser(
            prog="cgderivatives",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows list of crypto derivatives from CoinGecko
               Crypto derivatives are secondary contracts or financial tools that derive their value from a primary
               underlying asset. In this case, the primary asset would be a cryptocurrency such as Bitcoin.
               The most popular crypto derivatives are crypto futures, crypto options, and perpetual contracts.
               You can look on only N number of records with --limit,
               You can sort by Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate,
               Volume_24h with --sort and also with --descend flag to set it to sort descending.
               Displays:
                   Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.DERIVATIVES_FILTERS,
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
            pycoingecko_view.display_derivatives(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_cgglobal(self, other_args):
        """Process global command"""
        parser = argparse.ArgumentParser(
            prog="cgglobal",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows global statistics about Crypto Market""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_global_market_info(export=ns_parser.export)

    @try_except
    def call_cgdefi(self, other_args):
        """Process defi command"""
        parser = argparse.ArgumentParser(
            prog="cgdefi",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows global DeFi statistics
               DeFi or Decentralized Finance refers to financial services that are built
               on top of distributed networks with no central intermediaries.
               Displays metrics like:
                   Market Cap, Trading Volume, Defi Dominance, Top Coins...""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_global_defi_info(export=ns_parser.export)

    @try_except
    def call_cpglobal(self, other_args):
        """Process global command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpglobal",
            description="""Show most important global crypto statistics like: Market Cap, Volume,
            Number of cryptocurrencies, All Time High, All Time Low""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_global_market(export=ns_parser.export)

    @try_except
    def call_cpmarkets(self, other_args):
        """Process markets command"""
        parser = argparse.ArgumentParser(
            prog="cpmarkets",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Show market related (price, supply, volume) coin information for all coins on CoinPaprika.
            You can display only N number of coins with --limit parameter.
            You can sort data by rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h,
            ath_price, pct_from_ath, --sort parameter and also with --descend flag to sort descending.
            Displays:
               rank, name, symbol, price, volume_24h, mcap_change_24h,
               pct_change_1h, pct_change_24h, ath_price, pct_from_ath,
                """,
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
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="rank",
            choices=coinpaprika_model.MARKETS_FILTERS,
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
            coinpaprika_view.display_all_coins_market_info(
                currency=ns_parser.vs,
                top=ns_parser.limit,
                descend=ns_parser.descend,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
            )

    @try_except
    def call_cpexmarkets(self, other_args):
        """Process exmarkets command"""
        parser = argparse.ArgumentParser(
            prog="cpexmarkets",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Get all exchange markets found for given exchange
                You can display only N number of records with --limit parameter.
                You can sort data by pair, base_currency_name, quote_currency_name, market_url, category,
                reported_volume_24h_share, trust_score --sort parameter and also with --descend flag to sort descending.
                You can use additional flag --urls to see urls for each market
                Displays:
                    exchange_id, pair, base_currency_name, quote_currency_name, market_url,
                    category, reported_volume_24h_share, trust_score,""",
        )

        parser.add_argument(
            "-e",
            "--exchange",
            help="Identifier of exchange e.g for Binance Exchange -> binance",
            dest="exchange",
            default="binance",
            type=str,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: reported_volume_24h_share",
            default="reported_volume_24h_share",
            choices=coinpaprika_model.EXMARKETS_FILTERS,
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

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_exchange_markets(
                exchange=ns_parser.exchange,
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
            )

    @try_except
    def call_cpinfo(self, other_args):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpinfo",
            description="""Show basic coin information for all coins from CoinPaprika API
                You can display only N number of coins with --limit parameter.
                You can sort data by rank, name, symbol, price, volume_24h, circulating_supply, total_supply, max_supply,
                market_cap, beta_value, ath_price --sort parameter and also with --descend flag to sort descending.
                Displays:
                    rank, name, symbol, price, volume_24h, circulating_supply,
                    total_supply, max_supply, market_cap, beta_value, ath_price
                """,
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
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=20,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="rank",
            choices=coinpaprika_model.INFO_FILTERS,
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
            coinpaprika_view.display_all_coins_info(
                currency=ns_parser.vs,
                top=ns_parser.limit,
                descend=ns_parser.descend,
                sortby=ns_parser.sortby,
                export=ns_parser.export,
            )

    @try_except
    def call_cpexchanges(self, other_args):
        """Process coins_market command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpexchanges",
            description="""Show all exchanges from CoinPaprika
               You can display only N number of coins with --limit parameter.
               You can sort data by  rank, name, currencies, markets, fiats, confidence,
               volume_24h,volume_7d ,volume_30d, sessions_per_month --sort parameter
               and also with --descend flag to sort descending.
               Displays:
                   rank, name, currencies, markets, fiats, confidence, volume_24h,
                   volume_7d ,volume_30d, sessions_per_month""",
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
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=20,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="rank",
            choices=coinpaprika_model.EXCHANGES_FILTERS,
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
            coinpaprika_view.display_all_exchanges(
                currency=ns_parser.vs,
                top=ns_parser.limit,
                descend=ns_parser.descend,
                sortby=ns_parser.sortby,
                export=ns_parser.export,
            )

    @try_except
    def call_cpplatforms(self, other_args):
        """Process platforms command"""
        parser = argparse.ArgumentParser(
            prog="cpplatforms",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama""",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_all_platforms(export=ns_parser.export)

    @try_except
    def call_cpcontracts(self, other_args):
        """Process contracts command"""
        platforms = get_all_contract_platforms()["platform_id"].tolist()

        parser = argparse.ArgumentParser(
            prog="cpcontracts",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Gets all contract addresses for given platform.
               Provide platform id with -p/--platform parameter
               You can display only N number of smart contracts with --limit parameter.
               You can sort data by id, type, active, balance  --sort parameter
               and also with --descend flag to sort descending.

               Displays:
                   id, type, active, balance
               """,
        )

        parser.add_argument(
            "-p",
            "--platform",
            help="Blockchain platform like eth-ethereum",
            dest="platform",
            default="eth-ethereum",
            type=str,
            choices=platforms,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column",
            default="id",
            choices=coinpaprika_model.CONTRACTS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_contracts(
                platform=ns_parser.platform,
                top=ns_parser.limit,
                descend=ns_parser.descend,
                sortby=ns_parser.sortby,
                export=ns_parser.export,
            )

    @try_except
    def call_cbpairs(self, other_args):
        """Process news command"""
        parser = argparse.ArgumentParser(
            prog="cbpairs",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Shows available trading pairs on Coinbase ",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            help="display N number of news >=10",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: id",
            default="id",
            choices=coinbase_model.PAIRS_FILTERS,
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
            coinbase_view.display_trading_pairs(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
            )

    @try_except
    def call_news(self, other_args):
        """Process news command"""
        parser = argparse.ArgumentParser(
            prog="news",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display recent news from CryptoPanic aggregator platform. [Source: https://cryptopanic.com/]",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=20,
        )

        parser.add_argument(
            "-k",
            "--kind",
            dest="kind",
            type=str,
            help="Filter by category of news. Available values: news or media.",
            default="news",
            choices=cryptopanic_model.CATEGORIES,
        )

        parser.add_argument(
            "-f",
            "--filter",
            dest="filter",
            type=str,
            help="Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol",
            default=None,
            required=False,
            choices=cryptopanic_model.FILTERS,
        )

        parser.add_argument(
            "-r",
            "--region",
            dest="region",
            type=str,
            help="Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch), es (Español), "
            "fr (Français), it (Italiano), pt (Português), ru (Русский)",
            default="en",
            choices=cryptopanic_model.REGIONS,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: published_at",
            default="published_at",
            choices=cryptopanic_model.SORT_FILTERS,
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
            cryptopanic_view.display_news(
                top=ns_parser.limit,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                links=ns_parser.urls,
                post_kind=ns_parser.kind,
                filter_=ns_parser.filter,
                region=ns_parser.region,
            )


def menu(queue: List[str] = None):
    overview_controller = OverviewController(queue=queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if overview_controller.queue and len(overview_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if overview_controller.queue[0] in ("q", "..", "quit"):
                if len(overview_controller.queue) > 1:
                    return overview_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = overview_controller.queue[0]
            overview_controller.queue = overview_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in overview_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /crypto/ov/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                overview_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT:
                choices: dict = {c: {} for c in overview_controller.CHOICES}
                choices["cghold"] = {c: None for c in pycoingecko_model.HOLD_COINS}
                choices["cgnews"]["-s"] = {
                    c: None for c in pycoingecko_model.NEWS_FILTERS
                }
                choices["cgcategories"]["-s"] = {
                    c: None for c in pycoingecko_model.CATEGORIES_FILTERS
                }
                choices["cgstables"]["-s"] = {
                    c: None for c in pycoingecko_model.STABLES_FILTERS
                }
                choices["cgproducts"]["-s"] = {
                    c: None for c in pycoingecko_model.PRODUCTS_FILTERS
                }
                choices["cgplatforms"]["-s"] = {
                    c: None for c in pycoingecko_model.PLATFORMS_FILTERS
                }
                choices["cgexrates"]["-s"] = {
                    c: None for c in pycoingecko_model.EXRATES_FILTERS
                }
                choices["cgindexes"]["-s"] = {
                    c: None for c in pycoingecko_model.INDEXES_FILTERS
                }
                choices["cgderivatives"]["-s"] = {
                    c: None for c in pycoingecko_model.DERIVATIVES_FILTERS
                }
                choices["cpmarkets"]["-s"] = {
                    c: None for c in coinpaprika_model.MARKETS_FILTERS
                }
                choices["cpexmarkets"]["-s"] = {
                    c: None for c in coinpaprika_model.EXMARKETS_FILTERS
                }
                choices["cpexchanges"]["-s"] = {
                    c: None for c in coinpaprika_model.EXCHANGES_FILTERS
                }
                choices["cpcontracts"] = {
                    c: None
                    for c in get_all_contract_platforms()["platform_id"].tolist()
                }
                choices["cpcontracts"]["-s"] = {
                    c: None for c in coinpaprika_model.CONTRACTS_FILTERS
                }
                choices["cpinfo"]["-s"] = {
                    c: None for c in coinpaprika_model.INFO_FILTERS
                }
                choices["cbpairs"]["-s"] = {
                    c: None for c in coinbase_model.PAIRS_FILTERS
                }
                choices["news"]["-k"] = {c: None for c in cryptopanic_model.CATEGORIES}
                choices["news"]["-f"] = {c: None for c in cryptopanic_model.FILTERS}
                choices["news"]["-r"] = {c: None for c in cryptopanic_model.REGIONS}
                choices["news"]["-s"] = {
                    c: None for c in cryptopanic_model.SORT_FILTERS
                }
                choices["wfpe"] = {
                    c: None for c in withdrawalfees_model.POSSIBLE_CRYPTOS
                }
                completer = NestedCompleter.from_nested_dict(choices)
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /crypto/ov/ $ ",
                        completer=completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/ov/ $ ")

        try:
            # Process the input command
            overview_controller.queue = overview_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                overview_controller.CHOICES,
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
                        overview_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                overview_controller.queue.insert(0, an_input)
            else:
                print("\n")
