"""Intrinio Forward EBITDA Estimates Model."""

# pylint: disable=unused-argument

import asyncio
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.forward_ebitda_estimates import (
    ForwardEbitdaEstimatesData,
    ForwardEbitdaEstimatesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from openbb_core.provider.utils.helpers import (
    amake_request,
    get_querystring,
)
from openbb_intrinio.utils.helpers import response_callback
from pydantic import Field


class IntrinioForwardEbitdaEstimatesQueryParams(ForwardEbitdaEstimatesQueryParams):
    """Intrinio Forward EBITDA Estimates Query.

    https://docs.intrinio.com/documentation/web_api/get_zacks_sales_estimates_v2
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}
    __alias_dict__ = {"estimate_type": "type"}

    fiscal_period: Optional[Literal["annual", "quarter"]] = Field(
        default=None, description="Filter for only full-year or quarterly estimates."
    )
    estimate_type: Optional[
        Literal[
            "ebitda",
            "ebit",
            "enterprise_value",
            "cash_flow_per_share",
            "pretax_income",
        ]
    ] = Field(
        default=None,
        description="Limit the EBITDA estimates to this type.",
    )


class IntrinioForwardEbitdaEstimatesData(ForwardEbitdaEstimatesData):
    """Intrinio Forward EBITDA Estimates Data."""

    __alias_dict__ = {
        "last_updated": "updated_date",
        "symbol": "ticker",
        "calendar_period": "estimate_month",
        "name": "company_name",
        "fiscal_year": "estimate_year",
        "fiscal_period": "period",
        "low_estimate": "low",
        "high_estimate": "high",
        "number_of_analysts": "estimate_count",
        "standard_deviation": "std_dev",
    }

    conensus_type: Optional[
        Literal[
            "ebitda",
            "ebitda",
            "ebit",
            "enterprise_value",
            "cash_flow_per_share",
            "pretax_income",
        ]
    ] = Field(
        default=None,
        description="The type of estimate.",
    )


class IntrinioForwardEbitdaEstimatesFetcher(
    Fetcher[
        IntrinioForwardEbitdaEstimatesQueryParams,
        List[IntrinioForwardEbitdaEstimatesData],
    ]
):
    """Intrinio Forward EBITDA Estimates Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> IntrinioForwardEbitdaEstimatesQueryParams:
        """Transform the query params."""
        return IntrinioForwardEbitdaEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioForwardEbitdaEstimatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        BASE_URL = (
            "https://api-v2.intrinio.com/zacks/ebitda_consensus?"
            + f"page_size=10000&api_key={api_key}"
        )
        symbols = query.symbol.split(",") if query.symbol else None
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])
        results: List[Dict] = []

        async def get_one(symbol):
            """Get the data for one symbol."""
            url = f"{BASE_URL}&identifier={symbol}"
            url = url + f"&{query_str}" if query_str else url
            data = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            consensus = (
                data.get("ebitda_consensus")
                if isinstance(data, dict) and "ebitda_consensus" in data
                else []
            )
            if not data or not consensus:
                warn(f"Symbol Error: No data found for {symbol}")
            if consensus:
                results.extend(consensus)

        if symbols:
            await asyncio.gather(*[get_one(symbol) for symbol in symbols])
            if not results:
                raise EmptyDataError(f"No results were found. -> {query.symbol}")
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

            estimates = data.get("ebitda_consensus", [])  # type: ignore
            if estimates and len(estimates) > 0:
                results.extend(estimates)
                while data.get("next_page"):  # type: ignore
                    next_page = data["next_page"]  # type: ignore
                    next_url = f"{url}&next_page={next_page}"
                    data = await amake_request(next_url, session=session, **kwargs)
                    consensus = (
                        data.get("ebitda_consensus")
                        if isinstance(data, dict) and "ebitda_consensus" in data
                        else []
                    )
                    if consensus:
                        results.extend(consensus)  # type: ignore
            return results

        url = f"{BASE_URL}&{query_str}" if query_str else BASE_URL

        results = await amake_request(url, response_callback=fetch_callback, **kwargs)  # type: ignore

        if not results:
            raise EmptyDataError("The request was successful but was returned empty.")

        return results

    @staticmethod
    def transform_data(
        query: IntrinioForwardEbitdaEstimatesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioForwardEbitdaEstimatesData]:
        """Transform the raw data into the standard format."""
        if not data:
            raise EmptyDataError()
        results: List[IntrinioForwardEbitdaEstimatesData] = []
        fiscal_period = None
        if query.fiscal_period is not None:
            fiscal_period = "fy" if query.fiscal_period == "annual" else "fq"
        for item in data:
            estimate_count = item.get("estimate_count")
            if (
                not estimate_count
                or estimate_count == 0
                or not item.get("updated_date")
            ):
                continue
            if fiscal_period and item.get("period") != fiscal_period:
                continue
            results.append(IntrinioForwardEbitdaEstimatesData.model_validate(item))
        if not results:
            raise EmptyDataError()

        return sorted(
            results, key=lambda x: (x.fiscal_year, x.last_updated), reverse=True
        )
