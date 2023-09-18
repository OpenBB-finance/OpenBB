"""Intrinio Cash Flow Statement Fetcher."""


from datetime import date
from typing import Any, Dict, List, Literal, Optional

from openbb_intrinio.utils.helpers import get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from pydantic import Field


class IntrinioCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Intrinio Cash Flow Statement QueryParams.

    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_reported_financials_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    type: Literal["reported", "standardized"] = Field(
        default="reported", description="Type of the statement to be fetched."
    )
    year: Optional[int] = Field(
        description="Year of the statement to be fetched.",
    )


class IntrinioCashFlowStatementData(CashFlowStatementData):
    """Intrinio Cash Flow Statement Data."""

    class Config:
        fields = {
            "net_income": "NetIncomeLoss",
            "depreciation_and_amortization": "DepreciationDepletionAndAmortization",
            "stock_based_compensation": "ShareBasedCompensation",
            "deferred_income_tax": "DeferredIncomeTaxExpenseBenefit",
            "other_non_cash_items": "OtherNoncashIncomeExpense",
            "accounts_receivables": "IncreaseDecreaseInAccountsReceivable",
            "inventory": "IncreaseDecreaseInInventories",
            "vendor_non_trade_receivables": "IncreaseDecreaseInOtherReceivables",
            "other_current_and_non_current_assets": "IncreaseDecreaseInOtherOperatingAssets",
            "accounts_payables": "IncreaseDecreaseInAccountsPayable",
            "deferred_revenue": "IncreaseDecreaseInContractWithCustomerLiability",
            "other_current_and_non_current_liabilities": "IncreaseDecreaseInOtherOperatingLiabilities",
            "net_cash_flow_from_operating_activities": "NetCashProvidedByUsedInOperatingActivities",
            "purchases_of_marketable_securities": "PaymentsToAcquireAvailableForSaleSecuritiesDebt",
            "sales_from_maturities_of_investments": "ProceedsFromSaleOfAvailableForSaleSecuritiesDebt",
            "investments_in_property_plant_and_equipment": "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities",  # noqa: E501
            "payments_from_acquisitions": "PaymentsToAcquireBusinessesNetOfCashAcquired",
            "other_investing_activities": "PaymentsForProceedsFromOtherInvestingActivities",
            "net_cash_flow_from_investing_activities": "NetCashProvidedByUsedInInvestingActivities",
            "taxes_paid_on_net_share_settlement": "PaymentsRelatedToTaxWithholdingForShareBasedCompensation",
            "dividends_paid": "PaymentsOfDividends",
            "common_stock_repurchased": "PaymentsForRepurchaseOfCommonStock",
            "debt_proceeds": "ProceedsFromIssuanceOfLongTermDebt",
            "debt_repayment": "RepaymentsOfLongTermDebt",
            "other_financing_activities": "ProceedsFromPaymentsForOtherFinancingActivities",
            "net_cash_flow_from_financing_activities": "NetCashProvidedByUsedInFinancingActivities",
            "net_change_in_cash": "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",  # noqa: E501
        }


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
        transform_params = params

        if not params.get("year"):
            transform_params["year"] = date.today().year - 1

        return IntrinioCashFlowStatementQueryParams(**transform_params)

    @staticmethod
    def extract_data(
        query: IntrinioCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        url_params = f"{query.symbol}-cash_flow_statement-{query.year}"
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
    def transform_data(data: List[Dict]) -> List[IntrinioCashFlowStatementData]:
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

            transformed_data.append(IntrinioCashFlowStatementData(**sub_dict))

        return transformed_data
