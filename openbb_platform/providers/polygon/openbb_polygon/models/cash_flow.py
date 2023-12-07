"""Polygon Cash Flow Statement Model."""

from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_polygon.utils.helpers import get_data
from pydantic import Field, field_validator


class PolygonCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Polygon Cash Flow Statement Query.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials
    """

    __alias_dict__ = {"symbol": "ticker", "period": "timeframe"}

    filing_date: Optional[date] = Field(
        default=None, description="Filing date of the financial statement."
    )
    filing_date_lt: Optional[date] = Field(
        default=None, description="Filing date less than the given date."
    )
    filing_date_lte: Optional[date] = Field(
        default=None,
        description="Filing date less than or equal to the given date.",
    )
    filing_date_gt: Optional[date] = Field(
        default=None,
        description="Filing date greater than the given date.",
    )
    filing_date_gte: Optional[date] = Field(
        default=None,
        description="Filing date greater than or equal to the given date.",
    )
    period_of_report_date: Optional[date] = Field(
        default=None, description="Period of report date of the financial statement."
    )
    period_of_report_date_lt: Optional[date] = Field(
        default=None,
        description="Period of report date less than the given date.",
    )
    period_of_report_date_lte: Optional[date] = Field(
        default=None,
        description="Period of report date less than or equal to the given date.",
    )
    period_of_report_date_gt: Optional[date] = Field(
        default=None,
        description="Period of report date greater than the given date.",
    )
    period_of_report_date_gte: Optional[date] = Field(
        default=None,
        description="Period of report date greater than or equal to the given date.",
    )
    include_sources: Optional[bool] = Field(
        default=None,
        description="Whether to include the sources of the financial statement.",
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        default=None, description="Order of the financial statement."
    )
    sort: Optional[Literal["filing_date", "period_of_report_date"]] = Field(
        default=None, description="Sort of the financial statement."
    )


class PolygonCashFlowStatementData(CashFlowStatementData):
    """Polygon Cash Flow Statement Data."""

    __alias_dict__ = {"date": "start_date"}

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def symbol_from_tickers(cls, v):
        """Return a list of symbols as a list."""
        if isinstance(v, list):
            return ",".join(v)
        return v


class PolygonCashFlowStatementFetcher(
    Fetcher[
        PolygonCashFlowStatementQueryParams,
        List[PolygonCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Polygon endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCashFlowStatementQueryParams:
        """Transform the query params."""
        return PolygonCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/vX/reference/financials"
        period = "quarterly" if query.period == "quarter" else query.period
        query_string = get_querystring(
            query.model_dump(by_alias=True), ["ticker", "period"]
        )

        if query.symbol.isdigit():
            query_string = f"cik={query.symbol}&period={period}&{query_string}"
        else:
            query_string = f"ticker={query.symbol}&period={period}&{query_string}"

        request_url = f"{base_url}?{query_string}&apiKey={api_key}"

        return get_data(request_url, **kwargs).get("results", [])

    @staticmethod
    def transform_data(
        query: PolygonCashFlowStatementQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> List[PolygonCashFlowStatementData]:
        """Return the transformed data."""
        transformed_data = []

        for item in data:
            sub_data = {
                key: value["value"]
                for key, value in item["financials"]["cash_flow_statement"].items()
            }
            sub_data["date"] = item["start_date"]
            sub_data["cik"] = item["cik"]
            sub_data["symbol"] = item["tickers"]
            sub_data["period"] = item["fiscal_period"]
            transformed_data.append(PolygonCashFlowStatementData(**sub_data))

        return transformed_data
