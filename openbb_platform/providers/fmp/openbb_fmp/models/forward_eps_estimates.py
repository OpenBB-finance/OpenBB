"""FMP Forward EPS Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.forward_eps_estimates import (
    ForwardEpsEstimatesData,
    ForwardEpsEstimatesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback
from pydantic import Field, field_validator


class FMPForwardEpsEstimatesQueryParams(ForwardEpsEstimatesQueryParams):
    """FMP Forward EPS Query.

    Source: https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    __alias_dict__ = {"fiscal_period": "period"}

    fiscal_period: Literal["annual", "quarter"] = Field(
        default="annual",
        description="The future fiscal period to retrieve estimates for.",
    )
    limit: Optional[int] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    include_historical: bool = Field(
        default=False,
        description="If True, the data will include all past data and the limit will be ignored.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def check_symbol(cls, value):
        """Check the symbol."""
        if not value:
            raise OpenBBError("Symbol is a required field for FMP.")
        return value


class FMPForwardEpsEstimatesData(ForwardEpsEstimatesData):
    """FMP Forward EPS Data."""

    __alias_dict__ = {
        "number_of_analysts": "numberAnalystsEstimatedEps",
        "high_estimate": "estimatedEpsHigh",
        "low_estimate": "estimatedEpsLow",
        "mean": "estimatedEpsAvg",
    }


class FMPForwardEpsEstimatesFetcher(
    Fetcher[
        FMPForwardEpsEstimatesQueryParams,
        List[FMPForwardEpsEstimatesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPForwardEpsEstimatesQueryParams:
        """Transform the query params."""
        return FMPForwardEpsEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPForwardEpsEstimatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        symbols = query.symbol.split(",")  # type: ignore

        results: List[Dict] = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = create_url(
                3, f"analyst-estimates/{symbol}", api_key, query, ["symbol"]
            )
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data returned for the given symbols.")

        return results

    @staticmethod
    def transform_data(
        query: FMPForwardEpsEstimatesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPForwardEpsEstimatesData]:
        """Return the transformed data."""
        symbols = query.symbol.split(",") if query.symbol else []
        cols = [
            "symbol",
            "date",
            "estimatedEpsAvg",
            "estimatedEpsHigh",
            "estimatedEpsLow",
            "numberAnalystsEstimatedEps",
        ]
        year = datetime.now().year
        results: List[FMPForwardEpsEstimatesData] = []
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
            for col in cols:
                temp[col] = item.get(col)

            if (
                query.include_historical is False
                and datetime.strptime(temp["date"], "%Y-%m-%d").year < year
            ):
                continue
            results.append(FMPForwardEpsEstimatesData.model_validate(temp))

        return (
            results[: query.limit]
            if query.limit and query.include_historical is False
            else results
        )
