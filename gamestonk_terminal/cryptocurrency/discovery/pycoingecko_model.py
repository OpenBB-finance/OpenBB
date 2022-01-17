"""CoinGecko model"""
__docformat__ = "numpy"

import os
import json
from typing import Any, List
import pandas as pd
from pycoingecko import CoinGeckoAPI

PERIODS = {
    "1h": "?time=h1",
    "24h": "?time=h24",
    "7d": "?time=d7",
    "14d": "?time=d14",
    "30d": "?time=d30",
    "60d": "?time=d60",
    "1y": "?time=y1",
}

API_PERIODS = ["14d", "1h", "1y", "200d", "24h", "30d", "7d"]

CATEGORIES = {
    "trending": 0,
    "most_voted": 1,
    "positive_sentiment": 2,
    "recently_added": 3,
    "most_visited": 4,
}

GAINERS_FILTERS = ["Rank", "Symbol", "Name", "Volume", "Price", "Change"]
TRENDING_FILTERS = [
    "Rank",
    "Name",
    "Price_BTC",
    "Price_USD",
]
RECENTLY_FILTERS = [
    "Rank",
    "Name",
    "Symbol",
    "Price",
    "Change_1h",
    "Change_24h",
    "Added",
    "Url",
]

YFARMS_FILTERS = [
    "Rank",
    "Name",
    "Value_Locked",
    "Return_Year",
]

CAP_FILTERS = [
    "Rank",
    "Name",
    "Symbol",
    "Price",
    "Change_1h",
    "Change_24h",
    "Change_7d",
    "Volume_24h",
    "Market_Cap",
]

DEX_FILTERS = [
    "Name",
    "Rank",
    "Volume_24h",
    "Coins",
    "Pairs",
    "Visits",
    "Most_Traded",
    "Market_Share",
]


def read_file_data(file_name: str):
    if file_name.split(".")[1] != "json":
        raise TypeError("Please load json file")

    par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(par_dir, "data", file_name)
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    return data


def get_categories_keys():
    categories = read_file_data("coingecko_categories.json")
    return categories.keys()


