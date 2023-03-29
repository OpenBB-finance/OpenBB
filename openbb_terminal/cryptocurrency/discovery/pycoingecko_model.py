"""CoinGecko model"""
__docformat__ = "numpy"

import json
import logging
import os
from typing import List

import pandas as pd
from pycoingecko import CoinGeckoAPI

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

COINS_COLUMNS_MAP = {
    "Symbol": "symbol",
    "Name": "name",
    "Volume [$]": "total_volume",
    "Market Cap": "market_cap",
    "Market Cap Rank": "market_cap_rank",
    "7D Change [%]": "price_change_percentage_7d_in_currency",
    "24H Change [%]": "price_change_percentage_24h_in_currency",
}

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

GAINERS_LOSERS_COLUMNS = [
    "Symbol",
    "Name",
    "Price [$]",
    "Market Cap",
    "Market Cap Rank",
    "Volume [$]",
]


@log_start_end(log=logger)
def read_file_data(file_name: str) -> dict:
    if file_name.split(".")[1] != "json":
        raise TypeError("Please load json file")

    par_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(par_dir, "data", file_name)
    with open(path, encoding="utf8") as f:
        data = json.load(f)
    return data


@log_start_end(log=logger)
def get_categories_keys() -> List[str]:
    """Get list of categories keys

    Returns
    -------
    List[str]
        List of categories keys
    """
    categories = read_file_data("coingecko_categories.json")
    return list(categories.keys())


@log_start_end(log=logger)
def get_coins(
    limit: int = 250,
    category: str = "",
    sortby: str = "Symbol",
    ascend: bool = False,
) -> pd.DataFrame:
    """Get N coins from CoinGecko [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Number of top coins to grab from CoinGecko
    category: str
        Category of the coins we want to retrieve
    sortby: str
        Key to sort data
    ascend: bool
        Sort data in ascending order

    Returns
    -------
    pd.DataFrame
        N coins
    """

    sortby = sortby.replace("_", " ").title()

    client = CoinGeckoAPI()
    df = pd.DataFrame()
    table_size = limit
    # CoinGecko's API returns all coins without limit when the category is set.
    if category:
        kwargs = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "sparkline": False,
            "price_change_percentage": "1h,24h,7d,14d,30d,200d,1y",
            "category": category,
        }
        data = client.get_coins_markets(**kwargs)
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    else:
        page_size = min(limit, 250)
        page = 1
        while limit > 0:
            kwargs = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": page_size,
                "sparkline": False,
                "price_change_percentage": "1h,24h,7d,14d,30d,200d,1y",
                "page": page,
            }

            data = client.get_coins_markets(**kwargs)
            df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
            limit -= page_size
            page += 1

    if sortby in COINS_COLUMNS_MAP:
        df = df[(df["total_volume"].notna()) & (df["market_cap"].notna())]
        df = df.sort_values(by=COINS_COLUMNS_MAP[sortby], ascending=ascend)

    df = df.astype({"market_cap_rank": "Int64"})

    return df.head(table_size)


@log_start_end(log=logger)
def get_gainers_or_losers(
    limit: int = 20,
    interval: str = "1h",
    typ: str = "gainers",
    sortby: str = "market_cap",
    ascend: bool = True,
) -> pd.DataFrame:
    """Returns data about top gainers - coins which gain the most in given period and
    top losers - coins that lost the most in given period of time. [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        Num of coins to get
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation)
    ascend: bool
        Sort data in ascending order
    interval: str
        One from {14d,1h,1y,200d,24h,30d,7d}
    typ: str
        Either "gainers" or "losers"

    Returns
    -------
    pd.DataFrame
        Top Gainers / Top Losers - coins which gain/lost most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url
    """

    sortby = sortby.replace("_", " ").title()

    if interval not in API_PERIODS:
        raise ValueError(
            f"Wrong time period\nPlease chose one from list: {API_PERIODS}"
        )
    df = get_coins(limit)
    sorted_df = df.sort_values(
        by=[f"price_change_percentage_{interval}_in_currency"],
        ascending=typ != "gainers",
    )
    sorted_df = sorted_df[
        [
            "symbol",
            "name",
            "current_price",
            "market_cap",
            "market_cap_rank",
            "total_volume",
            f"price_change_percentage_{interval}_in_currency",
        ]
    ]
    sorted_df = sorted_df.set_axis(
        GAINERS_LOSERS_COLUMNS + [f"Change {interval} [%]"],
        axis=1,
        copy=True,
    )

    if sortby in GAINERS_LOSERS_COLUMNS:
        sorted_df = sorted_df[
            (sorted_df["Volume [$]"].notna()) & (sorted_df["Market Cap"].notna())
        ]
        sorted_df = sorted_df.sort_values(by=sortby, ascending=ascend)

    return sorted_df


def get_gainers(
    interval: str = "1h",
    limit: int = 50,
    sortby: str = "market_cap_rank",
    ascend: bool = True,
) -> pd.DataFrame:
    """Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]

    Parameters
    ----------
    interval: str
        Time interval by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation)
    ascend: bool
        Sort data in ascending order

    Returns
    -------
    pd.DataFrame
        Top Gainers  - coins which gain most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url
    """
    return get_gainers_or_losers(
        limit=limit,
        interval=interval,
        typ="gainers",
        sortby=sortby,
        ascend=ascend,
    )


def get_losers(
    interval: str = "1h",
    limit: int = 50,
    sortby: str = "market_cap_rank",
    ascend: bool = True,
) -> pd.DataFrame:
    """Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]

    Parameters
    ----------
    interval: str
        Time interval by which data is displayed. One from [1h, 24h, 7d, 14d, 30d, 60d, 1y]
    limit: int
        Number of records to display
    sortby: str
        Key to sort data. The table can be sorted by every of its columns. Refer to
        API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation)
    ascend: bool
        Sort data in ascending order

    Returns
    -------
    pd.DataFrame
        Top Losers  - coins which lost most in price in given period of time.
        Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url
    """
    return get_gainers_or_losers(
        limit=limit, interval=interval, typ="losers", sortby=sortby, ascend=ascend
    )


@log_start_end(log=logger)
def get_trending_coins() -> pd.DataFrame:
    """Returns trending coins [Source: CoinGecko]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        Trending Coins
    """
    client = CoinGeckoAPI()
    data = client.get_search_trending()
    coins = data["coins"]
    df = pd.DataFrame(columns=["Symbol", "Name", "market_cap Cap Rank"])
    for i, coin in enumerate(coins):
        coin = coin["item"]
        df.loc[i] = [coin["id"], coin["name"], coin["market_cap_rank"]]
    return df


@log_start_end(log=logger)
def get_coin_list() -> pd.DataFrame:
    """Get list of coins available on CoinGecko [Source: CoinGecko]

    Returns
    -------
    pd.DataFrame
        Coins available on CoinGecko
        Columns: id, symbol, name
    """

    client = CoinGeckoAPI()
    return pd.DataFrame(
        client.get_coins_list(),
        columns=["id", "symbol", "name"],
    ).reset_index()


@log_start_end(log=logger)
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


@log_start_end(log=logger)
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
