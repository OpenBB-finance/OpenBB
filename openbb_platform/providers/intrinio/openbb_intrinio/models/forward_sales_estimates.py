"""Intrinio Forward Sales Estimates Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.forward_sales_estimates import (
    ForwardSalesEstimatesData,
    ForwardSalesEstimatesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from openbb_core.provider.utils.helpers import (
    amake_request,
    get_querystring,
)
from openbb_intrinio.utils.helpers import response_callback
from pydantic import Field, field_validator, model_validator


class IntrinioForwardSalesEstimatesQueryParams(ForwardSalesEstimatesQueryParams):
    """Intrinio Forward Sales Estimates Query.

    https://docs.intrinio.com/documentation/web_api/get_zacks_sales_estimates_v2
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    fiscal_year: Optional[int] = Field(
        default=None,
        description="The future fiscal year to retrieve estimates for."
        + " When no symbol and year is supplied the current calendar year is used.",
    )
    fiscal_period: Optional[Literal["fy", "q1", "q2", "q3", "q4"]] = Field(
        default=None,
        description="The future fiscal period to retrieve estimates for.",
    )
    calendar_year: Optional[int] = Field(
        default=None,
        description="The future calendar year to retrieve estimates for."
        + " When no symbol and year is supplied the current calendar year is used.",
    )
    calendar_period: Optional[Literal["q1", "q2", "q3", "q4"]] = Field(
        default=None,
        description="The future calendar period to retrieve estimates for.",
    )

    @model_validator(mode="after")
    @classmethod
    def validate_choices(cls, values):
        """Validate the model and set a safe default state."""
        if values.symbol is None and (
            values.calendar_year is None and values.fiscal_year is None
        ):
            values.calendar_year = datetime.now().year
        return values


class IntrinioForwardSalesEstimatesData(ForwardSalesEstimatesData):
    """Intrinio Forward Sales Estimates Data."""

    __alias_dict__ = {
        "low_estimate": "low",
        "high_estimate": "high",
        "number_of_analysts": "count",
        "mean": "estimated_sales_mean",
        "revisions_1w_up": "analyst_revisions_up_1w",
        "revisions_1w_down": "analyst_revisions_down_1w",
        "revisions_1w_change_percent": "analyst_revisions_percent_change_1w",
        "revisions_1m_up": "analyst_revisions_up_1m",
        "revisions_1m_down": "analyst_revisions_down_1m",
        "revisions_1m_change_percent": "analyst_revisions_percent_change_1m",
        "revisions_3m_up": "analyst_revisions_up_3m",
        "revisions_3m_down": "analyst_revisions_down_3m",
        "revisions_3m_change_percent": "analyst_revisions_percent_change_3m",
    }

    revisions_1w_up: Optional[int] = Field(
        default=None, description="Number of revisions up in the last week."
    )
    revisions_1w_down: Optional[int] = Field(
        default=None, description="Number of revisions down in the last week."
    )
    revisions_1w_change_percent: Optional[float] = Field(
        default=None,
        description="The analyst revisions percent change in estimate for the period of 1 week.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    revisions_1m_up: Optional[int] = Field(
        default=None, description="Number of revisions up in the last month."
    )
    revisions_1m_down: Optional[int] = Field(
        default=None, description="Number of revisions down in the last month."
    )
    revisions_1m_change_percent: Optional[float] = Field(
        default=None,
        description="The analyst revisions percent change in estimate for the period of 1 month.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    revisions_3m_up: Optional[int] = Field(
        default=None, description="Number of revisions up in the last 3 months."
    )
    revisions_3m_down: Optional[int] = Field(
        default=None, description="Number of revisions down in the last 3 months."
    )
    revisions_3m_change_percent: Optional[float] = Field(
        default=None,
        description="The analyst revisions percent change in estimate for the period of 3 months.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator(
        "revisions_1w_change_percent",
        "revisions_1m_change_percent",
        "revisions_3m_change_percent",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(
        cls, v: Optional[Union[int, float]]
    ) -> Optional[Union[int, float]]:
        """Normalize percent values."""
        return v / 100 if v else None


class IntrinioForwardSalesEstimatesFetcher(
    Fetcher[
        IntrinioForwardSalesEstimatesQueryParams,
        List[IntrinioForwardSalesEstimatesData],
    ]
):
    """Intrinio Forward Sales Estimates Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioForwardSalesEstimatesQueryParams:
        """Transform the query params."""
        return IntrinioForwardSalesEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioForwardSalesEstimatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        BASE_URL = "https://api-v2.intrinio.com/zacks/sales_estimates?page_size=10000"

        symbols = query.symbol.split(",") if query.symbol else None

        query_str = get_querystring(
            query.model_dump(by_alias=True),
            ["symbol", "calendar_period", "fiscal_period", "limit"],
        )

        results: List[Dict] = []

        async def get_one(symbol):
            """Get the data for one symbol."""
            url = f"{BASE_URL}&identifier={symbol}&{query_str}&api_key={api_key}"
            new_data: List[Dict] = []
            data = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not data or not isinstance(data, dict) or not data.get("estimates"):
                warn(f"Symbol Error: No data found for {symbol}")
            if isinstance(data, dict) and data.get("estimates"):
                new_data = data.get("estimates")  # type: ignore
                if new_data:
                    results.extend(new_data)

        if symbols:
            await asyncio.gather(*[get_one(symbol) for symbol in symbols])
            return results

        async def fetch_callback(response, session):
            """Use callback for pagination."""
            data = await response.json()
            error = data.get("error", None)
            if error:
                message = data.get("message", "")
                if "api key" in message.lower():
                    raise UnauthorizedError(
                        f"Unauthorized Intrinio request -> {message}"
                    )
                raise OpenBBError(f"Error: {error} -> {message}")
            if data.get("estimates") and len(data.get("estimates")) > 0:  # type: ignore
                results.extend(data.get("estimates"))  # type: ignore
                while data.get("next_page"):  # type: ignore
                    next_page = data["next_page"]  # type: ignore
                    next_url = f"{url}&next_page={next_page}"
                    data = await amake_request(next_url, session=session, **kwargs)
                    if (
                        "estimates" in data
                        and len(data.get("estimates")) > 0  # type: ignore
                    ):
                        results.extend(data.get("estimates"))  # type: ignore
            return results

        url = f"{BASE_URL}&{query_str}&api_key={api_key}"

        results = await amake_request(url, response_callback=fetch_callback, **kwargs)  # type: ignore

        if not results:
            raise EmptyDataError("The request was successful but was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: IntrinioForwardSalesEstimatesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioForwardSalesEstimatesData]:
        """Transform the raw data into the standard format."""
        symbols = query.symbol.split(",") if query.symbol else []
        results: List[IntrinioForwardSalesEstimatesData] = []
        for item in sorted(
            data,
            key=lambda item: (  # type: ignore
                (
                    symbols.index(item.get("symbol")) if item.get("symbol") in symbols else len(symbols),  # type: ignore
                    item.get("date"),
                )
                if symbols
                else item.get("date")
            ),
        ):
            temp: Dict[str, Any] = {}
            company = item.pop("company")
            if company.get("ticker") is None:
                continue
            temp["symbol"] = company.get("ticker")
            temp["name"] = company.get("name")
            if query.fiscal_period and query.fiscal_period.upper() != item.get(
                "fiscal_period"
            ):
                continue
            if query.calendar_period and query.calendar_period.upper() != item.get(
                "calendar_period"
            ):
                continue
            temp.update(item)
            results.append(IntrinioForwardSalesEstimatesData.model_validate(temp))

        return results
