"""FRED Selected Treasury Constant Maturity Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.ffrmc import (
    SelectedTreasuryConstantMaturityData,
    SelectedTreasuryConstantMaturityQueryParams,
)
from openbb_fred.utils.fred_base import Fred
from pydantic import field_validator

FFRMC_PARAMETER_TO_FRED_ID = {
    "10y": "T10YFF",
    "5y": "T5YFF",
    "1y": "T1YFF",
    "6m": "T6MFF",
    "3m": "T3MFF",
}


class FREDSelectedTreasuryConstantMaturityQueryParams(
    SelectedTreasuryConstantMaturityQueryParams
):
    """FRED Selected Treasury Constant Maturity Query."""


class FREDSelectedTreasuryConstantMaturityData(SelectedTreasuryConstantMaturityData):
    """FRED Selected Treasury Constant Maturity Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDSelectedTreasuryConstantMaturityFetcher(
    Fetcher[
        FREDSelectedTreasuryConstantMaturityQueryParams,
        List[FREDSelectedTreasuryConstantMaturityData],
    ]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    data_type = FREDSelectedTreasuryConstantMaturityData

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FREDSelectedTreasuryConstantMaturityQueryParams:
        """Transform query."""
        return FREDSelectedTreasuryConstantMaturityQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDSelectedTreasuryConstantMaturityQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> list:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        data = fred.get_series(
            series_id=FFRMC_PARAMETER_TO_FRED_ID[query.maturity],
            start_date=query.start_date,
            end_date=query.end_date,
            **kwargs,
        )

        return data

    @staticmethod
    def transform_data(
        query: FREDSelectedTreasuryConstantMaturityQueryParams,
        data: list,
        **kwargs: Any
    ) -> List[FREDSelectedTreasuryConstantMaturityData]:
        """Transform data."""
        return [
            FREDSelectedTreasuryConstantMaturityData.model_validate(d) for d in data
        ]
