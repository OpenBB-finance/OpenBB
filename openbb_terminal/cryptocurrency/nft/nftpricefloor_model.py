""" NFT Price Floor Model """

import logging
from typing import List

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)

API_URL = "https://api-bff.nftpricefloor.com"


@log_start_end(log=logger)
def get_collection_slugs() -> List[str]:
    df = get_collections()
    if not df.empty and "slug" in df.columns:
        return df["slug"].tolist()
    return []


@log_start_end(log=logger)
def get_collections() -> pd.DataFrame:
    """Get nft collections [Source: https://nftpricefloor.com/]

    Parameters
    ----------

    Returns
    -------
    pd.DataFrame
        nft collections
    """
    res = request(f"{API_URL}/projects", timeout=10)
    if res.status_code == 200:
        data = res.json()
        df = pd.DataFrame(data)
        df_stats = pd.json_normalize(df["stats"])
        df = pd.concat([df, df_stats], axis=1)
        return df
    return pd.DataFrame()


@log_start_end(log=logger)
def get_floor_price(slug: str) -> pd.DataFrame:
    """Get nft collections [Source: https://nftpricefloor.com/]

    Parameters
    ----------
    slug: str
        nft collection slug

    Returns
    -------
    pd.DataFrame
        nft collections
    """
    res = request(f"{API_URL}/projects/{slug}/charts/all", timeout=10)
    if res.status_code == 200:
        data = res.json()
        df = pd.DataFrame(
            data, columns=["timestamps", "floorEth", "volumeEth", "salesCount"]
        )
        df = df.set_index("timestamps")
        df.index = pd.to_datetime(df.index * 1_000_000)
        df.index = pd.DatetimeIndex(df.index.rename("date").strftime("%Y-%m-%d"))
        df = df.reset_index().drop_duplicates(subset=["date"])
        return df.set_index("date")
    return pd.DataFrame()
