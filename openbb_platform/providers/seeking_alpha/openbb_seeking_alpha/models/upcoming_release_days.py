"""Seeking Alpha Upcoming Release Days Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.upcoming_release_days import (
    UpcomingReleaseDaysData,
    UpcomingReleaseDaysQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class SAUpcomingReleaseDaysQueryParams(UpcomingReleaseDaysQueryParams):
    """Seeking Alpha Upcoming Release Days Query.

    Source: https://seekingalpha.com/api/v3/earnings_calendar/tickers
    """

    limit: int = Field(
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + "In this case, the number of lookahead days.",
        default=10,
    )


class SAUpcomingReleaseDaysData(UpcomingReleaseDaysData):
    """Seeking Alpha Upcoming Release Days Data."""

    __alias_dict__ = {"symbol": "slug", "release_time_type": "release_time"}

    sector_id: Optional[int] = Field(
        description="The sector ID of the asset.",
    )

    @field_validator("release_date", mode="before", check_fields=False)
    def validate_release_date(cls, v: Any) -> Any:  # pylint: disable=E0213
        """Validate the release date."""
        v = v.split("T")[0]
        return datetime.strptime(v, "%Y-%m-%d").date()


class SAUpcomingReleaseDaysFetcher(
    Fetcher[
        SAUpcomingReleaseDaysQueryParams,
        List[SAUpcomingReleaseDaysData],
    ]
):
    """Transform the query, extract and transform the data from the Seeking Alpha endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SAUpcomingReleaseDaysQueryParams:
        """Transform the query."""
        return SAUpcomingReleaseDaysQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SAUpcomingReleaseDaysQueryParams,  # pylint: disable=W0613
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Seeking Alpha endpoint."""
        url = (
            f"https://seekingalpha.com/api/v3/earnings_calendar/tickers?"
            f"filter%5Bselected_date%5D={str(datetime.now().date())}"  # cspell:disable-line
            f"&filter%5Bwith_rating%5D=false&filter%5Bcurrency%5D=USD"  # cspell:disable-line
        )
        response = requests.get(
            url=url,
            timeout=5,
        )
        if response.status_code != 200:
            raise ValueError(
                f"Seeking Alpha Upcoming Release Days Fetcher failed with status code "
                f"{response.status_code}"
            )

        if not response.json()["data"]:
            raise ValueError(
                "Seeking Alpha Upcoming Release Days Fetcher failed with empty response."
            )

        return response.json()

    @staticmethod
    def transform_data(
        query: SAUpcomingReleaseDaysQueryParams, data: Dict, **kwargs: Any
    ) -> List[SAUpcomingReleaseDaysData]:
        """Transform the data to the standard format."""
        transformed_data: List[Dict[str, Any]] = []
        data = data["data"]
        for row in data:
            transformed_data.append(
                {
                    "symbol": row["attributes"]["slug"],
                    "name": row["attributes"]["name"],
                    "exchange": row["attributes"]["exchange"],
                    "release_time_type": row["attributes"]["release_time"],
                    "release_date": row["attributes"]["release_date"],
                    "sector_id": row["attributes"]["sector_id"],
                }
            )

        return [
            SAUpcomingReleaseDaysData(**row) for row in transformed_data[: query.limit]
        ]
