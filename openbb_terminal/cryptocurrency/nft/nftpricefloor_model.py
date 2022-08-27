""" NFT Price Floor Model """

import logging
from typing import List

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

API_URL = "https://api-bff.nftpricefloor.com"


def get_collection_slugs() -> List[str]:
    df = get_collections()
    return df["slug"].values


@log_start_end(log=logger)
def get_collections() -> pd.DataFrame:
    """Get nft collections [Source: https://nftpricefloor.com/]

    Parameters
    -------

    Returns
    -------
    pd.DataFrame
        nft collections
    """
    res = requests.get(f"{API_URL}/nfts")
    if res.status_code == 200:
        data = res.json()
        df = pd.DataFrame(data)
        return df
    return pd.DataFrame()


@log_start_end(log=logger)
def get_floor_price(slug) -> pd.DataFrame:
    """Get nft collections [Source: https://nftpricefloor.com/]

    Parameters
    -------
    slug: str
        nft collection slug

    Returns
    -------
    pd.DataFrame
        nft collections
    """
    res = requests.get(f"{API_URL}/nft/{slug}/chart/pricefloor?interval=all")
    if res.status_code == 200:
        data = res.json()
        df = pd.DataFrame(
            data, columns=["dates", "dataPriceFloorETH", "dataVolumeETH", "sales"]
        )
        df = df.set_index("dates")
        df.index = pd.to_datetime(df.index)
        return df
    return pd.DataFrame()
