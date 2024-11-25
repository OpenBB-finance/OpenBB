"""Intrinio Unusual Options Model."""

# pylint: disable = unused-argument

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Literal, Optional, Union

from dateutil.parser import parse
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_unusual import (
    OptionsUnusualData,
    OptionsUnusualQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_request,
    get_querystring,
)
from pydantic import Field, field_validator, model_validator
from pytz import timezone


class IntrinioOptionsUnusualQueryParams(OptionsUnusualQueryParams):
    """Intrinio Unusual Options Query.

    source: https://docs.intrinio.com/documentation/web_api/get_unusual_activity_v2
    """

    __alias_dict__ = {
        "min_value": "minimum_total_value",
        "max_value": "maximum_total_value",
        "trade_type": "activity_type",
    }

    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " If no symbol is supplied, requests are only allowed for a single date."
        + " Use the start_date for the target date."
        + " Intrinio appears to have data beginning Feb/2022,"
        + " but is unclear when it actually began.",
        default=None,
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " If a symbol is not supplied, do not include an end date.",
        default=None,
    )
    trade_type: Optional[Literal["block", "sweep", "large"]] = Field(
        description="The type of unusual activity to query for.",
        default=None,
    )
    sentiment: Optional[Literal["bullish", "bearish", "neutral"]] = Field(
        description="The sentiment type to query for.",
        default=None,
    )
    min_value: Optional[Union[int, float]] = Field(
        description="The inclusive minimum total value for the unusual activity.",
        default=None,
    )
    max_value: Optional[Union[int, float]] = Field(
        description="The inclusive maximum total value for the unusual activity.",
        default=None,
    )
    limit: int = Field(
        description=QUERY_DESCRIPTIONS.get("limit", "")
        + " A typical day for all symbols will yield 50-80K records."
        + " The API will paginate at 1000 records."
        + " The high default limit (100K) is to be able to reliably capture the most days."
        + " The high absolute limit (1.25M) is to allow for outlier days."
        + " Queries at the absolute limit will take a long time, and might be unreliable."
        + " Apply filters to improve performance.",
        default=100000,
        lt=1250000,
    )
    source: Literal["delayed", "realtime"] = Field(
        default="delayed",
        description="The source of the data." + " Either realtime or delayed.",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_params(cls, params):
        """Validate the query parameters."""
        if params.get("start_date") is None:
            # If the symbol is provided, there will be considerably less results.
            # Broad market data needs to be confined to a single date.
            params["start_date"] = (
                dateType.today() - timedelta(days=10)
                if params.get("symbol") is not None
                else dateType.today()
            )

        # Ensure the start date is not on a weekend.
        if params.get("start_date").weekday() > 4:  # type: ignore
            params["start_date"] = params.get("start_date") + timedelta(
                days=4 - params.get("start_date").weekday()
            )  # type: ignore

        # If the end date is not provided, set it to the start date.
        if params.get("end_date") is None:
            params["end_date"] = params.get("start_date")

        # Ensure the start date is before the end date.
        if params.get("start_date") > params.get("end_date"):  # type: ignore
            params["start_date"], params["end_date"] = (
                params["end_date"],
                params["start_date"],
            )

        # Ensure we are not overloading API.
        if (
            params.get("symbol") is None
            and (params.get("end_date") - params.get("start_date")).days >= 1
        ):
            raise OpenBBError(
                "When no symbol is supplied, queries are not allowed if"
                + " the date range covers more than one trading day."
                + " Supply only the start_date for queries with no symbol."
            )

        # Ensure the end date is not on a weekend.
        if params.get("end_date").weekday() > 4:  # type: ignore
            params["end_date"] = params.get("end_date") + timedelta(
                days=7 - params.get("end_date").weekday()
            )  # type: ignore

        # Intrinio appears to make the end date not inclusive.
        # It doesn't want the start/end dates to be the same, set the end date to the next day.
        if params.get("end_date") is not None or params.get("start_date") == params.get(
            "end_date"
        ):
            params["end_date"] = params.get("end_date") + timedelta(days=1)  # type: ignore

        return params


class IntrinioOptionsUnusualData(OptionsUnusualData):
    """Intrinio Unusual Options Data."""

    __alias_dict__ = {
        "contract_symbol": "contract",
        "underlying_symbol": "symbol",
        "trade_type": "type",
        "trade_timestamp": "timestamp",
    }

    trade_timestamp: datetime = Field(description="The datetime of order placement.")
    trade_type: Literal["block", "sweep", "large", "sweep"] = Field(
        description="The type of unusual trade."
    )
    sentiment: Literal["bullish", "bearish", "neutral"] = Field(
        description=(
            "Bullish, Bearish, or Neutral Sentiment is estimated based on whether"
            + " the trade was executed at the bid, ask, or mark price."
        )
    )
    bid_at_execution: float = Field(description="Bid price at execution.")
    ask_at_execution: float = Field(description="Ask price at execution.")
    average_price: float = Field(
        description="The average premium paid per option contract."
    )
    underlying_price_at_execution: Optional[float] = Field(
        default=None,
        description="Price of the underlying security at execution of trade.",
    )
    total_size: int = Field(
        description="The total number of contracts involved in a single transaction."
    )
    total_value: Union[int, float] = Field(
        description="The aggregated value of all option contract premiums included in the trade."
    )

    @field_validator("trade_timestamp", mode="before", check_fields=False)
    @classmethod
    def validate_timestamp(cls, v):
        """Convert the timestamp string to a datetime object."""
        if v:
            v = parse(v)
            v = v.replace(microsecond=0)
            v = v.astimezone(timezone("America/New_York"))
            return v
        return None

    @field_validator("contract_symbol", mode="before", check_fields=False)
    @classmethod
    def validate_contract_symbol(cls, v):
        """Return the symbol as the OCC standard format."""
        return v.replace("_", "") if v else None

    @field_validator("trade_type", mode="before", check_fields=False)
    @classmethod
    def validate_trade_type(cls, v):
        """Validate the trade type."""
        if v and "_" in v:
            v = v.split("_")[-1]
        return v.lower()

    @field_validator("underlying_price_at_execution", mode="before", check_fields=False)
    @classmethod
    def replace_zero(cls, v):
        """Replace a 0 with None."""
        if v:
            return None if v == 0 else v
        return None


class IntrinioOptionsUnusualFetcher(
    Fetcher[IntrinioOptionsUnusualQueryParams, List[IntrinioOptionsUnusualData]]
):
    """Intrinio Unusual Options Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioOptionsUnusualQueryParams:
        """Transform the query."""
        return IntrinioOptionsUnusualQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioOptionsUnusualQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        data: List = []

        base_url = "https://api-v2.intrinio.com/options/unusual_activity"

        query_str = get_querystring(query.model_dump(), ["symbol", "limit"])

        # Page size is capped at 1000 for this endpoint. They don't tell you though.
        url = (
            base_url
            + f"/{query.symbol}/intraday?{query_str}&page_size=1000&api_key={api_key}"
            if query.symbol
            else base_url + f"/intraday?{query_str}&page_size=1000&api_key={api_key}"
        )

        data = []

        async def response_callback(response: ClientResponse, session: ClientSession):
            """Async response callback."""
            results = await response.json()
            if "trades" in results and len(results.get("trades")) > 0:  # type: ignore
                data.extend(
                    sorted(
                        results["trades"],  # type: ignore
                        key=lambda x: x["timestamp"],
                        reverse=True,
                    )
                )
                records = len(data)
                while (
                    "next_page" in results
                    and results.get("next_page") is not None  # type: ignore
                    and records < query.limit
                ):
                    next_page = results["next_page"]  # type: ignore
                    next_url = f"{url}&next_page={next_page}"
                    results = await amake_request(next_url, session=session, **kwargs)
                    if (
                        "trades" in results
                        and len(results.get("trades")) > 0  # type: ignore
                    ):
                        data.extend(
                            sorted(
                                results["trades"],  # type: ignore
                                key=lambda x: x["timestamp"],
                                reverse=True,
                            )
                        )
                        records = len(data)
            return data

        return await amake_request(url, response_callback=response_callback, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: IntrinioOptionsUnusualQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioOptionsUnusualData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError()
        return [
            IntrinioOptionsUnusualData.model_validate(d) for d in data[: query.limit]
        ]
