"""FMP SEC Filings fetcher."""

import datetime
import warnings
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.filings import (
    FilingsData,
    FilingsQueryParams,
)
from pydantic import field_validator


class FMPFilingsQueryParams(FilingsQueryParams):
    """FMP SEC Filings Params."""


class FMPFilingsData(FilingsData):
    """FMP SEC Filings Data."""

    __alias_dict__ = {"symbol": "ticker"}

    @field_validator("date", mode="before")
    def validate_date(cls, v: Any) -> Any:  # pylint: disable=no-self-argument
        """Validate the date."""
        return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()


class FMPFilingsFetcher(
    Fetcher[
        FMPFilingsQueryParams,
        List[FMPFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPFilingsQueryParams:
        """Transform the query."""
        return FMPFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        response: List[Dict] = []
        for page in range(1, query.pages + 1):
            url = create_url(
                version=3,
                endpoint=f"rss_feed?&page={page}",
                api_key=api_key,
            )
            data: List[Dict] = get_data_many(url, sub_dict="rss_feed", **kwargs)

            response.extend(data)

        return response

    @staticmethod
    def transform_data(
        query: FMPFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPFilingsData]:
        """Return the transformed data."""
        if query.today is True:
            now: str = datetime.datetime.now().strftime("%Y-%m-%d")
            iso_today: int = datetime.datetime.today().isoweekday()
            if iso_today < 6 and data:
                data = [x for x in data if x["date"] == now]
                query.limit = 1000
            else:
                warnings.warn(
                    "No filings today, displaying the most recent submissions instead."
                )

        # remove duplicates
        data = [dict(t) for t in {tuple(d.items()) for d in data}]

        return [FMPFilingsData(**x) for x in data[: query.limit]]
