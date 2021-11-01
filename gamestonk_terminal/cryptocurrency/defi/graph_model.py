"""The Graph"""
__docformat__ = "numpy"

import datetime
import requests
import pandas as pd


UNI_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"


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

    request = requests.post(url, json={"query": query})
    if request.status_code == 200:
        return request.json()["data"]
    return {}


def get_uni_tokens(skip: int = 0, limit: int = 100) -> pd.DataFrame:
    """Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]

    Parameters
    ----------
    skip:
        Skip n number of records.
    limit: int
        Show n number of records.

    Returns
    -------
    pd.DataFrame
        Uniswap tokens with trading volume, transaction count, liquidity.
    """

    query = """
            {
            tokens(first: %s, skip:%s) {
                symbol
                name
                tradeVolumeUSD
                totalLiquidity
                txCount
                }
            }
        """ % (
        limit,
        skip,
    )

    data = query_graph(UNI_URL, query)
    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data["tokens"]).reset_index()


def get_uniswap_stats():
    """Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]

    Returns
    -------
    pd.DataFrame
        Uniswap DEX statistics like liquidity, volume, number of pairs...
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
    return df


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
    query = """
        {
          pairs(first: 1000,
          where: {createdAtTimestamp_gt: "%s", volumeUSD_gt: "%s", reserveUSD_gt: "%s", txCount_gt: "%s" },
          orderBy: createdAtTimestamp, orderDirection: desc) {
            token0 {
              symbol
              name
            }
            token1 {
              symbol
              name
            }
            reserveUSD
            volumeUSD
            createdAtTimestamp
            totalSupply
            txCount
          }
        }
    """ % (
        days,
        min_volume,
        min_liquidity,
        min_tx,
    )
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


def get_last_uni_swaps() -> pd.DataFrame:
    """Get the last 100 swaps done on Uniswap

    Returns
    -------
    pd.DataFrame
        Last 100 swaps on Uniswap
    """

    query = """
    {
        swaps(first: 100, orderBy: timestamp, orderDirection: desc) {
          timestamp
          pair {
            token0 {
              symbol
            }
            token1 {
              symbol
            }
          }
          amountUSD
        }
    }
    """

    data = query_graph(UNI_URL, query)
    if not data:
        return pd.DataFrame()
    df = pd.json_normalize(data["swaps"])

    df["timestamp"] = df["timestamp"].apply(
        lambda x: datetime.datetime.fromtimestamp(int(x))
    )
    df.columns = ["amountUSD", "timestamp", "token0", "token1"]
    return df[["timestamp", "token0", "token1", "amountUSD"]]
