"""SEC Institutions Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot_search import CotSearchQueryParams
from openbb_sec.utils.helpers import get_all_ciks
from pydantic import Field


class SecInstitutionsSearchQueryParams(CotSearchQueryParams):
    """SEC Institutions Search Query.

    Source: https://sec.gov/
    """


class SecInstitutionsSearchData(Data):
    """SEC Institutions Search Data."""

    name: Optional[str] = Field(
        default=None, description="The name of the institution.", alias="Institution"
    )
    cik: Optional[Union[str, int]] = Field(
        default=None, description="Central Index Key (CIK)", alias="CIK Number"
    )


class SecInstitutionsSearchFetcher(
    Fetcher[
        SecInstitutionsSearchQueryParams,
        List[SecInstitutionsSearchData],
    ]
):
    """Transform the query, extract and transform the data from the SEC endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecInstitutionsSearchQueryParams:
        """Transform the query."""
        return SecInstitutionsSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInstitutionsSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the SEC endpoint."""
        institutions = await get_all_ciks(use_cache=query.use_cache)
        hp = institutions["Institution"].str.contains(query.query, case=False)
        return institutions[hp].astype(str).to_dict("records")

    @staticmethod
    def transform_data(
        query: SecInstitutionsSearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[SecInstitutionsSearchData]:
        """Transform the data to the standard format."""
        return [SecInstitutionsSearchData.model_validate(d) for d in data]