def get_coins(top: int = 250, category: str = ""):
    """Get N coins from CoinGecko [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Number of top coins to grab from CoinGecko
    Returns
    -------
    pandas.DataFrame
        N coins
    """
    i = 1
    remaining_top = top
    client = CoinGeckoAPI()
    if category:
        categories_dict = read_file_data("coingecko_categories.json")
        if category not in categories_dict:
            raise ValueError(
                f"Category does not exist\nPlease chose one from list: {categories_dict.keys()}"
            )
    if top > 250:
        if category:
            data = client.get_coins_markets(
                category=category,
                vs_currency="usd",
                order="market_cap_desc",
                per_page=top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        else:
            data = client.get_coins_markets(
                vs_currency="usd",
                order="market_cap_desc",
                per_page=top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        df = pd.DataFrame(data)
        remaining_top -= 250
        i += 1
    else:
        if category:
            data = client.get_coins_markets(
                category=category,
                vs_currency="usd",
                order="market_cap_desc",
                per_page=top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        else:
            data = client.get_coins_markets(
                vs_currency="usd",
                order="market_cap_desc",
                per_page=top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        df = pd.DataFrame(data)
        return df
    while remaining_top > 250:
        if category:
            data = client.get_coins_markets(
                category=category,
                vs_currency="usd",
                order="market_cap_desc",
                per_page=top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        else:
            data = client.get_coins_markets(
                vs_currency="usd",
                order="market_cap_desc",
                per_page=top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        df = df.append(pd.DataFrame(data), ignore_index=True)
        remaining_top -= 250
        i += 1
    if remaining_top > 0:
        if category:
            data = client.get_coins_markets(
                category=category,
                vs_currency="usd",
                order="market_cap_desc",
                per_page=remaining_top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        else:
            data = client.get_coins_markets(
                vs_currency="usd",
                order="market_cap_desc",
                per_page=top,
                page=i,
                sparkline=False,
                price_change_percentage="1h,24h,7d,14d,30d,200d,1y",
            )
        df = df.append(pd.DataFrame(data), ignore_index=True)
    return df


# TODO: convert Volume and other str that should be int to int otherwise sort won't work


def get_gainers_or_losers(
    top: int = 20, period: str = "1h", typ: str = "gainers"
) -> pd.DataFrame:
    """Scrape data about top gainers - coins which gain the most in given period and
    top losers - coins that lost the most in given period of time. [Source: CoinGecko]

    Parameters
    ----------
    top: int
        Num of coins to get
    period: str
        One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    typ: str
        Either "gainers" or "losers"
    Returns
    -------
    pandas.DataFrame
        Top Gainers / Top Losers - coins which gain/lost most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{period}, Url
    """

    if period not in API_PERIODS:
        raise ValueError(
            f"Wrong time period\nPlease chose one from list: {API_PERIODS}"
        )
    df = get_coins(top)
    sorted_df = df.sort_values(
        by=[f"price_change_percentage_{period}_in_currency"],
        ascending=typ != "gainers",
    )
    return sorted_df[
        [
            "symbol",
            "name",
            "current_price",
            "market_cap",
            "market_cap_rank",
            f"price_change_percentage_{period}_in_currency",
        ]
    ]


def get_trending_coins() -> pd.DataFrame:
    """Returns trending coins [Source: CoinGecko]

    Parameters
    ----------

    Returns
    -------
    pandas.DataFrame:
        Trending Coins
        Columns:
    """
    client = CoinGeckoAPI()
    data = client.get_search_trending()
    coins = data["coins"]
    df = pd.DataFrame(columns=["Symbol", "Name", "Market Cap Rank"])
    for i, coin in enumerate(coins):
        coin = coin["item"]
        df.loc[i] = [coin["id"], coin["name"], coin["market_cap_rank"]]
    return df


def get_top_volume_coins(top: int = 50) -> pd.DataFrame:
    """Returns N coins with top volume [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Top Coins by Trading Volume
        Columns: Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap
    """

    df = get_coins(top)
    sorted_df = df.sort_values(
        by=["total_volume"],
        ascending=False,
    )
    return sorted_df[
        [
            "symbol",
            "name",
            "market_cap",
            "market_cap_rank",
            "price_change_percentage_7d_in_currency",
            "price_change_percentage_24h_in_currency",
            "total_volume",
        ]
    ]


def get_top_defi_coins(top: int = 20) -> List[Any]:
    """Scrapes top decentralized finance coins "https://www.coingecko.com/en/defi" [Source: CoinGecko]

    Returns
    -------
    str
        Top defi coins stats
    pandas.DataFrame
        Top Decentralized Finance Coins
        Columns: Rank, Name, Symbol, Price, Change_1h, Change_24h, Change_7d, Volume_24h, Market_Cap, Url
    """

    cg = CoinGeckoAPI()
    data = cg.get_global_decentralized_finance_defi()

    stats_str = f"""
Defi has currently a market cap of {int(float(data['defi_market_cap']))} USD dollars:
    - {data["defi_to_eth_ratio"]}% of ETH market cap
    - {round(float(data["defi_dominance"]),2)}% of total market cap
{data["top_coin_name"]} is the most popular Defi cryptocurrency with {round(float(data["top_coin_defi_dominance"]), 2)}% of defi dominance
    """  # noqa

    df = get_coins(top, "decentralized-finance-defi")

    return [
        stats_str,
        df[
            [
                "symbol",
                "name",
                "current_price",
                "market_cap",
                "market_cap_rank",
                "price_change_percentage_7d_in_currency",
                "price_change_percentage_24h_in_currency",
                "total_volume",
            ]
        ],
    ]


def get_coin_list() -> pd.DataFrame:
    """Get list of coins available on CoinGecko [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Coins available on CoinGecko
        Columns: id, symbol, name
    """

    client = CoinGeckoAPI()
    return pd.DataFrame(
        client.get_coins_list(),
        columns=["id", "symbol", "name"],
    ).reset_index()


def get_coins_for_given_exchange(exchange_id: str = "binance", page: int = 1) -> dict:
    """Helper method to get all coins available on binance exchange [Source: CoinGecko]

    Parameters
    ----------
    exchange_id: str
        id of exchange
    page: int
        number of page. One page contains 100 records

    Returns
    -------
    dict
        dictionary with all trading pairs on binance
    """

    client = CoinGeckoAPI()
    binance_coins = client.get_exchanges_tickers_by_id(id=exchange_id, page=page)
    return binance_coins["tickers"]


def get_mapping_matrix_for_exchange(exchange_id: str, pages: int = 12) -> dict:
    """Creates a matrix with all coins available on Binance with corresponding coingecko coin_id. [Source: CoinGecko]

    Parameters
    ----------
    exchange_id: str
        id of exchange: binance
    pages: int
        number of pages. One page contains 100 records

    Returns
    -------
    dict
        dictionary with all coins: {"ETH" : "ethereum"}
    """

    coins_dct = {}
    for i in range(pages):
        coins = get_coins_for_given_exchange(exchange_id=exchange_id, page=i)
        for coin in coins:
            bin_symbol, gecko_id = coin["base"], coin["coin_id"]
            if bin_symbol not in coins_dct:
                coins_dct[bin_symbol] = gecko_id
    return coins_dct
