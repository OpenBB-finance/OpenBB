"""Commercial Paper Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import get_cp_series_id
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cp import (
    CommercialPaperData,
    CommercialPaperParams,
)
from pydantic import field_validator


class FREDCommercialPaperParams(CommercialPaperParams):
    """CommercialPaperParams Query."""


class FREDCommercialPaperData(CommercialPaperData):
    """CommercialPaperParams Data."""

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
    """CommercialPaperParams Fetcher."""

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
