"""Intrinio Balance Sheet Fetcher."""


from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_intrinio.utils.helpers import get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from pydantic import Field


class IntrinioBalanceSheetQueryParams(BalanceSheetQueryParams):
    """Intrinio Balance Sheet QueryParams.

    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_reported_financials_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    type: Literal["reported", "standardized"] = Field(
        default="reported", description="Type of the statement to be fetched."
    )
    year: Optional[int] = Field(
        description="Year of the statement to be fetched.",
    )


class IntrinioBalanceSheetData(BalanceSheetData):
    """Intrinio Balance Sheet Data."""

    class Config:
        fields = {
            "cash_and_cash_equivalents": "cash_and_equivalents",
            "marketable_securities": "short_term_investments",
            "net_receivables": "note_and_lease_receivable",
            "inventory": "inventory_net",
            "total_non_current_assets": "total_noncurrent_assets",
            "tax_payables": "other_taxes_payables",
            "deferred_revenue": "current_deferred_revenue",
            "deferred_revenue_non_current": "noncurrent_deferred_revenue",
            "deferred_tax_liabilities_non_current": "noncurrent_deferred_and_payable_income_tax_liabilities",
            "other_liabilities": "other_long_term_liabilities",
            "accumulated_other_comprehensive_income_loss": "accumulated_other_comprehensive_income_loss",
        }


class IntrinioBalanceSheetFetcher(
    Fetcher[
        IntrinioBalanceSheetQueryParams,
        List[IntrinioBalanceSheetData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioBalanceSheetQueryParams:
        """Transform the query params."""
        transform_params = params

        if not params.get("year"):
            transform_params["year"] = date.today().year - 1

        return IntrinioBalanceSheetQueryParams(**transform_params)

    @staticmethod
    def extract_data(
        query: IntrinioBalanceSheetQueryParams,
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
    def transform_data(data: List[Dict]) -> List[IntrinioBalanceSheetData]:
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
                    sub_dict[sub_item[sub_tag]["name"]] = int(
                        sub_item[sub_tag]["factor"] + str(sub_item["value"])
                    )
                except (ValueError, KeyError):
                    sub_dict[sub_item[sub_tag]["name"]] = int(sub_item["value"])

            sub_dict["date"] = item["fundamental"]["end_date"]
            sub_dict["period"] = item["fundamental"]["fiscal_period"]
            sub_dict["cik"] = item["fundamental"]["company"]["cik"]
            sub_dict["symbol"] = item["fundamental"]["company"]["ticker"]

            transformed_data.append(IntrinioBalanceSheetData(**sub_dict))

        return transformed_data
