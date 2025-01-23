"""FMP ETF Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import Field


class FMPEtfSearchQueryParams(EtfSearchQueryParams):
    """FMP ETF Search Query."""

    __json_schema_extra__ = {
        "exchange": {
            "multiple_items_allowed": False,
            "choices": ["AMEX", "NYSE", "NASDAQ", "ETF", "TSX", "EURONEXT"],
        }
    }

    exchange: Optional[Literal["AMEX", "NYSE", "NASDAQ", "ETF", "TSX", "EURONEXT"]] = (
        Field(
            description="The exchange code the ETF trades on.",
            default=None,
        )
    )
    is_active: Optional[Literal[True, False]] = Field(
        description="Whether the ETF is actively trading.",
        default=None,
    )


class FMPEtfSearchData(EtfSearchData):
    """FMP ETF Search Data."""

    __alias_dict__ = {
        "name": "companyName",
        "market_cap": "marketCap",
        "last_annual_dividend": "lastAnnualDividend",
        "exchange": "exchangeShortName",
        "exchange_name": "exchange",
        "actively_trading": "isActivelyTrading",
    }

    market_cap: Optional[float] = Field(
        description="The market cap of the ETF.", default=None
    )
    sector: Optional[str] = Field(description="The sector of the ETF.", default=None)
    industry: Optional[str] = Field(
        description="The industry of the ETF.", default=None
    )
    beta: Optional[float] = Field(description="The beta of the ETF.", default=None)
    price: Optional[float] = Field(
        description="The current price of the ETF.", default=None
    )
    last_annual_dividend: Optional[float] = Field(
        description="The last annual dividend paid.",
        default=None,
    )
    volume: Optional[float] = Field(
        description="The current trading volume of the ETF.", default=None
    )
    exchange: Optional[str] = Field(
        description="The exchange code the ETF trades on.",
        default=None,
    )
    exchange_name: Optional[str] = Field(
        description="The full name of the exchange the ETF trades on.",
        default=None,
    )
    country: Optional[str] = Field(
        description="The country the ETF is registered in.", default=None
    )
    actively_trading: Optional[Literal[True, False]] = Field(
        description="Whether the ETF is actively trading.",
        default=None,
    )


class FMPEtfSearchFetcher(
    Fetcher[
        FMPEtfSearchQueryParams,
        List[FMPEtfSearchData],
    ]
):
    """FMP ETF Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEtfSearchQueryParams:
        """Transform the query."""
        return FMPEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import create_url, get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            version=3,
            endpoint="stock-screener",
            api_key=api_key,
            query={"isEtf": True, "limit": 10000},
            exclude=["symbol"],
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfSearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEtfSearchData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        etfs = DataFrame(data)
        etfs.drop(columns="isEtf", inplace=True)

        if query.is_active:
            etfs = etfs[etfs["isActivelyTrading"] == query.is_active]

        if query.exchange:
            etfs = etfs[etfs["exchangeShortName"] == query.exchange]

        if query.query:
            etfs = etfs[
                etfs["companyName"].str.contains(query.query, case=False)
                | etfs["exchangeShortName"].str.contains(query.query, case=False)
                | etfs["exchange"].str.contains(query.query, case=False)
                | etfs["sector"].str.contains(query.query, case=False)
                | etfs["industry"].str.contains(query.query, case=False)
                | etfs["country"].str.contains(query.query, case=False)
            ]
        etfs = (
            etfs.fillna("N/A").replace("N/A", None).replace("", None).replace(0, None)
        )
        return [FMPEtfSearchData.model_validate(d) for d in etfs.to_dict("records")]
