"""SEC Litigation RSS Feed Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import xmltodict
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_sec.utils.definitions import SEC_HEADERS
from pydantic import Field


class SecRssLitigationQueryParams(QueryParams):
    """SEC Litigation RSS Feed Query.

    Source: https://sec.gov/
    """


class SecRssLitigationData(Data):
    """SEC Litigation RSS Feed Data."""

    published: datetime = Field(description="The date of publication.", alias="date")
    title: str = Field(description="The title of the release.")
    summary: str = Field(description="Short summary of the release.")
    id: str = Field(description="The identifier associated with the release.")
    link: str = Field(description="URL to the release.")


class SecRssLitigationFetcher(
    Fetcher[SecRssLitigationQueryParams, List[SecRssLitigationData]]
):
    """Transform the query, extract and transform the data from the SEC endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecRssLitigationQueryParams:
        """Transform the query."""
        return SecRssLitigationQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecRssLitigationQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the SEC endpoint."""
        results = []
        url = "https://www.sec.gov/rss/litigation/litreleases.xml"
        r = requests.get(url, headers=SEC_HEADERS, timeout=5)

        if r.status_code == 200:
            data = xmltodict.parse(r.content)
            cols = ["title", "link", "summary", "date", "id"]
            feed = pd.DataFrame.from_records(data["rss"]["channel"]["item"])[
                ["title", "link", "description", "pubDate", "dc:creator"]
            ]
            feed.columns = cols
            feed["date"] = pd.to_datetime(feed["date"])
            feed = feed.set_index("date")
            # Remove special characters
            for column in ["title", "summary"]:
                feed[column] = (
                    feed[column]
                    .replace(r"[^\w\s]|_", "", regex=True)
                    .replace(r"\n", "", regex=True)
                )

            results = feed.reset_index().to_dict(orient="records")

        return results

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[SecRssLitigationData]:
        """Transform the data to the standard format."""
        return [SecRssLitigationData.model_validate(d) for d in data]
