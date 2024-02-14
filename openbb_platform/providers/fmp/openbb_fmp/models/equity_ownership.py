"""FMP Equity Ownership Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_ownership import (
    EquityOwnershipData,
    EquityOwnershipQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many, most_recent_quarter
from pydantic import field_validator


class FMPEquityOwnershipQueryParams(EquityOwnershipQueryParams):
    """FMP Equity Ownership Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Ownership-by-Holders
    """

    @field_validator("date", mode="before", check_fields=True)
    @classmethod
    def time_validate(cls, v: str):
        """Validate the date."""
        if v is None:
            v = dateType.today()
        if isinstance(v, str):
            base = datetime.strptime(v, "%Y-%m-%d").date()
            return most_recent_quarter(base)
        return most_recent_quarter(v)


class FMPEquityOwnershipData(EquityOwnershipData):
    """FMP Equity Ownership Data."""


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
        own = [FMPEquityOwnershipData.model_validate(d) for d in data]
        own.sort(key=lambda x: x.filing_date, reverse=True)
        return own
