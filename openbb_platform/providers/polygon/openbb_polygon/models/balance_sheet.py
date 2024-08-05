"""Polygon Balance Sheet Statement Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class PolygonBalanceSheetQueryParams(BalanceSheetQueryParams):
    """Polygon Balance Sheet Statement Query.

    Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials
    """

    __alias_dict__ = {"symbol": "ticker", "period": "timeframe"}
    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
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
        default=True,
        description="Whether to include the sources of the financial statement.",
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        default=None, description="Order of the financial statement."
    )
    sort: Optional[Literal["filing_date", "period_of_report_date"]] = Field(
        default=None, description="Sort of the financial statement."
    )


class PolygonBalanceSheetData(BalanceSheetData):
    """Polygon Balance Sheet Statement Data."""

    __alias_dict__ = {
        "date": "start_date",
        "total_liabilities_and_shareholders_equity": "liabilities_and_equity",
        "minority_interest": "equity_attributable_to_noncontrolling_interest",
        "total_current_assets": "current_assets",
        "marketable_securities": "fixed_assets",
        "property_plant_equipment_net": "public_utilities_property_plant_and_equipment_net",
        "other_non_current_assets": "other_noncurrent_assets",
        "total_non_current_assets": "noncurrent_assets",
        "total_assets": "assets",
        "total_current_liabilities": "current_liabilities",
        "other_non_current_liabilities": "other_noncurrent_liabilities",
        "total_non_current_liabilities": "noncurrent_liabilities",
        "total_liabilities": "liabilities",
        "total_shareholders_equity": "equity_attributable_to_parent",
        "total_equity": "equity",
        "employee_wages": "wages",
        "redeemable_non_controlling_interest": "redeemable_noncontrolling_interest",
        "redeemable_non_controlling_interest_other": "redeemable_noncontrolling_interest_other",
    }

    accounts_receivable: Optional[float] = Field(
        description="Accounts receivable", default=None
    )
    marketable_securities: Optional[float] = Field(
        description="Marketable securities", default=None
    )
    prepaid_expenses: Optional[float] = Field(
        description="Prepaid expenses", default=None
    )
    other_current_assets: Optional[float] = Field(
        description="Other current assets", default=None
    )
    total_current_assets: Optional[float] = Field(
        description="Total current assets", default=None
    )
    property_plant_equipment_net: Optional[float] = Field(
        description="Property plant and equipment net", default=None
    )
    inventory: Optional[float] = Field(description="Inventory", default=None)
    other_non_current_assets: Optional[float] = Field(
        description="Other non-current assets", default=None
    )
    total_non_current_assets: Optional[float] = Field(
        description="Total non-current assets", default=None
    )
    intangible_assets: Optional[float] = Field(
        description="Intangible assets", default=None
    )
    total_assets: Optional[float] = Field(description="Total assets", default=None)
    accounts_payable: Optional[float] = Field(
        description="Accounts payable", default=None
    )
    employee_wages: Optional[float] = Field(description="Employee wages", default=None)
    other_current_liabilities: Optional[float] = Field(
        description="Other current liabilities", default=None
    )
    total_current_liabilities: Optional[float] = Field(
        description="Total current liabilities", default=None
    )
    other_non_current_liabilities: Optional[float] = Field(
        description="Other non-current liabilities", default=None
    )
    total_non_current_liabilities: Optional[float] = Field(
        description="Total non-current liabilities", default=None
    )
    long_term_debt: Optional[float] = Field(description="Long term debt", default=None)
    total_liabilities: Optional[float] = Field(
        description="Total liabilities", default=None
    )
    minority_interest: Optional[float] = Field(
        description="Minority interest", default=None
    )
    temporary_equity_attributable_to_parent: Optional[float] = Field(
        description="Temporary equity attributable to parent", default=None
    )
    equity_attributable_to_parent: Optional[float] = Field(
        description="Equity attributable to parent", default=None
    )
    temporary_equity: Optional[float] = Field(
        description="Temporary equity", default=None
    )
    preferred_stock: Optional[float] = Field(
        description="Preferred stock", default=None
    )
    redeemable_non_controlling_interest: Optional[float] = Field(
        description="Redeemable non-controlling interest", default=None
    )
    redeemable_non_controlling_interest_other: Optional[float] = Field(
        description="Redeemable non-controlling interest other", default=None
    )
    total_shareholders_equity: Optional[float] = Field(
        description="Total stock holders equity", default=None
    )
    total_equity: Optional[float] = Field(description="Total equity", default=None)
    total_liabilities_and_shareholders_equity: Optional[float] = Field(
        description="Total liabilities and stockholders equity", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class PolygonBalanceSheetFetcher(
    Fetcher[
        PolygonBalanceSheetQueryParams,
        List[PolygonBalanceSheetData],
    ]
):
    """Polygon Balance Sheet Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonBalanceSheetQueryParams:
        """Transform the query params."""
        return PolygonBalanceSheetQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PolygonBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_polygon.utils.helpers import get_data_many

        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/vX/reference/financials"
        period = "quarterly" if query.period == "quarter" else query.period
        query_string = get_querystring(
            query.model_dump(by_alias=True), ["ticker", "timeframe"]
        )

        if query.symbol.isdigit():
            query_string = f"cik={query.symbol}&timeframe={period}&{query_string}"
        else:
            query_string = f"ticker={query.symbol}&timeframe={period}&{query_string}"

        request_url = f"{base_url}?{query_string}&apiKey={api_key}"

        return await get_data_many(request_url, "results", **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: PolygonBalanceSheetQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[PolygonBalanceSheetData]:
        """Return the transformed data."""
        transformed_data: List[PolygonBalanceSheetData] = []

        for item in data:
            if "balance_sheet" in item["financials"]:
                sub_data = {
                    key: value["value"]
                    for key, value in item["financials"]["balance_sheet"].items()
                }
                sub_data["period_ending"] = item["end_date"]
                sub_data["fiscal_period"] = item["fiscal_period"]
                transformed_data.append(PolygonBalanceSheetData(**sub_data))

        return transformed_data
