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
from pydantic import alias_generators


class IntrinioIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Intrinio Income Statement Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """


class IntrinioIncomeStatementData(IncomeStatementData):
    """Intrinio Income Statement Data."""

    __alias_dict__ = {
        "research_and_development_expenses": "ResearchAndDevelopmentExpense",
        "selling_general_and_administrative_expenses": "SellingGeneralAndAdministrativeExpense",
        "ebit": "earnings before interest and taxes (ebit)",
        "ebitda": "earnings before interest, taxes, depreciation and amortization (ebitda)",
        "ebitda_margin": "ebitda margin",
        "operating_income": "OperatingIncomeLoss",
        "income_before_tax": "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",  # noqa: E501
        "eps_diluted": "EarningsPerShareDiluted",
        "weighted_average_shares_outstanding": "WeightedAverageNumberOfSharesOutstandingBasic",
        "weighted_average_shares_outstanding_dil": "WeightedAverageNumberOfDilutedSharesOutstanding",
    }


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
                field_name = alias_generators.to_snake(sub_item["data_tag"]["name"])
                sub_dict[field_name] = float(sub_item["value"])

            sub_dict["date"] = item["date"]
            sub_dict["period"] = item["period"]

            # Intrinio does not return Q4 data but FY data instead
            if query.period == "quarter" and item["period"] == "FY":
                sub_dict["period"] = "Q4"

            transformed_data.append(IntrinioIncomeStatementData(**sub_dict))

        return transformed_data
