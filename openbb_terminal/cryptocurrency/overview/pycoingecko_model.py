"""CoinGecko model"""
__docformat__ = "numpy"

# pylint: disable=C0301, E1101
# pylint: disable=unsupported-assignment-operation

import logging
import re
from typing import List, Union

import numpy as np
import pandas as pd
from pycoingecko import CoinGeckoAPI

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    create_df_index,
    lambda_long_number_format_with_type_check,
    lambda_replace_underscores_in_column_names,
)
from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import get_coins
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation

HOLD_COINS = ["ethereum", "bitcoin"]

NEWS_FILTERS = ["Index", "Title", "Author", "Posted"]

CATEGORIES_FILTERS = [
    "Rank",
    "Name",
    "Change_1h",
    "Change_24h",
    "Change_7d",
    "Market_Cap",
    "Volume_24h",
    "Coins",
]

STABLES_FILTERS = [
    "Rank",
    "Name",
    "Symbol",
    "Price",
    "Change_24h",
    "Exchanges",
    "Market_Cap",
    "Change_30d",
]

PRODUCTS_FILTERS = [
    "Rank",
    "Platform",
    "Identifier",
    "Supply_Rate",
    "Borrow_Rate",
]

PLATFORMS_FILTERS = ["Rank", "Name", "Category", "Centralized"]

EXCHANGES_FILTERS = [
    "Rank",
    "Trust_Score",
    "Id",
    "Name",
    "Country",
    "Year Established",
    "Trade_Volume_24h_BTC",
]

EXRATES_FILTERS = ["Index", "Name", "Unit", "Value", "Type"]

INDEXES_FILTERS = ["Rank", "Name", "Id", "Market", "Last", "MultiAsset"]

DERIVATIVES_FILTERS = [
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
]

COINS_COLUMNS = [
    "symbol",
    "name",
    "current_price",
    "market_cap",
    "market_cap_rank",
    "price_change_percentage_7d_in_currency",
    "price_change_percentage_24h_in_currency",
    "total_volume",
]


@log_start_end(log=logger)
def get_holdings_overview(endpoint: str = "bitcoin") -> List[Union[str, pd.DataFrame]]:
    """Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]

    Parameters
    ----------
    endpoint : str
        "bitcoin" or "ethereum"

    Returns
    -------
    List[Union[str, pd.DataFrame]]
        - str:              Overall statistics
        - pd.DataFrame: Companies holding crypto
    """
    cg = CoinGeckoAPI()
    data = cg.get_companies_public_treasury_by_coin_id(coin_id=endpoint)

    stats_str = f"""{len(data["companies"])} companies hold a total of {lambda_long_number_format_with_type_check(data["total_holdings"])} {endpoint} ({data["market_cap_dominance"]}% of market cap dominance) with the current value of {lambda_long_number_format_with_type_check(int(data["total_value_usd"]))} USD dollars"""  # noqa

    df = pd.json_normalize(data, record_path=["companies"])

    df.columns = list(
        map(
            lambda x: lambda_replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x,
            df.columns,
        )
    )

    return [stats_str, df]


SORT_VALUES = ["market_cap", "name", "market_cap_change_24h"]


def lambda_coin_formatter(n):
    # TODO: can be improved
    coins = []
    re_str = "small/(.*)(.jpg|.png|.JPG|.PNG)"
    for coin in n:
        if re.search(re_str, coin):
            coin_stripped = re.search(re_str, coin).group(1)
            coins.append(coin_stripped)
    return ",".join(coins)


@log_start_end(log=logger)
def get_top_crypto_categories(sort_filter: str = SORT_VALUES[0]) -> pd.DataFrame:
    """Returns top crypto categories [Source: CoinGecko]

    Parameters
    ----------
    sort_filter : str
        Can be one of - "market_cap_desc", "market_cap_asc", "name_desc", "name_asc",
        "market_cap_change_24h_desc", "market_cap_change_24h_asc"

    Returns
    -------
    pd.DataFrame
        Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url
    """
    if sort_filter.lower() in SORT_VALUES:
        client = CoinGeckoAPI()
        data = client.get_coins_categories()
        df = pd.DataFrame(data)
        del df["id"]
        del df["content"]
        del df["updated_at"]
        df["top_3_coins"] = df["top_3_coins"].apply(lambda_coin_formatter)
        df.columns = [
            lambda_replace_underscores_in_column_names(col)
            if isinstance(col, str)
            else col
            for col in df.columns
        ]
        return df
    return pd.DataFrame()


# TODO: add string with overview
@log_start_end(log=logger)
def get_stable_coins(
    limit: int = 15, sortby: str = "Market_Cap_[$]", ascend: bool = False
) -> pd.DataFrame:
    """Returns top stable coins [Source: CoinGecko]

    Parameters
    ----------
    limit: int
        How many rows to show
    sortby: str
        Key by which to sort data, default is Market_Cap_[$]
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Dataframe with stable coins data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.crypto.ov.stables(sortby="Volume_[$]", ascend=True, limit=10)
    """

    df = get_coins(limit=limit, category="stablecoins")
    df = df[COINS_COLUMNS]
    df = df.set_axis(
        [
            "Symbol",
            "Name",
            "Price_[$]",
            "Market_Cap_[$]",
            "Market_Cap_Rank",
            "Change_7d_[%]",
            "Change_24h_[%]",
            "Volume_[$]",
        ],
        axis=1,
        copy=False,
    )
    total_market_cap = int(df["Market_Cap_[$]"].sum())
    df[f"Percentage_[%]_of_top_{limit}"] = (
        df["Market_Cap_[$]"] / total_market_cap
    ) * 100
    sortby = sortby.replace(" ", "_")
    df = df.sort_values(by=sortby, ascending=ascend)

    return df


