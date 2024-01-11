"""Benzinga Analyst Ratings Model."""

import math
from copy import deepcopy
from typing import Any, Dict, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.analyst_ratings import (
    AnalystRatingsData,
    AnalystRatingsQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests, get_querystring
from pydantic import Field, PrivateAttr, model_validator


class BenzingaAnalystRatingsQueryParams(AnalystRatingsQueryParams):
    """Benzinga Analyst Ratings Query.

    Source: https://docs.benzinga.io/benzinga-apis/calendar/get-ratings
    """

    __alias_dict__ = {
        "limit": "pageSize",
    }

    fields: Optional[str] = Field(
        default=None,
        description="Comma-separated list of fields to include in the response."
        " See https://docs.benzinga.io/benzinga-apis/calendar/get-ratings to learn about the available fields.",
    )
    date: Optional[str] = Field(
        default=None,
        description="Date for calendar data, shorthand for date_from and date_to.",
        is_parameters=True,
    )
    date_from: Optional[str] = Field(
        default=None,
        description="Date to query from point in time.",
        is_parameters=True,
    )
    date_to: Optional[str] = Field(
        default=None, description="Date to query to point in time.", is_parameters=True
    )
    tickers: Optional[str] = Field(
        default=None,
        description="Comma-separated list of tickers to filter by.",
        is_parameters=True,
    )
    importance: Optional[int] = Field(
        default=None, description="Importance level to filter by.", is_parameters=True
    )
    updated: Optional[int] = Field(
        default=None,
        description="Records last updated Unix timestamp (UTC).",
        is_parameters=True,
    )
    action: Optional[
        Literal[
            "Downgrades",
            "Maintains",
            "Reinstates",
            "Reiterates",
            "Upgrades",
            "Assumes",
            "Initiates Coverage On",
            "Terminates Coverage On",
            "Removes",
            "Suspends",
            "Firm Dissolved",
        ]
    ] = Field(
        default=None,
        description="Filter by a specific action_company.",
        is_parameters=True,
    )
    analyst: Optional[str] = Field(
        default=None, description="Comma-separated list of analyst (person) IDs."
    )
    firm: Optional[str] = Field(
        default=None, description="Comma-separated list of analyst firm IDs."
    )
    _parameters: Dict[str, Any] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    @classmethod
    def assemble_parameters(
        cls, values: "BenzingaAnalystRatingsQueryParams"
    ) -> "BenzingaAnalystRatingsQueryParams":
        """Assemble the parameters private attribute."""
        model_fields = values.model_fields

        for field in deepcopy(values):
            key, value = field
            field_info = model_fields[key]
            if field_info.json_schema_extra and field_info.json_schema_extra.get(
                "is_parameters", False
            ):
                if value:
                    # add to parameters
                    # pylint: disable=protected-access
                    values._parameters[f"parameters[{key}]"] = value
                # remove from values
                delattr(values, key)

        return values


class BenzingaAnalystRatingsData(AnalystRatingsData):
    """Benzinga Analyst Ratings Data."""


class BenzingaAnalystRatingsFetcher(
    Fetcher[
        BenzingaAnalystRatingsQueryParams,
        BenzingaAnalystRatingsData,
    ]
):
    """Transform the query, extract and transform the data from the Benzinga endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BenzingaAnalystRatingsQueryParams:
        """Transform the query params."""
        return BenzingaAnalystRatingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: BenzingaAnalystRatingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Benzinga endpoint."""
        token = credentials.get("benzinga_api_key") if credentials else ""

        base_url = "https://api.benzinga.com/api/v2.1/calendar/ratings"
        full_query = {
            **query.model_dump(by_alias=True),
            **query._parameters,  # pylint: disable=protected-access
        }
        querystring = get_querystring(full_query, exclude=[])

        pages = math.ceil(query.limit / 100) if query.limit else 1

        urls = [
            f"{base_url}?{querystring}&page={page}&token={token}"
            for page in range(pages)
        ]

        data = await amake_requests(urls, **kwargs)

        return data[: query.limit]

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: BenzingaAnalystRatingsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> BenzingaAnalystRatingsData:
        """Return the transformed data."""
        return [
            BenzingaAnalystRatingsData.model_validate(d) for d in data[0]["ratings"]
        ]
