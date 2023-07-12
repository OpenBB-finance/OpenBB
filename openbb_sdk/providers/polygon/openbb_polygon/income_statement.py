# IMPORT STANDARD
from datetime import (
    date as dateType,
    datetime,
)
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data
from openbb_provider.model.data.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer, get_querystring

# IMPORT THIRD-PARTY
from pydantic import Field

from openbb_polygon.helpers import get_data
from openbb_polygon.types import PolygonFundamentalQueryParams


class PolygonIncomeStatementQueryParams(PolygonFundamentalQueryParams):
    __doc__ = PolygonFundamentalQueryParams.__doc__


class PolygonIncomeStatementData(Data):
    start_date: dateType = Field(alias="date")
    tickers: Optional[List[str]]
    cik: Optional[str]
    filing_date: Optional[dateType]
    acceptance_datetime: Optional[datetime] = Field(alias="accepted_date")
    fiscal_period: Optional[str] = Field(alias="period")
    revenues: Optional[float] = Field(alias="revenue")
    cost_of_revenue: Optional[float]
    gross_profit: Optional[float]
    operating_expenses: Optional[float]
    income_loss_from_continuing_operations_before_tax: Optional[float] = Field(
        alias="income_before_tax"
    )
    income_loss_from_continuing_operations_after_tax: Optional[float]
    income_tax_expense_benefit: Optional[float] = Field(alias="income_tax_expense")
    net_income_loss: Optional[float] = Field(alias="net_income")
    basic_earnings_per_share: Optional[float] = Field(alias="eps")
    diluted_earnings_per_share: Optional[float] = Field(alias="eps_diluted")
    benefits_costs_expenses: Optional[float]
    interest_expense_operating: Optional[float] = Field(alias="interest_expense")
    net_income_loss_attributable_to_noncontrolling_interest: Optional[int]
    net_income_loss_attributable_to_parent: Optional[float]
    net_income_loss_available_to_common_stockholders_basic: Optional[float]
    operating_income_loss: Optional[float]
    participating_securities_distributed_and_undistributed_earnings_loss_basic: Optional[
        float
    ]
    preferred_stock_dividends_and_other_adjustments: Optional[float]


class PolygonIncomeStatementFetcher(
    Fetcher[
        IncomeStatementQueryParams,
        IncomeStatementData,
        PolygonIncomeStatementQueryParams,
        PolygonIncomeStatementData,
    ]
):
    @staticmethod
    def transform_query(
        query: IncomeStatementQueryParams, extra_params: Optional[Dict] = None
    ) -> PolygonIncomeStatementQueryParams:
        period = "annual" if query.period == "annually" else "quarterly"
        return PolygonIncomeStatementQueryParams(
            symbol=query.symbol, period=period, **extra_params if extra_params else {}  # type: ignore
        )

    @staticmethod
    def extract_data(
        query: PolygonIncomeStatementQueryParams, api_key: str
    ) -> List[PolygonIncomeStatementData]:
        base_url = "https://api.polygon.io/vX/reference/financials"
        query_string = get_querystring(query.dict(), [])
        request_url = f"{base_url}?{query_string}&apiKey={api_key}"
        data = get_data(request_url)["results"]

        if len(data) == 0:
            raise RuntimeError("No Income Statement found")

        to_return = []
        for item in data:
            new = {"acceptance_datetime": item.get("acceptance_datetime")}
            new["start_date"] = item["start_date"]
            new["filing_date"] = item.get("filing_date")
            new["fiscal_period"] = item["fiscal_period"]
            new["tickers"] = item["tickers"]
            new["cik"] = item["cik"]
            incs = item["financials"]["income_statement"]
            new["revenues"] = incs["revenues"].get("value")
            new["cost_of_revenue"] = incs.get("cost_of_revenue", {}).get("value", 0)
            new["gross_profit"] = incs.get("gross_profit", {}).get("value", 0)
            new["operating_expenses"] = incs["operating_expenses"].get("value")
            new["income_loss_from_continuing_operations_before_tax"] = incs[
                "income_loss_from_continuing_operations_before_tax"
            ].get("value")
            new["income_tax_expense_benefit"] = incs["income_tax_expense_benefit"].get(
                "value"
            )
            new["net_income_loss"] = incs["net_income_loss"].get("value")
            new["basic_earnings_per_share"] = incs.get(
                "basic_earnings_per_share", {}
            ).get("value")
            new["diluted_earnings_per_share"] = incs.get(
                "diluted_earnings_per_share", {}
            ).get("value")
            new["net_income_loss_attributable_to_noncontrolling_interest"] = incs[
                "net_income_loss_attributable_to_noncontrolling_interest"
            ].get("value")
            new["net_income_loss_attributable_to_parent"] = incs[
                "net_income_loss_attributable_to_parent"
            ].get("value")
            new["net_income_loss_available_to_common_stockholders_basic"] = incs[
                "net_income_loss_available_to_common_stockholders_basic"
            ].get("value")
            new["operating_income_loss"] = incs["operating_income_loss"].get("value")
            new[
                "participating_securities_distributed_and_undistributed_earnings_loss_basic"
            ] = incs[
                "participating_securities_distributed_and_undistributed_earnings_loss_basic"
            ].get(
                "value"
            )
            new["preferred_stock_dividends_and_other_adjustments"] = incs[
                "preferred_stock_dividends_and_other_adjustments"
            ].get("value")
            new["income_loss_from_continuing_operations_after_tax"] = incs[
                "income_loss_from_continuing_operations_after_tax"
            ].get("value")
            new["benefits_costs_expenses"] = incs["benefits_costs_expenses"].get(
                "value"
            )
            new["interest_expense_operating"] = incs.get(
                "interest_expense_operating", {}
            ).get("value", 0)
            to_return.append(PolygonIncomeStatementData(**new))
        return to_return

    @staticmethod
    def transform_data(
        data: List[PolygonIncomeStatementData],
    ) -> List[IncomeStatementData]:
        processors = {"tickers": lambda x: "" if not x else ",".join(x)}
        return data_transformer(data, IncomeStatementData, processors)
