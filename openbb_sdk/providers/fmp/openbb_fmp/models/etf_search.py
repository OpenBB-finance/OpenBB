"""FMP ETF Search fetcher."""

from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from openbb_fmp.utils.helpers import get_available_etfs
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field


class FMPEtfSearchQueryParams(EtfSearchQueryParams):
    """FMP ETF Search Query Params"""

    exchange: Optional[
        Literal["AMEX", "NYSE", "NASDAQ", "ETF", "TSX", "EURONEXT"]
    ] = Field(
        description="The exchange code the ETF trades on.",
        default=None,
    )
    is_active: Optional[Literal[True, False]] = Field(
        description="Whether the ETF is actively trading.",
        default=None,
    )


class FMPEtfSearchData(EtfSearchData):
    """FMP ETF Search Data."""

    class Config:
        """Pydantic alias config using fields Dict."""

        fields = {
            "name": "companyName",
        }

    market_cap: Optional[float] = Field(
        description="The market cap of the ETF.", alias="marketCap"
    )
    sector: Optional[str] = Field(description="The sector of the ETF.")
    industry: Optional[str] = Field(description="The industry of the ETF.")
    beta: Optional[float] = Field(description="The beta of the ETF.")
    price: Optional[float] = Field(description="The current price of the ETF.")
    last_annual_dividend: Optional[float] = Field(
        description="The last annual dividend paid.", alias="lastAnnualDividend"
    )
    volume: Optional[float] = Field(
        description="The current trading volume of the ETF."
    )
    exchange: Optional[str] = Field(
        description="The exchange code the ETF trades on.", alias="exchangeShortName"
    )
    exchange_name: Optional[str] = Field(
        description="The full name of the exchange the ETF trades on.", alias="exchange"
    )
    country: Optional[str] = Field(description="The country the ETF is registered in.")
    actively_trading: Optional[Literal[True, False]] = Field(
        description="Whether the ETF is actively trading.", alias="isActivelyTrading"
    )


class FMPEtfSearchFetcher(
    Fetcher[
        FMPEtfSearchQueryParams,
        List[FMPEtfSearchData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfSearchQueryParams:
        """Transform the query."""
        return FMPEtfSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""

        api_key = credentials.get("fmp_api_key") if credentials else ""
        etfs = get_available_etfs(api_key=api_key)  # type: ignore
        if len(etfs) == 0:
            raise ValueError("No ETFs found")
        etfs = pd.DataFrame(etfs)
        etfs.drop(columns="isEtf", inplace=True)

        if query.is_active is True:
            etfs = etfs[etfs["isActivelyTrading"] == True]  # noqa

        if query.is_active is False:
            etfs = etfs[etfs["isActivelyTrading"] == False]  # noqa

        if query.exchange is not None:
            etfs = etfs[etfs["exchangeShortName"] == query.exchange]

        if query.query:
            etfs = etfs[
                etfs["companyName"].str.contains(query.query, case=False)
                | etfs["exchangeShortName"].str.contains(query.query, case=False)
                | etfs["exchange"].str.contains(query.query, case=False)
                | etfs["sector"].str.contains(query.query, case=False)
                | etfs["industry"].str.contains(query.query, case=False)
            ]

        return etfs.to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPEtfSearchData]:
        """Return the transformed data."""
        return [FMPEtfSearchData(**d) for d in data]
