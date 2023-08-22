"""Factors model"""
__docformat__ = "numpy"

import logging
from io import BytesIO
from typing import Tuple
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd
import statsmodels.api as sm
import yfinance as yf

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_fama_raw() -> pd.DataFrame:
    """Gets base Fama French data to calculate risk

    Returns
    -------
    fama : pd.DataFrame
        A data with fama french model information
    """
    url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
    file = "F-F_Research_Data_Factors.CSV"
    with urlopen(url) as data, ZipFile(  # noqa: S310
        BytesIO(data.read())
    ) as zipfile, zipfile.open(file) as zip_open:
        df = pd.read_csv(
            zip_open,
            header=0,
            names=["Date", "MKT-RF", "SMB", "HML", "RF"],
            skiprows=3,
        )

    df = df[df["Date"].apply(lambda x: len(str(x).strip()) == 6)]
    df["Date"] = df["Date"].astype(str) + "01"
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
    df["MKT-RF"] = pd.to_numeric(df["MKT-RF"], downcast="float")
    df["SMB"] = pd.to_numeric(df["SMB"], downcast="float")
    df["HML"] = pd.to_numeric(df["HML"], downcast="float")
    df["RF"] = pd.to_numeric(df["RF"], downcast="float")
    df["MKT-RF"] = df["MKT-RF"] / 100
    df["SMB"] = df["SMB"] / 100
    df["HML"] = df["HML"] / 100
    df["RF"] = df["RF"] / 100
    df = df.set_index("Date")
    return df


@log_start_end(log=logger)
def get_historical_5(symbol: str) -> pd.DataFrame:
    """Get 5 year monthly historical performance for a ticker with dividends filtered

    Parameters
    ----------
    symbol : str
        A ticker symbol in string form

    Returns
    -------
    data : pd.DataFrame
        A dataframe with historical information
    """
    tick = yf.Ticker(symbol)
    df = tick.history(period="5y", interval="1mo")
    df = df[df.index.to_series().apply(lambda x: x.day == 1)]
    df = df.drop(["Dividends", "Stock Splits"], axis=1)
    df = df.dropna()
    df.index = [d.replace(tzinfo=None) for d in df.index]
    return df


@log_start_end(log=logger)
def capm_information(symbol: str) -> Tuple[float, float]:
    """Provides information that relates to the CAPM model

    Parameters
    ----------
    symbol : str
        A ticker symbol in string form

    Returns
    -------
    Tuple[float, float]
        The beta for a stock, The systematic risk for a stock
    """
    df_f = get_fama_raw()
    df_h = get_historical_5(symbol)
    df = df_h.join(df_f)
    df = df.dropna()
    df["Monthly Return"] = df["Close"].pct_change()
    df["Excess Monthly Return"] = df["Monthly Return"] - df["RF"]
    df["Excess MKT-RF"] = df["MKT-RF"] - df["RF"]
    df = df.dropna()
    y = df[["Excess Monthly Return"]]
    x = df["Excess MKT-RF"]
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    beta = model.params["Excess MKT-RF"]
    sy = model.rsquared
    return beta, sy
