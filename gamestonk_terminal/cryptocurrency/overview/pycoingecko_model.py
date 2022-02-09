"""CoinGecko model"""
__docformat__ = "numpy"

# pylint: disable=C0301, E1101

import logging
import re
from typing import Any, List

import numpy as np
import pandas as pd
from pycoingecko import CoinGeckoAPI

from gamestonk_terminal.cryptocurrency.dataframe_helpers import (
    create_df_index,
    long_number_format_with_type_check,
    replace_underscores_in_column_names,
)
from gamestonk_terminal.cryptocurrency.discovery.pycoingecko_model import get_coins
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

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
def get_holdings_overview(endpoint: str = "bitcoin") -> List[Any]:
    """Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]

    Parameters
    ----------
    endpoint : str
        "bitcoin" or "ethereum"

    Returns
    -------
    List:
        - str:              Overall statistics
        - pandas.DataFrame: Companies holding crypto
    """
    cg = CoinGeckoAPI()
    data = cg.get_companies_public_treasury_by_coin_id(coin_id=endpoint)

    stats_str = f"""{len(data["companies"])} companies hold a total of {long_number_format_with_type_check(data["total_holdings"])} {endpoint} ({data["market_cap_dominance"]}% of market cap dominance) with the current value of {long_number_format_with_type_check(int(data["total_value_usd"]))} USD dollars"""  # noqa

    df = pd.json_normalize(data, record_path=["companies"])

    df.columns = list(
        map(
            lambda x: replace_underscores_in_column_names(x)
            if isinstance(x, str)
            else x,
            df.columns,
        )
    )

    return [stats_str, df]


SORT_VALUES = [
    "market_cap_desc",
    "market_cap_asc",
    "name_desc",
    "name_asc",
    "market_cap_change_24h_desc",
    "market_cap_change_24h_asc",
]


@log_start_end(log=logger)
def coin_formatter(n):
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

    Returns
    -------
    pandas.DataFrame
       Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url
    """
    if sort_filter in SORT_VALUES:
        client = CoinGeckoAPI()
        data = client.get_coins_categories()
        df = pd.DataFrame(data)
        del df["id"]
        del df["content"]
        del df["updated_at"]
        df["top_3_coins"] = df["top_3_coins"].apply(coin_formatter)
        df.columns = [
            replace_underscores_in_column_names(col) if isinstance(col, str) else col
            for col in df.columns
        ]
        return df
    return pd.DataFrame()


# TODO: add string with overview
@log_start_end(log=logger)
def get_stable_coins(top: int = 20) -> pd.DataFrame:
    """Returns top stable coins [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Rank, Name, Symbol, Price, Change_24h, Exchanges, Market_Cap, Change_30d, Url
    """

    df = get_coins(top=top, category="stablecoins")
    return df[COINS_COLUMNS]


@log_start_end(log=logger)
def get_exchanges() -> pd.DataFrame:
    """Get list of top exchanges from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
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
    return df


@log_start_end(log=logger)
def get_financial_platforms() -> pd.DataFrame:
    """Get list of financial platforms from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Rank, Name, Category, Centralized, Url
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_finance_platforms())
    df.drop("facts", axis=1, inplace=True)
    create_df_index(df, "rank")
    df.columns = ["Rank", "Name", "Category", "Centralized", "Url"]
    return df


@log_start_end(log=logger)
def get_finance_products() -> pd.DataFrame:
    """Get list of financial products from CoinGecko API

    Returns
    -------
    pandas.DataFrame
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
    return df


@log_start_end(log=logger)
def get_indexes() -> pd.DataFrame:
    """Get list of crypto indexes from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Name, Id, Market, Last, MultiAsset
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_indexes(per_page=250))
    df.columns = ["Name", "Id", "Market", "Last", "MultiAsset"]
    create_df_index(df, "Rank")
    return df


@log_start_end(log=logger)
def get_derivatives() -> pd.DataFrame:
    """Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h,
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
    return df


@log_start_end(log=logger)
def get_exchange_rates() -> pd.DataFrame:
    """Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
        Index, Name, Unit, Value, Type
    """

    client = CoinGeckoAPI()
    df = pd.DataFrame(client.get_exchange_rates()["rates"]).T.reset_index()
    df.drop("index", axis=1, inplace=True)
    create_df_index(df, "index")
    df.columns = ["Index", "Name", "Unit", "Value", "Type"]
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
    pandas.DataFrame
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
        lambda x: replace_underscores_in_column_names(x) if isinstance(x, str) else x
    )
    return df


@log_start_end(log=logger)
def get_global_markets_info() -> pd.DataFrame:
    """Get global statistics about crypto markets from CoinGecko API like:
        Market_Cap, Volume, Market_Cap_Percentage

    [Source: CoinGecko]

    Returns
    -------
    pandas.DataFrame
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
    pandas.DataFrame
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
        lambda x: replace_underscores_in_column_names(x) if isinstance(x, str) else x
    )
    return df
