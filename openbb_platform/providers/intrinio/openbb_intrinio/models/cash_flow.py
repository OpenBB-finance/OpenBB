"""Intrinio Cash Flow Statement Model."""


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_statements import (
    CashFlowStatementData,
    FinancialStatementsQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one


class IntrinioCashFlowStatementQueryParams(FinancialStatementsQueryParams):
    """Intrinio Cash Flow Statement Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """


class IntrinioCashFlowStatementData(CashFlowStatementData):
    """Intrinio Cash Flow Statement Data."""

    __alias_dict__ = {
        "acquisitions": "acquisitions",
        "amortization_expense": "amortizationexpense",
        "cash_income_taxes_paid": "cashincometaxespaid",
        "cash_interest_paid": "cashinterestpaid",
        "cash_interest_received": "cashinterestreceived",
        "depreciation_expense": "depreciationexpense",
        "divestitures": "divestitures",
        "effect_of_exchange_rate_changes": "effectofexchangeratechanges",
        "changes_in_operating_assets_and_liabilities": "increasedecreaseinoperatingcapital",
        "issuance_of_common_equity": "issuanceofcommonequity",
        "issuance_of_debt": "issuanceofdebt",
        "issuance_of_preferred_equity": "issuanceofpreferredequity",
        "loans_held_for_sale": "loansheldforsalenet",
        "net_cash_from_continuing_financing_activities": "netcashfromcontinuingfinancingactivities",
        "net_cash_from_continuing_investing_activities": "netcashfromcontinuinginvestingactivities",
        "net_cash_from_continuing_operating_activities": "netcashfromcontinuingoperatingactivities",
        "net_cash_from_discontinued_financing_activities": "netcashfromdiscontinuedfinancingactivities",
        "net_cash_from_discontinued_investing_activities": "netcashfromdiscontinuedinvestingactivities",
        "net_cash_from_discontinued_operating_activities": "netcashfromdiscontinuedoperatingactivities",
        "net_cash_from_financing_activities": "netcashfromfinancingactivities",
        "net_cash_from_investing_activities": "netcashfrominvestingactivities",
        "net_cash_from_operating_activities": "netcashfromoperatingactivities",
        "net_change_in_cash_and_equivalents": "netchangeincash",
        "net_change_in_deposits": "netchangeindeposits",
        "consolidated_net_income": "netincome",
        "net_income_continuing_operations": "netincomecontinuing",
        "net_income_discontinued_operations": "netincomediscontinued",
        "net_increase_in_fed_funds_sold": "netincreaseinfedfundssold",
        "non_cash_adjustments_to_reconcile_net_income": "noncashadjustmentstonetincome",
        "other_financing_activities": "otherfinancingactivitiesnet",
        "other_investing_activities": "otherinvestingactivitiesnet",
        "other_net_changes_in_cash": "othernetchangesincash",
        "payment_of_dividends": "paymentofdividends",
        "provision_for_loan_losses": "provisionforloanlosses",
        "purchase_of_investments": "purchaseofinvestments",
        "purchase_of_investment_securities": "purchaseofinvestments",
        "purchase_of_property_plant_and_equipment": "purchaseofplantpropertyandequipment",
        "repayment_of_debt": "repaymentofdebt",
        "repurchase_of_common_equity": "repurchaseofcommonequity",
        "repurchase_of_preferred_equity": "repurchaseofpreferredequity",
        "sale_and_maturity_of_investments": "saleofinvestments",
        "sale_of_property_plant_and_equipment": "saleofplantpropertyandequipment",
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
                    "period_ending": statement_data["fundamental"]["end_date"],
                    "fiscal_year": statement_data["fundamental"]["fiscal_year"],
                    "fiscal_period": statement_data["fundamental"]["fiscal_period"],
                    "financials": statement_data["standardized_financials"],
                }
            )

        with ThreadPoolExecutor() as executor:
            executor.map(get_financial_statement_data, fiscal_periods, repeat(data))

        return sorted(data, key=lambda x: x["period_ending"], reverse=True)

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

            sub_dict["period_ending"] = item["period_ending"]
            sub_dict["fiscal_year"] = item["fiscal_year"]
            sub_dict["fiscal_period"] = item["fiscal_period"]

            transformed_data.append(IntrinioCashFlowStatementData(**sub_dict))

        return transformed_data
