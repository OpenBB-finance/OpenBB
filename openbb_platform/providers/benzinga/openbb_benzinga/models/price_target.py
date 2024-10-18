"""Benzinga Price Target Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
    time,
    timezone,
)
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator

COVERAGE_DICT = {
    "downgrades": "Downgrades",
    "maintains": "Maintains",
    "reinstates": "Reinstates",
    "reiterates": "Reiterates",
    "upgrades": "Upgrades",
    "assumes": "Assumes",
    "initiates": "Initiates Coverage On",
    "terminates": "Terminates Coverage On",
    "removes": "Removes",
    "suspends": "Suspends",
    "firm_dissolved": "Firm Dissolved",
}


class BenzingaPriceTargetQueryParams(PriceTargetQueryParams):
    """Benzinga Price Target Query.

    Source: https://docs.benzinga.io/benzinga-apis/calendar/get-ratings
    """

    __alias_dict__ = {
        "limit": "pagesize",
        "symbol": "parameters[tickers]",
        "date": "parameters[date]",
        "start_date": "parameters[date_from]",
        "end_date": "parameters[date_to]",
        "updated": "parameters[updated]",
        "importance": "parameters[importance]",
        "action": "parameters[action]",
        "analyst_ids": "parameters[analyst_id]",
        "firm_ids": "parameters[firm_id]",
    }
    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "analyst_ids": {"multiple_items_allowed": True},
        "firm_ids": {"multiple_items_allowed": True},
        "fields": {"multiple_items_allowed": True},
        "action": {
            "multiple_items_allowed": False,
            "choices": [
                "downgrades",
                "maintains",
                "reinstates",
                "reiterates",
                "upgrades",
                "assumes",
                "initiates",
                "terminates",
                "removes",
                "suspends",
                "firm_dissolved",
            ],
        },
    }

    page: Optional[int] = Field(
        default=0,
        description="Page offset. For optimization, performance and technical reasons,"
        + " page offsets are limited from 0 - 100000. Limit the query results by other parameters such as date."
        + " Used in conjunction with the limit and date parameters.",
    )
    date: Optional[dateType] = Field(
        default=None,
        description="Date for calendar data, shorthand for date_from and date_to.",
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    updated: Optional[Union[dateType, int]] = Field(
        default=None,
        description="Records last Updated Unix timestamp (UTC)."
        + " This will force the sort order to be Greater Than or Equal to the timestamp indicated."
        + " The date can be a date string or a Unix timestamp."
        + " The date string must be in the format of YYYY-MM-DD.",
    )
    importance: Optional[int] = Field(
        default=None,
        description="Importance level to filter by."
        + " Uses Greater Than or Equal To the importance indicated",
    )
    action: Optional[
        Literal[
            "downgrades",
            "maintains",
            "reinstates",
            "reiterates",
            "upgrades",
            "assumes",
            "initiates",
            "terminates",
            "removes",
            "suspends",
            "firm_dissolved",
        ]
    ] = Field(
        default=None,
        description="Filter by a specific action_company.",
    )
    analyst_ids: Optional[Union[List[str], str]] = Field(
        default=None,
        description="Comma-separated list of analyst (person) IDs."
        + " Omitting will bring back all available analysts.",
    )
    firm_ids: Optional[Union[List[str], str]] = Field(
        default=None,
        description="Comma-separated list of firm IDs.",
    )
    fields: Optional[Union[List[str], str]] = Field(
        default=None,
        description="Comma-separated list of fields to include in the response."
        " See https://docs.benzinga.io/benzinga-apis/calendar/get-ratings to learn about the available fields.",
    )

    @field_validator("action", mode="after", check_fields=False)
    @classmethod
    def convert_action(cls, v):
        """Convert to the action string."""
        return COVERAGE_DICT[v] if v else None

    @field_validator("updated", mode="after", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Convert the the dates to a standard format."""
        if isinstance(v, datetime):
            v = v.replace(tzinfo=timezone.utc)
            return int(v.timestamp())
        if isinstance(v, dateType):
            v = datetime.combine(v, time(), tzinfo=timezone.utc)
            return int(v.timestamp())
        return None

    @field_validator(
        "fields", "firm_ids", "analyst_ids", mode="before", check_fields=False
    )
    @classmethod
    def convert_list(cls, v: Union[str, List[str]]):
        """Convert a List[str] to a string list."""
        if isinstance(v, str):
            return v
        return ",".join(v) if v else None


