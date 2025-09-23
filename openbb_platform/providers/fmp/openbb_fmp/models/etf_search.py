"""FMP ETF Search Model."""

# pylint: disable=unused-argument

from typing import Any, Literal, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_search import (
    EtfSearchData,
    EtfSearchQueryParams,
)
from pydantic import ConfigDict, Field


class FMPEtfSearchQueryParams(EtfSearchQueryParams):
    """FMP ETF Search Query."""

    __json_schema_extra__ = {
        "exchange": {
            "x-widget_config": {
                "options": [
                    {"label": "AMEX", "value": "amex"},
                    {"label": "NYSE", "value": "nyse"},
                    {"label": "NASDAQ", "value": "nasdaq"},
                    {"label": "TSX", "value": "tsx"},
                    {"label": "Euronext", "value": "euronext"},
                ],
            }
        }
    }

    exchange: Optional[Literal["amex", "nyse", "nasdaq", "tsx", "euronext"]] = Field(
        description="Exchange where the ETF is listed. If not provided, all exchanges are searched.",
        default=None,
    )


class FMPEtfSearchData(EtfSearchData):
    """FMP ETF Search Data."""

    model_config = ConfigDict(extra="ignore")

    __alias_dict__ = {
        "name": "companyName",
        "market_cap": "marketCap",
        "last_annual_dividend": "lastAnnualDividend",
        "exchange": "exchangeShortName",
        "exchange_name": "exchange",
    }
    country: Optional[str] = Field(
        description="Country where the ETF is domiciled.", default=None
    )
    exchange: Optional[str] = Field(
        description="Exchange where the ETF is listed.",
        default=None,
    )
    exchange_name: Optional[str] = Field(
        description="The full name of the exchange.",
        default=None,
    )
    market_cap: Optional[Union[int, float]] = Field(
        description="Market capitalization of the ETF.", default=None
    )
    beta: Optional[float] = Field(description="Beta of the ETF.", default=None)
    price: Optional[float] = Field(
        description="Current price of the ETF.", default=None
    )
    last_annual_dividend: Optional[float] = Field(
        description="Last annual dividend paid.",
        default=None,
    )
    volume: Optional[Union[int, float]] = Field(
        description="Current trading volume of the ETF.", default=None
    )


class FMPEtfSearchFetcher(
    Fetcher[
        FMPEtfSearchQueryParams,
        list[FMPEtfSearchData],
    ]
):
    """FMP ETF Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEtfSearchQueryParams:
        """Transform the query."""
        return FMPEtfSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfSearchQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = "https://financialmodelingprep.com/stable/company-screener?isEtf=true&isFund=false&isActivelyTrading=true"
        if query.exchange:
            url += f"&exchange={query.exchange.upper()}"

        url += f"&limit=10000&apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfSearchQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPEtfSearchData]:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame

        etfs = DataFrame(data)

        if query.query:
            etfs = etfs[
                etfs["companyName"].str.contains(query.query, case=False)
                | etfs["exchangeShortName"].str.contains(query.query, case=False)
                | etfs["exchange"].str.contains(query.query, case=False)
                | etfs["symbol"].str.contains(query.query, case=False)
            ]

        etfs = etfs.replace(
            {
                nan: None,
                "": None,
                0: None,
            }
        )
        return [FMPEtfSearchData.model_validate(d) for d in etfs.to_dict("records")]
