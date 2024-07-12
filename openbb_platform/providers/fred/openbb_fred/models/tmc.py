"""FRED Treasury Constant Maturity Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.tmc import (
    TreasuryConstantMaturityData,
    TreasuryConstantMaturityQueryParams,
)
from pydantic import field_validator

TMC_PARAMETER_TO_FRED_ID = {
    "3m": "T10Y3M",
    "2y": "T10Y2Y",
}


class FREDTreasuryConstantMaturityQueryParams(TreasuryConstantMaturityQueryParams):
    """FRED Treasury Constant Maturity Query."""


class FREDTreasuryConstantMaturityData(TreasuryConstantMaturityData):
    """FRED Treasury Constant Maturity Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDTreasuryConstantMaturityFetcher(
    Fetcher[
        FREDTreasuryConstantMaturityQueryParams,
        List[FREDTreasuryConstantMaturityData],
    ]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FREDTreasuryConstantMaturityQueryParams:
        """Transform query."""
        return FREDTreasuryConstantMaturityQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDTreasuryConstantMaturityQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        from openbb_fred.utils.fred_base import Fred

        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        data = fred.get_series(
            series_id=TMC_PARAMETER_TO_FRED_ID[query.maturity],  # type: ignore
            start_date=query.start_date,
            end_date=query.end_date,
            **kwargs,
        )

        return data

    @staticmethod
    def transform_data(
        query: FREDTreasuryConstantMaturityQueryParams, data: List, **kwargs: Any
    ) -> List[FREDTreasuryConstantMaturityData]:
        """Transform data."""
        return [FREDTreasuryConstantMaturityData.model_validate(d) for d in data]
