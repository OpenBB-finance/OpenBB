"""The Graph model"""
__docformat__ = "numpy"

import datetime
import logging

import pandas as pd

from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_very_long_number_formatter,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

# pylint: disable=unsupported-assignment-operation

logger = logging.getLogger(__name__)
# pylint: disable=unsupported-assignment-operation

UNI_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"

SWAPS_FILTERS = ["Datetime", "USD", "From", "To"]

POOLS_FILTERS = [
    "volumeUSD",
    "token0.name",
    "token0.symbol",
    "token1.name",
    "token1.symbol",
    "volumeUSD",
    "txCount",
]

TOKENS_FILTERS = [
    "index",
    "symbol",
    "name",
    "tradeVolumeUSD",
    "totalLiquidity",
    "txCount",
]

PAIRS_FILTERS = [
    "created",
    "pair",
    "token0",
    "token1",
    "volumeUSD",
    "txCount",
    "totalSupply",
]

# TODO: convert USD values to int. otherwise sort by these columns won't work


@log_start_end(log=logger)
def query_graph(url: str, query: str) -> dict:
    """Helper methods for querying graphql api. [Source: https://thegraph.com/en/]

    Parameters
    ----------
    url: str
        Endpoint url
    query: str
        Graphql query

    Returns
    -------
    dict:
        Dictionary with response data
    """

    response = request(url, method="POST", json={"query": query})
    if response.status_code == 200:
        return response.json()["data"]
    return {}


@log_start_end(log=logger)
def get_uni_tokens(
    skip: int = 0, limit: int = 100, sortby: str = "index", ascend: bool = False
) -> pd.DataFrame:
    """Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]

    Parameters
    ----------
    skip: int
        Skip n number of records.
    limit: int
        Show n number of records.
    sortby: str
        The column to sort by
    ascend: bool
        Whether to sort in ascending order

    Returns
    -------
    pd.DataFrame
        Uniswap tokens with trading volume, transaction count, liquidity.
    """

    limit = min(limit, 1000)
    query = f"""
    {{
    tokens(first: {limit}, skip:{skip}) {{
        symbol
        name
        tradeVolumeUSD
        totalLiquidity
        txCount
        }}
    }}
    """

    data = query_graph(UNI_URL, query)
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data["tokens"]).reset_index()
    return df.sort_values(by=sortby, ascending=ascend)


@log_start_end(log=logger)
def get_uniswap_stats() -> pd.DataFrame:
    """Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]

    uniswapFactory id: 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f - ethereum address on which Uniswap Factory
    smart contract was deployed. The factory contract is deployed once from the off-chain source code, and it contains
    functions that make it possible to create exchange contracts for any ERC20 token that does not already have one.
    It also functions as a registry of ERC20 tokens that have been added to the system, and the exchange with which they
    are associated. More: https://docs.uniswap.org/protocol/V1/guides/connect-to-uniswap
    We use 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f address to fetch all smart contracts that were
    created with usage of this factory.


    Returns
    -------
    pd.DataFrame
        Uniswap DEX statistics like liquidity, volume, number of pairs, number of transactions.
    """

    query = """
    {
    uniswapFactory(id: "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"){
        totalVolumeUSD
        totalLiquidityUSD
        pairCount
        txCount
        totalLiquidityUSD
        totalLiquidityETH
    }
    }
    """
    data = query_graph(UNI_URL, query)
    if not data:
        return pd.DataFrame()
    df = pd.Series(data["uniswapFactory"]).reset_index()
    df.columns = ["Metric", "Value"]
    df["Value"] = df["Value"].apply(lambda x: lambda_very_long_number_formatter(x))
    return df


