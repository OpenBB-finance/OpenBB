"""Factors model"""
__docformat__ = "numpy"

from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO

import statsmodels.api as sm
import yfinance as yf
import pandas as pd


def get_fama_raw():
    """Gets base Fama French data to calculate risk"""
    with urlopen(
        "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
    ) as url:

        # Download Zipfile and create pandas DataFrame
        with ZipFile(BytesIO(url.read())) as zipfile:
            with zipfile.open("F-F_Research_Data_Factors.CSV") as zip_open:
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


def get_historical_5(ticker: str):
    """Get 5 year monthly historical performance for a ticker with dividends filtered"""
    tick = yf.Ticker(ticker)
    df = tick.history(period="5y", interval="1mo")
    df = df[df.index.to_series().apply(lambda x: x.day == 1)]
    df = df.drop(["Dividends", "Stock Splits"], axis=1)
    df = df.dropna()
    return df


def capm_information(ticker):
    """Provides information that relates to the CAPM model"""
    df_f = get_fama_raw()
    df_h = get_historical_5(ticker)
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
