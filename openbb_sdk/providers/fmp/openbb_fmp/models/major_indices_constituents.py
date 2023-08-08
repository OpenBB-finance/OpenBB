"""FMP Major Indices end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.major_indices_constituents import (
    MajorIndicesConstituentsData,
    MajorIndicesConstituentsQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import get_data_many


class FMPMajorIndicesConstituentsQueryParams(MajorIndicesConstituentsQueryParams):
    """FMP Major Indices Constituents query.

    Source: https://site.financialmodelingprep.com/developer/docs/list-of-dow-companies-api/
            https://site.financialmodelingprep.com/developer/docs/list-of-sp-500-companies-api/
            https://site.financialmodelingprep.com/developer/docs/list-of-nasdaq-companies-api/
    """


class FMPMajorIndicesConstituentsData(MajorIndicesConstituentsData):
    """FMP Major Indices Constituents data."""

    class Config:
        fields = {
            "sub_sector": "subSector",
            "headquarter": "headQuarter",
            "date_first_added": "dateFirstAdded",
        }

    @validator("dateFirstAdded", pre=True, check_fields=False)
    def date_first_added_validate(cls, v):  # pylint: disable=E0213
        try:
            return datetime.strptime(v, "%Y-%m-%d") if v else None
        except Exception:
            # For returning string in case of mismatched dates
            return v

    @validator("founded", pre=True, check_fields=False)
    def founded_validate(cls, v):  # pylint: disable=E0213
        try:
            return datetime.strptime(v, "%Y-%m-%d") if v else None
        except Exception:
            # For returning string in case of mismatched dates
            return v


class FMPMajorIndicesConstituentsFetcher(
    Fetcher[
        FMPMajorIndicesConstituentsQueryParams,
        List[FMPMajorIndicesConstituentsData],
    ]
):
    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FMPMajorIndicesConstituentsQueryParams:
        return FMPMajorIndicesConstituentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPMajorIndicesConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPMajorIndicesConstituentsData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/{query.index}_constituent/?apikey={api_key}"

        return get_data_many(url, FMPMajorIndicesConstituentsData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPMajorIndicesConstituentsData],
    ) -> List[MajorIndicesConstituentsData]:
        return [MajorIndicesConstituentsData.parse_obj(d.dict()) for d in data]