@log_start_end(log=logger)
def get_uniswap_pool_recently_added(
    last_days: int = 14,
    min_volume: int = 100,
    min_liquidity: int = 0,
    min_tx: int = 100,
) -> pd.DataFrame:
    """Get lastly added trade-able pairs on Uniswap with parameters like:
        * number of days the pair has been active,
        * minimum trading volume,
        * minimum liquidity,
        * number of transactions.

    [Source: https://thegraph.com/en/]

    Parameters
    ----------
    last_days: int
        How many days back to look for added pairs.
    min_volume: int
        Minimum volume
    min_liquidity: int
        Minimum liquidity
    min_tx: int
        Minimum number of transactions done in given pool.

    Returns
    -------
    pd.DataFrame
        Lastly added pairs on Uniswap DEX.
    """

    days = int(
        (datetime.datetime.now() - datetime.timedelta(days=last_days)).timestamp()
    )
    query = f"""
    {{
        pairs(first: 1000,
        where: {{createdAtTimestamp_gt: "{days}", volumeUSD_gt: "{min_volume}", reserveUSD_gt: "{min_liquidity}",
        txCount_gt: "{min_tx}" }},
        orderBy: createdAtTimestamp, orderDirection: desc) {{
        token0 {{
            symbol
            name
        }}
        token1 {{
            symbol
            name
        }}
        reserveUSD
        volumeUSD
        createdAtTimestamp
        totalSupply
        txCount
        }}
    }}
    """

    data = query_graph(UNI_URL, query)
    if not data:
        return pd.DataFrame()

    df = pd.json_normalize(data["pairs"])
    df["createdAtTimestamp"] = df["createdAtTimestamp"].apply(
        lambda x: datetime.datetime.fromtimestamp(int(x))
    )

    df["pair"] = df["token0.symbol"] + "/" + df["token1.symbol"]
    df.rename(
        columns={
            "createdAtTimestamp": "created",
            "token0.name": "token0",
            "token1.name": "token1",
        },
        inplace=True,
    )
    return df[
        [
            "created",
            "pair",
            "token0",
            "token1",
            "volumeUSD",
            "txCount",
            "totalSupply",
        ]
    ]


@log_start_end(log=logger)
def get_uni_pools_by_volume() -> pd.DataFrame:
    """Get uniswap pools by volume. [Source: https://thegraph.com/en/]

    Returns
    -------
    pd.DataFrame
        Trade-able pairs listed on Uniswap by top volume.
    """

    query = """
    {
        pairs(first: 1000, where: {reserveUSD_gt: "1000", volumeUSD_gt: "10000"},
        orderBy: volumeUSD, orderDirection: desc) {
        token0 {
            symbol
            name
        }
        token1 {
            symbol
            name
        }
        volumeUSD
        txCount
        }
    }
    """
    data = query_graph(UNI_URL, query)
    if not data:
        return pd.DataFrame()
    df = pd.json_normalize(data["pairs"])
    return df[
        [
            "token0.name",
            "token0.symbol",
            "token1.name",
            "token1.symbol",
            "volumeUSD",
            "txCount",
        ]
    ]


@log_start_end(log=logger)
def get_last_uni_swaps(
    limit: int = 100, sortby: str = "timestamp", ascend: bool = False
) -> pd.DataFrame:
    """Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]

    Parameters
    ----------
    limit: int
        Number of swaps to return. Maximum possible number: 1000.
    sortby: str
        Key by which to sort data. The table can be sorted by every of its columns
        (see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2).
    ascend: bool
        Flag to sort data descending

    Returns
    -------
    pd.DataFrame
        Last 100 swaps on Uniswap
    """

    limit = min(limit, 1000)

    query = f"""
    {{
        swaps(first: {limit}, orderBy: timestamp, orderDirection: desc) {{
            timestamp
            pair {{
                token0 {{
                    symbol
                }}
                token1 {{
                    symbol
                }}
            }}
            amountUSD
        }}
    }}
    """

    data = query_graph(UNI_URL, query)
    if not data:
        return pd.DataFrame()
    df = pd.json_normalize(data["swaps"])

    df["timestamp"] = df["timestamp"].apply(
        lambda x: datetime.datetime.fromtimestamp(int(x))
    )
    df["amountUSD"] = df["amountUSD"].apply(lambda x: round(float(x), 2))
    to_rename = {
        "timestamp": "Datetime",
        "amountUSD": "USD",
        "pair.token0.symbol": "From",
        "pair.token1.symbol": "To",
    }
    df = df.rename(columns=to_rename)
    if sortby in df.columns:
        df = df.sort_values(by=sortby, ascending=ascend)
    else:
        console.print(f"[red]Dataframe does not have column {sortby}[/red]\n")
    return df