@log_start_end(log=logger)
def get_exchanges(sortby: str = "Rank", ascend: bool = True) -> pd.DataFrame:
    """Get list of top exchanges from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
        Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC, Url
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_exchanges_list(per_page=250))
    df.replace({float(np.NaN): None}, inplace=True)
    df = df[
        [
            "trust_score",
            "id",
            "name",
            "country",
            "year_established",
            "trade_volume_24h_btc",
            "url",
        ]
    ]
    df.columns = [
        "Trust_Score",
        "Id",
        "Name",
        "Country",
        "Year_Established",
        "Trade_Volume_24h_BTC",
        "Url",
    ]
    create_df_index(df, "Rank")
    if sortby == "Rank":
        df = df.sort_values(by=sortby, ascending=not ascend)
    else:
        df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_financial_platforms(sortby: str = "Name", ascend: bool = True) -> pd.DataFrame:
    """Get list of financial platforms from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Rank, Name, Category, Centralized, Url
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_finance_platforms())
    df.drop("facts", axis=1, inplace=True)
    create_df_index(df, "rank")
    df.columns = ["Rank", "Name", "Category", "Centralized", "Url"]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_finance_products(sortby: str = "Name", ascend: bool = True) -> pd.DataFrame:
    """Get list of financial products from CoinGecko API

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(
        client.get_finance_products(per_page=250),
        columns=[
            "platform",
            "identifier",
            "supply_rate_percentage",
            "borrow_rate_percentage",
        ],
    )
    df.columns = ["Platform", "Identifier", "Supply_Rate", "Borrow_Rate"]
    create_df_index(df, "Rank")
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_indexes(sortby: str = "Name", ascend: bool = True) -> pd.DataFrame:
    """Get list of crypto indexes from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Name, Id, Market, Last, MultiAsset
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_indexes(per_page=250))
    df.columns = ["Name", "Id", "Market", "Last", "MultiAsset"]
    create_df_index(df, "Rank")
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_derivatives(sortby: str = "Rank", ascend: bool = False) -> pd.DataFrame:
    """Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
        Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread,
        Funding_Rate, Volume_24h,
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_derivatives(include_tickers="unexpired"))
    df.drop(
        ["index", "last_traded_at", "expired_at", "index_id", "open_interest"],
        axis=1,
        inplace=True,
    )

    df.rename(columns={"price_percentage_change_24h": "pct_change_24h"}, inplace=True)
    create_df_index(df, "rank")
    df["price"] = df["price"].apply(
        lambda x: "" if not x else float(x.strip("$").replace(",", ""))
    )

    df.columns = [
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
    ]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_exchange_rates(sortby: str = "Name", ascend: bool = False) -> pd.DataFrame:
    """Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]

    Parameters
    ----------
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data ascending

    Returns
    -------
    pd.DataFrame
        Index, Name, Unit, Value, Type
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_exchange_rates()["rates"]).T.reset_index()
    df.drop("index", axis=1, inplace=True)
    create_df_index(df, "index")
    df.columns = ["Index", "Name", "Unit", "Value", "Type"]
    df = df.sort_values(by=sortby, ascending=ascend)
    return df


@log_start_end(log=logger)
def get_global_info() -> pd.DataFrame:
    """Get global statistics about crypto from CoinGecko API like:
        - market cap change
        - number of markets
        - icos
        - number of active crypto

    [Source: CoinGecko]

    Returns
    -------
    pd.DataFrame
        Metric, Value
    """

    client = CoinGeckoAPI()
    results = client.get_global()

    total_mcap = results.pop("market_cap_percentage")
    btc, eth = total_mcap.get("btc"), total_mcap.get("eth")
    for key in ["total_market_cap", "total_volume", "updated_at"]:
        del results[key]
    results["btc_market_cap_in_pct"] = btc
    results["eth_market_cap_in_pct"] = eth
    results["altcoin_market_cap_in_pct"] = 100 - (float(eth) + float(btc))
    df = pd.Series(results).reset_index()
    df.columns = ["Metric", "Value"]
    df["Metric"] = df["Metric"].apply(
        lambda x: lambda_replace_underscores_in_column_names(x)
        if isinstance(x, str)
        else x
    )
    return df


@log_start_end(log=logger)
def get_global_markets_info() -> pd.DataFrame:
    """Get global statistics about crypto markets from CoinGecko API like:
        Market_Cap, Volume, Market_Cap_Percentage

    [Source: CoinGecko]

    Returns
    -------
    pd.DataFrame
        Market_Cap, Volume, Market_Cap_Percentage
    """

    columns = [
        "Market_Cap",
        "Volume",
        "Market_Cap_Percentage",
    ]
    data = []
    client = CoinGeckoAPI()
    results = client.get_global()
    for key in columns:
        data.append(results.get(key))
    df = pd.DataFrame(data).T
    df.columns = columns
    df.replace({float("nan"): None}, inplace=True)
    return df.reset_index()


@log_start_end(log=logger)
def get_global_defi_info() -> pd.DataFrame:
    """Get global statistics about Decentralized Finances [Source: CoinGecko]

    Returns
    -------
    pd.DataFrame
        Metric, Value
    """

    client = CoinGeckoAPI()
    results = client.get_global_decentralized_finance_defi()
    for key, value in results.items():
        try:
            results[key] = round(float(value), 4)
        except (ValueError, TypeError):
            pass

    df = pd.Series(results).reset_index()
    df.columns = ["Metric", "Value"]
    df["Metric"] = df["Metric"].apply(
        lambda x: lambda_replace_underscores_in_column_names(x)
        if isinstance(x, str)
        else x
    )
    return df
