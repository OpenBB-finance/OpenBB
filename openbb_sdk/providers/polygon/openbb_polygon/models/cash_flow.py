"""Polygon Cash Flow Statement Fetcher"""


from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_polygon.utils.helpers import get_data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, validator


class PolygonCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Polygon Fundamental QueryParams.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials
    """

    class Config:
        fields = {
            "symbol": "ticker",
            "period": "timeframe",
        }

    company_name: Optional[str] = Field(description="Name of the company.")
    company_name_search: Optional[str] = Field(
        description="Name of the company to search."
    )
    sic: Optional[str] = Field(
        description="The Standard Industrial Classification (SIC) of the company."
    )
    filing_date: Optional[date] = Field(
        description="Filing date of the financial statement."
    )
    filing_date_lt: Optional[date] = Field(
        description="Filing date less than the given date."
    )
    filing_date_lte: Optional[date] = Field(
        description="Filing date less than or equal to the given date.",
    )
    filing_date_gt: Optional[date] = Field(
        description="Filing date greater than the given date.",
    )
    filing_date_gte: Optional[date] = Field(
        description="Filing date greater than or equal to the given date.",
    )
    period_of_report_date: Optional[date] = Field(
        description="Period of report date of the financial statement."
    )
    period_of_report_date_lt: Optional[date] = Field(
        description="Period of report date less than the given date.",
    )
    period_of_report_date_lte: Optional[date] = Field(
        description="Period of report date less than or equal to the given date.",
    )
    period_of_report_date_gt: Optional[date] = Field(
        description="Period of report date greater than the given date.",
    )
    period_of_report_date_gte: Optional[date] = Field(
        description="Period of report date greater than or equal to the given date.",
    )
    include_sources: Optional[bool] = Field(
        description="Whether to include the sources of the financial statement."
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        description="Order of the financial statement."
    )
    sort: Optional[Literal["filing_date", "period_of_report_date"]] = Field(
        description="Sort of the financial statement."
    )


class PolygonCashFlowStatementData(CashFlowStatementData):
    """Return Balance Sheet Data."""

    @validator("symbol", pre=True, check_fields=False)
    def symbol_from_tickers(cls, v):  # pylint: disable=no-self-argument
        if isinstance(v, list):
            return ",".join(v)
        return v


class PolygonCashFlowStatementFetcher(
    Fetcher[
        PolygonCashFlowStatementQueryParams,
        List[PolygonCashFlowStatementData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCashFlowStatementQueryParams:
        return PolygonCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/vX/reference/financials"
        query_string = get_querystring(query.dict(by_alias=True), [])
        request_url = f"{base_url}?{query_string}&apiKey={api_key}"
        data = get_data(request_url, **kwargs)["results"]

        if len(data) == 0:
            raise RuntimeError("No balance sheet found")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[PolygonCashFlowStatementData]:
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
