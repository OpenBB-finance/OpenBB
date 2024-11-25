"""Polygon Cash Flow Statement Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class PolygonCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Polygon Cash Flow Statement Query.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials
    """

    __alias_dict__ = {"symbol": "ticker", "period": "timeframe"}
    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter", "ttm"],
        }
    }

    period: Literal["annual", "quarter", "ttm"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    filing_date: Optional[dateType] = Field(
        default=None, description="Filing date of the financial statement."
    )
    filing_date_lt: Optional[dateType] = Field(
        default=None, description="Filing date less than the given date."
    )
    filing_date_lte: Optional[dateType] = Field(
        default=None,
        description="Filing date less than or equal to the given date.",
    )
    filing_date_gt: Optional[dateType] = Field(
        default=None,
        description="Filing date greater than the given date.",
    )
    filing_date_gte: Optional[dateType] = Field(
        default=None,
        description="Filing date greater than or equal to the given date.",
    )
    period_of_report_date: Optional[dateType] = Field(
        default=None, description="Period of report date of the financial statement."
    )
    period_of_report_date_lt: Optional[dateType] = Field(
        default=None,
        description="Period of report date less than the given date.",
    )
    period_of_report_date_lte: Optional[dateType] = Field(
        default=None,
        description="Period of report date less than or equal to the given date.",
    )
    period_of_report_date_gt: Optional[dateType] = Field(
        default=None,
        description="Period of report date greater than the given date.",
    )
    period_of_report_date_gte: Optional[dateType] = Field(
        default=None,
        description="Period of report date greater than or equal to the given date.",
    )
    include_sources: bool = Field(
        default=False,
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

    net_cash_flow_from_operating_activities_continuing: Optional[float] = Field(
        description="Net cash flow from operating activities continuing.", default=None
    )
    net_cash_flow_from_operating_activities_discontinued: Optional[float] = Field(
        description="Net cash flow from operating activities discontinued.",
        default=None,
    )
    net_cash_flow_from_operating_activities: Optional[float] = Field(
        description="Net cash flow from operating activities.", default=None
    )
    net_cash_flow_from_investing_activities_continuing: Optional[float] = Field(
        description="Net cash flow from investing activities continuing.", default=None
    )
    net_cash_flow_from_investing_activities_discontinued: Optional[float] = Field(
        description="Net cash flow from investing activities discontinued.",
        default=None,
    )
    net_cash_flow_from_investing_activities: Optional[float] = Field(
        description="Net cash flow from investing activities.", default=None
    )
    net_cash_flow_from_financing_activities_continuing: Optional[float] = Field(
        description="Net cash flow from financing activities continuing.", default=None
    )
    net_cash_flow_from_financing_activities_discontinued: Optional[float] = Field(
        description="Net cash flow from financing activities discontinued.",
        default=None,
    )
    net_cash_flow_from_financing_activities: Optional[float] = Field(
        description="Net cash flow from financing activities.", default=None
    )
    net_cash_flow_continuing: Optional[float] = Field(
        description="Net cash flow continuing.", default=None
    )
    net_cash_flow_discontinued: Optional[float] = Field(
        description="Net cash flow discontinued.", default=None
    )
    exchange_gains_losses: Optional[float] = Field(
        description="Exchange gains losses.", default=None
    )
    net_cash_flow: Optional[float] = Field(description="Net cash flow.", default=None)

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class PolygonCashFlowStatementFetcher(
    Fetcher[
        PolygonCashFlowStatementQueryParams,
        List[PolygonCashFlowStatementData],
    ]
):
    """Polygon Cash Flow Statement Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonCashFlowStatementQueryParams:
        """Transform the query params."""
        return PolygonCashFlowStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PolygonCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_polygon.utils.helpers import get_data_many

        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/vX/reference/financials"
        period_dict = {
            "annual": "annual",
            "quarter": "quarterly",
            "ttm": "ttm",
        }
        query_string = get_querystring(
            query.model_dump(by_alias=True), ["ticker", "timeframe"]
        )

        if query.symbol.isdigit():
            query_string = f"cik={query.symbol}&timeframe={period_dict[query.period]}&{query_string}"
        else:
            query_string = f"ticker={query.symbol}&timeframe={period_dict[query.period]}&{query_string}"

        request_url = f"{base_url}?{query_string}&apiKey={api_key}"

        return await get_data_many(request_url, "results", **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: PolygonCashFlowStatementQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[PolygonCashFlowStatementData]:
        """Return the transformed data."""
        transformed_data: List[PolygonCashFlowStatementData] = []

        for item in data:
            sub_data = {
                key: value["value"]
                for key, value in item["financials"]["cash_flow_statement"].items()
            }
            sub_data["period_ending"] = item["end_date"]
            sub_data["fiscal_period"] = item["fiscal_period"]
            transformed_data.append(PolygonCashFlowStatementData(**sub_data))

        return transformed_data
