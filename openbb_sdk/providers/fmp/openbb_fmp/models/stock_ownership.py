"""FMP Stock Ownership fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many, most_recent_quarter
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_ownership import (
    StockOwnershipData,
    StockOwnershipQueryParams,
)
from pydantic import validator


class FMPStockOwnershipQueryParams(StockOwnershipQueryParams):
    """FMP Stock Ownership query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Ownership-by-Holders
    """

    @validator("date", pre=True, check_fields=True)
    def time_validate(cls, v: str):  # pylint: disable=E021
        """Validate the date."""
        if v is None:
            v = dateType.today()
        if isinstance(v, str):
            base = datetime.strptime(v, "%Y-%m-%d").date()
            return most_recent_quarter(base)
        return most_recent_quarter(v)


class FMPStockOwnershipData(StockOwnershipData):
    """FMP Stock Ownership Data."""


class FMPStockOwnershipFetcher(
    Fetcher[
        FMPStockOwnershipQueryParams,
        List[FMPStockOwnershipData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockOwnershipQueryParams:
        """Transform the query params."""
        return FMPStockOwnershipQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockOwnershipQueryParams,
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

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPStockOwnershipData]:
        """Return the transformed data."""
        own = [FMPStockOwnershipData.parse_obj(d) for d in data]
        own.sort(key=lambda x: x.filing_date, reverse=True)
        return own
