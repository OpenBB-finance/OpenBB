"""Government US Weather Bulletin Download Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.weather_bulletin_download import (
    WeatherBulletinDownloadData,
    WeatherBulletinDownloadQueryParams,
)
from pydantic import Field


class GovernmentUsWeatherBulletinDownloadQueryParams(
    WeatherBulletinDownloadQueryParams
):
    """US Government Weather Bulletin Download Query Params."""

    __json_schema_extra__ = {
        "urls": {
            "multiple_items_allowed": True,
        }
    }


class GovernmentUsWeatherBulletinDownloadData(WeatherBulletinDownloadData):
    """US Government Weather Bulletin Download Data."""

    data_format: dict[str, str] = Field(description="Data format information.")


class GovernmentUsWeatherBulletinDownloadFetcher(
    Fetcher[
        GovernmentUsWeatherBulletinDownloadQueryParams,
        list[GovernmentUsWeatherBulletinDownloadData],
    ]
):
    """US Government Weather Bulletin Download Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> GovernmentUsWeatherBulletinDownloadQueryParams:
        """Transform params into the query params model."""
        return GovernmentUsWeatherBulletinDownloadQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: GovernmentUsWeatherBulletinDownloadQueryParams,
        credentials: dict[str, Any] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the raw PDF content."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_async_requests_session

        results: dict = {}
        urls = query.urls

        # Verify that all URLs are going to be valid USDA URLs
        for url in urls:
            if not url.lower().startswith("https://esmis.nal.usda.gov/"):
                raise OpenBBError(
                    ValueError(
                        f"Invalid URL '{url}'. Only URLs from 'esmis.nal.usda.gov' are supported."
                    )
                )
            if not url.lower().endswith(".pdf"):
                raise OpenBBError(
                    ValueError(
                        f"Invalid URL '{url}'. Only PDF documents are supported."
                    )
                )

        try:
            async with await get_async_requests_session() as session:
                session._max_field_size = 32768  # pylint: disable=protected-access

                for url in urls:
                    async with await session.get(url) as response:
                        if response.status != 200:
                            raise OpenBBError(
                                ValueError(
                                    f"Failed to download document from {url}. Status code: {response.status}"
                                )
                            )
                        content_bytes = await response.read()
                        results[url] = content_bytes

            return results
        except Exception as e:
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: GovernmentUsWeatherBulletinDownloadQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[GovernmentUsWeatherBulletinDownloadData]:
        """Transform the raw PDF content into the data model."""
        # pylint: disable=import-outside-toplevel
        import base64

        output: list[GovernmentUsWeatherBulletinDownloadData] = []

        for url, content in data.items():
            content_b64 = base64.b64encode(content).decode("utf-8")
            data_format = {
                "data_type": "pdf",
                "filename": url.split("/")[-1],
            }
            bulletin_data = GovernmentUsWeatherBulletinDownloadData(
                content=content_b64,
                data_format=data_format,
            )
            output.append(bulletin_data)

        return output
