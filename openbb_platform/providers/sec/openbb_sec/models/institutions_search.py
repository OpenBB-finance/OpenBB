"""SEC Institutions Search Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot_search import CotSearchQueryParams
from pydantic import Field


class SecInstitutionsSearchQueryParams(CotSearchQueryParams):
    """SEC Institutions Search Query.

    Source: https://sec.gov/
    """

    use_cache: bool | None = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecInstitutionsSearchData(Data):
    """SEC Institutions Search Data."""

    __alias_dict__ = {
        "name": "Institution",
        "cik": "CIK Number",
    }

    name: str | None = Field(
        default=None,
        description="The name of the institution.",
    )
    cik: str | int | None = Field(
        default=None,
        description="Central Index Key (CIK)",
    )


class SecInstitutionsSearchFetcher(
    Fetcher[
        SecInstitutionsSearchQueryParams,
        list[SecInstitutionsSearchData],
    ]
):
    """SEC Institutions Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecInstitutionsSearchQueryParams:
        """Transform the query."""
        return SecInstitutionsSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInstitutionsSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.helpers import get_all_ciks

        institutions = await get_all_ciks(use_cache=query.use_cache)
        hp = institutions["Institution"].str.contains(query.query, case=False)
        return institutions[hp].astype(str).to_dict("records")

    @staticmethod
    def transform_data(
        query: SecInstitutionsSearchQueryParams, data: list[dict], **kwargs: Any
    ) -> list[SecInstitutionsSearchData]:
        """Transform the data to the standard format."""
        return [SecInstitutionsSearchData.model_validate(d) for d in data]
