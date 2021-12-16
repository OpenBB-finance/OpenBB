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
    pycoingecko_view,
    coinpaprika_view,
    cryptopanic_view,
    withdrawalfees_model,
    withdrawalfees_view,
)
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_view import CURRENCIES
from gamestonk_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_all_contract_platforms,
)
from gamestonk_terminal.cryptocurrency.overview import coinbase_view


class Controller:

    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
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
        "cgcompanies",
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

    def __init__(self):
        """CONSTRUCTOR"""

        self._overview_parser = argparse.ArgumentParser(add_help=False, prog="ov")
        self._overview_parser.add_argument("cmd", choices=self.CHOICES)

    def print_help(self):
        """Print help"""
        help_text = """
Overview:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

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
    cgcompanies       ethereum, bitcoin holdings by public companies
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

        (known_args, other_args) = self._overview_parser.parse_known_args(
            an_input.split()
        )

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
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

        withdrawalfees_view.display_overall_withdrawal_fees(
            export=ns_parser.export, top=ns_parser.limit
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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        if ns_parser.coin:
            if ns_parser.coin in withdrawalfees_model.POSSIBLE_CRYPTOS:
                withdrawalfees_view.display_crypto_withdrawal_fees(
                    export=ns_parser.export, symbol=ns_parser.coin
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
                        export=ns_parser.export, symbol=similar_cmd[0]
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
            for coin in withdrawalfees_model.POSSIBLE_CRYPTOS:
                print(coin)

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
            choices=["ethereum", "bitcoin"],
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
        pycoingecko_view.display_holdings_overview(
            coin=ns_parser.coin, export=ns_parser.export
        )

    @try_except
    def call_cgcompanies(self, other_args):
        """Process companies command"""
        parser = argparse.ArgumentParser(
            prog="cgcompanies",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Track publicly traded companies around the world that
            are buying ethereum or bitcoin as part of corporate treasury:
            Rank, Company, Ticker, Country, Total_Btc, Entry_Value, Today_Value, Pct_Supply, Url
            You can use additional flag --links to see urls to announcement about buying btc or eth by given company.
            In this case you will see only columns like rank, company, url
            """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            dest="coin",
            type=str,
            help="companies with ethereum or bitcoin",
            default="bitcoin",
            choices=["ethereum", "bitcoin"],
        )

        parser.add_argument(
            "-l",
            "--links",
            dest="links",
            action="store_true",
            help="Flag to show urls. If you will use that flag you will see only rank, company, url columns",
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

        pycoingecko_view.display_holdings_companies_list(
            coin=ns_parser.coin, export=ns_parser.export, links=ns_parser.links
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
            "To display urls to news use --links flag.",
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=int,
            help="top N number of news >=10",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: index",
            default="Index",
            choices=["Index", "Title", "Author", "Posted"],
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
        pycoingecko_view.display_news(
            top=ns_parser.top,
            export=ns_parser.export,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
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
            "To display urls use --links flag.",
            Displays: Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h, Coins,""",
        )

        parser.add_argument(
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number of records",
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
                "Change_1h",
                "Change_24h",
                "Change_7d",
                "Market_Cap",
                "Volume_24h",
                "Coins",
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
        pycoingecko_view.display_categories(
            top=ns_parser.top,
            export=ns_parser.export,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
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
                You can display only top N number of coins with --top parameter.
                You can sort data by Rank, Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d with --sort
                and also with --descend flag to sort descending.
                Flag --links will display stablecoins urls""",
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
                "Change_24h",
                "Exchanges",
                "Market_Cap",
                "Change_30d",
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

        pycoingecko_view.display_stablecoins(
            top=ns_parser.top,
            export=ns_parser.export,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
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

        pycoingecko_view.display_nft_of_the_day(export=ns_parser.export)

    @try_except
    def call_cgproducts(self, other_args):
        """Process products command"""
        parser = argparse.ArgumentParser(
            prog="cgproducts",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top Crypto Financial Products with which you can earn yield, borrow or lend your crypto.
                You can display only top N number of platforms with --top parameter.
                You can sort data by Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate with --sort
                and also with --descend flag to sort descending.
                Displays: Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate""",
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
                "Platform",
                "Identifier",
                "Supply_Rate",
                "Borrow_Rate",
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

        pycoingecko_view.display_products(
            top=ns_parser.top,
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
                You can display only top N number of platforms with --top parameter.
                You can sort data by Rank, Name, Category, Centralized with --sort
                and also with --descend flag to sort descending.
                Displays: Rank, Name, Category, Centralized, Url""",
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
            choices=["Rank", "Name", "Category", "Centralized"],
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

        pycoingecko_view.display_platforms(
            top=ns_parser.top,
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
                You can display only top N number exchanges with --top parameter.
                You can sort data by Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC with --sort
                and also with --descend flag to sort descending.
                Flag --links will display urls.
                Displays: Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC""",
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
                "Trust_Score",
                "Id",
                "Name",
                "Country",
                "Year Established",
                "Trade_Volume_24h_BTC",
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

        pycoingecko_view.display_exchanges(
            top=ns_parser.top,
            export=ns_parser.export,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
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
                You can look on only top N number of records with --top,
                You can sort by Index, Name, Unit, Value, Type, and also use --descend flag to sort descending.""",
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
            help="Sort by given column. Default: Index",
            default="Index",
            choices=["Index", "Name", "Unit", "Value", "Type"],
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
        pycoingecko_view.display_exchange_rates(
            sortby=ns_parser.sortby,
            top=ns_parser.top,
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
            You can display only top N number of indexes with --top parameter.
            You can sort data by Rank, Name, Id, Market, Last, MultiAsset with --sort
            and also with --descend flag to sort descending.
            Displays: Rank, Name, Id, Market, Last, MultiAsset
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
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=["Rank", "Name", "Id", "Market", "Last", "MultiAsset"],
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

        pycoingecko_view.display_indexes(
            top=ns_parser.top,
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
               You can look on only top N number of records with --top,
               You can sort by Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate,
               Volume_24h with --sort and also with --descend flag to set it to sort descending.
               Displays:
                   Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h""",
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
                "Market",
                "Symbol",
                "Price",
                "Pct_Change_24h",
                "Contract_Type",
                "Basis",
                "Spread",
                "Funding_Rate",
                "Volume_24h",
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
        pycoingecko_view.display_derivatives(
            top=ns_parser.top,
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

        coinpaprika_view.display_global_market(export=ns_parser.export)

    @try_except
    def call_cpmarkets(self, other_args):
        """Process markets command"""
        parser = argparse.ArgumentParser(
            prog="cpmarkets",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Show market related (price, supply, volume) coin information for all coins on CoinPaprika.
            You can display only top N number of coins with --top parameter.
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
            help="Sort by given column. Default: rank",
            default="rank",
            choices=[
                "rank",
                "name",
                "symbol",
                "price",
                "volume_24h",
                "mcap_change_24h",
                "pct_change_1h",
                "pct_change_24h",
                "ath_price",
                "pct_from_ath",
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

        coinpaprika_view.display_all_coins_market_info(
            currency=ns_parser.vs,
            top=ns_parser.top,
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
                You can display only top N number of records with --top parameter.
                You can sort data by pair, base_currency_name, quote_currency_name, market_url, category,
                reported_volume_24h_share, trust_score --sort parameter and also with --descend flag to sort descending.
                You can use additional flag --links to see urls for each market
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
            help="Sort by given column. Default: reported_volume_24h_share",
            default="reported_volume_24h_share",
            choices=[
                "pair",
                "base_currency_name",
                "quote_currency_name",
                "category",
                "reported_volume_24h_share",
                "trust_score",
                "market_url",
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

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        coinpaprika_view.display_exchange_markets(
            exchange=ns_parser.exchange,
            top=ns_parser.top,
            export=ns_parser.export,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
        )

    @try_except
    def call_cpinfo(self, other_args):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cpinfo",
            description="""Show basic coin information for all coins from CoinPaprika API
                You can display only top N number of coins with --top parameter.
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
            help="Sort by given column. Default: rank",
            default="rank",
            choices=[
                "rank",
                "name",
                "symbol",
                "price",
                "volume_24h",
                "circulating_supply",
                "total_supply",
                "max_supply",
                "ath_price",
                "market_cap",
                "beta_value",
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
        coinpaprika_view.display_all_coins_info(
            currency=ns_parser.vs,
            top=ns_parser.top,
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
               You can display only top N number of coins with --top parameter.
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
            help="Sort by given column. Default: rank",
            default="rank",
            choices=[
                "rank",
                "name",
                "currencies",
                "markets",
                "fiats",
                "confidence",
                "volume_24h",
                "volume_7d",
                "volume_30d",
                "sessions_per_month",
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
        coinpaprika_view.display_all_exchanges(
            currency=ns_parser.vs,
            top=ns_parser.top,
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
               You can display only top N number of smart contracts with --top parameter.
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
            help="Sort by given column",
            default="id",
            choices=["id", "type", "active", "balance"],
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

        coinpaprika_view.display_contracts(
            platform=ns_parser.platform,
            top=ns_parser.top,
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
            "-t",
            "--top",
            dest="top",
            type=int,
            help="top N number of news >=10",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: id",
            default="id",
            choices=[
                "id",
                "display_name",
                "base_currency",
                "quote_currency",
                "base_min_size",
                "base_max_size",
                "min_market_funds",
                "max_market_funds",
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

        coinbase_view.display_trading_pairs(
            top=ns_parser.top,
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
            "-t",
            "--top",
            dest="top",
            type=int,
            help="top N number of news >=10",
            default=20,
        )

        parser.add_argument(
            "-k",
            "--kind",
            dest="kind",
            type=str,
            help="Filter by category of news. Available values: news or media.",
            default="news",
            choices=["news", "media"],
        )

        parser.add_argument(
            "-f",
            "--filter",
            dest="filter",
            type=str,
            help="Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol",
            default=None,
            required=False,
            choices=[
                "rising",
                "hot",
                "bullish",
                "bearish",
                "important",
                "saved",
                "lol",
            ],
        )

        parser.add_argument(
            "-r",
            "--region",
            dest="region",
            type=str,
            help="Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch), es (Español), "
            "fr (Français), it (Italiano), pt (Português), ru (Русский)",
            default="en",
            choices=["en", "de", "es", "fr", "nl", "it", "pt", "ru"],
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: published_at",
            default="published_at",
            choices=[
                "published_at",
                "domain",
                "title",
                "negative_votes",
                "positive_votes",
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if not ns_parser:
            return

        cryptopanic_view.display_news(
            top=ns_parser.top,
            export=ns_parser.export,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            links=ns_parser.links,
            post_kind=ns_parser.kind,
            filter_=ns_parser.filter,
            region=ns_parser.region,
        )


def menu():
    overview_controller = Controller()
    overview_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in overview_controller.CHOICES}

            choices["wfpe"] = {c: None for c in withdrawalfees_model.POSSIBLE_CRYPTOS}
            choices["wfpe"]["-c"] = {
                c: None for c in withdrawalfees_model.POSSIBLE_CRYPTOS
            }
            choices["wfpe"]["--coin"] = {
                c: None for c in withdrawalfees_model.POSSIBLE_CRYPTOS
            }

            completer = NestedCompleter.from_nested_dict(choices)
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(ov)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(ov)> ")

        try:
            process_input = overview_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