class BenzingaPriceTargetData(PriceTargetData):
    """Benzinga Price Target Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "published_date": "date",
        "adj_price_target": "adjusted_pt_current",
        "price_target": "pt_current",
        "price_target_previous": "pt_prior",
        "previous_adj_price_target": "adjusted_pt_prior",
        "published_time": "time",
        "analyst_firm": "analyst",
        "company_name": "name",
        "rating_previous": "rating_prior",
        "url_analyst": "url",
        "action": "action_company",
        "action_change": "action_pt",
        "last_updated": "updated",
    }

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
        description="Description of the change in rating from firm's last rating."
        "Note that all of these terms are precisely defined.",
    )
    action_change: Optional[
        Literal["Announces", "Maintains", "Lowers", "Raises", "Removes", "Adjusts"]
    ] = Field(
        default=None,
        description="Description of the change in price target from firm's last price target.",
    )
    importance: Optional[Literal[0, 1, 2, 3, 4, 5]] = Field(
        default=None,
        description="Subjective Basis of How Important Event is to Market. 5 = High",
    )
    notes: Optional[str] = Field(default=None, description="Notes of the price target.")
    analyst_id: Optional[str] = Field(default=None, description="Id of the analyst.")
    url_news: Optional[str] = Field(
        default=None,
        description="URL for analyst ratings news articles for this ticker on Benzinga.com.",
    )
    url_analyst: Optional[str] = Field(
        default=None,
        description="URL for analyst ratings page for this ticker on Benzinga.com.",
    )
    id: Optional[str] = Field(default=None, description="Unique ID of this entry.")
    last_updated: Optional[datetime] = Field(
        default=None,
        description="Last updated timestamp, UTC.",
    )

    @field_validator("published_date", mode="before", check_fields=False)
    @classmethod
    def parse_date(cls, v: str):
        """Parse the publisihed_date."""
        return datetime.strptime(v, "%Y-%m-%d").date() if v else None

    @field_validator("last_updated", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v: float) -> Optional[dateType]:
        """Convert the Unix timestamp to a datetime object."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import safe_fromtimestamp

        if v:
            dt = safe_fromtimestamp(v, tz=timezone.utc)
            return dt.date() if dt.time() == dt.min.time() else dt
        return None

    @model_validator(mode="before")
    @classmethod
    def replace_empty_strings(cls, values):
        """Check for empty strings and replace with None."""
        return {k: None if v == "" else v for k, v in values.items()}


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
    ) -> List[Dict]:
        """Return the raw data from the Benzinga endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_benzinga.utils.helpers import response_callback
        from openbb_core.provider.utils.helpers import amake_request, get_querystring

        token = credentials.get("benzinga_api_key") if credentials else ""

        base_url = "https://api.benzinga.com/api/v2.1/calendar/ratings"
        querystring = get_querystring(query.model_dump(by_alias=True), [])

        url = f"{base_url}?{querystring}&token={token}"
        data = await amake_request(url, response_callback=response_callback, **kwargs)

        if isinstance(data, dict) and "ratings" not in data:
            raise OpenBBError(
                f"Unexpected data format. Expected 'ratings' key, got: {list(data.keys())}"
            )
        if not isinstance(data, dict):
            raise OpenBBError(
                f"Unexpected data format. Expected dict, got: {type(data)}"
            )
        if isinstance(data, dict) and not data.get("ratings"):
            raise EmptyDataError("No ratings data returned.")

        return data["ratings"]

    @staticmethod
    def transform_data(
        query: BenzingaPriceTargetQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[BenzingaPriceTargetData]:
        """Return the transformed data."""
        results: List[BenzingaPriceTargetData] = []
        # Remove duplicated field with a URL
        for item in data:
            item.pop("url_calendar", None)
            results.append(BenzingaPriceTargetData.model_validate(item))
        return results
