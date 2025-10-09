"""FMP Analyst Estimates Model."""

# pylint: disable=unused-argument

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.analyst_estimates import (
    AnalystEstimatesData,
    AnalystEstimatesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FMPAnalystEstimatesQueryParams(AnalystEstimatesQueryParams):
    """FMP Analyst Estimates Query.

    Source: https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    period: Literal["quarter", "annual"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: int | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )
    page: int | None = Field(
        default=None, description="Page number for paginated results. Used with limit."
    )


class FMPAnalystEstimatesData(AnalystEstimatesData):
    """FMP Analyst Estimates Data."""

    __alias_dict__ = {
        "estimated_revenue_low": "revenueLow",
        "estimated_revenue_high": "revenueHigh",
        "estimated_revenue_avg": "revenueAvg",
        "estimated_sga_expense_low": "sgaExpenseLow",
        "estimated_sga_expense_high": "sgaExpenseHigh",
        "estimated_sga_expense_avg": "sgaExpenseAvg",
        "estimated_ebitda_low": "ebitdaLow",
        "estimated_ebitda_high": "ebitdaHigh",
        "estimated_ebitda_avg": "ebitdaAvg",
        "estimated_ebit_low": "ebitLow",
        "estimated_ebit_high": "ebitHigh",
        "estimated_ebit_avg": "ebitAvg",
        "estimated_net_income_low": "netIncomeLow",
        "estimated_net_income_high": "netIncomeHigh",
        "estimated_net_income_avg": "netIncomeAvg",
        "estimated_eps_low": "epsLow",
        "estimated_eps_high": "epsHigh",
        "estimated_eps_avg": "epsAvg",
        "number_analysts_estimated_revenue": "numAnalystsRevenue",
        "number_analysts_eps": "numAnalystsEps",
    }


class FMPAnalystEstimatesFetcher(
    Fetcher[
        FMPAnalystEstimatesQueryParams,
        list[FMPAnalystEstimatesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPAnalystEstimatesQueryParams:
        """Transform the query params."""
        return FMPAnalystEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPAnalystEstimatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import warnings
        from openbb_core.provider.utils.helpers import amake_request
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""

        symbols = query.symbol.split(",")  # type: ignore

        results: list[dict] = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = (
                "https://financialmodelingprep.com/stable/analyst-estimates?"
                + f"symbol={symbol}&period={query.period}"
                + f"&page={query.page if query.page else 0}&limit={query.limit if query.limit else 1000}"
                + f"&apikey={api_key}"
            )
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warnings.warn(f"Symbol Error: No data found for {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data returned for the given symbols.")

        return sorted(results, key=lambda x: (x["date"], x["symbol"]), reverse=False)

    @staticmethod
    def transform_data(
        query: FMPAnalystEstimatesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPAnalystEstimatesData]:
        """Return the transformed data."""
        return [FMPAnalystEstimatesData.model_validate(d) for d in data]
