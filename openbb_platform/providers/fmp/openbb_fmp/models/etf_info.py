"""FMP ETF Info Model."""

# pylint: disable=unused-argument

from typing import Any, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field, field_validator


class FMPEtfInfoQueryParams(EtfInfoQueryParams):
    """FMP ETF Info Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FMPEtfInfoData(EtfInfoData):
    """FMP ETF Info Data."""

    __alias_dict__ = {
        "issuer": "etfCompany",
    }

    issuer: Optional[str] = Field(
        default=None,
        description="Company of the ETF.",
    )
    cusip: Optional[str] = Field(default=None, description="CUSIP of the ETF.")
    isin: Optional[str] = Field(default=None, description="ISIN of the ETF.")
    domicile: Optional[str] = Field(default=None, description="Domicile of the ETF.")
    asset_class: Optional[str] = Field(
        default=None, description="Asset class of the ETF."
    )
    aum: Optional[float] = Field(
        default=None,
        description="Assets under management.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    nav: Optional[float] = Field(
        default=None,
        description="Net asset value of the ETF.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    nav_currency: Optional[str] = Field(
        default=None, description="Currency of the ETF's net asset value."
    )
    expense_ratio: Optional[float] = Field(
        default=None,
        description="The expense ratio, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    holdings_count: Optional[int] = Field(
        default=None, description="Number of holdings."
    )
    avg_volume: Optional[float] = Field(
        default=None, description="Average daily trading volume."
    )
    website: Optional[str] = Field(default=None, description="Website of the issuer.")

    @field_validator("expense_ratio", mode="before", check_fields=False)
    @classmethod
    def validate_expense_ratio(cls, v):
        """Format expense ratio as percent."""
        return v / 100 if v else None


class FMPEtfInfoFetcher(
    Fetcher[
        FMPEtfInfoQueryParams,
        list[FMPEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEtfInfoQueryParams:
        """Transform the query."""
        return FMPEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfInfoQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_fmp.utils.helpers import response_callback
        from warnings import warn

        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: list = []

        async def get_one(symbol):
            """Get one symbol."""
            url = f"https://financialmodelingprep.com/api/v4/etf-info?symbol={symbol}&apikey={api_key}"
            response = await amake_request(url, response_callback=response_callback)
            if not response:
                warn(f"No results found for {symbol}.")
            results.extend(response)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        return results

    @staticmethod
    def transform_data(
        query: FMPEtfInfoQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPEtfInfoData]:
        """Return the transformed data."""
        # Pop the nested dictionaries from the data returned by other endpoints.
        transformed: list[FMPEtfInfoData] = []
        for d in data:
            if d.get("sectorsList"):
                d.pop("sectorsList")
            transformed.append(FMPEtfInfoData.model_validate(d))
        return transformed
