"""FRED Commercial Paper Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cp import (
    CommercialPaperData,
    CommercialPaperParams,
)
from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import get_cp_series_id
from pydantic import field_validator


class FREDCommercialPaperParams(CommercialPaperParams):
    """FRED Commercial Paper Query."""


class FREDCommercialPaperData(CommercialPaperData):
    """FRED Commercial Paper Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDCommercialPaperFetcher(
    Fetcher[
        FREDCommercialPaperParams,
        List[FREDCommercialPaperData],
    ]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    data_type = FREDCommercialPaperData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDCommercialPaperParams:
        """Transform query."""
        return FREDCommercialPaperParams(**params)

    @staticmethod
    def extract_data(
        query: FREDCommercialPaperParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> list:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        series = get_cp_series_id(
            maturity=query.maturity,
            category=query.category,
            grade=query.grade,
        )

        data = []

        for s in series:
            id_ = s["FRED Series ID"]
            title = s["Title"]
            d = fred.get_series(
                series_id=id_,
                start_date=query.start_date,
                end_date=query.end_date,
                **kwargs,
            )
            for item in d:
                item["title"] = title
            data.extend(d)

        return data

    @staticmethod
    def transform_data(
        query: FREDCommercialPaperParams, data: list, **kwargs: Any
    ) -> List[FREDCommercialPaperData]:
        """Transform data."""
        return [FREDCommercialPaperData.model_validate(d) for d in data]
