"""FMP ETF Holdings Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator


class FMPEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """FMP ETF Holdings Query.

    Source: https://site.financialmodelingprep.com/developer/docs#holdings
    """


class FMPEtfHoldingsData(EtfHoldingsData):
    """FMP ETF Holdings Data."""

    model_config = ConfigDict(extra="ignore")

    __alias_dict__ = {
        "shares": "sharesNumber",
        "value": "marketValue",
        "weight": "weightPercentage",
        "symbol": "asset",
        "updated": "updatedAt",
        "cusip": "securityCusip",
    }

    cusip: Optional[str] = Field(
        description="The CUSIP of the holding.", default=None, title="CUSIP"
    )
    isin: Optional[str] = Field(
        description="The ISIN of the holding.", default=None, title="ISIN"
    )
    weight: Optional[float] = Field(
        description="The weight of the holding, as a normalized percent.",
        default=None,
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    shares: Optional[Union[float, str]] = Field(
        description="The number of shares held.", default=None
    )
    value: Optional[float] = Field(
        description="The market value of the holding.",
        default=None,
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    updated: Optional[Union[dateType, datetime]] = Field(
        description="The date the data was updated.", default=None
    )

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        return float(v) / 100 if v else None

    @field_validator(
        "cusip", "isin", "name", "asset", "value", mode="before", check_fields=False
    )
    @classmethod
    def replace_empty(cls, v):
        """Replace empty strings and 0s with None."""
        if isinstance(v, str):
            return v if v not in ("", "0", "-") else None
        return v if v and v != 0 else None


class FMPEtfHoldingsFetcher(
    Fetcher[
        FMPEtfHoldingsQueryParams,
        list[FMPEtfHoldingsData],
    ]
):
    """FMP ETF Holdings Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEtfHoldingsQueryParams:
        """Transform the query."""
        return FMPEtfHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEtfHoldingsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = f"https://financialmodelingprep.com/stable/etf/holdings?symbol={query.symbol}&apikey={api_key}"
        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEtfHoldingsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FMPEtfHoldingsData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("No data was found for the given symbol.")
        return [FMPEtfHoldingsData.model_validate(item) for item in data]
