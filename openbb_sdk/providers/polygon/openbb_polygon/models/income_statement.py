from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement import IncomeStatementData
from openbb_provider.utils.helpers import get_querystring
from pydantic import Field, validator

from openbb_polygon.utils.helpers import get_data
from openbb_polygon.utils.types import PolygonFundamentalQueryParams


class PolygonIncomeStatementQueryParams(PolygonFundamentalQueryParams):
    """Polygon Income Statement Query Parameters"""


class PolygonIncomeStatementData(IncomeStatementData):
    class Config:
        fields = {
            "revenue": "Revenues",
            "cost_of_revenue": "Cost Of Revenue",
            "gross_profit": "Gross Profit",
            "cost_and_expenses": "Costs And Expenses",
            "operating_expenses": "Operating Expenses",
            "operating_income": "Operating Income/Loss",
            "interest_expense": "Interest Expense, Operating",
            "income_tax_expense": "Income Tax Expense/Benefit",
            "net_income": "Net Income/Loss",
            "eps": "Basic Earnings Per Share",
            "eps_diluted": "Diluted Earnings Per Share",
        }

    income_loss_from_continuing_operations_before_tax: Optional[float] = Field(
        description="Income/Loss From Continuing Operations After Tax"
    )
    income_loss_from_continuing_operations_after_tax: Optional[float] = Field(
        description="Income/Loss From Continuing Operations After Tax"
    )
    benefits_costs_expenses: Optional[float] = Field(
        description="Benefits, Costs And Expenses"
    )
    net_income_loss_attributable_to_noncontrolling_interest: Optional[float] = Field(
        description="Net Income/Loss Attributable To Noncontrolling Interest"
    )
    net_income_loss_attributable_to_parent: Optional[float] = Field(
        description="Net Income/Loss Attributable To Parent"
    )
    income_tax_expense_benefit_deferred: Optional[float] = Field(
        description="Income Tax Expense/Benefit Deferred"
    )
    participating_securities_distributed_and_undistributed_earnings_loss_basic: Optional[
        float
    ] = Field(
        description="Participating Securities Distributed And Undistributed Earnings Loss Basic"
    )
    net_income_loss_available_to_common_stockholders_basic: Optional[float] = Field(
        description="Net Income/Loss Available To Common Stockholders Basic"
    )
    nonoperating_income_loss: Optional[float] = Field(
        description="Nonoperating Income Loss"
    )
    preferred_stock_dividends_and_other_adjustments: Optional[float] = Field(
        description="Preferred Stock Dividends And Other Adjustments"
    )

    @validator("symbol", pre=True, check_fields=False)
    def symbol_from_tickers(cls, v):  # pylint: disable=E0213
        if isinstance(v, list):
            return ",".join(v)
        return v


class PolygonIncomeStatementFetcher(
    Fetcher[
        PolygonIncomeStatementQueryParams,
        List[PolygonIncomeStatementData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> PolygonIncomeStatementQueryParams:
        return PolygonIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: PolygonIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        api_key = credentials.get("polygon_api_key") if credentials else ""

        base_url = "https://api.polygon.io/vX/reference/financials"
        query_string = get_querystring(query.dict(by_alias=True), [])
        request_url = f"{base_url}?{query_string}&apiKey={api_key}"
        data = get_data(request_url, **kwargs)["results"]

        if len(data) == 0:
            raise RuntimeError("No Income Statement found")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[PolygonIncomeStatementData]:
        transformed_data = []

        for item in data:
            sub_data = {
                key: value["value"]
                for key, value in item["financials"]["income_statement"].items()
            }
            sub_data["date"] = item["start_date"]
            sub_data["cik"] = item["cik"]
            sub_data["symbol"] = item["tickers"]
            sub_data["period"] = item["fiscal_period"]
            transformed_data.append(PolygonIncomeStatementData(**sub_data))

        return transformed_data
