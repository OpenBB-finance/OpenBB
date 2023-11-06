"""Moody Corporate Bond Index Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.moody import (
    MoodyCorporateBondIndexData,
    MoodyCorporateBondIndexParams,
)
from pydantic import Field, field_validator

MOODY_TO_OPTIONS = {
    "aaa": {
        "index": {
            "id": "DAAA",
            "name": "Moody's Seasoned Aaa Corporate Bond Yield",
        },
        "treasury": {
            "id": "AAA10Y",
            "name": "Moody's Seasoned Aaa Corporate Bond Yield Relative to Yield "
            "on 10-Year Treasury Constant Maturity",
        },
        "fed_funds": {
            "id": "AAAFF",
            "name": "Moody's Seasoned Aaa Corporate Bond Minus Federal Funds Rate",
        },
    },
    "baa": {
        "index": {
            "id": "DBAA",
            "name": "Moody's Seasoned Baa Corporate Bond Yield",
        },
        "treasury": {
            "id": "BAA10Y",
            "name": "Moody's Seasoned Baa Corporate Bond Yield Relative "
            "to Yield on 10-Year Treasury Constant Maturity",
        },
        "fed_funds": {
            "id": "BAAFF",
            "name": "Moody's Seasoned Baa Corporate Bond Minus Federal Funds Rate",
        },
    },
}


class FREDMoodyCorporateBondIndexParams(MoodyCorporateBondIndexParams):
    """MoodyCorporateBondIndexParams Query."""

    spread: Optional[Literal["treasury", "fed_funds"]] = Field(
        default=None, description="The type of spread."
    )


class FREDMoodyCorporateBondIndexData(MoodyCorporateBondIndexData):
    """MoodyCorporateBondIndexParams Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDMoodyCorporateBondIndexFetcher(
    Fetcher[
        FREDMoodyCorporateBondIndexParams,
        List[FREDMoodyCorporateBondIndexData],
    ]
):
    """MoodyCorporateBondIndexParams Fetcher."""

    data_type = FREDMoodyCorporateBondIndexData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDMoodyCorporateBondIndexParams:
        """Transform query."""
        return FREDMoodyCorporateBondIndexParams(**params)

    @staticmethod
    def extract_data(
        query: FREDMoodyCorporateBondIndexParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> list:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        opt_key = query.spread if query.spread else "index"
        id_ = MOODY_TO_OPTIONS[query.index_type][opt_key]["id"]

        data = fred.get_series(
            series_id=id_,
            start_date=query.start_date,
            end_date=query.end_date,
            **kwargs,
        )

        return data

    @staticmethod
    def transform_data(
        query: FREDMoodyCorporateBondIndexParams, data: list, **kwargs: Any
    ) -> List[FREDMoodyCorporateBondIndexData]:
        """Transform data."""
        return [FREDMoodyCorporateBondIndexData.model_validate(d) for d in data]
