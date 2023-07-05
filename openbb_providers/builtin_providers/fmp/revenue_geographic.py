"""FMP Revenue Geographic Fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.data.revenue_geographic import (
    RevenueGeographicData,
    RevenueGeographicQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from pydantic import validator

from builtin_providers.fmp.helpers import create_url, get_data

# This part is only provided by FMP and not by the other providers for now.


class FMPRevenueGeographicQueryParams(RevenueGeographicQueryParams):
    """FMP Revenue Geographic QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Revenue-Geographic-Segmentation

    Parameter
    ---------
    symbol : Optional[str]
        The symbol of the company if no CIK is provided.
    period : Literal["annual", "quarterly"]
        The period of the income statement. Default is "annual".
    structure : Literal["hierarchical", "flat"]
        The structure of the revenue geographic. Default is "flat".
    """


class FMPRevenueGeographicData(RevenueGeographicData):
    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPRevenueGeographicFetcher(
    Fetcher[  # type: ignore
        RevenueGeographicQueryParams,
        RevenueGeographicData,
        FMPRevenueGeographicQueryParams,
        FMPRevenueGeographicData,
    ]
):
    @staticmethod
    def transform_query(
        query: RevenueGeographicQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPRevenueGeographicQueryParams:
        return FMPRevenueGeographicQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPRevenueGeographicQueryParams, api_key: str
    ) -> List[FMPRevenueGeographicData]:
        query.period = "quarter" if query.period == "quarterly" else "annual"  # type: ignore
        url = create_url(4, "revenue-geographic-segmentation", api_key, query)
        data = get_data(url)
        if isinstance(data, dict):
            raise ValueError("Expected list of dicts, got dict")

        data = [
            {**v, "date": k} for d in data for k, v in d.items() if isinstance(v, dict)
        ]

        data = [
            {
                "date": d.get("date"),
                "americas": d.get("Americas Segment")
                or d.get("North America Segment")
                or d.get("Americas")
                or d.get("North America"),
                "europe": d.get("Europe Segment") or d.get("Europe"),
                "greater_china": d.get("Greater China Segment")
                or d.get("Greater China"),
                "japan": d.get("Japan Segment") or d.get("Japan") or d.get("J P"),
                "rest_of_asia_pacific": d.get("Rest of Asia Pacific Segment")
                or d.get("Rest of Asia Pacific")
                or d.get("Asia-Pacific"),
            }
            for d in data
        ]

        return [FMPRevenueGeographicData(**d) for d in data]

    @staticmethod
    def transform_data(
        data: List[FMPRevenueGeographicData],
    ) -> List[RevenueGeographicData]:
        # Parse data to RevenueGeographicData
        return data_transformer(data, RevenueGeographicData)
