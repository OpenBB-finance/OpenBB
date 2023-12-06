"""Intrinio Cash Flow Statement Model."""


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field


class IntrinioCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Intrinio Cash Flow Statement Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """


class IntrinioCashFlowStatementData(CashFlowStatementData):
    """Intrinio Cash Flow Statement Data."""

    __alias_dict__ = {
        "net_income": "netincome",
        "depreciation_and_amortization": "depreciationexpense",
        "other_non_cash_items": "noncashadjustmentstonetincome",
        "accounts_receivables": "IncreaseDecreaseInAccountsReceivable",
        "inventory": "IncreaseDecreaseInInventories",
        "vendor_non_trade_receivables": "IncreaseDecreaseInOtherReceivables",
        "other_current_and_non_current_assets": "IncreaseDecreaseInOtherOperatingAssets",
        "accounts_payables": "IncreaseDecreaseInAccountsPayable",
        "deferred_revenue": "IncreaseDecreaseInContractWithCustomerLiability",
        "other_current_and_non_current_liabilities": "IncreaseDecreaseInOtherOperatingLiabilities",
        "net_cash_flow_from_operating_activities": "netcashfromoperatingactivities",
        "purchases_of_marketable_securities": "purchaseofinvestments",
        "sales_from_maturities_of_investments": "saleofinvestments",
        "investments_in_property_plant_and_equipment": "purchaseofplantpropertyandequipment",
        "payments_from_acquisitions": "acquisitions",
        "other_investing_activities": "otherinvestingactivitiesnet",
        "net_cash_flow_from_investing_activities": "netcashfrominvestingactivities",
        "dividends_paid": "paymentofdividends",
        "common_stock_repurchased": "repurchaseofcommonequity",
        "debt_proceeds": "issuanceofdebt",
        "debt_repayment": "repaymentofdebt",
        "other_financing_activities": "otherfinancingactivitiesnet",
        "net_cash_flow_from_financing_activities": "netcashfromfinancingactivities",
        "net_change_in_cash": "netchangeincash",
    }

    changes_in_operating_assets_and_liabilities: Optional[float] = Field(
        None,
        alias="increasedecreaseinoperatingcapital",
        description="Changes in operating assets and liabilities.",
    )

    net_income_continuing: Optional[float] = Field(
        default=None,
        alias="netincomecontinuing",
        description="Net income from continuing operations.",
    )
    net_cash_from_continuing_operating_activities: Optional[float] = Field(
        default=None,
        alias="netcashfromcontinuingoperatingactivities",
        description="Net cash from continuing operating activities.",
    )
    net_cash_from_continuing_investing_activities: Optional[float] = Field(
        default=None,
        alias="netcashfromcontinuinginvestingactivities",
        description="Net cash from continuing investing activities.",
    )
    net_cash_from_continuing_financing_activities: Optional[float] = Field(
        default=None,
        alias="netcashfromcontinuingfinancingactivities",
        description="Net cash from continuing financing activities.",
    )
    cash_interest_paid: Optional[float] = Field(
        default=None, alias="cashinterestpaid", description="Cash paid for interest."
    )
    cash_income_taxes_paid: Optional[float] = Field(
        default=None,
        alias="cashincometaxespaid",
        description="Cash paid for income taxes.",
    )
    issuance_of_common_equity: Optional[float] = Field(
        default=None,
        alias="issuanceofcommonequity",
        description="Issuance of common equity.",
    )


class IntrinioCashFlowStatementFetcher(
    Fetcher[
        IntrinioCashFlowStatementQueryParams,
        List[IntrinioCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioCashFlowStatementQueryParams:
        """Transform the query params."""
        return IntrinioCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "cash_flow_statement"
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
        query: IntrinioCashFlowStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioCashFlowStatementData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioCashFlowStatementData] = []

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

            transformed_data.append(IntrinioCashFlowStatementData(**sub_dict))

        return transformed_data
