"""FRED ICE BofA US Corporate Bond Indices Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.ice_bofa import (
    ICEBofAData,
    ICEBofAQueryParams,
)
from pydantic import Field, field_validator


class FREDICEBofAQueryParams(ICEBofAQueryParams):
    """FRED ICE BofA US Corporate Bond Indices Query."""

    category: Literal["all", "duration", "eur", "usd"] = Field(
        default="all", description="The type of category."
    )
    area: Literal["asia", "emea", "eu", "ex_g10", "latin_america", "us"] = Field(
        default="us", description="The type of area."
    )
    grade: Literal[
        "a",
        "aa",
        "aaa",
        "b",
        "bb",
        "bbb",
        "ccc",
        "crossover",
        "high_grade",
        "high_yield",
        "non_financial",
        "non_sovereign",
        "private_sector",
        "public_sector",
    ] = Field(default="non_sovereign", description="The type of grade.")
    options: bool = Field(
        default=False, description="Whether to include options in the results."
    )


class FREDICEBofAData(ICEBofAData):
    """FRED ICE BofA US Corporate Bond Indices Data."""

    __alias_dict__ = {"rate": "value", "title": "fred_series_title"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDICEBofAFetcher(
    Fetcher[
        FREDICEBofAQueryParams,
        List[FREDICEBofAData],
    ]
):
    """FRED ICE BofA Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDICEBofAQueryParams:
        """Transform query."""
        return FREDICEBofAQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDICEBofAQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        from openbb_fred.utils.fred_base import Fred
        from openbb_fred.utils.fred_helpers import get_ice_bofa_series_id

        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        series = get_ice_bofa_series_id(
            type_=query.index_type,
            category=query.category,
            area=query.area,
            grade=query.grade,
        )

        data: List = []

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
        query: FREDICEBofAQueryParams, data: List, **kwargs: Any
    ) -> List[FREDICEBofAData]:
        """Transform data."""
        return [FREDICEBofAData.model_validate(d) for d in data]
