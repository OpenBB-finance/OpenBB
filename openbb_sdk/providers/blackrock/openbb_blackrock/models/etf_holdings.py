"""Blackrock ETF Holdings fetcher."""

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional, Tuple

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field

from openbb_blackrock.utils.helpers import Canada


class BlackrockEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """Blackrock ETF Holdings query.

    Source: https://www.blackrock.com/
    """

    date: Optional[str | dateType] = Field(
        description="The as-of date for historical daily holdings.", default=""
    )
    country: Optional[Literal["canada"]] = Field(
        description="The country the ETF is registered in.", default="canada"
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
    sector: Optional[str | None] = Field(
        description="The sector the asset belongs to.", alias="Sector"
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
    ytm: Optional[float | str | None] = Field(
        description="The yield-to-maturity of the asset.", alias="YTM (%)"
    )
    yield_to_worst: Optional[float | str | None] = Field(
        description="The yield-to-worst of the asset.", alias="Yield to Worst (%)"
    )
    duration: Optional[float | str | None] = Field(
        description="The duration of the asset.", alias="Duration"
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
    ) -> Tuple[pd.DataFrame, Dict]:
        """Return the raw data from the Blackrock endpoint."""
        data = ()
        if query.country == "canada":
            symbols = Canada.get_all_etfs()["symbol"].to_list()

            if query.symbol not in symbols:
                raise ValueError(
                    f"Symbol, {query.symbol}, not found from Blackrock Canada. Use search(provider='blackrock')"
                )

            holdings, metadata = Canada.get_holdings(query.symbol, query.date)
            holdings = holdings.to_dict("records")
        data = (holdings, metadata)

        return data

    @staticmethod
    def transform_data(
        data: Tuple[pd.DataFrame, Dict]
    ) -> Tuple[List[BlackrockEtfHoldingsData], Dict]:
        """Transform the data to the standard format."""

        results = [BlackrockEtfHoldingsData.parse_obj(d) for d in data[0]]
        metadata = data[1].to_dict()

        return results, metadata
