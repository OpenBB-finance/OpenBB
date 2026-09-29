"""Deribit Announcements Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class DeribitAnnouncementsQueryParams(QueryParams):
    """Deribit Announcements Query.

    Source: https://docs.deribit.com/api-reference/account-management/public-get_announcements
    """

    start_date: Any | None = Field(
        default=None,
        description="Return announcements published on or after this date.",
    )
    limit: int = Field(
        default=50, description="The number of announcements to return.", ge=1
    )


class DeribitAnnouncementsData(Data):
    """Deribit Announcements Data."""

    __alias_dict__ = {"date": "publication_timestamp"}

    date: datetime = Field(
        description="When the announcement was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    title: str = Field(
        description="The title of the announcement.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    body: str = Field(
        description="The body of the announcement, as HTML.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded", "cellDataType": "text"}
        },
    )
    important: bool | None = Field(
        default=None,
        description="Whether the exchange flagged the announcement.",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "excluded",
                "cellDataType": "boolean",
            }
        },
    )
    confirmation: bool | None = Field(
        default=None,
        description="Whether the announcement needs acknowledging.",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "excluded",
                "cellDataType": "boolean",
                "hide": True,
            }
        },
    )
    id: int | None = Field(
        default=None,
        description="The identifier of the announcement.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)


class DeribitAnnouncementsFetcher(
    Fetcher[DeribitAnnouncementsQueryParams, list[DeribitAnnouncementsData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitAnnouncementsQueryParams:
        """Transform the query."""
        return DeribitAnnouncementsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitAnnouncementsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange published no announcements over the span.
        """
        from openbb_deribit.utils.client import request
        from openbb_deribit.utils.helpers import to_timestamp

        data = await request(
            "get_announcements",
            {
                "start_timestamp": (
                    to_timestamp(query.start_date) if query.start_date else None
                ),
                "count": query.limit,
            },
        )

        if not data:
            raise EmptyDataError("Deribit published no announcements over the span.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitAnnouncementsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitAnnouncementsData]:
        """Transform the data to the model."""
        return [
            DeribitAnnouncementsData.model_validate(record)
            for record in sorted(
                data, key=lambda d: d.get("publication_timestamp") or 0, reverse=True
            )
        ]
