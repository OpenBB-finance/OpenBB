"""Invesco Helpers Module"""

from datetime import timedelta
from io import StringIO
from typing import List, Literal

import numpy as np
import pandas as pd
import requests
import requests_cache
from openbb_provider.utils.helpers import make_request

invesco_america_products = requests_cache.CachedSession(
    "OpenBB_Invesco_America_ETF_Products",
    expire_after=timedelta(days=2),
    use_cache_dir=True,
)

invesco_america_etf_info = requests_cache.CachedSession(
    "OpenBB_Invesco_America_ETF_Info",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

invesco_america_etf_holdings = requests_cache.CachedSession(
    "OpenBB_Invesco_America_ETF_Holdings",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

COUNTRIES = Literal["america", "canada"]

INFO_DATA_TYPE = Literal["performance", "nav_performance", "distributions", "holdings_summary"]


class America:
    @staticmethod
    def get_all_etfs(use_cache: bool = True) -> pd.DataFrame:
        """Gets info for all US Invesco ETFs."""

        etfs = pd.DataFrame()
        url = (
            "https://www.invesco.com/us/financial-products/etfs/performance/prices"
            "/main/performance/0?audienceType=Investor&action=download"
        )
        r = invesco_america_products.get(url, timeout=5) if use_cache is True else make_request(url)

        if r.status_code != 200:
            raise RuntimeError(f"HTTP Error -> {str(r.status_code)}")

        try:
            etfs = pd.read_csv(StringIO(r.text), header=4)

            etfs["Inception_Date"] = pd.to_datetime(
                etfs["Inception_Date"], yearfirst=True
            )
            etfs["Date"] = pd.to_datetime(etfs["Date"], yearfirst=True)
            etfs["Distribution_Frequency"] = (
                etfs["Distribution_Frequency"].astype(str).replace("nan", None)
            )
            etfs["Twelve_Month_Yield"] = (
                etfs["Twelve_Month_Yield"].astype(float).replace(np.nan, None)
            )
            # etfs = etfs.fillna(value=None)
            etfs["Index_Ticker"] = (
                etfs["Index_Ticker"].astype(str).str.replace("nan", "")
            )
            etfs["IIV_Ticker"] = etfs["IIV_Ticker"].astype(str).str.replace("nan", "")
            etfs["ISIN"] = etfs["ISIN"].astype(str).str.replace("nan", "")
            etfs["CUSIP"] = etfs["CUSIP"].astype(str).str.replace("nan", "")
            etfs["Options"] = etfs["Options"].astype(str)
            etfs["Short"] = etfs["Short"].astype(str)
            etfs["Marginable"] = etfs["Marginable"].astype(str)

        except Exception as e:
            raise RuntimeError("Error with Invesco endpoint ->" + str(e))

        return etfs

    @staticmethod
    def get_etf_info(
        symbol: str,
        data_type: INFO_DATA_TYPE = "performance",
        use_cache: bool = True
    ) -> pd.DataFrame:
        """Gets a list of tables for a given ETF from HTML."""

        data_type_dict = {"performance": 0, "nav_performance": -2, "distributions": 3, "holdings_summary": -4}

        data = pd.DataFrame()
        symbols = America.get_all_etfs().Ticker.tolist()

        if symbol not in symbols:
            return pd.DataFrame()

        url = f"https://www.invesco.com/us/financial-products/etfs/product-detail?audienceType=Investor&ticker={symbol}"
        r = invesco_america_etf_info.get(url, timeout=5) if use_cache is True else make_request(url)

        if r.status_code != 200:
            raise RuntimeError(f"HTTP Error -> {str(r.status_code)}")

        data = pd.read_html(StringIO(r.text))

        # Dividends and Distributions are [-3]
        # Bid/Ask MidPoint Above NAV are [-2]
        data[-2] = (
            data[-2]
            .droplevel(0, axis=1)
            .rename(columns={"Days": "Days Midpoint Above NAV"})
        )
        # Bid/Ask MidPoint Below NAV are [-1]
        data[-1] = (
            data[-1]
            .droplevel(0, axis=1)
            .rename(columns={"Days": "Days Midpoint Below NAV"})
        )
        # Performance vs Index are [0] and split on row 4. [1] appears to duplicate.
        data[0] = (
            data[0]
            .dropna(how="all")
            .rename(columns={"Index History (%)" : "performance"})
            .set_index("performance")
            .drop("Fund History (%)")
            .reset_index()
        )
        # Percent of Fund are [-4]

        return data[data_type_dict[data_type]]


    @staticmethod
    def get_historical_nav_discount(symbol: str):

        data = pd.DataFrame()

        symbols = America.get_all_etfs().Ticker.tolist()
        if symbol not in symbols:
            return data

        url = f"https://www.invesco.com/us/financial-products/etfs/product-detail/main/distributions/03?audienceType=Investor&action=download&ticker={symbol}"

        r = make_request(url)

        if r.status_code != 200:
            raise RuntimeError(f"HTTP Error -> {str(r.status_code)}")

        data = pd.read_csv(StringIO(r.content.decode())).dropna()
        data["Date"] = pd.to_datetime(data["Date"], yearfirst=True).dt.strftime("%Y-%m-%d")
        data = data.rename(columns = {" Premium/Discount": "Premium/Discount (%)"})
        data["Premium/Discount (%)"] = data["Premium/Discount (%)"].astype(str).str.replace("%", "").astype(float)

        return data.sort_values(by="Date", ascending=True).to_dict("records")
