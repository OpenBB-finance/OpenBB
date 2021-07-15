"""WSJ model"""
__docformat__ = "numpy"
import requests
import pandas as pd


def etf_movers(sort_type: str = "gainers") -> pd.DataFrame:
    """
    Scrape data for top etf movers.
    Parameters
    ----------
    sort_type: str
        Data to get.  Can be "gainers", "decliners" or "activity

    Returns
    -------
    etfmovers: pd.DataFrame
        Datafame containing the name, price, change and the volume of the etf
    """

    if sort_type == "gainers":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22leaders%22%2C%22count%22%3A25%7D&type=mdc_etfmovers"
        )
    elif sort_type == "decliners":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22laggards%22%2C%22count%22%3A25%7D&type=mdc_etfmovers"
        )
    elif sort_type == "active":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22most_active%22%2C%22count%22%3A25%7D&type=mdc_etfmovers"
        )

    data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).json()
    name, last_price, net_change, percent_change, volume = [], [], [], [], []

    for entry in data["data"]["instruments"]:
        name.append(entry["name"])
        last_price.append(entry["lastPrice"])
        net_change.append(entry["priceChange"])
        percent_change.append(entry["percentChange"])
        volume.append(entry["formattedVolume"])

    etfmovers = pd.DataFrame(
        {
            " ": name,
            "Price": last_price,
            "Chg": net_change,
            "%Chg": percent_change,
            "Vol": volume,
        }
    )

    return etfmovers
