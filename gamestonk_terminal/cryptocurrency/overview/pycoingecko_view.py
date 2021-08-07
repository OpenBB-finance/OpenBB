""" pycoingecko_api """
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
            )
        )
        print("")

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
        rank, company, ticker, country, total_btc, entry_value, today_value, pct_of_supply
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
            df = df[["rank", "company", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

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
            )
        )
        print("")

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
            )
        )
        print("")

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
        You can sort by index,name,unit, value, type, and also use --descend flag to sort descending.""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: index",
        default="index",
        choices=["index", "name", "unit", "value", "type"],
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
            )
        )
        print("")

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
        description="""Shows global statistics about Crypto Market like:
        active_cryptocurrencies, upcoming_icos, ongoing_icos, ended_icos, markets, market_cap_change_percentage_24h,
        eth_market_cap_in_pct, btc_market_cap_in_pct, altcoin_market_cap_in_pct""",
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
            )
        )
        print("")

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
            defi_market_cap, eth_market_cap, defi_to_eth_ratio, trading_volume_24h, defi_dominance, top_coin_name,
            top_coin_defi_dominance""",
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
            )
        )
        print("")

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
            )
        )
        print("")

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
        You can sort data by rank, name, symbol, price, change_24h, exchanges, market_cap, change_30d with --sort
        and also with --descend flag to sort descending.
        Flag --links will display stablecoins urls""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
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
            "change_24h",
            "exchanges",
            "market_cap",
            "change_30d",
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
            df = df[["rank", "name", "symbol", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

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
        "You will see index, title, author, posted columns. "
        "You can sort by each of column above, using --sort parameter and also do it descending with --descend flag"
        "To display urls to news use --links flag.",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=int,
        help="top N number of news >=10",
        default=50,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: index",
        default="index",
        choices=["index", "title", "author", "posted"],
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

        df["title"] = df["title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=50)) if isinstance(x, str) else x
        )

        if not ns_parser.links:
            df.drop("url", axis=1, inplace=True)
        else:
            df = df[["index", "url"]]

        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

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
        "To display urls to news use --links flag.",
        Displays: rank, name, change_1h, change_24h, change_7d, market_cap, volume_24h, n_of_coins""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number of news >=10",
        default=20,
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
            "change_1h",
            "change_24h",
            "change_7d",
            "market_cap",
            "volume_24h",
            "n_of_coins",
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
            df.drop("url", axis=1, inplace=True)
        else:
            df = df[["rank", "name", "url"]]

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".0f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

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
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, trust_score, id, name, country, established, trade_volume_24h_btc with --sort
        and also with --descend flag to sort descending.
        Flag --links will display urls.
        Displays: rank, trust_score, id, name, country, established, trade_volume_24h_btc""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
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
            "trust_score",
            "id",
            "name",
            "country",
            "year_established",
            "trade_volume_24h_btc",
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
            df = df[["rank", "name", "url"]]
        else:
            df.drop("url", axis=1, inplace=True)

        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".1f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

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
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, category, centralized with --sort
        and also with --descend flag to sort descending.
        Displays: rank, name, category, centralized, website_url""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "name", "category", "centralized"],
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
            )
        )
        print("")

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
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, platform, identifier, supply_rate_percentage, borrow_rate_percentage  with --sort
        and also with --descend flag to sort descending.
        Displays: rank, platform, identifier, supply_rate_percentage, borrow_rate_percentage""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
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
            "platform",
            "identifier",
            "supply_rate_percentage",
            "borrow_rate_percentage",
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
            )
        )
        print("")

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
        You can display only top N number of coins with --top parameter.
        You can sort data by rank, name, id, market, last, is_multi_asset_composite with --sort
        and also with --descend flag to sort descending.
        Displays: rank, name, id, market, last, is_multi_asset_composite
        """,
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sortby",
        type=str,
        help="Sort by given column. Default: rank",
        default="rank",
        choices=["rank", "name", "id", "market", "last", "is_multi_asset_composite"],
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
            )
        )
        print("")

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
        You can sort by rank, market, symbol, price, pct_change_24h, contract_type, basis, spread,
        funding_rate, volume_24h with --sort and also with --descend flag to set it to sort descending.
        Displays:
            rank, market, symbol, price, pct_change_24h, contract_type, basis, spread, funding_rate, volume_24h""",
    )
    parser.add_argument(
        "-t",
        "--top",
        dest="top",
        type=check_positive,
        help="top N number records",
        default=20,
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
            "market",
            "symbol",
            "price",
            "pct_change_24h",
            "contract_type",
            "basis",
            "spread",
            "funding_rate",
            "volume_24h",
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
                floatfmt=".2f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")
