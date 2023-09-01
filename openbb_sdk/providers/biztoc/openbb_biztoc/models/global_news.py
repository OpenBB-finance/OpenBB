"""Biztoc Globl News Fetcher."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.global_news import (
    GlobalNewsData,
    GlobalNewsQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pandas import to_datetime
from pydantic import Field, validator

from openbb_biztoc.utils.helpers import get_all_tags, get_pages, get_sources


class BiztocGlobalNewsQueryParams(GlobalNewsQueryParams):
    """Biztoc Global News QueryParams."""

    filter: Literal[
        "crypto", "hot", "latest", "main", "media", "source", "tag"
    ] = Field(default="latest", description="Filter by type of news.")
    source: str = Field(
        description="Filter by a specific publisher.", default="bloomberg"
    )
    tag: str = Field(description="Tag, topic, to filter articles by.", default="")


class BiztocGlobalNewsData(GlobalNewsData):
    """Biztoc Global News Data."""

    class Config:
        fields = {"date": "created", "text": "body", "image": "img", "site": "domain"}

    favicon: Optional[str] = Field(
        description="Icon image for the source of the article."
    )
    domain: Optional[str] = Field(description="Domain base url for the article source.")

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        v = to_datetime(v).strftime("%Y-%m-%d %H:%M:%S")
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class BiztocGlobalNewsFetcher(
    Fetcher[
        BiztocGlobalNewsQueryParams,
        List[BiztocGlobalNewsData],
    ]
):
    """Transform the query, extract and transform the data from the Biztoc endpoints."""

    @staticmethod
    def get_news(
        api_key: str,
        filter: Literal[
            "crypto", "hot", "latest", "main", "media", "source", "tag"
        ] = "latest",
        source: str = "bloomberg",
        tag: str = "",
    ) -> List[Dict]:
        _tags = get_all_tags()
        pages = get_pages()
        tags = []
        for page in pages:
            tags.extend(_tags[page][:])

        _sources = get_sources()
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
            "tag": f"tag/{tag.lower()}",
        }
        if filter == "source" and source.lower() not in sources:
            raise ValueError(f"{source} not a valid source. Valid sources: {sources}")

        if filter == "tag" and tag.lower() not in tags:
            raise ValueError(f"{tag} not a valid tag. Valid tags: {tags}")

        r = make_request(
            f"https://biztoc.p.rapidapi.com/{filter_dict[filter]}", headers=headers
        )

        return r.json()

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BiztocGlobalNewsQueryParams:
        """Transform the query."""
        return BiztocGlobalNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BiztocGlobalNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        api_key = credentials.get("biztoc_api_key") if credentials else ""

        return BiztocGlobalNewsFetcher.get_news(
            api_key=api_key, filter=query.filter, source=query.source, tag=query.tag
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[BiztocGlobalNewsData]:
        """Transform the data to the standard format."""
        return [BiztocGlobalNewsData.parse_obj(d) for d in data]
