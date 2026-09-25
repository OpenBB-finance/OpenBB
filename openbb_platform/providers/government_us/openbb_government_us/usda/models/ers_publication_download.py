"""USDA ERS Publication Download Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class ErsPublicationDownloadQueryParams(QueryParams):
    """USDA ERS Publication Download Query Parameters.

    Source: https://www.ers.usda.gov/publications
    """

    __json_schema_extra__ = {
        "urls": {
            "multiple_items_allowed": True,
        }
    }

    urls: str | list[str] | dict[str, list[str]] = Field(
        description="Publication page URLs to download, as returned by the"
        + " ers_publications endpoint. Each page is resolved to its Full"
        + " Report PDF.",
        kw_only=True,
    )


class ErsPublicationDownloadData(Data):
    """USDA ERS Publication Download Data.

    The Full Report PDF of each requested publication page.
    """

    error_type: str | None = Field(
        default=None,
        description="Error type, if the report could not be downloaded.",
    )
    content: str = Field(
        description="Base64-encoded PDF document.",
    )
    filename: str | None = Field(
        default=None,
        description="The filename of the downloaded PDF.",
    )
    data_format: dict[str, str] | None = Field(
        default=None,
        description="Data format information, including data type and filename.",
    )


class ErsPublicationDownloadFetcher(
    Fetcher[
        ErsPublicationDownloadQueryParams,
        list[ErsPublicationDownloadData],
    ]
):
    """Fetch USDA ERS Publications as PDFs."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> ErsPublicationDownloadQueryParams:
        """Transform the query params."""
        return ErsPublicationDownloadQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ErsPublicationDownloadQueryParams,
        credentials: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list:
        """Download the Full Report PDF behind each publication page."""
        import base64

        from openbb_government_us.usda.utils.ers_publications import (
            afetch_publication,
            validate_publication_url,
        )

        urls = (
            query.urls.get("urls", [])
            if isinstance(query.urls, dict)
            else (query.urls if isinstance(query.urls, list) else query.urls.split(","))
        )
        results: list = []

        for url in urls:
            try:
                target = validate_publication_url(url)
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "error_type": "invalid_url",
                        "content": f"{exc.__class__.__name__}: {exc}",
                        "filename": None,
                    }
                )
                continue
            try:
                content, filename = await afetch_publication(target)
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "error_type": "download_error",
                        "content": f"{exc.__class__.__name__}: {exc}",
                        "filename": None,
                    }
                )
                continue
            results.append(
                {
                    "content": base64.b64encode(content).decode("utf-8"),
                    "filename": filename,
                    "data_format": {"data_type": "pdf", "filename": filename},
                }
            )

        return results

    @staticmethod
    def transform_data(
        query: ErsPublicationDownloadQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[ErsPublicationDownloadData]:
        """Transform the data."""
        return [ErsPublicationDownloadData(**item) for item in data]
