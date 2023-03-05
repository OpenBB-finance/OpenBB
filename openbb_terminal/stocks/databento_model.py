__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
from datetime import datetime, timedelta
from io import StringIO

# IMPORTATION THIRDPARTY
import pandas as pd
import requests
from pydantic import BaseModel

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
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
        one minute, so try to keep smaller requests."""
        base_url = "https://hist.databento.com/v0/symbology.resolve"
        params = {
            "dataset": self.exchange,
            "symbols": self.symbol,
            "start_date": self.start,
            "end_date": self.end,
            "stype_in": "smart",
            "stype_out": "product_id",
        }
        auth = requests.auth.HTTPBasicAuth(
            get_current_user().credentials.API_DATABENTO_KEY, ""
        )
        # This seems to only work for futures? Assume the user is entering correct stock ticker
        if self.exchange == "XNAS.ITCH":
            return True
        result = request(base_url, params=params, auth=auth, timeout=30)
        if "message" not in result.json():
            console.print(
                "Issue validating symbol in the date range. Please check with DataBento for symbology."
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

    @log_start_end(log=logger)
    @check_api_key(["API_DATABENTO_KEY"])
    def get_historical(self) -> pd.DataFrame:
        """Prepares the request to be made.  I am using their https interface instead of their python client.
        Their next update will change symbol.V.0 to symbol.C.0"""

        base_url = "https://hist.databento.com/v0/timeseries.stream"
        symbol = self.symbol + ".V.0" if self.exchange == "GLBX.MDP3" else self.symbol
        params = {
            "dataset": self.exchange,
            "symbols": symbol,
            "schema": "ohlcv-1d",
            "start": self.start,
            "end": self.end,
            "stype_in": self.stype,
            "encoding": "csv",
        }
        auth = requests.auth.HTTPBasicAuth(
            get_current_user().credentials.API_DATABENTO_KEY, ""
        )
        data = self.process_request(base_url, params, auth)
        if data.empty:
            console.print(f"No data found for symbol `{self.symbol}`.")
        return data

    def process_request(self, base_url, params, auth) -> pd.DataFrame:
        """Takes the request and returns the adjusted dataframe"""
        r = request(base_url, params=params, auth=auth)
        if r.status_code != 200:
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


@log_start_end(log=logger)
@check_api_key(["API_DATABENTO_KEY"])
def get_historical_stock(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Gets historical EOD data from DataBento.  Currently, just NASDAQ is supported.

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


@log_start_end(log=logger)
@check_api_key(["API_DATABENTO_KEY"])
def get_historical_futures(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
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
