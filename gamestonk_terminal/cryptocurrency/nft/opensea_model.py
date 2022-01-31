""" opensea.io Model """

import logging
from datetime import datetime

import pandas as pd
import requests

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

API_URL = "https://api.opensea.io/api/v1"


@log_start_end(log=logger)
def get_collection_stats(slug: str) -> pd.DataFrame:
    """Get stats of a nft collection [Source: opensea.io]

    Parameters
    -------
    slug : str
        Opensea collection slug. If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club

    Returns
    -------
    pd.DataFrame
        collection stats
    """
    res = requests.get(f"{API_URL}/collection/{slug}")
    if res.status_code == 200:
        data = res.json()
        collection = data["collection"]
        stats = collection["stats"]
        metrics = [
            "Name",
            "Floor Price (ETH)",
            "Number of Owners",
            "Market Cap (ETH)",
            "Average Price ETH",
            "One day volume (ETH)",
            "One day change (%)",
            "One day sales (ETH)",
            "One day average price (ETH)",
            "Thirty day volume (ETH)",
            "Thirty day change (%)",
            "Thirty day sales (ETH)",
            "Thirty day average price (ETH)",
            "Total Supply (ETH)",
            "Total Sales (ETH)",
            "Total Volume (ETH)",
            "Creation Date",
            "URL",
        ]
        values = [
            collection["name"],
            "-" if not stats["floor_price"] else float(stats["floor_price"]),
            round(float(stats["num_owners"]), 2),
            round(float(stats["market_cap"]), 2),
            round(float(stats["average_price"]), 2),
            round(float(stats["one_day_volume"]), 2),
            round(float(stats["one_day_change"]) * 100, 2),
            round(float(stats["one_day_sales"]), 2),
            round(float(stats["one_day_average_price"]), 2),
            round(float(stats["thirty_day_volume"]), 2),
            round(float(stats["thirty_day_change"]) * 100, 2),
            round(float(stats["thirty_day_sales"]), 2),
            round(float(stats["thirty_day_average_price"]), 2),
            round(float(stats["total_supply"]), 2),
            round(float(stats["total_sales"]), 2),
            round(float(stats["total_volume"]), 2),
            datetime.strptime(
                collection["created_date"], "%Y-%m-%dT%H:%M:%S.%f"
            ).strftime("%b %d, %Y"),
            "-" if not collection["external_url"] else collection["external_url"],
        ]
        df = pd.DataFrame({"Metric": metrics, "Value": values})
        return df
    return pd.DataFrame()
