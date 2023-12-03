"""Biztoc World News Model."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_biztoc.utils.helpers import get_news
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.world_news import (
    WorldNewsData,
    WorldNewsQueryParams,
)
from pandas import to_datetime
from pydantic import Field, field_validator


class BiztocWorldNewsQueryParams(WorldNewsQueryParams):
    """Biztoc World News Query."""

    filter: Literal[
        "crypto", "hot", "latest", "main", "media", "source", "tag"
    ] = Field(default="latest", description="Filter by type of news.")
    source: str = Field(
        description="Filter by a specific publisher. Only valid when filter is set to source.",
        default="bloomberg",
    )
    tag: Optional[str] = Field(
        description="Tag, topic, to filter articles by. Only valid when filter is set to tag.",
        default=None,
    )
    term: Optional[str] = Field(
        description="Search term to filter articles by. This overrides all other filters.",
        default=None,
    )


class BiztocWorldNewsData(WorldNewsData):
    """Biztoc World News Data."""

    __alias_dict__ = {"date": "created", "text": "body", "site": "domain"}

    images: Optional[Dict[str, str]] = Field(
        description="Images for the article.", alias="images", default=None
    )
    favicon: Optional[str] = Field(
        description="Icon image for the source of the article.", default=None
    )
    tags: Optional[List[str]] = Field(description="Tags for the article.", default=None)
    id: Optional[str] = Field(description="Unique Article ID.", default=None)
    score: Optional[float] = Field(
        description="Search relevance score for the article.", default=None
    )

    @field_validator("date", "updated", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return formatted datetime."""
        return to_datetime(v).strftime("%Y-%m-%d %H:%M:%S")


class BiztocWorldNewsFetcher(
    Fetcher[
        BiztocWorldNewsQueryParams,
        List[BiztocWorldNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Biztoc endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BiztocWorldNewsQueryParams:
        """Transform the query."""
        return BiztocWorldNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BiztocWorldNewsQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Biztoc endpoint."""
        api_key = credentials.get("biztoc_api_key") if credentials else ""

        data = get_news(
            api_key=api_key, filter_=query.filter, source=query.source, tag=query.tag, term=query.term  # type: ignore
        )
        if query.filter == "hot":
            data = [post for sublist in data for post in sublist["posts"]]

        times = {"2 Hours Ago": 2, "4 Hours Ago": 4}
        # Drop 'body_preview' because it is always nan, empty string, or empty string with space.
        for _, item in enumerate(data):
            item.pop("body_preview", None)  # Removes 'body_preview' if it exists
            # Adjust 'created' time if necessary
            if item.get("created") in times:
                item["created"] = datetime.now() - timedelta(
                    hours=times[item["created"]]
                )

        return data

    @staticmethod
    def transform_data(
        query: BiztocWorldNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[BiztocWorldNewsData]:
        """Transform the data to the standard format."""
        return [BiztocWorldNewsData.model_validate(d) for d in data]
