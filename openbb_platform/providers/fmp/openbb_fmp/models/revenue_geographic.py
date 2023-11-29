"""FMP Revenue Geographic Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.revenue_geographic import (
    RevenueGeographicData,
    RevenueGeographicQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data
from pydantic import field_validator


class FMPRevenueGeographicQueryParams(RevenueGeographicQueryParams):
    """FMP Revenue Geographic Query.

    Source: https://site.financialmodelingprep.com/developer/docs/revenue-geographic-by-segments-api/
    """


class FMPRevenueGeographicData(RevenueGeographicData):
    """FMP Revenue Geographic Data."""

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPRevenueGeographicFetcher(
    Fetcher[  # type: ignore
        FMPRevenueGeographicQueryParams,
        List[FMPRevenueGeographicData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPRevenueGeographicQueryParams:
        """Transform the query params."""
        return FMPRevenueGeographicQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPRevenueGeographicQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "revenue-geographic-segmentation", api_key, query)
        data = get_data(url, **kwargs)

        if isinstance(data, Dict):
            raise ValueError("Expected list of Dicts, got Dict")

        return data

    @staticmethod
    def transform_data(
        query: FMPRevenueGeographicQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPRevenueGeographicData]:
        """Return the transformed data."""
        return [
            FMPRevenueGeographicData(
                date=key,
                geographic_segment=v,
                americas=v.get("Americas Segment", v.get("North America", None)),
                europe=v.get("Europe Segment", v.get("Europe", None)),
                greater_china=v.get(
                    "Greater China Segment", v.get("Greater China", None)
                ),
                japan=v.get("Japan Segment", v.get("Japan", v.get("J P", None))),
                rest_of_asia_pacific=v.get(
                    "Rest of Asia Pacific Segment", v.get("Asia-Pacific", None)
                ),
            )
            for d in data
            for key, v in d.items()
            if isinstance(v, Dict)
        ]
