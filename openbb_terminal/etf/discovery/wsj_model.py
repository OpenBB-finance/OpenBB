"""WSJ model"""
__docformat__ = "numpy"
import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def etf_movers(sort_type: str = "gainers", export: bool = False) -> pd.DataFrame:
    """
    Scrape data for top etf movers.
    Parameters
    ----------
    sort_type: str
        Data to get. Can be "gainers", "decliners" or "active"

    Returns
    -------
    etfmovers: pd.DataFrame
        Datafame containing the name, price, change and the volume of the etf
    """

    if sort_type.lower() == "gainers":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22leaders%22%2C%22count%22%3A25%7D&type="
            "mdc_etfmovers"
        )
    elif sort_type.lower() == "decliners":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22laggards%22%2C%22count%22%3A25%7D&type="
            "mdc_etfmovers"
        )
    elif sort_type.lower() == "active":
        url = (
            "https://www.wsj.com/market-data/mutualfunds-etfs/etfmovers?id=%7B%22application"
            "%22%3A%22WSJ%22%2C%22etfMover%22%3A%22most_active%22%2C%22count%22%3A25%7D&type="
            "mdc_etfmovers"
        )
    else:
        url = ""

    if url:
        data = request(url, headers={"User-Agent": get_user_agent()}).json()
        symbol, name, last_price, net_change, percent_change, volume = (
            [],
            [],
            [],
            [],
            [],
            [],
        )

        for entry in data["data"]["instruments"]:
            symbol.append(entry["ticker"])
            name.append(entry["name"])
            last_price.append(entry["lastPrice"])
            net_change.append(entry["priceChange"])
            percent_change.append(entry["percentChange"])
            volume.append(entry["formattedVolume"])

        if export:
            etfmovers = pd.DataFrame(
                {
                    " ": symbol,
                    "Name": name,
                    "Price": last_price,
                    "Chg": net_change,
                    "%Chg": percent_change,
                    "Vol": volume,
                }
            )
        else:
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

    return pd.DataFrame()
