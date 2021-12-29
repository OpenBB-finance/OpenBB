""" opensea.io Model """

import requests
import pandas as pd

API_URL = "https://api.opensea.io/api/v1"


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
            float(stats["num_owners"]),
            float(stats["market_cap"]),
            float(stats["average_price"]),
            float(stats["one_day_volume"]),
            float(stats["one_day_change"]) * 100,
            float(stats["one_day_sales"]),
            float(stats["one_day_average_price"]),
            float(stats["thirty_day_volume"]),
            float(stats["thirty_day_change"]) * 100,
            float(stats["thirty_day_sales"]),
            float(stats["thirty_day_average_price"]),
            float(stats["total_supply"]),
            float(stats["total_sales"]),
            float(stats["total_volume"]),
            collection["created_date"],
            "-" if not collection["external_url"] else collection["external_url"],
        ]
        df = pd.DataFrame({"Metric": metrics, "Value": values})
        return df
    return pd.DataFrame()
