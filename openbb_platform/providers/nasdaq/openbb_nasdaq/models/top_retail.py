"""Nasdaq Top Retail Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.top_retail import (
    TopRetailData,
    TopRetailQueryParams,
)
from pydantic import field_validator


class NasdaqTopRetailQueryParams(TopRetailQueryParams):
    """Nasdaq Top Retail Query.

    Source: https://data.nasdaq.com/databases/RTAT/data
    """


class NasdaqTopRetailData(TopRetailData):
    """Nasdaq Top Retail Data."""

    @field_validator("date", mode="before", check_fields=False)
    def validate_date(cls, v: Any) -> Any:  # pylint: disable=E0213
        """Validate the date."""
        return datetime.strptime(v, "%Y-%m-%d").date()


class NasdaqTopRetailFetcher(
    Fetcher[NasdaqTopRetailQueryParams, List[NasdaqTopRetailData]]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqTopRetailQueryParams:
        """Transform the params to the provider-specific query."""
        return NasdaqTopRetailQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqTopRetailQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Get data from Nasdaq."""
        api_key = credentials.get("nasdaq_api_key") if credentials else None
        response = requests.get(
            f"https://data.nasdaq.com/api/v3/datatables/NDAQ/RTAT10/?api_key={api_key}",
            timeout=5,
        ).json()
        return response["datatable"]["data"][: query.limit]

    @staticmethod
    def transform_data(
        query: TopRetailQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqTopRetailData]:
        """Transform the data."""
        transformed_data: List[Dict[str, Any]] = []
        for row in data:
            transformed_data.append(
                {
                    "date": row[0],
                    "symbol": row[1],
                    "activity": row[2],
                    "sentiment": row[3],
                }
            )

        return [NasdaqTopRetailData(**row) for row in transformed_data]
