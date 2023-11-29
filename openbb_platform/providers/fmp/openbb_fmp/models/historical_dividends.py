"""FMP Historical Dividends Model."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, field_validator


class FMPHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """FMP Historical Dividends Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Dividends
    """


class FMPHistoricalDividendsData(HistoricalDividendsData):
    """FMP Historical Dividends Data."""

    label: str = Field(description="Label of the historical dividends.")
    adj_dividend: float = Field(
        description="Adjusted dividend of the historical dividends."
    )
    record_date: Optional[dateType] = Field(
        default=None,
        description="Record date of the historical dividends.",
    )
    payment_date: Optional[dateType] = Field(
        default=None,
        description="Payment date of the historical dividends.",
    )
    declaration_date: Optional[dateType] = Field(
        default=None,
        description="Declaration date of the historical dividends.",
    )

    @field_validator(
        "declaration_date",
        "record_date",
        "payment_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Validate dates."""
        if not isinstance(v, str):
            return v
        return dateType.fromisoformat(v) if v else None


class FMPHistoricalDividendsFetcher(
    Fetcher[
        FMPHistoricalDividendsQueryParams,
        List[FMPHistoricalDividendsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHistoricalDividendsQueryParams:
        """Transform the query params."""
        return FMPHistoricalDividendsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPHistoricalDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"historical-price-full/stock_dividend/{query.symbol}", api_key
        )
        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(
        query: FMPHistoricalDividendsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPHistoricalDividendsData]:
        """Return the transformed data."""
        return [FMPHistoricalDividendsData.model_validate(d) for d in data]
