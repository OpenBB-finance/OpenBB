"""Biztoc Globl News Fetcher."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_biztoc.utils.helpers import get_all_tags, get_pages, get_sources
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import (
    GlobalNewsData,
    GlobalNewsQueryParams,
)
from openbb_provider.utils.helpers import make_request
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
        description="Images for the article.", alias="img", default=None
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
    def get_news(
        api_key: str,
        filter: Literal[
            "crypto", "hot", "latest", "main", "media", "source", "tag"
        ] = "latest",
        source: str = "bloomberg",
        tag: str = "",
        term: str = "",
    ) -> List[Dict]:
        """Calls the BizToc API and returns the data."""

        term = term.replace(" ", "%20") if term else ""
        _tags = get_all_tags(api_key)
        pages = get_pages(api_key)
        tags = []
        tag = tag.lower() if tag else ""
        for page in pages:
            tags.extend(_tags[page][:])

        _sources = get_sources(api_key)
        sources = sorted([i["id"] for i in _sources])

        headers = {
            "X-RapidAPI-Key": f"{api_key}",
            "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
        }

        filter_dict = {
            "hot": "news/hot",
            "latest": "news/latest",
            "crypto": "news/latest/crypto",
            "main": "news/latest/main",
            "media": "news/latest/media",
            "source": f"news/source/{source.lower()}",
            "tag": f"tag/{tag}",
        }
        if filter == "source" and source.lower() not in sources:
            raise ValueError(f"{source} not a valid source. Valid sources: {sources}")

        if filter == "tag" and tag.lower().replace(" ", "") not in tags:
            raise ValueError(f"{tag} not a valid tag. Valid tags: {tags}")

        url = (
            f"https://biztoc.p.rapidapi.com/search?q={term}"
            if term
            else f"https://biztoc.p.rapidapi.com/{filter_dict[filter]}"
        )
        r = make_request(url, headers=headers)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP error - > {r.text}")

        return r.json()

    @staticmethod
    def extract_data(
        query: BiztocGlobalNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Biztoc endpoint."""

        api_key = credentials.get("biztoc_api_key") if credentials else ""

        data = BiztocGlobalNewsFetcher.get_news(
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
    def transform_data(data: List[Dict]) -> List[BiztocGlobalNewsData]:
        """Transform the data to the standard format."""
        return [BiztocGlobalNewsData.model_validate(d) for d in data]
