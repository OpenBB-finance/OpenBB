"""FMP Equity Ownership Model."""

# pylint: disable=unused-argument
from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_ownership import (
    EquityOwnershipData,
    EquityOwnershipQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many, most_recent_quarter
from pydantic import Field, field_validator


class FMPEquityOwnershipQueryParams(EquityOwnershipQueryParams):
    """FMP Equity Ownership Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Ownership-by-Holders
    """

    date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("date", "")
    )
    page: Optional[int] = Field(
        default=0, description="Page number of the data to fetch."
    )


class FMPEquityOwnershipData(EquityOwnershipData):
    """FMP Equity Ownership Data."""

    __alias_dict__ = {
        "change_in_weight_percent": "changeInWeightPercentage",
        "change_in_market_value_percent": "changeInMarketValuePercentage",
        "change_in_shares_percent": "changeInSharesNumberPercentage",
        "change_in_ownership_percent": "changeInOwnershipPercentage",
        "performance_percent": "performancePercentage",
    }

    @field_validator(
        "change_in_weight_percent",
        "change_in_market_value_percent",
        "change_in_shares_percent",
        "change_in_ownership_percent",
        "performance_percent",
        "weight",
        "last_weight",
        "change_in_weight",
        "change_in_weight_percent",
        "ownership",
        "last_ownership",
        "change_in_ownership",
        "change_in_ownership_percent",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        return float(v) / 100 if v else None


class FMPEquityOwnershipFetcher(
    Fetcher[
        FMPEquityOwnershipQueryParams,
        List[FMPEquityOwnershipData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEquityOwnershipQueryParams:
        """Transform the query params."""
        params["date"] = (
            most_recent_quarter().strftime("%Y-%m-%d")
            if params.get("date") is None
            else most_recent_quarter(params.get("date")).strftime("%Y-%m-%d")
        )
        return FMPEquityOwnershipQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityOwnershipQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = create_url(
            4,
            "institutional-ownership/institutional-holders/symbol-ownership-percent",
            api_key,
            query,
        )
        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityOwnershipQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEquityOwnershipData]:
        """Return the transformed data."""
        return [FMPEquityOwnershipData.model_validate(d) for d in data]
