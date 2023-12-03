"""Intrinio Income Statement Model."""


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field


class IntrinioIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Intrinio Income Statement Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """


class IntrinioIncomeStatementData(IncomeStatementData):
    """Intrinio Income Statement Data."""

    __alias_dict__ = {
        "revenue": "totalrevenue",
        "cost_of_revenue": "totalcostofrevenue",
        "gross_profit": "totalgrossprofit",
        "research_and_development_expenses": "rdexpense",
        "selling_general_and_administrative_expenses": "sgaexpense",
        "operating_expenses": "totaloperatingexpenses",
        "operating_income": "totaloperatingincome",
        "interest_expense": "interestexpense",
        "income_before_tax": "totalpretaxincome",
        "income_tax_expense": "incometaxexpense",
        "net_income": "netincome",
        "eps": "basiceps",
        "eps_diluted": "dilutedeps",
        "weighted_average_shares_outstanding": "weightedavebasicsharesos",
        "ebit": "ebit",
        "ebitda": "ebitda",
    }
    # Intrinio-specific fields that don't have a direct mapping to the standard model
    operating_revenue: Optional[float] = Field(
        default=None, alias="operatingrevenue", description="Operating revenue."
    )
    operating_cost_of_revenue: Optional[float] = Field(
        default=None,
        alias="operatingcostofrevenue",
        description="Operating cost of revenue.",
    )
    total_other_income_expenses_net: Optional[float] = Field(
        default=None,
        alias="totalotherincome",
        description="Total other income/expenses net.",
    )
    net_income_continuing: Optional[float] = Field(
        default=None,
        alias="netincomecontinuing",
        description="Net income from continuing operations.",
    )
    net_income_to_common: Optional[float] = Field(
        default=None,
        alias="netincometocommon",
        description="Net income to common shareholders.",
    )
    weighted_average_shares_outstanding_dil: Optional[float] = Field(
        default=None,
        alias="weightedavedilutedsharesos",
        description="Weighted average diluted shares outstanding.",
    )
    cash_dividends_per_share: Optional[float] = Field(
        default=None,
        alias="cashdividendspershare",
        description="Cash dividends per share.",
    )
    ebitda_ratio: Optional[float] = Field(
        default=None, alias="ebitdamargin", description="EBITDA margin."
    )
    other_income: Optional[float] = Field(
        default=None, alias="otherincome", description="Other income."
    )
    weighted_ave_basic_diluted_shares_os: Optional[float] = Field(
        default=None,
        alias="weightedavebasicdilutedsharesos",
        description="Weighted average basic and diluted shares outstanding.",
    )


class IntrinioIncomeStatementFetcher(
    Fetcher[
        IntrinioIncomeStatementQueryParams,
        List[IntrinioIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioIncomeStatementQueryParams:
        """Transform the query params."""
        return IntrinioIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "income_statement"
        period_type = "FY" if query.period == "annual" else "QTR"
        data_tags = ["ebit", "ebitda", "ebitdamargin"]

        fundamentals_data: Dict = {}
        data: List[Dict] = []

        base_url = "https://api-v2.intrinio.com"
        fundamentals_url_params = f"statement_code={statement_code}&type={period_type}"
        fundamentals_url = (
            f"{base_url}/companies/{query.symbol}/fundamentals?"
            f"{fundamentals_url_params}&api_key={api_key}"
        )

        fundamentals_data = get_data_one(fundamentals_url, **kwargs).get(
            "fundamentals", []
        )
        fiscal_periods = [
            f"{item['fiscal_year']}-{item['fiscal_period']}"
            for item in fundamentals_data
        ]
        fiscal_periods = fiscal_periods[: query.limit]

        def get_financial_statement_data(period: str, data: List[Dict]) -> None:
            statement_data: Dict = {}
            calculations_data: List = []

            intrinio_id = f"{query.symbol}-{statement_code}-{period}"
            statement_url = f"{base_url}/fundamentals/{intrinio_id}/standardized_financials?api_key={api_key}"
            statement_data = get_data_one(statement_url, **kwargs)

            intrinio_id = f"{query.symbol}-calculations-{period}"
            calculations_url = f"{base_url}/fundamentals/{intrinio_id}/standardized_financials?api_key={api_key}"
            calculations_data = get_data_one(calculations_url, **kwargs).get(
                "standardized_financials", []
            )
            calculations_data = [
                item
                for item in calculations_data
                if item["data_tag"]["tag"] in data_tags
            ]

            data.append(
                {
                    "date": statement_data["fundamental"]["end_date"],
                    "period": statement_data["fundamental"]["fiscal_period"],
                    "financials": statement_data["standardized_financials"]
                    + calculations_data,
                }
            )

        with ThreadPoolExecutor() as executor:
            executor.map(get_financial_statement_data, fiscal_periods, repeat(data))

        return data

    @staticmethod
    def transform_data(
        query: IntrinioIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioIncomeStatementData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioIncomeStatementData] = []

        for item in data:
            sub_dict: Dict[str, Any] = {}

            for sub_item in item["financials"]:
                field_name = sub_item["data_tag"]["tag"]
                sub_dict[field_name] = float(sub_item["value"])

            sub_dict["date"] = item["date"]
            sub_dict["period"] = item["period"]

            # Intrinio does not return Q4 data but FY data instead
            if query.period == "quarter" and item["period"] == "FY":
                sub_dict["period"] = "Q4"

            transformed_data.append(IntrinioIncomeStatementData(**sub_dict))

        return transformed_data
