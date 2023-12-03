"""FMP Index Constituents Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_constituents import (
    IndexConstituentsData,
    IndexConstituentsQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many
from pydantic import field_validator


class FMPIndexConstituentsQueryParams(IndexConstituentsQueryParams):
    """FMP Index Constituents Query.

    Source: https://site.financialmodelingprep.com/developer/docs/list-of-dow-companies-api/
            https://site.financialmodelingprep.com/developer/docs/list-of-sp-500-companies-api/
            https://site.financialmodelingprep.com/developer/docs/list-of-nasdaq-companies-api/
    """


class FMPIndexConstituentsData(IndexConstituentsData):
    """FMP Index Constituents Data."""

    __alias_dict__ = {"headquarter": "headQuarter"}

    @field_validator("dateFirstAdded", mode="before", check_fields=False)
    @classmethod
    def date_first_added_validate(cls, v):  # pylint: disable=E0213
        """Return the date_first_added date as a datetime object for valid cases."""
        try:
            return datetime.strptime(v, "%Y-%m-%d") if v else None
        except Exception:
            # For returning string in case of mismatched dates
            return v

    @field_validator("founded", mode="before", check_fields=False)
    @classmethod
    def founded_validate(cls, v):  # pylint: disable=E0213
        """Return the founded date as a datetime object for valid cases."""
        try:
            return datetime.strptime(v, "%Y-%m-%d") if v else None
        except Exception:
            # For returning string in case of mismatched dates
            return v


class FMPIndexConstituentsFetcher(
    Fetcher[
        FMPIndexConstituentsQueryParams,
        List[FMPIndexConstituentsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIndexConstituentsQueryParams:
        """Transform the query params."""
        return FMPIndexConstituentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIndexConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/{query.index}_constituent/?apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPIndexConstituentsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPIndexConstituentsData]:
        """Return the raw data from the FMP endpoint."""
        return [FMPIndexConstituentsData.model_validate(d) for d in data]
