"""Benzinga Price Target Model."""

import math
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from openbb_core.provider.utils.helpers import amake_requests, get_querystring
from pydantic import Field, PrivateAttr, field_validator, model_validator


class BenzingaPriceTargetQueryParams(PriceTargetQueryParams):
    """Benzinga Price Target Query.

    Source: https://docs.benzinga.io/benzinga-apis/calendar/get-ratings
    """

    __alias_dict__ = {
        "limit": "pageSize",
        "symbol": "parameters[tickers]",
    }
    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}

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
        cls, values: "BenzingaPriceTargetQueryParams"
    ) -> "BenzingaPriceTargetQueryParams":
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


class BenzingaPriceTargetData(PriceTargetData):
    """Benzinga Price Target Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "published_date": "date",
        "news_url": "url_news",
        "adj_price_target": "adjusted_pt_current",
        "price_target": "pt_current",
    }

    action_company: Literal[
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
        "",
    ] = Field(
        default="",
        description="Description of the change in rating from firm's last rating."
        "Note that all of these terms are precisely defined.",
    )
    action_pt: Literal[
        "Announces", "Maintains", "Lowers", "Raises", "Removes", "Adjusts", ""
    ] = Field(
        default="",
        description="Description of the change in price target from firm's last price target.",
    )
    adjusted_pt_prior: Optional[str] = Field(
        default=None,
        description="Analyst's prior price target, adjusted to account for stock splits and stock dividends."
        " If none are applicable, the pt_prior value is used.",
    )
    analyst_id: Optional[str] = Field(default=None, description="Id of the analyst.")
    currency: Optional[str] = Field(
        default=None, description="Currency the data is denominated in."
    )
    exchange: Optional[str] = Field(
        default=None, description="Exchange of the price target."
    )
    id: Optional[str] = Field(default=None, description="Unique ID of this entry.")
    importance: Optional[Literal[0, 1, 2, 3, 4, 5]] = Field(
        default=None,
        description="Subjective Basis of How Important Event is to Market. 5 = High",
    )
    notes: Optional[str] = Field(default=None, description="Notes of the price target.")
    pt_prior: Optional[str] = Field(
        default=None, description="Analyst's prior price target."
    )
    rating_current: Optional[str] = Field(
        default=None, description="The analyst's rating for the company."
    )
    rating_prior: Optional[str] = Field(
        default=None, description="Prior analyst rating for the company."
    )
    ratings_accuracy: Optional[str] = Field(
        default=None, description="Ratings accuracy of the price target."
    )
    time: Optional[str] = Field(
        default=None, description="Last updated timestamp, UTC."
    )
    updated: Optional[int] = Field(
        default=None, description="Last updated timestamp, UTC."
    )
    url: str = Field(
        default=None,
        description="URL for analyst ratings page for this ticker on Benzinga.com.",
    )
    url_calendar: Optional[str] = Field(
        default=None,
        description="URL for analyst ratings page for this ticker on Benzinga.com.",
    )
    name: Optional[str] = Field(
        default=None, description="Name of company that is subject of rating."
    )

    @field_validator("published_date", mode="before", check_fields=False)
    @classmethod
    def parse_date(cls, v: str) -> datetime:
        """Parse the date field."""
        if v:
            v = datetime.strptime(v, "%Y-%m-%d")

        return v

    @field_validator("adj_price_target", mode="before", check_fields=False)
    @classmethod
    def parse_adj_price_target(cls, v: str) -> float:
        """Parse the adj_price_target field."""
        return float(v) if v else 0.0

    @field_validator("price_target", mode="before", check_fields=False)
    @classmethod
    def parse_price_target(cls, v: str) -> float:
        """Parse the price_target field."""
        return float(v) if v else 0.0


class BenzingaPriceTargetFetcher(
    Fetcher[
        BenzingaPriceTargetQueryParams,
        List[BenzingaPriceTargetData],
    ]
):
    """Transform the query, extract and transform the data from the Benzinga endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BenzingaPriceTargetQueryParams:
        """Transform the query params."""
        return BenzingaPriceTargetQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: BenzingaPriceTargetQueryParams,
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
        query: BenzingaPriceTargetQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[BenzingaPriceTargetData]:
        """Return the transformed data."""
        return [BenzingaPriceTargetData.model_validate(d) for d in data[0]["ratings"]]
