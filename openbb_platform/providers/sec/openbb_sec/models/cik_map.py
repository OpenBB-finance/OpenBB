"""SEC CIK Mapping Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cik_map import CikMapData, CikMapQueryParams
from pydantic import Field


class SecCikMapQueryParams(CikMapQueryParams):
    """SEC CIK Mapping Query.

    Source: https://sec.gov/
    """

    use_cache: bool | None = Field(
        default=True,
        description="Whether or not to use cache for the request, default is True.",
    )


class SecCikMapData(CikMapData):
    """SEC CIK Mapping Data."""


class SecCikMapFetcher(
    Fetcher[
        SecCikMapQueryParams,
        SecCikMapData,
    ]
):
    """SEC CIK Map Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecCikMapQueryParams:
        """Transform the query."""
        return SecCikMapQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecCikMapQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.helpers import symbol_map

        results = {"cik": await symbol_map(query.symbol, query.use_cache)}
        if not results:
            return {"Error": "Symbol not found."}
        return results

    @staticmethod
    def transform_data(
        query: SecCikMapQueryParams, data: dict, **kwargs: Any
    ) -> SecCikMapData:
        """Transform the data to the standard format."""
        return SecCikMapData.model_validate(data)
