"""NYSE Short Data Model"""
__docformat__ = "numpy"

import logging

import pandas as pd
import pymongo

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_short_data_by_exchange(ticker: str) -> pd.DataFrame:
    """Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021

    Parameters
    ----------
    ticker : str
        Ticker to get data for

    Returns
    -------
    pd.DataFrame
        DataFrame of short data by exchange
    """
    exchanges = ["ARCA", "Amex", "Chicago", "National", "NYSE"]
    mongo_url = "mongodb+srv://terminal:terminal@cluster0.rdmzt.mongodb.net/"  # pragma: allowlist secret
    mongo_url += (
        "NYSE_ShortData?retryWrites=true&w=majority"  # pragma: allowlist secret
    )
    client = pymongo.MongoClient(mongo_url)
    db = client.NYSE_ShortData
    short_data = pd.DataFrame()
    exchanges = ["ARCA", "Amex", "Chicago", "National", "NYSE"]
    for exchange in exchanges:
        exch_collection = db[exchange]
        try:
            df = pd.DataFrame(exch_collection.find_one({"index": ticker})["data"])
            df["Exchange"] = exchange
            short_data = pd.concat([short_data, df])
        except Exception:
            pass

    if short_data.empty:
        return pd.DataFrame()

    short_data.reset_index(drop=True, inplace=True)
    short_data["NetShort"] = (
        short_data["Short Exempt Volume"] + short_data["Short Volume"]
    )
    short_data["PctShort"] = short_data["NetShort"] / short_data["Total Volume"]
    short_data = short_data.rename(
        columns={
            "Short Exempt Volume": "ShortExempt",
            "Short Volume": "ShortVolume",
            "Total Volume": "TotalVolume",
        }
    )
    return short_data
