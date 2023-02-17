__docformat__ = "numpy"
import logging
from datetime import datetime, timedelta
from io import StringIO
from typing import Optional

import pandas as pd
import requests
from pydantic import BaseModel

from openbb_terminal.config_terminal import API_DATABENTO_KEY as key
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods


class DataBento(BaseModel):
    symbol: str
    exchange: str = "XNAS.ITCH"
    stype: str = "native"
    start: str = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end: str = datetime.now().strftime("%Y-%m-%d")

    class Config:
        arbitrary_types_allowed = True

    def get_historical_stock(self):
        """Gets historical EOD stock data from DataBento.  Currnetly, just NASDAQ is supported.
        Note that only nonadjusted data is available."""
        self.exchange = "XNAS.ITCH"
        self.stype = "native"
        if not self.validate_symbol():
            return pd.DataFrame()
        return self.get_historical()

    def validate_symbol(self):
        """Validates the symbol is supported by DataBento.  There is no API for this, so we will use their
        Symbology endpoint to see if something exists.  Doing a long time range can make this request on the order of
        one minute, so lets just do end = end and start = end - 5 days"""
        base_url = "https://hist.databento.com/v0/symbology.resolve"
        params = {
            "dataset": self.exchange,
            "symbols": self.symbol,
            "start_date": (
                datetime.strptime(self.end, "%Y-%m-%d") - timedelta(days=5)
            ).strftime("%Y-%m-%d"),
            "end_date": self.end,
            "stype_in": "smart",
            "stype_out": "product_id",
        }
        auth = requests.auth.HTTPBasicAuth(key, "")
        # This seems to only work for futures?  Assume the user is entering correct stock ticker
        if self.exchange == "XNAS.ITCH":
            return True
        result = request(base_url, params=params, auth=auth)
        if "message" not in result.json():
            logger.error("Error validating symbol")
            console.print(
                "Issue validating symbol.  Please check with DataBento that the symbol and dates are valid."
            )
            return False
        return result.json()["message"] != "Not found"

    def get_historical_futures(self):
        """Gets historical EODfutures data from DataBento.  Currently, just CME is supported.
        Note this gets the highest volume contract each day"""
        self.exchange = "GLBX.MDP3"
        self.stype = "smart"
        if not self.validate_symbol():
            return pd.DataFrame()
        return self.get_historical()

    def get_historical(self) -> pd.DataFrame:
        """Prepares the request to be made.  I am using their https interface instead of their python client"""

        base_url = "https://hist.databento.com/v0/timeseries.stream"
        if self.exchange == "GLBX.MDP3":
            # This uses their smart contract notation to get the highest volume contract each day
            # Getting the closest calendar results in low volume spreads
            symbol = self.symbol + ".V.0"
        else:
            # Stock symbols are just the symbol
            symbol = self.symbol
        params = {
            "dataset": self.exchange,
            "symbols": symbol,
            "schema": "ohlcv-1d",
            "start": self.start,
            "end": self.end,
            "stype_in": self.stype,
            "encoding": "csv",
        }
        auth = requests.auth.HTTPBasicAuth(key, "")
        print(key)
        return self.process_request(base_url, params, auth)

    def process_request(self, base_url, params, auth) -> pd.DataFrame:
        """Takes the request and returns the adjusted dataframe"""
        r = request(base_url, params=params, auth=auth)
        if r.status_code != 200:
            print(r.text)
            raise Exception(f"Error: Status Code {r.status_code}")
        df = pd.read_csv(StringIO(r.text))
        df["time"] = pd.to_datetime(df.ts_event, unit="ns")
        df[["open", "high", "low", "close"]] /= 1_000_000_000
        df = df.drop(columns=["ts_event", "publisher_id", "product_id"]).set_index(
            "time"
        )
        df = df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
        )
        return df


def get_historical_stock(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Gets historical EOD data from DataBento.  Currnetly, just NASDAQ is supported.

    Parameters
    ----------
    symbol : str
        Symbol to get data for
    start_date : str
        Start date of data
    end_date : str
        End date to get data for

    """
    db = DataBento(symbol=symbol, start=start_date, end=end_date)
    return db.get_historical_stock()


def get_historical_futures(
    symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None
) -> pd.DataFrame:
    """Gets historical EODfutures data from DataBento.  Currently, just CME is supported.

    Parameters
    ----------
    symbol : str
        Symbol to get data for
    start_date : str
        Start date of data
    end_date : str
        End date to get data for

    """
    db = DataBento(symbol=symbol, start=start_date, end=end_date)
    return db.get_historical_futures()
