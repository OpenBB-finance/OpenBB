"""CoinPaprika View"""
__docformat__ = "numpy"

import argparse
from typing import List
from tabulate import tabulate
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, check_positive
import gamestonk_terminal.cryptocurrency.overview.coinpaprika_model as paprika
from gamestonk_terminal.cryptocurrency.cryptocurrency_helpers import (
    long_number_format_with_type_check,
)


register_matplotlib_converters()

# pylint: disable=inconsistent-return-statements
# pylint: disable=C0302, too-many-lines

CURRENCIES = [
    "BTC",
    "ETH",
    "USD",
    "EUR",
    "PLN",
    "KRW",
    "GBP",
    "CAD",
    "JPY",
    "RUB",
    "TRY",
    "NZD",
    "AUD",
    "CHF",
    "UAH",
    "HKD",
    "SGD",
    "NGN",
    "PHP",
    "MXN",
    "BRL",
    "THB",
    "CLP",
    "CNY",
    "CZK",
    "DKK",
    "HUF",
    "IDR",
    "ILS",
    "INR",
    "MYR",
    "NOK",
    "PKR",
    "SEK",
    "TWD",
    "ZAR",
    "VND",
    "BOB",
    "COP",
    "PEN",
    "ARS",
    "ISK",
]
PLATFORMS = paprika.get_all_contract_platforms()["platform_id"].tolist()
COINS = paprika.get_list_of_coins()
COINS_DCT = dict(zip(COINS.id, COINS.symbol))
# see https://github.com/GamestonkTerminal/GamestonkTerminal/pull/562#issuecomment-887842888
# EXCHANGES = paprika.get_list_of_exchanges()


def global_market(other_args: List[str]):
    """Return data frame with most important global crypto statistics like:
    market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
    market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
    market_cap_change_24h, volume_24h_change_24h, last_updated,

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="global",
        description="""Show most important global crypto statistics like:
        market_cap_usd, volume_24h_usd, bitcoin_dominance_percentage, cryptocurrencies_number,
        market_cap_ath_value, market_cap_ath_date, volume_24h_ath_value, volume_24h_ath_date,
        market_cap_change_24h, volume_24h_change_24h, last_updated.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = paprika.get_global_market()
        df["Value"] = df["Value"].apply(lambda x: long_number_format_with_type_check(x))
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


def all_coins_market_info(other_args: List[str]):
    """Displays basic market information for all coins from CoinPaprika API

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="markets",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = paprika.get_coins_market_info(quotes=ns_parser.vs).sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if df.empty:
            print("No data found", "\n")
            return

        cols = [col for col in df.columns if col != "rank"]
        df[cols] = df[cols].applymap(lambda x: long_number_format_with_type_check(x))
        print("")
        print(f"Displaying data vs {ns_parser.vs}")
        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def all_coins_info(other_args: List[str]):
    """Displays basic coin information for all coins from CoinPaprika API

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="info",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = paprika.get_coins_info(quotes=ns_parser.vs).sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if df.empty:
            print("Not data found", "\n")
            return

        cols = [col for col in df.columns if col != "rank"]
        df[cols] = df[cols].applymap(lambda x: long_number_format_with_type_check(x))

        print("")
        print(f"Displaying data vs {ns_parser.vs}")
        print(
            tabulate(
                df.head(ns_parser.top),
                headers=df.columns,
                floatfmt=".3f",
                showindex=False,
                tablefmt="fancy_grid",
            )
        )
        print("")

    except Exception as e:
        print(e, "\n")


def all_exchanges(other_args: List[str]):
    """List exchanges from CoinPaprika API

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="exchanges",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = paprika.get_list_of_exchanges(quotes=ns_parser.vs).sort_values(
            by=ns_parser.sortby, ascending=ns_parser.descend
        )

        if df.empty:
            print("No data found", "\n")
            return

        cols = [col for col in df.columns if col != "rank"]
        df[cols] = df[cols].applymap(lambda x: long_number_format_with_type_check(x))
        print("")
        print(f"Displaying data vs {ns_parser.vs}")
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


def exchange_markets(other_args: List[str]):
    """Get all markets for given exchange

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse

    """
    parser = argparse.ArgumentParser(
        prog="exmarkets",
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

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = paprika.get_exchanges_market(exchange_id=ns_parser.exchange)

        if df.empty:
            print("No data found", "\n")
            return

        df = df.sort_values(by=ns_parser.sortby, ascending=ns_parser.descend)

        if ns_parser.links is True:
            df = df[["exchange_id", "pair", "trust_score", "market_url"]]
        else:
            df.drop("market_url", axis=1, inplace=True)

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


def all_platforms(other_args: List[str]):
    """List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="platforms",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        df = paprika.get_all_contract_platforms()
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


def contracts(other_args: List[str]):
    """Gets all contract addresses for given platform

    Parameters
    ----------
    other_args: List[str]
        Arguments to pass to argparse
    """
    parser = argparse.ArgumentParser(
        prog="contracts",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="""Gets all contract addresses for given platform.
        Provide platform id with -p/--platform parameter
        You can display only top N number of smart contracts with --top parameter.
        You can sort data by id, type, active, address  --sort parameter
        and also with --descend flag to sort descending.

        Displays:
            id, type, active, address
        """,
    )
    parser.add_argument(
        "-p",
        "--platform",
        help="Blockchain platform like eth-ethereum",
        dest="platform",
        default="eth-ethereum",
        type=str,
        choices=PLATFORMS,
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
        help="Sort by given column",
        default="id",
        choices=["id", "type", "active", "address"],
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

        df = paprika.get_contract_platform(ns_parser.platform)

        if df.empty:
            print(f"Nothing found for platform: {ns_parser.platform}", "\n")
            return

        df = df.sort_values(ns_parser.sortby, ascending=ns_parser.descend)
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
