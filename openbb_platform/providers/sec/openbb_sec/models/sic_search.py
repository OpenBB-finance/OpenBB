"""SEC Standard Industrial Classification Code (SIC) Model."""

from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot_search import CotSearchQueryParams
from openbb_sec.utils.helpers import SEC_HEADERS, sec_session_companies
from pydantic import Field


class SecSicSearchQueryParams(CotSearchQueryParams):
    """SEC Standard Industrial Classification Code (SIC) Query.

    Source: https://sec.gov/
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use the cache or not. The full list will be cached for seven days if True.",
    )


class SecSicSearchData(Data):
    """SEC Standard Industrial Classification Code (SIC) Data."""

    sic: int = Field(description="Sector Industrial Code (SIC)", alias="SIC Code")
    industry: str = Field(description="Industry title.", alias="Industry Title")
    office: str = Field(
        description="Reporting office within the Corporate Finance Office",
        alias="Office",
    )


class SecSicSearchFetcher(
    Fetcher[
        SecSicSearchQueryParams,
        List[SecSicSearchData],
    ]
):
    """Transform the query, extract and transform the data from the SEC endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any], **kwargs: Any
    ) -> SecSicSearchQueryParams:
        """Transform the query."""
        return SecSicSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecSicSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data from the SEC website table."""
        data = pd.DataFrame()
        results: List[Dict] = []
        url = (
            "https://www.sec.gov/corpfin/"
            "division-of-corporation-finance-standard-industrial-classification-sic-code-list"
        )
        r = (
            sec_session_companies.get(url, timeout=5, headers=SEC_HEADERS)
            if query.use_cache is True
            else requests.get(url, timeout=5, headers=SEC_HEADERS)
        )

        if r.status_code == 200:
            data = pd.read_html(r.content.decode())[0].astype(str)
            if len(data) == 0:
                return results
            if query:
                data = data[
                    data["SIC Code"].str.contains(query.query, case=False)
                    | data["Office"].str.contains(query.query, case=False)
                    | data["Industry Title"].str.contains(query.query, case=False)
                ]
            data["SIC Code"] = data["SIC Code"].astype(int)
        results = data.to_dict("records")

        return results

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[SecSicSearchData]:
        """Transform the data."""
        return [SecSicSearchData.model_validate(d) for d in data]
