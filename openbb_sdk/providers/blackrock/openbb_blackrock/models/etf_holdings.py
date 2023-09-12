"""Blackrock ETF Holdings fetcher."""

from datetime import (
    date as dateType,
    timedelta,
)
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests_cache
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field

from openbb_blackrock.utils.helpers import COUNTRIES, America, Canada

blackrock_canada_holdings = requests_cache.CachedSession(
    "OpenBB_Blackrock_Canada_Holdings",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

blackrock_america_holdings = requests_cache.CachedSession(
    "OpenBB_Blackrock_America_Holdings",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)


class BlackrockEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """Blackrock ETF Holdings query.

    Source: https://www.blackrock.com/
    """

    date: Optional[str | dateType] = Field(
        description="The as-of date for historical daily holdings.", default=""
    )
    country: Optional[COUNTRIES] = Field(
        description="The country the ETF is registered in.", default="america"
    )


class BlackrockEtfHoldingsData(EtfHoldingsData):
    """Blackrock ETF Holdings Data."""

    symbol: Optional[str | None] = Field(
        description="The asset's ticker symbol.", alias="Ticker"
    )
    name: Optional[str | None] = Field(
        description="The name of the asset.", alias="Name"
    )
    weight: Optional[float | str | None] = Field(
        description="The weight of the holding.", alias="Weight (%)"
    )
    price: Optional[float | str | None] = Field(
        description="The price-per-share of the asset.", alias="Price"
    )
    shares: Optional[int | str | None] = Field(
        description="The number of shares held.", alias="Shares"
    )
    market_value: Optional[float | str | None] = Field(
        description="The market value of the holding.", alias="Market Value"
    )
    notional_value: Optional[float | str | None] = Field(
        description="The notional value of the holding.", alias="Notional Value"
    )
    asset_class: Optional[str] = Field(description="The asset class of the asset.")
    sector: Optional[str | None] = Field(
        description="The sector the asset belongs to.", alias="Sector"
    )
    isin: Optional[str | None] = Field(
        description="The ISIN of the asset.", alias="ISIN"
    )
    sedol: Optional[str | None] = Field(
        description="The SEDOL of the asset.", alias="SEDOL"
    )
    cusip: Optional[str | None] = Field(
        description="The CUSIP of the asset.", alias="CUSIP"
    )
    exchange: Optional[str | None] = Field(
        description="The exchange the asset is traded on.", alias="Exchange"
    )
    country: Optional[str | None] = Field(
        description="The location of the risk exposure is.", alias="Location of Risk"
    )
    currency: Optional[str | None] = Field(
        description="The currency of the asset.", alias="Currency"
    )
    market_currency: Optional[str | None] = Field(
        description="The currency for the market the asset trades in.",
        alias="Market Currency",
    )
    fx_rate: Optional[float | None] = Field(
        description="The exchange rate of the asset against the fund's base currency.",
    )
    coupon: Optional[float | str | None] = Field(
        description="The coupon rate of the asset.", alias="Coupon (%)"
    )
    par_value: Optional[float | str | None] = Field(
        description="The par value of the asset.", alias="Par Value"
    )
    ytm: Optional[float | str | None] = Field(
        description="The yield-to-maturity of the asset.", alias="YTM (%)"
    )
    real_ytm: Optional[float | str | None] = Field(
        description="The real yield-to-maturity of the asset.",
        alias="Real YTM (%)",
    )
    yield_to_worst: Optional[float | str | None] = Field(
        description="The yield-to-worst of the asset.", alias="Yield to Worst (%)"
    )
    duration: Optional[float | str | None] = Field(
        description="The duration of the asset.", alias="Duration"
    )
    real_duration: Optional[float | str | None] = Field(
        description="The real duration of the asset.", alias="Real Duration"
    )
    yield_to_call: Optional[float | str | None] = Field(
        description="The yield-to-call of the asset.",
        alias="Yield to Call (%)",
    )
    mod_duration: Optional[float | str | None] = Field(
        description="The modified duration of the asset.",
        alias="Mod. Duration",
    )
    maturity: Optional[float | str | None] = Field(
        description="The maturity date of the asset.", alias="Maturity"
    )
    accrual_date: Optional[str | dateType | None] = Field(
        description="The accrual date of the asset.",
    )
    effective_date: Optional[str | dateType | None] = Field(
        description="The effective date of the asset.",
    )


class BlackrockEtfHoldingsFetcher(
    Fetcher[
        BlackrockEtfHoldingsQueryParams,
        List[BlackrockEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the Blackrock endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BlackrockEtfHoldingsQueryParams:
        """Transform the query."""
        return BlackrockEtfHoldingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlackrockEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Return the raw data from the Blackrock endpoint."""
        query.symbol = query.symbol.upper()
        data: Tuple[pd.DataFrame, Dict[str, Any]]
        holdings: pd.DataFrame = pd.DataFrame()
        metadata = pd.Series(dtype="object")

        if ".TO" in query.symbol or query.country == "canada":
            query.symbol = query.symbol.replace(".TO", "")  # noqa
            query.country = "canada"

        if query.country == "canada":
            symbols = Canada.get_all_etfs()["symbol"].to_list()
            if query.symbol not in symbols:
                raise ValueError(
                    f"Symbol, {query.symbol}, not found from Blackrock Canada. "
                    "Use search(provider='blackrock', country='canada')"
                )
            url = Canada.generate_holdings_url(query.symbol, query.date)  # type: ignore
            r = blackrock_canada_holdings.get(url, timeout=10)

        if query.country == "america":
            symbols = America.get_all_etfs()["symbol"].to_list()
            if query.symbol not in symbols:
                raise ValueError(
                    f"Symbol, {query.symbol}, not found from Blackrock US. "
                    "Use search(provider='blackrock', country='america')"
                )
            url = America.generate_holdings_url(query.symbol, query.date)  # type: ignore
            r = blackrock_america_holdings.get(url, timeout=10)

        if r.status_code != 200:  # type: ignore
            raise RuntimeError(r.status_code)  # type: ignore

        indexed = pd.read_csv(StringIO(r.text), usecols=[0])  # type: ignore
        target = "Ticker" if "Name" not in indexed.iloc[:, 0].to_list() else "Name"
        idx = []
        idx = indexed[indexed.iloc[:, 0] == target].index.tolist()
        idx_value = idx[1] if len(idx) > 1 else idx[0]
        _holdings = pd.read_csv(StringIO(r.text), header=idx_value, thousands=",")  # type: ignore
        _holdings = _holdings.reset_index()
        columns = _holdings.iloc[0, :].values.tolist()
        _holdings.columns = columns
        holdings = (
            _holdings.iloc[1:-1, :]
            if query.country == "canada"
            else _holdings.iloc[1:-2, :]
        )
        holdings = holdings.convert_dtypes().fillna("0")
        try:
            metadata = pd.read_csv(StringIO(r.text), nrows=3).iloc[:, 0]  # type: ignore
        except Exception:
            _metadata = pd.read_csv(
                StringIO(r.text), nrows=1, header=0  # type: ignore
            ).columns.to_list()
            metadata["Fund Holdings as of"] = _metadata[1]

        holdings.loc[:, "Market Value"] = (
            holdings["Market Value"].astype(str).str.replace(",", "")
        )
        holdings.loc[:, "Notional Value"] = (
            holdings["Notional Value"].astype(str).str.replace(",", "")
        )
        if "Shares" in holdings.columns:
            holdings.loc[:, "Shares"] = (
                holdings["Shares"].astype(str).str.replace(",", "").astype(float)
            )
        holdings = holdings.replace("-", "")
        if "Par Value" in holdings.columns:
            holdings.loc[:, "Par Value"] = (
                holdings["Par Value"].astype(str).str.replace(",", "").astype(float)
            )
        holdings = holdings.sort_values(by="Weight (%)", ascending=False).rename(
            columns={"Location": "country"}
        )

        data = (holdings, metadata.to_dict())

        return data

    @staticmethod
    def transform_data(
        data: Tuple[pd.DataFrame, Dict]
    ) -> Tuple[List[BlackrockEtfHoldingsData], Dict]:
        """Transform the data to the standard format."""
        holdings: List[Dict] = data[0].to_dict("records")
        results = [BlackrockEtfHoldingsData.parse_obj(d) for d in holdings]
        metadata = data[1]

        return results, metadata
