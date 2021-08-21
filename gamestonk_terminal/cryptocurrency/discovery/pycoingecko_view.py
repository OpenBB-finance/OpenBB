"""CoinGecko view"""
__docformat__ = "numpy"

import argparse
from typing import List

import difflib
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from tabulate import tabulate
from gamestonk_terminal.helper_funcs import check_positive, parse_known_args_and_warn
import gamestonk_terminal.cryptocurrency.discovery.pycoingecko_model as gecko

register_matplotlib_converters()


# pylint: disable=inconsistent-return-statements
# pylint: disable=R0904, C0302


def gainers(other_args: List[str]):
    """Shows Largest Gainers - coins which gain the most in given period from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="gainers",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows Largest Gainers - coins which gain the most in given period.
        You can use parameter --period to set which timeframe are you interested in. eg. 1h, 24h, 7d, 14d, 30d, 60d, 1y
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
        type=int,
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.sortby == "Change":
            sortby = f"%Change_{ns_parser.period}"
        else:
            sortby = ns_parser.sortby

        df = gecko.get_gainers_or_losers(
            period=ns_parser.period, typ="gainers"
        ).sort_values(by=sortby, ascending=ns_parser.descend)

        if not ns_parser.links:
            df.drop("Url", axis=1, inplace=True)

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


def losers(other_args: List[str]):
    """Shows Largest Losers - coins which lost the most in given period of time from www.coingecko.com

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="losers",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Shows Largest Losers - coins which price dropped the most in given period
        You can use parameter --period to set which timeframe are you interested in. eg. 1h, 24h, 7d, 14d, 30d, 60d, 1y
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if ns_parser.sortby == "Change":
            sortby = f"%Change_{ns_parser.period}"
        else:
            sortby = ns_parser.sortby

        df = gecko.get_gainers_or_losers(
            period=ns_parser.period, typ="losers"
        ).sort_values(by=sortby, ascending=ns_parser.descend)

        if not ns_parser.links:
            df.drop("Url", axis=1, inplace=True)

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


def discover(category: str, other_args: List[str]):
    """Discover coins by different categories
        - Most voted coins
        - Most popular coins
        - Recently added coins
        - Most positive sentiment coins

    Parameters
    ----------
    category: str
        one from list: [trending, most_voted, positive_sentiment, most_visited]
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog=f"{category}",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=f"""Discover {category} coins.
        Use --top parameter to display only top N number of records,
        You can sort by Rank, Name, Price_BTC, Price_USD, using --sort parameter and also with --descend flag
        to sort descending.
        Flag --links will display one additional column with all coingecko urls for listed coins.
        {category} will display: Rank, Name, Price_BTC, Price_USD
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.discover_coins(category=category)
        df.index = df.index + 1
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Rank"}, inplace=True)

        df = df.sort_values(by=ns_parser.sortby, ascending=ns_parser.descend)

        if not ns_parser.links:
            df.drop("Url", axis=1, inplace=True)

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


def recently_added(other_args: List[str]):
    """Shows recently added coins from "https://www.coingecko.com/en/coins/recently_added"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="recently",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_recently_added_coins().sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if ns_parser.links is True:
            df = df[["Rank", "Symbol", "Added", "Url"]]
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


def top_defi_coins(other_args: List[str]):
    """Shows Top 100 DeFi Coins by Market Capitalization from "https://www.coingecko.com/en/defi"
    DeFi or Decentralized Finance refers to financial services that are built
    on top of distributed networks with no central intermediaries.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_defi",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_defi_coins().sort_values(
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
                floatfmt=".4f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    except Exception as e:
        print(e, "\n")


def top_dex(other_args: List[str]):
    """Shows Top Decentralized Exchanges on CoinGecko by Trading Volume from "https://www.coingecko.com/en/dex"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_dex",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_dexes().sort_values(
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


def top_volume_coins(other_args: List[str]):
    """Shows Top 100 Coins by Trading Volume from "https://www.coingecko.com/en/yield-farming"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="top_volume",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_volume_coins().sort_values(
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


def top_nft(other_args: List[str]):
    """Shows Top 100 NFT Coins by Market Capitalization from "https://www.coingecko.com/en/nft"
    Top 100 NFT Coins by Market Capitalization
    NFT (Non-fungible Token) refers to digital assets with unique characteristics.
    Examples of NFT include crypto artwork, collectibles, game items, financial products, and more.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="top_nft",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_top_nfts().sort_values(
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
                floatfmt=".4f",
                showindex=False,
                tablefmt="fancy_grid",
            ),
            "\n",
        )

    except Exception as e:
        print(e, "\n")


def yfarms(other_args: List[str]):
    """Shows Top Yield Farming Pools by Value Locked from "https://www.coingecko.com/en/yield-farming"

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="yfarms",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Shows Top Yield Farming Pools by Value Locked
        Yield farming, also referred to as liquidity mining, is a way to generate rewards with cryptocurrency holdings.
        In simple terms, it means locking up cryptocurrencies and getting rewards.
        You can display only top N number of coins with --top parameter.
        You can sort data by Rank, Name,  Value_Locked, Return_Year with --sort parameter
        and also with --descend flag to sort descending.""",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = gecko.get_yield_farms()
        df = df.sort_values(by=ns_parser.sortby, ascending=ns_parser.descend)

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


def find(other_args: List[str]):
    """Find similar coin by coin name,symbol or id.

    If you don't remember exact name or id of the Coin at CoinGecko,
    you can use this command to display coins with similar name, symbol or id to your search query.
    Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
    It will search for coin that has similar name to polka and display top 25 matches.
      -c, --coin stands for coin - you provide here your search query
      -k, --key it's a searching key. You can search by symbol, id or name of coin
      -t, --top it displays top N number of records.

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="find",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""
        Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at CoinGecko,
        you can use this command to display coins with similar name, symbol or id to your search query.
        Example of usage: coin name is something like "polka". So I can try: find -c polka -k name -t 25
        It will search for coin that has similar name to polka and display top 25 matches.
        -c, --coin stands for coin - you provide here your search query
        -k, --key it's a searching key. You can search by symbol, id or name of coin
        -t, --top it displays top N number of records.""",
    )
    parser.add_argument(
        "-c",
        "--coin",
        help="Symbol Name or Id of Coin",
        dest="coin",
        required="-h" not in other_args,
        type=str,
    )
    parser.add_argument(
        "-k",
        "--key",
        dest="key",
        help="Specify by which column you would like to search: symbol, name, id",
        type=str,
        choices=["id", "symbol", "name"],
        default="symbol",
    )
    parser.add_argument(
        "-t",
        "--top",
        default=10,
        dest="top",
        help="Limit of records",
        type=check_positive,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        coins_df = gecko.get_coin_list()
        coins_list = coins_df[ns_parser.key].to_list()
        sim = difflib.get_close_matches(ns_parser.coin, coins_list, ns_parser.top)
        df = pd.Series(sim).to_frame().reset_index()
        df.columns = ["index", ns_parser.key]
        coins_df.drop("index", axis=1, inplace=True)
        df = df.merge(coins_df, on=ns_parser.key)
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
        default=15,
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

        df = gecko.get_coin_list()

        letter = ns_parser.letter
        if letter and isinstance(letter, str):
            if letter.isalpha():
                letter = letter.lower()
            df = df[df[ns_parser.key].str.startswith(letter)]

        try:
            df = df[ns_parser.skip : ns_parser.skip + ns_parser.top]
        except Exception as e:
            print(e)
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
