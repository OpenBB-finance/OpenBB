"""FRED Selected Treasury Bill Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.tbffr import (
    SelectedTreasuryBillData,
    SelectedTreasuryBillQueryParams,
)
from openbb_fred.utils.fred_base import Fred
from pydantic import field_validator

TBFFR_PARAMETER_TO_FRED_ID = {
    "3m": "TB3SMFFM",
    "6m": "TB6SMFFM",
}


class FREDSelectedTreasuryBillQueryParams(SelectedTreasuryBillQueryParams):
    """FRED Selected Treasury Bill Query."""


class FREDSelectedTreasuryBillData(SelectedTreasuryBillData):
    """FRED Selected Treasury Bill Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDSelectedTreasuryBillFetcher(
    Fetcher[
        FREDSelectedTreasuryBillQueryParams,
        List[FREDSelectedTreasuryBillData],
    ]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    data_type = FREDSelectedTreasuryBillData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDSelectedTreasuryBillQueryParams:
        """Transform query."""
        return FREDSelectedTreasuryBillQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDSelectedTreasuryBillQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> list:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        data = fred.get_series(
            series_id=TBFFR_PARAMETER_TO_FRED_ID[query.maturity],
            start_date=query.start_date,
            end_date=query.end_date,
            **kwargs,
        )

        return data

    @staticmethod
    def transform_data(
        query: FREDSelectedTreasuryBillQueryParams, data: list, **kwargs: Any
    ) -> List[FREDSelectedTreasuryBillData]:
        """Transform data."""
        return [FREDSelectedTreasuryBillData.model_validate(d) for d in data]
