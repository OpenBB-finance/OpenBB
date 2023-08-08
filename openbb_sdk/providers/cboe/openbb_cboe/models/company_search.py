"""CBOE Company Search fetcher."""

# IMPORT STANDARD
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.company_search import (
    CompanySearchData,
    CompanySearchQueryParams,
)
from pydantic import Field, validator

from openbb_cboe.utils.helpers import search_companies


class CboeCompanySearchQueryParams(CompanySearchQueryParams):
    """CBOE Company Search query.

    Source: https://www.cboe.com/
    """


class CboeCompanySearchData(CompanySearchData):
    """CBOE Company Search Data."""

    class Config:
        fields = {
            "name": "Company Name",
            "symbol": "Symbol",
        }

    dpmName: Optional[str] = Field(
        description="The name of the primary market maker.",
        alias="DPM Name",
    )
    postStation: Optional[str] = Field(
        description="The post and station location on the CBOE trading floor.",
        alias="Post/Station",
    )

    @validator("symbol", pre=True, check_fields=False)
    def name_validate(cls, v):  # pylint: disable=E0213
        return v.upper()


class CboeCompanySearchFetcher(
    Fetcher[
        CboeCompanySearchQueryParams,
        List[CboeCompanySearchData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeCompanySearchQueryParams:
        return CboeCompanySearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeCompanySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[CboeCompanySearchData]:
        data = search_companies(query.query, ticker=query.ticker)

        return [CboeCompanySearchData.parse_obj(d) for d in data.get("results", [])]

    @staticmethod
    def transform_data(data: List[CboeCompanySearchData]) -> List[CboeCompanySearchData]:
        return data
