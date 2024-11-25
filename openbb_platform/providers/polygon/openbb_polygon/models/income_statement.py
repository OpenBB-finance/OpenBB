"""Polygon Income Statement Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class PolygonIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Polygon Income Statement Query.

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


class PolygonIncomeStatementData(IncomeStatementData):
    """Polygon Income Statement Data."""

    __alias_dict__ = {
        # pylint: disable=line-too-long
        "revenue": "revenues",
        "provisions_for_loan_lease_and_other_losses": "provision_for_loan_lease_and_other_losses",
        "income_tax_expense_benefit_current": "income_tax_expense_benefit_current",
        "deferred_tax_benefit": "income_tax_expense_benefit_deferred",
        "operating_income": "operating_income_loss",
        "non_operating_income": "nonoperating_income_loss",
        "income_before_equity_method_investments": "income_loss_before_equity_method_investments",
        "income_from_equity_method_investments": "income_loss_from_equity_method_investments",
        "total_pre_tax_income": "income_loss_from_continuing_operations_before_tax",
        "income_tax_expense": "income_tax_expense_benefit",
        "interest_and_debt_expense": "interest_and_debt_expense",
        "consolidated_net_income": "net_income_loss",
        "eps": "basic_earnings_per_share",
        "eps_diluted": "diluted_earnings_per_share",
        "interest_and_dividend_income": "interest_and_dividend_income_operating",
        "total_interest_expense": "interest_expense_operating",
        "interest_income_after_provision_for_losses": "interest_income_expense_after_provision_for_losses",
        "net_interest_income": "interest_income_expense_operating_net",
        "non_interest_income": "noninterest_income",
        "non_interest_expense": "noninterest_expense",
        "income_after_tax": "income_loss_from_continuing_operations_after_tax",
        "income_from_discontinued_operations_net_of_tax_on_disposal": "income_loss_from_discontinued_operations_net_of_tax_gain_loss_on_disposal",  # noqa  # pylint: disable=line-too-long
        "income_from_discontinued_operations_net_of_tax": "income_loss_from_discontinued_operations_net_of_tax",
        "net_income_attributable_to_noncontrolling_interest": "net_income_loss_attributable_to_noncontrolling_interest",
        "net_income_attributable_to_parent": "net_income_loss_attributable_to_parent",
        "net_income_attributable_to_common_shareholders": "net_income_loss_available_to_common_stockholders_basic",
        "participating_securities_earnings": "participating_securities_distributed_and_undistributed_earnings_loss_basic",
        "undistributed_earnings_allocated_to_participating_securities": "undistributed_earnings_loss_allocated_to_participating_securities_basic",  # noqa  # pylint: disable=line-too-long
        "weighted_average_diluted_shares_outstanding": "diluted_average_shares",
        "weighted_average_basic_shares_outstanding": "basic_average_shares",
        "basic_earnings_per_share": "eps",
        "diluted_earnings_per_share": "eps_diluted",
    }

    revenue: Optional[float] = Field(default=None, description="Total Revenue")
    cost_of_revenue_goods: Optional[float] = Field(
        default=None, description="Cost of Revenue - Goods"
    )
    cost_of_revenue_services: Optional[float] = Field(
        default=None, description="Cost of Revenue - Services"
    )
    cost_of_revenue: Optional[float] = Field(
        default=None, description="Cost of Revenue"
    )
    gross_profit: Optional[float] = Field(default=None, description="Gross Profit")
    provisions_for_loan_lease_and_other_losses: Optional[float] = Field(
        default=None, description="Provisions for loan lease and other losses"
    )
    depreciation_and_amortization: Optional[float] = Field(
        default=None, description="Depreciation and Amortization"
    )
    income_tax_expense_benefit_current: Optional[float] = Field(
        default=None, description="Income tax expense benefit current"
    )
    deferred_tax_benefit: Optional[float] = Field(
        default=None, description="Deferred tax benefit"
    )
    benefits_costs_expenses: Optional[float] = Field(
        default=None, description="Benefits, costs and expenses"
    )
    selling_general_and_administrative_expense: Optional[float] = Field(
        default=None, description="Selling, general and administrative expense"
    )
    research_and_development: Optional[float] = Field(
        default=None, description="Research and development"
    )
    costs_and_expenses: Optional[float] = Field(
        default=None, description="Costs and expenses"
    )
    other_operating_expenses: Optional[float] = Field(
        default=None, description="Other Operating Expenses"
    )
    operating_expenses: Optional[float] = Field(
        default=None, description="Operating expenses"
    )
    operating_income: Optional[float] = Field(
        default=None, description="Operating Income/Loss"
    )
    non_operating_income: Optional[float] = Field(
        default=None, description="Non Operating Income/Loss"
    )
    interest_and_dividend_income: Optional[float] = Field(
        default=None, description="Interest and Dividend Income"
    )
    total_interest_expense: Optional[float] = Field(
        default=None, description="Interest Expense"
    )
    interest_and_debt_expense: Optional[float] = Field(
        default=None, description="Interest and Debt Expense"
    )
    net_interest_income: Optional[float] = Field(
        default=None, description="Interest Income Net"
    )
    interest_income_after_provision_for_losses: Optional[float] = Field(
        default=None, description="Interest Income After Provision for Losses"
    )
    non_interest_expense: Optional[float] = Field(
        default=None, description="Non-Interest Expense"
    )
    non_interest_income: Optional[float] = Field(
        default=None, description="Non-Interest Income"
    )
    income_from_discontinued_operations_net_of_tax_on_disposal: Optional[float] = Field(
        default=None,
        description="Income From Discontinued Operations Net of Tax on Disposal",
    )
    income_from_discontinued_operations_net_of_tax: Optional[float] = Field(
        default=None, description="Income From Discontinued Operations Net of Tax"
    )
    income_before_equity_method_investments: Optional[float] = Field(
        default=None, description="Income Before Equity Method Investments"
    )
    income_from_equity_method_investments: Optional[float] = Field(
        default=None, description="Income From Equity Method Investments"
    )
    total_pre_tax_income: Optional[float] = Field(
        default=None, description="Income Before Tax"
    )
    income_tax_expense: Optional[float] = Field(
        default=None, description="Income Tax Expense"
    )
    income_after_tax: Optional[float] = Field(
        default=None, description="Income After Tax"
    )
    consolidated_net_income: Optional[float] = Field(
        default=None, description="Net Income/Loss"
    )
    net_income_attributable_noncontrolling_interest: Optional[float] = Field(
        default=None,
        description="Net income (loss) attributable to noncontrolling interest",
    )
    net_income_attributable_to_parent: Optional[float] = Field(
        default=None, description="Net income (loss) attributable to parent"
    )
    net_income_attributable_to_common_shareholders: Optional[float] = Field(
        default=None,
        description="Net Income/Loss Available To Common Stockholders Basic",
    )
    participating_securities_earnings: Optional[float] = Field(
        default=None,
        description="Participating Securities Distributed And Undistributed Earnings Loss Basic",
    )
    undistributed_earnings_allocated_to_participating_securities: Optional[float] = (
        Field(
            default=None,
            description="Undistributed Earnings Allocated To Participating Securities",
        )
    )
    common_stock_dividends: Optional[float] = Field(
        default=None, description="Common Stock Dividends"
    )
    preferred_stock_dividends_and_other_adjustments: Optional[float] = Field(
        default=None, description="Preferred stock dividends and other adjustments"
    )
    basic_earnings_per_share: Optional[float] = Field(
        default=None, description="Earnings Per Share"
    )
    diluted_earnings_per_share: Optional[float] = Field(
        default=None, description="Diluted Earnings Per Share"
    )
    weighted_average_basic_shares_outstanding: Optional[float] = Field(
        default=None, description="Basic Average Shares"
    )
    weighted_average_diluted_shares_outstanding: Optional[float] = Field(
        default=None, description="Diluted Average Shares"
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


class PolygonIncomeStatementFetcher(
    Fetcher[
        PolygonIncomeStatementQueryParams,
        List[PolygonIncomeStatementData],
    ]
):
    """Polygon Income Statement Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonIncomeStatementQueryParams:
        """Transform the query params."""
        return PolygonIncomeStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: PolygonIncomeStatementQueryParams,
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
            query.model_dump(by_alias=True), ["ticker", "period"]
        )

        if query.symbol.isdigit():
            query_string = f"cik={query.symbol}&timeframe={period}&{query_string}"
        else:
            query_string = f"ticker={query.symbol}&timeframe={period}&{query_string}"

        request_url = f"{base_url}?{query_string}&apiKey={api_key}"

        return await get_data_many(request_url, "results", **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: PolygonIncomeStatementQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[PolygonIncomeStatementData]:
        """Return the transformed data."""
        transformed_data: List[PolygonIncomeStatementData] = []

        for item in data:
            sub_data = {
                key: value["value"]
                for key, value in item["financials"]["income_statement"].items()
            }
            sub_data["period_ending"] = item["end_date"]
            sub_data["fiscal_period"] = item["fiscal_period"]
            transformed_data.append(PolygonIncomeStatementData(**sub_data))

        return transformed_data
