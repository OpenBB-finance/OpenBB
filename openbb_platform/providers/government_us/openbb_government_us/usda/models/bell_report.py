"""FAS Bell Report Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class FasBellReportQueryParams(QueryParams):
    """FAS Bell Report Query Parameters.

    Source: https://apps.fas.usda.gov/esrqs/#/reports/bellreport
    """

    __json_schema_extra__ = {
        "urls": {
            "multiple_items_allowed": True,
        }
    }

    urls: str | list[str] | dict[str, list[str]] = Field(
        description="Report viewer URLs to download, as returned by the"
        + " bell_report_urls endpoint.",
        kw_only=True,
    )


class FasBellReportData(Data):
    """FAS Bell Report Data.

    Weekly export sales commitments by commodity and marketing year. The
    source embargoes each report until its release time, so only published
    weeks are offered.
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


class FasBellReportFetcher(Fetcher[FasBellReportQueryParams, list[FasBellReportData]]):
    """Fetch USDA FAS Bell Reports as PDFs."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FasBellReportQueryParams:
        """Transform the query params."""
        return FasBellReportQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FasBellReportQueryParams,
        credentials: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list:
        """Download each report from the FAS report viewer."""
        import base64

        from openbb_government_us.usda.utils.fas_bell_report import (
            afetch_report,
            report_file_name,
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
                filename = report_file_name(target)
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
                content = await afetch_report(target)
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
        query: FasBellReportQueryParams, data: list, **kwargs: Any
    ) -> list[FasBellReportData]:
        """Transform the data."""
        return [FasBellReportData(**item) for item in data]
