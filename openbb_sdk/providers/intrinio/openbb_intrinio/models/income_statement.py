"""Intrinio Income Statement Fetcher."""


from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_intrinio.utils.helpers import get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field


class IntrinioIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Intrinio Income Statement QueryParams.

    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_reported_financials_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    type: Literal["reported", "standardized"] = Field(
        default="reported", description="Type of the statement to be fetched."
    )
    year: Optional[int] = Field(
        description="Year of the statement to be fetched.",
    )


class IntrinioIncomeStatementData(IncomeStatementData):
    """Intrinio Income Statement Data."""

    class Config:
        fields = {
            "research_and_development_expenses": "ResearchAndDevelopmentExpense",
            "selling_general_and_administrative_expenses": "SellingGeneralAndAdministrativeExpense",
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
        transform_params = params

        if not params.get("year"):
            transform_params["year"] = date.today().year - 1

        return IntrinioIncomeStatementQueryParams(**transform_params)

    @staticmethod
    def extract_data(
        query: IntrinioIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        url_params = f"{query.symbol}-balance_sheet_statement-{query.year}"
        statement_param = f"{query.type}_financials"

        data = []

        if query.period == "annual":
            url = f"{base_url}/fundamentals/{url_params}-FY/{statement_param}?api_key={api_key}"
            data.append(get_data_one(url, **kwargs))

        elif query.period == "quarter":
            # TODO: Fix quarter range after Intrinio's response
            for quarter in range(1, 4):
                url = f"{base_url}/fundamentals/{url_params}-Q{quarter}/{statement_param}?api_key={api_key}"
                data.append(get_data_one(url, **kwargs))

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioIncomeStatementData]:
        """Return the transformed data."""

        transformed_data = []

        for item in data:
            sub_dict = {}

            if "reported_financials" in item:
                key = "reported_financials"
                sub_tag = "xbrl_tag"
            elif "standardized_financials" in item:
                key = "standardized_financials"
                sub_tag = "data_tag"

            for sub_item in item[key]:
                try:
                    sub_dict[sub_item[sub_tag]["tag"]] = int(
                        sub_item[sub_tag]["factor"] + str(sub_item["value"])
                    )
                except (ValueError, KeyError):
                    sub_dict[sub_item[sub_tag]["tag"]] = int(sub_item["value"])

            sub_dict["date"] = item["fundamental"]["end_date"]
            sub_dict["period"] = item["fundamental"]["fiscal_period"]
            sub_dict["cik"] = item["fundamental"]["company"]["cik"]
            sub_dict["symbol"] = item["fundamental"]["company"]["ticker"]

            transformed_data.append(IntrinioIncomeStatementData(**sub_dict))

        return transformed_data
