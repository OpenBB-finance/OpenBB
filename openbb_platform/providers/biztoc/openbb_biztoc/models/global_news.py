"""Biztoc Globl News Fetcher."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_biztoc.utils.helpers import get_news
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import (
    GlobalNewsData,
    GlobalNewsQueryParams,
)
from pandas import to_datetime
from pydantic import Field, field_validator


class BiztocGlobalNewsQueryParams(GlobalNewsQueryParams):
    """Biztoc Global News QueryParams."""

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


class BiztocGlobalNewsData(GlobalNewsData):
    """Biztoc Global News Data."""

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
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        return to_datetime(v).strftime("%Y-%m-%d %H:%M:%S")


class BiztocGlobalNewsFetcher(
    Fetcher[
        BiztocGlobalNewsQueryParams,
        List[BiztocGlobalNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Biztoc endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BiztocGlobalNewsQueryParams:
        """Transform the query."""
        return BiztocGlobalNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BiztocGlobalNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Biztoc endpoint."""
        api_key = credentials.get("biztoc_api_key") if credentials else ""

        data = get_news(
            api_key=api_key, filter=query.filter, source=query.source, tag=query.tag, term=query.term  # type: ignore
        )
        if query.filter == "hot":
            _data = []
            for i in range(0, len(data)):
                _posts = data[i]["posts"]
                _data.extend(_posts)
            data = _data

        times = {"2 Hours Ago": 2, "4 Hours Ago": 4}
        # Drop 'body_preview' because it is always nan, empty string, or empty string with space.
        for i in range(0, len(data)):
            if "body_preview" in data[i]:
                data[i].pop("body_preview")
            # Some items when filter is 'hot' don't have a proper timestamp, only a label.
            if "created" in data[i] and data[i]["created"] in times:
                data[i]["created"] = datetime.now() - timedelta(
                    hours=times[data[i]["created"]]
                )

        return data

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[BiztocGlobalNewsData]:
        """Transform the data to the standard format."""
        return [BiztocGlobalNewsData.model_validate(d) for d in data]
