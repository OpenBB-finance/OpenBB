"""Intrinio Balance Sheet Model."""


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field


class IntrinioBalanceSheetQueryParams(BalanceSheetQueryParams):
    """Intrinio Balance Sheet Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """


class IntrinioBalanceSheetData(BalanceSheetData):
    """Intrinio Balance Sheet Data."""

    __alias_dict__ = {
        "cash_and_cash_equivalents": "cashandequivalents",
        "short_term_investments": "shortterminvestments",
        "accounts_receivable": "accountsreceivable",
        "net_inventory": "netinventory",
        "other_current_assets": "othercurrentassets",
        "total_current_assets": "totalcurrentassets",
        "long_term_investments": "longterminvestments",
        "other_noncurrent_assets": "othernoncurrentassets",
        "total_assets": "totalassets",
        "short_term_debt": "shorttermdebt",
        "accounts_payable": "accountspayable",
        "other_current_liabilities": "othercurrentliabilities",
        "total_current_liabilities": "totalcurrentliabilities",
        "long_term_debt": "longtermdebt",
        "total_liabilities": "totalliabilities",
        "common_stock": "commonequity",
        "retained_earnings": "retainedearnings",
        "total_equity": "totalequity",
    }
    note_receivable: Optional[float] = Field(
        default=None, alias="notereceivable", description="Notes and lease receivable."
    )
    net_ppe: Optional[float] = Field(
        default=None, alias="netppe", description="Plant, property, and equipment, net."
    )
    total_noncurrent_assets: Optional[float] = Field(
        default=None,
        alias="totalnoncurrentassets",
        description="Total noncurrent assets.",
    )
    current_deferred_revenue: Optional[float] = Field(
        default=None,
        alias="currentdeferredrevenue",
        description="Current deferred revenue.",
    )
    other_noncurrent_liabilities: Optional[float] = Field(
        default=None,
        alias="othernoncurrentliabilities",
        description="Other noncurrent operating liabilities.",
    )
    total_noncurrent_liabilities: Optional[float] = Field(
        default=None,
        alias="totalnoncurrentliabilities",
        description="Total noncurrent liabilities.",
    )
    commitments_and_contingencies: Optional[float] = Field(
        default=None,
        alias="commitmentsandcontingencies",
        description="Commitments and contingencies.",
    )
    aoci: Optional[float] = Field(
        default=None,
        alias="aoci",
        description="Accumulated other comprehensive income / (loss).",
    )
    total_common_equity: Optional[float] = Field(
        default=None, alias="totalcommonequity", description="Total common equity."
    )
    total_equity_and_noncontrolling_interests: Optional[float] = Field(
        default=None,
        alias="totalequityandnoncontrollinginterests",
        description="Total equity & noncontrolling interests.",
    )
    total_liabilities_and_equity: Optional[float] = Field(
        default=None,
        alias="totalliabilitiesandequity",
        description="Total liabilities & shareholders' equity.",
    )


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
        return IntrinioBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "balance_sheet_statement"
        period_type = "FY" if query.period == "annual" else "QTR"

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

            intrinio_id = f"{query.symbol}-{statement_code}-{period}"
            statement_url = f"{base_url}/fundamentals/{intrinio_id}/standardized_financials?api_key={api_key}"
            statement_data = get_data_one(statement_url, **kwargs)

            data.append(
                {
                    "date": statement_data["fundamental"]["end_date"],
                    "period": statement_data["fundamental"]["fiscal_period"],
                    "financials": statement_data["standardized_financials"],
                }
            )

        with ThreadPoolExecutor() as executor:
            executor.map(get_financial_statement_data, fiscal_periods, repeat(data))

        return data

    @staticmethod
    def transform_data(
        query: IntrinioBalanceSheetQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioBalanceSheetData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioBalanceSheetData] = []

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

            transformed_data.append(IntrinioBalanceSheetData(**sub_dict))

        return transformed_data
