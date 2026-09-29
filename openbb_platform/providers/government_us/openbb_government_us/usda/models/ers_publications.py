"""USDA ERS Publications Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator

from openbb_government_us.usda.utils.ers_publications import (
    SERIES_CODES,
    SERIES_GROUPS,
    resolve_series,
)
from openbb_government_us.utils.serializers import OmitNoneMixin

DEFAULT_SERIES = "outlook-reports"


class ErsPublicationsQueryParams(QueryParams):
    """USDA ERS Publications Query Parameters.

    Source: https://www.ers.usda.gov/publications
    """

    __json_schema_extra__ = {
        "series": {
            "multiple_items_allowed": True,
            "choices": sorted(SERIES_GROUPS) + sorted(SERIES_CODES),
        },
    }

    series: str = Field(
        default=DEFAULT_SERIES,
        validate_default=True,
        description="Series to retrieve, as a comma-separated list of group"
        + " names or series codes. Groups expand to their member series."
        + " Valid groups are:\n    "
        + ", ".join(sorted(SERIES_GROUPS))
        + "\nValid series codes are:\n    "
        + ", ".join(f"{code} ({name})" for code, name in sorted(SERIES_CODES.items()))
        + "\n",
    )
    start_date: dateType | None = Field(
        default=None,
        description="Earliest release date to return."
        + " If None, returns from the first published report.",
    )
    end_date: dateType | None = Field(
        default=None,
        description="Latest release date to return."
        + " If None, returns up to the most recent report.",
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of reports to return, newest first."
        + " If None, returns every report in the selected series.",
    )

    @field_validator("series", mode="before", check_fields=False)
    @classmethod
    def _validate_series(cls, v):
        """Validate series."""
        return ",".join(resolve_series(v or DEFAULT_SERIES))


class ErsPublicationsData(OmitNoneMixin, Data):
    """USDA ERS Publications Data.

    One record per published report, carrying the publication page URL that
    the report viewer downloads.
    """

    id: str = Field(
        description="Publication ID, unique within the ERS publication catalog.",
    )
    title: str = Field(
        description="Title of the report, as published.",
    )
    release_date: dateType = Field(
        description="Date the report was released.",
    )
    series_code: str | None = Field(
        default=None,
        description="Code of the series the report belongs to, e.g. 'LDPM'.",
    )
    series_name: str | None = Field(
        default=None,
        description="Name of the series the report belongs to.",
    )
    report_number: str | None = Field(
        default=None,
        description="Report number within the series, e.g. 'LDP-M-385'.",
    )
    url: str = Field(
        description="URL of the publication page."
        + " This is the value the report viewer downloads.",
    )
    authors: str | None = Field(
        default=None,
        description="Authors of the report, as a comma-separated list.",
    )
    short_description: str | None = Field(
        default=None,
        description="Plain-text summary of the report, when the source"
        + " publishes one.",
    )
    topics: str | None = Field(
        default=None,
        description="Topics the report is filed under, as a comma-separated list.",
    )


class ErsPublicationsFetcher(
    Fetcher[
        ErsPublicationsQueryParams,
        list[ErsPublicationsData],
    ]
):
    """Fetch USDA ERS Publications."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ErsPublicationsQueryParams:
        """Transform the query params."""
        return ErsPublicationsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ErsPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the listing rows of the selected series."""
        from openbb_government_us.usda.utils.ers_publications import fetch_publications

        return await fetch_publications(
            query.series,
            start_date=query.start_date,
            end_date=query.end_date,
        )

    @staticmethod
    def transform_data(
        query: ErsPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ErsPublicationsData]:
        """Transform the data."""
        rows = data[: query.limit] if query.limit else data
        return [
            ErsPublicationsData.model_validate(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "release_date": row["release_date"],
                    "series_code": row["series_code"],
                    "series_name": row["series_name"],
                    "report_number": row["report_number"],
                    "url": row["url"],
                    "authors": ", ".join(
                        author["name"] for author in row["authors"] if author["name"]
                    )
                    or None,
                    "short_description": row["short_description"],
                    "topics": ", ".join(topic for topic in row["topics"] if topic)
                    or None,
                }
            )
            for row in rows
        ]
