"""FMP Forward EBITDA Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.forward_ebitda_estimates import (
    ForwardEbitdaEstimatesData,
    ForwardEbitdaEstimatesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback
from pydantic import Field, field_validator


class FMPForwardEbitdaEstimatesQueryParams(ForwardEbitdaEstimatesQueryParams):
    """FMP Forward EBITDA Query.

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


class FMPForwardEbitdaEstimatesData(ForwardEbitdaEstimatesData):
    """FMP Forward EBITDA Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "high_estimate": "estimatedEbitdaHigh",
        "low_estimate": "estimatedEbitdaLow",
        "mean": "estimatedEbitdaAvg",
    }


class FMPForwardEbitdaEstimatesFetcher(
    Fetcher[
        FMPForwardEbitdaEstimatesQueryParams,
        List[FMPForwardEbitdaEstimatesData],
    ]
):
    """FMP Forward EBITDA Estimates Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPForwardEbitdaEstimatesQueryParams:
        """Transform the query params."""
        return FMPForwardEbitdaEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPForwardEbitdaEstimatesQueryParams,
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
        query: FMPForwardEbitdaEstimatesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPForwardEbitdaEstimatesData]:
        """Return the transformed data."""
        symbols = query.symbol.split(",") if query.symbol else []
        cols = [
            "symbol",
            "date",
            "estimatedEbitdaAvg",
            "estimatedEbitdaHigh",
            "estimatedEbitdaLow",
        ]
        year = datetime.now().year
        results: List[FMPForwardEbitdaEstimatesData] = []
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
            results.append(FMPForwardEbitdaEstimatesData.model_validate(temp))

        return (
            results[: query.limit]
            if query.limit and query.include_historical is False
            else results
        )
