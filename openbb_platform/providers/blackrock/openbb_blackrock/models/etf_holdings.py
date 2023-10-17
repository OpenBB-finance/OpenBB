"""Blackrock ETF Holdings fetcher."""

from datetime import date as dateType
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from openbb_blackrock.utils.helpers import (
    COUNTRIES,
    America,
    Canada,
    blackrock_america_historical_holdings,
    blackrock_america_holdings,
    blackrock_canada_historical_holdings,
    blackrock_canada_holdings,
)
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field


class BlackrockEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """Blackrock ETF Holdings query.

    Source: https://www.blackrock.com/
    """

    date: Optional[Union[str, dateType]] = Field(
        description="The as-of date for historical daily holdings.", default=None
    )
    country: Optional[COUNTRIES] = Field(
        description="The country the ETF is registered in.", default="america"
    )


class BlackrockEtfHoldingsData(EtfHoldingsData):
    """Blackrock ETF Holdings Data."""

    symbol: Optional[str] = Field(
        description="The asset's ticker symbol.", alias="Ticker", default=None
    )
    name: Optional[str] = Field(
        description="The name of the holding.", alias="Name", default=None
    )
    weight: Optional[Union[float, str]] = Field(
        description="The weight of the holding.", alias="Weight (%)", default=None
    )
    price: Optional[Union[float, str]] = Field(
        description="The price-per-share of the asset.", alias="Price", default=None
    )
    shares: Optional[Union[float, str]] = Field(
        description="The number of shares held.", alias="Shares", default=None
    )
    market_value: Optional[Union[float, str]] = Field(
        description="The market value of the holding.",
        alias="Market Value",
        default=None,
    )
    notional_value: Optional[Union[float, str]] = Field(
        description="The notional value of the holding.",
        alias="Notional Value",
        default=None,
    )
    asset_class: Optional[str] = Field(
        description="The asset class of the holding.", alias="Asset Class", default=None
    )
    sector: Optional[str] = Field(
        description="The sector the asset belongs to.", alias="Sector", default=None
    )
    isin: Optional[str] = Field(
        description="The ISIN of the asset.", alias="ISIN", default=None
    )
    sedol: Optional[str] = Field(
        description="The SEDOL of the asset.", alias="SEDOL", default=None
    )
    cusip: Optional[str] = Field(
        description="The CUSIP of the asset.", alias="CUSIP", default=None
    )
    exchange: Optional[str] = Field(
        description="The exchange the asset is traded on.",
        alias="Exchange",
        default=None,
    )
    country: Optional[str] = Field(
        description="The location of the risk exposure is.",
        alias="Location of Risk",
        default=None,
    )
    currency: Optional[str] = Field(
        description="The currency of the asset.", alias="Currency", default=None
    )
    market_currency: Optional[str] = Field(
        description="The currency for the market the asset trades in.",
        alias="Market Currency",
        default=None,
    )
    fx_rate: Optional[float] = Field(
        description="The exchange rate of the asset against the fund's base currency.",
        alias="FX Rate",
        default=None,
    )
    coupon: Optional[Union[float, str]] = Field(
        description="The coupon rate of the asset.", alias="Coupon (%)", default=None
    )
    par_value: Optional[Union[float, str]] = Field(
        description="The par value of the asset.", alias="Par Value", default=None
    )
    ytm: Optional[Union[float, str]] = Field(
        description="The yield-to-maturity of the asset.", alias="YTM (%)", default=None
    )
    real_ytm: Optional[Union[float, str]] = Field(
        description="The real yield-to-maturity of the asset.",
        alias="Real YTM (%)",
        default=None,
    )
    yield_to_worst: Optional[Union[float, str]] = Field(
        description="The yield-to-worst of the asset.",
        alias="Yield to Worst (%)",
        default=None,
    )
    duration: Optional[Union[float, str]] = Field(
        description="The duration of the asset.", alias="Duration", default=None
    )
    real_duration: Optional[Union[float, str]] = Field(
        description="The real duration of the asset.",
        alias="Real Duration",
        default=None,
    )
    yield_to_call: Optional[Union[float, str]] = Field(
        description="The yield-to-call of the asset.",
        alias="Yield to Call (%)",
        default=None,
    )
    mod_duration: Optional[Union[float, str]] = Field(
        description="The modified duration of the asset.",
        alias="Mod. Duration",
        default=None,
    )
    maturity: Optional[Union[float, str]] = Field(
        description="The maturity date of the asset.", alias="Maturity", default=None
    )
    accrual_date: Optional[Union[str, dateType]] = Field(
        description="The accrual date of the asset.", default=None, alias="Accrual Date"
    )
    effective_date: Optional[Union[str, dateType]] = Field(
        description="The effective date of the asset.",
        default=None,
        alias="Effective Date",
    )


class FinalEtfHoldingsData(Data):
    holdings_data: Optional[List[BlackrockEtfHoldingsData]] = Field(default=None)
    extra_info: Optional[Dict[str, Any]] = Field(default=None)


class BlackrockEtfHoldingsFetcher(
    Fetcher[
        BlackrockEtfHoldingsQueryParams,
        FinalEtfHoldingsData,
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
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        """Return the raw data from the Blackrock endpoint."""
        query.symbol = query.symbol.upper()
        data: Tuple[List[Dict], Dict[str, Any]]
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
            if not query.date:
                r = blackrock_canada_holdings.get(url, timeout=10)
            if query.date:
                r = blackrock_canada_historical_holdings.get(url, timeout=10)

        if query.country == "america":
            symbols = America.get_all_etfs()["symbol"].to_list()
            if query.symbol not in symbols:
                raise ValueError(
                    f"Symbol, {query.symbol}, not found from Blackrock US. "
                    "Use search(provider='blackrock', country='america')"
                )
            url = America.generate_holdings_url(query.symbol, query.date)  # type: ignore
            if not query.date:
                r = blackrock_america_holdings.get(url, timeout=10)
            if query.date:
                r = blackrock_america_historical_holdings.get(url, timeout=10)

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
            metadata = pd.read_csv(StringIO(r.text), nrows=4).iloc[:, 0]  # type: ignore
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

        data = (holdings.to_dict("records"), metadata.dropna().to_dict())

        return data

    @staticmethod
    def transform_data(
        data: Tuple[List[Dict], Dict], **kwargs: Any
    ) -> FinalEtfHoldingsData:
        """Transform the data to the standard format."""
        holdings: List[Dict] = data[0]
        results = [BlackrockEtfHoldingsData.model_validate(d) for d in holdings]
        metadata = data[1]
        output = FinalEtfHoldingsData()
        output.holdings_data = results
        output.extra_info = metadata
        return output
