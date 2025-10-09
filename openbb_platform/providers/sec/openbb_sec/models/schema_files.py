"""SEC Schema Files List Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot_search import CotSearchQueryParams
from pydantic import Field


class SecSchemaFilesQueryParams(CotSearchQueryParams):
    """SEC Schema Files List Query.

    Source: https://sec.gov/
    """

    url: str | None = Field(
        description="Enter an optional URL path to fetch the next level.", default=None
    )
    use_cache: bool | None = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecSchemaFilesData(Data):
    """SEC Schema Files List Data."""

    files: list[str] = Field(description="Dictionary of URLs to SEC Schema Files")


class SecSchemaFilesFetcher(Fetcher[SecSchemaFilesQueryParams, SecSchemaFilesData]):
    """SEC Schema Files Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecSchemaFilesQueryParams:
        """Transform the query."""
        return SecSchemaFilesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecSchemaFilesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.helpers import get_schema_filelist

        if query.url and ".xsd" in query.url or query.url and ".xml" in query.url:
            raise OpenBBError("Invalid URL. This endpoint does not parse the files.")
        results = get_schema_filelist(query.query, query.url)

        return {"files": results}

    @staticmethod
    def transform_data(
        query: SecSchemaFilesQueryParams, data: dict, **kwargs: Any
    ) -> SecSchemaFilesData:
        """Transform the data to the standard format."""
        return SecSchemaFilesData.model_validate(data)
