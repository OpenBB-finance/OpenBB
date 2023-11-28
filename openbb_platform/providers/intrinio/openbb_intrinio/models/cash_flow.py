"""Intrinio Cash Flow Statement Model."""

import asyncio
from typing import Any, Dict, List, Literal, Optional

import requests
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_statements import (
    CashFlowStatementData,
    FinancialStatementsQueryParams,
)
from openbb_intrinio.utils.helpers import (
    async_get_all_fundamentals_ids,
    generate_fundamentals_url,
    intrinio_fundamentals_session,
)
from pydantic import Field


class IntrinioCashFlowStatementQueryParams(FinancialStatementsQueryParams):
    """Intrinio Cash Flow Statement Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    period: Literal["annual", "quarter", "ttm", "ytd"] = Field(default="annual")
    use_cache: Optional[bool] = Field(
        default=True,
        description="If true, use cached data. Cache expires after one day.",
    )


class IntrinioCashFlowStatementData(CashFlowStatementData):
    """Intrinio Cash Flow Statement Data."""

    __alias_dict__ = {
        "cash_and_equivalents": "cashandequivalents",
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
        "net_income": "netincome",
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
    async def extract_data(
        query: IntrinioCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "cash_flow_statement"
        if query.period in ["quarter", "annual"]:
            period_type = "FY" if query.period == "annual" else "Q"
        if query.period in ["ttm", "ytd"]:
            period_type = query.period.upper()

        data: List[Dict] = []

        fundamentals_ids = await async_get_all_fundamentals_ids(
            symbol=query.symbol,
            api_key=api_key,
            period=period_type,
            statement=statement_code,
            as_reported=False,
            use_cache=query.use_cache,
        )

        if len(fundamentals_ids) > 0:
            ids = fundamentals_ids.iloc[: query.limit]["id"].to_list()

        urls = [generate_fundamentals_url(id, api_key, as_reported=False) for id in ids]

        def fetch_data(url):
            statement_data: Dict = {}
            response = (
                requests.get(url, timeout=5)
                if query.use_cache is False
                else intrinio_fundamentals_session.get(url, timeout=5)
            )
            if response.status_code != 200:
                return {}
            statement_data = response.json()
            data.append(
                {
                    "period_ending": statement_data["fundamental"]["end_date"],
                    "fiscal_year": statement_data["fundamental"]["fiscal_year"],
                    "fiscal_period": statement_data["fundamental"]["fiscal_period"],
                    "financials": statement_data["standardized_financials"],
                }
            )
            return data

        loop = asyncio.get_running_loop()
        [await loop.run_in_executor(None, fetch_data, url) for url in urls]

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
