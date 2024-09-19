"""Biztoc World News Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.world_news import (
    WorldNewsData,
    WorldNewsQueryParams,
)
from pydantic import Field, field_validator


class BiztocWorldNewsQueryParams(WorldNewsQueryParams):
    """Biztoc World News Query."""

    term: Optional[str] = Field(
        description="Search term to filter articles by. This overrides all other filters.",
        default=None,
    )
    source: Optional[str] = Field(
        description="Filter by a specific publisher. Only valid when filter is set to source.",
        default=None,
    )


class BiztocWorldNewsData(WorldNewsData):
    """Biztoc World News Data."""

    __alias_dict__ = {
        "date": "published",
        "text": "body",
        "images": "img",
    }

    images: Optional[List[Dict[str, str]]] = Field(
        description="Images for the article.", default=None
    )
    tags: Optional[List[str]] = Field(description="Tags for the article.", default=None)
    score: Optional[float] = Field(
        description="Search relevance score for the article.", default=None
    )

    @field_validator("date", "updated", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return formatted datetime."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        return to_datetime(v).strftime("%Y-%m-%d %H:%M:%S")

    @field_validator("title")
    @classmethod
    def title_validate(cls, v):
        """Strip empty title text."""
        return v.strip() if v else None


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
        if params.get("start_date") or params.get("end_date"):
            warn("start_date and end_date are not supported for this endpoint.")
        return BiztocWorldNewsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BiztocWorldNewsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from the Biztoc endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import make_request

        api_key = credentials.get("biztoc_api_key") if credentials else ""
        headers = {
            "X-RapidAPI-Key": f"{api_key}",
            "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        }
        base_url = "https://biztoc.p.rapidapi.com/"
        url = ""
        response: List = []
        if query.term:
            query.term = query.term.replace(" ", "%20")
            url = base_url + f"search?q={query.term}"
            response = make_request(url, headers=headers).json()
        if query.source is not None:
            sources_response = make_request(
                "https://biztoc.p.rapidapi.com/sources",
                headers=headers,
            ).json()
            sources = [source["id"] for source in sources_response]
            if query.source.lower() not in sources:
                raise OpenBBError(
                    f"{query.source} not a valid source. Valid sources: {sources}"
                )
            url = base_url + f"news/source/{query.source.lower()}"
            response = make_request(url, headers=headers).json()
        else:
            url1 = base_url + "news/latest"
            url2 = base_url + "news/topics"
            response = make_request(url1, headers=headers).json()
            response2 = make_request(url2, headers=headers).json()
            if response2:
                for topic in response2:
                    stories = topic.get("stories", [])
                    if stories:
                        response.extend(
                            {
                                "text" if k == "body_preview" else k: v
                                for k, v in story.items()
                            }
                            for story in stories
                        )

        return response

    @staticmethod
    def transform_data(
        query: BiztocWorldNewsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[BiztocWorldNewsData]:
        """Transform the data to the standard format."""
        results: List[BiztocWorldNewsData] = []
        for item in data:
            item.pop("id", None)
            item.pop("uid", None)
            item.pop("body_preview", None)
            item.pop("site", None)
            item.pop("domain", None)
            images = item.pop("img", [])
            if images:
                item["images"] = images if isinstance(images, list) else [images]
            results.append(BiztocWorldNewsData.model_validate(item))
        return results
