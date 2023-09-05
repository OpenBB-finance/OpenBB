"""BlackRock ETF Data"""

from datetime import timedelta
from io import StringIO
from typing import Literal, Optional, Tuple

import pandas as pd
import requests_cache

blackrock_canada_products = requests_cache.CachedSession(
    "OpenBB_Blackrock_Canada_Products",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

blackrock_canada_holdings = requests_cache.CachedSession(
    "OpenBB_Blackrock_Canada_Holdings",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

COUNTRIES = Literal["canada"]


class Canada:
    @staticmethod
    def get_all_etfs():
        r = blackrock_canada_products.get(
            "https://www.blackrock.com/ca/investors/en/product-screener/product-screener-v3.jsn?dcrPath=/templatedata/config/product-screener-v3/data/en/ca-one/ca-one&siteEntryPassthrough=true"
        )
        if r.status_code != 200:
            raise RuntimeError(r.status_code)

        columns = r.json()["data"]["tableData"]["columns"]
        column_names = []
        for column in columns:
            column_names.append(column["name"])

        data = pd.DataFrame.from_records(r.json()["data"]["tableData"]["data"])
        data.columns = column_names
        data = data.rename(columns={"localExchangeTicker": "symbol"})

        return data.convert_dtypes()

    @staticmethod
    def generate_holdings_url(symbol: str, date: str = "") -> str:
        """Generates the URL for the Blackrock Canada ETF holdings.

        Parameters
        ----------
        symbol: str
            The ETF symbol.
        date: str
            The as-of date for historical daily holdings.
        """

        symbol = symbol.upper()
        date = date.replace("-", "")
        etfs = Canada.get_all_etfs()
        # etf_url = etfs[etfs["symbol"] == symbol]["productPageUrl"].iloc[0]
        portfolioID = etfs[etfs["symbol"] == symbol]["portfolioId"].iloc[0]
        symbol = symbol.replace(".", "")

        base_url = f"https://www.blackrock.com/ca/investors/en/products/{portfolioID}/fund/1464253357814.ajax?fileType=csv"
        if not date:
            url = base_url + f"&asOfDate={date}"
        url = base_url + f"&fileName={symbol}_holdings&dataType=fund"

        # url = (
        #    f"https://www.blackrock.com{etf_url}/1464253357814.ajax?"
        #    + f"fileType=csv&asOfDate={date}&fileName={symbol}_holdings&dataType=fund"
        # )

        return url

    @staticmethod
    def get_holdings(symbol: str, date: str = "") -> Tuple[pd.DataFrame, pd.Series]:
        """Gets the Blackrock Canada ETF holdings."""

        url = Canada.generate_holdings_url(symbol, date)

        r = blackrock_canada_holdings.get(url, timeout=10)

        if r.status_code != 200:
            raise RuntimeError(r.status_code)

        metadata = pd.read_csv(StringIO(r.text), nrows=8).iloc[:, 0]

        holdings = pd.read_csv(StringIO(r.text), header=10, thousands=",")

        holdings = holdings.replace("-", "").convert_dtypes()

        return holdings, metadata
