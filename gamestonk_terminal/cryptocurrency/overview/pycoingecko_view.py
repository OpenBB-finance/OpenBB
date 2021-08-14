"""CoinGecko view"""
__docformat__ = "numpy"

import argparse
from typing import List
import textwrap
from pandas.plotting import register_matplotlib_converters
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import check_positive, parse_known_args_and_warn
import gamestonk_terminal.cryptocurrency.overview.pycoingecko_model as gecko
from gamestonk_terminal.cryptocurrency.discovery.pycoingecko_model import get_coin_list

register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


def holdings_overview(other_args: List[str]):
    """Shows overview of public companies that holds ethereum or bitcoin from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="hold",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_holdings_overview(endpoint=ns_parser.coin)
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def holdings_companies_list(other_args: List[str]):
    """Shows Ethereum/Bitcoin Holdings by Public Companies from www.coingecko.com

    Track publicly traded companies around the world that are buying ethereum as part of corporate treasury

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="companies",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_companies_assets(endpoint=ns_parser.coin)

        if ns_parser.links is True:
            df = df[["Rank", "Company", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def nft_of_the_day(other_args: List[str]):
    """Shows NFT of the day "https://www.coingecko.com/en/nft"

    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="nft_today",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows NFT of the day
        NFT (Non-fungible Token) refers to digital assets with unique characteristics.
        Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
        With nft_today command you will display:
            author, description, url, img url for NFT which was chosen on CoinGecko as a nft of the day.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_nft_of_the_day()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def nft_market_status(other_args: List[str]):
    """Shows overview data of nft markets "https://www.coingecko.com/en/nft"

    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="nft",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows NFT market status
        NFT (Non-fungible Token) refers to digital assets with unique characteristics.
        Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.
        Displays: NFT Market Cap, 24h Trading Volume, NFT Dominance vs Global market, Theta Network NFT Dominance
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_nft_market_status()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def exchange_rates(other_args: List[str]):
    """Shows  list of crypto, fiats, commodity exchange rates from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="exrates",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_exchange_rates().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )
        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def global_market_info(other_args: List[str]):
    """Shows global statistics about crypto from CoinGecko
        - market cap change
        - number of markets
        - icos
        - number of active crypto
        - market_cap_pct

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="global",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows global statistics about Crypto Market""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_global_info()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def global_defi_info(other_args: List[str]):
    """Shows global statistics about Decentralized Finances from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="defi",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows global DeFi statistics
        DeFi or Decentralized Finance refers to financial services that are built
        on top of distributed networks with no central intermediaries.
        Displays metrics like:
            Market Cap, Trading Volume, Defi Dominance, Top Coins...""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_global_defi_info()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def coin_list(other_args: List[str]):
    """Shows list of coins available on CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="coins",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Shows list of coins available on CoinGecko",
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
        "-t",
        "--top",
        default=100,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )
    parser.add_argument("-l", "--letter", dest="letter", help="First letters", type=str)
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Search in column symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = get_coin_list()

        letter = ns_parser.letter
        if letter and isinstance(letter, str):
            if letter.isalpha():
                letter = letter.lower()
            df = df[df[ns_parser.key].str.startswith(letter)]

        try:
            df = df[ns_parser.skip : ns_parser.skip + ns_parser.top]
        except Exception:
            df = get_coin_list()
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def stablecoins(other_args: List[str]):
    """Shows stablecoins data from "https://www.coingecko.com/en/stablecoins"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="stables",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_stable_coins().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["Rank", "Name", "Symbol", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def news(other_args: List[str]):
    """Shows latest crypto news from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="news",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_news(n=ns_parser.top).sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        df["Title"] = df["Title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=65)) if isinstance(x, str) else x
        )

        if not ns_parser.links:
            df.drop("Url", axis=1, inplace=True)
        else:
            df = df[["Index", "Url"]]

        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def categories(other_args: List[str]):
    """Shows top cryptocurrency categories by market capitalization from https://www.coingecko.com/en/categories

    The cryptocurrency category ranking is based on market capitalization.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="categories",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_crypto_categories().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if not ns_parser.links:
            df.drop("Url", axis=1, inplace=True)
        else:
            df = df[["Rank", "Name", "Url"]]

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def exchanges(other_args: List[str]):
    """Shows list of top exchanges from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="exchanges",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_exchanges().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["Rank", "Name", "Url"]]
        else:
            df.drop("Url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def platforms(other_args: List[str]):
    """Shows list of financial platforms from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="platforms",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_financial_platforms().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def products(other_args: List[str]):
    """Shows list of financial products from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="products",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_finance_products().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )
        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def indexes(other_args: List[str]):
    """Shows list of crypto indexes from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="indexes",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_indexes().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def derivatives(other_args: List[str]):
    """Shows  list of crypto derivatives from CoinGecko

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="derivatives",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_derivatives().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".4f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")
