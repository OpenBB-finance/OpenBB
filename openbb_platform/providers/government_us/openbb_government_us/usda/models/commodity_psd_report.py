"""US Government Production Supply & Distribution Circular Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_government_us.utils.serializers import OmitNoneMixin


class UsdaCommodityPsdReportQueryParams(QueryParams):
    """US Government Commodity PSD Report Query Params.

    Source: https://apps.fas.usda.gov/psdonline/app/index.html#/app/downloads
    """

    __json_schema_extra__ = {
        "urls": {
            "multiple_items_allowed": True,
        }
    }

    urls: str | list[str] | dict[str, list[str]] = Field(
        description="Circular URLs to download, as returned by the"
        + " psd_report_urls endpoint.",
        kw_only=True,
    )


class UsdaCommodityPsdReportData(OmitNoneMixin, Data):
    """US Government Commodity PSD Report Data.

    Monthly world markets and trade circulars by commodity. The source carries
    the most recent circular forward into every later month folder, so only
    the month that actually published a circular is offered.
    """

    error_type: str | None = Field(
        default=None,
        description="Error type, if the circular could not be downloaded.",
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


class UsdaCommodityPsdReportFetcher(
    Fetcher[
        UsdaCommodityPsdReportQueryParams,
        list[UsdaCommodityPsdReportData],
    ]
):
    """US Government Commodity PSD Report Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> UsdaCommodityPsdReportQueryParams:
        """Transform the query params."""
        return UsdaCommodityPsdReportQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: UsdaCommodityPsdReportQueryParams,
        credentials: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list:
        """Download each circular from the PSD Online host."""
        import base64

        from openbb_government_us.usda.utils.psd_circulars import (
            afetch_circular,
            circular_file_name,
        )

        urls = (
            query.urls.get("urls", [])
            if isinstance(query.urls, dict)
            else (query.urls if isinstance(query.urls, list) else query.urls.split(","))
        )
        results: list = []

        for url in urls:
            target = url.strip()
            try:
                filename = circular_file_name(target)
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
                content = await afetch_circular(target)
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "error_type": "download_error",
                        "content": f"{exc.__class__.__name__}: {exc}",
                        "filename": filename,
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
        query: UsdaCommodityPsdReportQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[UsdaCommodityPsdReportData]:
        """Transform the data."""
        return [UsdaCommodityPsdReportData(**item) for item in data]
