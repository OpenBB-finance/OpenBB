from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement import IncomeStatementData
from openbb_provider.utils.helpers import get_querystring
from pydantic import validator

from openbb_polygon.utils.helpers import get_data
from openbb_polygon.utils.types import PolygonFundamentalQueryParams


class PolygonIncomeStatementQueryParams(PolygonFundamentalQueryParams):
    """Polygon Income Statement Query Parameters"""


class PolygonIncomeStatementData(IncomeStatementData):
    class Config:
        fields = {
            "date": "start_date",
            "accepted_date": "acceptance_datetime",
            "period": "fiscal_period",
            "revenue": "revenues",
            "operating_income": "operating_income_loss",
            "income_before_tax": "income_loss_from_continuing_operations_before_tax",
            "income_tax_expense": "income_tax_expense_benefit",
            "net_income": "net_income_loss",
            "eps": "basic_earnings_per_share",
            "eps_diluted": "diluted_earnings_per_share",
            "interest_expense": "interest_expense_operating",
            "symbol": "tickers",
        }

    # tickers: Optional[List[str]]
    cik: Optional[str]
    filing_date: Optional[dateType]
    cost_of_revenue: Optional[int]
    gross_profit: Optional[int]
    operating_expenses: Optional[int]
    income_loss_from_continuing_operations_after_tax: Optional[float]
    benefits_costs_expenses: Optional[float]
    net_income_loss_attributable_to_noncontrolling_interest: Optional[int]
    net_income_loss_attributable_to_parent: Optional[float]
    net_income_loss_available_to_common_stockholders_basic: Optional[float]
    participating_securities_distributed_and_undistributed_earnings_loss_basic: Optional[
        float
    ]
    preferred_stock_dividends_and_other_adjustments: Optional[float]

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
        FIELDS = [
            "revenues",
            "cost_of_revenue",
            "gross_profit",
            "operating_expenses" "income_loss_from_continuing_operations_before_tax",
            "income_tax_expense_benefit",
            "net_income_loss",
            "basic_earnings_per_share",
            "diluted_earnings_per_share",
            "net_income_loss_attributable_to_noncontrolling_interest",
            "net_income_loss_attributable_to_parent",
            "net_income_loss_available_to_common_stockholders_basic",
            "operating_income_loss",
            "participating_securities_distributed_and_undistributed_earnings_loss_basic",
            "preferred_stock_dividends_and_other_adjustments",
            "income_loss_from_continuing_operations_after_tax",
            "benefits_costs_expenses",
            "interest_expense_operating",
        ]

        to_return = []
        for item in data:
            new = {"acceptance_datetime": item.get("acceptance_datetime")}
            new["start_date"] = item["start_date"]
            new["filing_date"] = item.get("filing_date")
            new["fiscal_period"] = item["fiscal_period"]
            new["tickers"] = item["tickers"]
            new["cik"] = item["cik"]
            incs = item["financials"].get("income_statement", {})

            if incs:
                for field in FIELDS:
                    new[field] = incs.get(field, {}).get("value", 0)

            to_return.append(PolygonIncomeStatementData(**new))
        return to_return
