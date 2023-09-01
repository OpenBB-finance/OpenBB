import http.client
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.news_search import (
    NewsSearchData,
    NewsSearchQueryParams,
)
from pandas import to_datetime
from pydantic import Field, validator


class BiztocNewsSearchQueryParams(NewsSearchQueryParams):
    """Biztoc News Search QueryParams."""


class BiztocNewsSearchData(NewsSearchData):
    """Biztoc News Search Data."""

    class Config:
        fields = {"date": "created", "text": "body", "image": "img"}

    score: Optional[float] = Field(description="Article score.")
    domain: Optional[str] = Field(description="Base url to the article source.")
    tags: Optional[List[str]] = Field(description="Tags for the article.")

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        v = to_datetime(v).strftime("%Y-%m-%d %H:%M:%S")
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


class BiztocNewsSearchFetcher(
    Fetcher[
        BiztocNewsSearchQueryParams,
        List[BiztocNewsSearchData],
    ]
):
    """Transform the query, extract and transform the data from the Biztoc endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BiztocNewsSearchQueryParams:
        """Transform the query."""
        return BiztocNewsSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BiztocNewsSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        query.term = query.term.replace(" ", "%20")
        conn = http.client.HTTPSConnection("biztoc.p.rapidapi.com")
        api_key = credentials.get("biztoc_api_key") if credentials else ""
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "biztoc.p.rapidapi.com",
        }
        conn.request("GET", f"/search?q={query.term}", headers=headers)

        res = conn.getresponse()
        data = res.read()

        return json.loads(data.decode("utf-8"))

    @staticmethod
    def transform_data(data: dict) -> List[BiztocNewsSearchData]:
        """Transform the data to the standard format."""
        return [BiztocNewsSearchData.parse_obj(d) for d in data]
