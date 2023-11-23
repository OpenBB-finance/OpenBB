"""Intrinio Balance Sheet Model."""


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_statements import (
    BalanceSheetData,
    FinancialStatementsQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one


class IntrinioBalanceSheetQueryParams(FinancialStatementsQueryParams):
    """Intrinio Balance Sheet Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """


class IntrinioBalanceSheetData(BalanceSheetData):
    """Intrinio Balance Sheet Data."""

    __alias_dict__ = {
        "cash_and_equivalents": "cashandequivalents",
        "restricted_cash": "restrictedcash",
        "short_term_investments": "shortterminvestments",
        "federal_funds_sold": "fedfundssold",
        "note_and_lease_receivable": "notereceivable",
        "interest_bearing_deposits_at_other_banks": "interestbearingdepositsatotherbanks",
        "accounts_receivable": "accountsreceivable",
        "time_deposits_placed_and_other_short_term_investments": "timedepositsplaced",
        "inventories_net": "netinventory",
        "trading_account_securities": "tradingaccountsecurities",
        "prepaid_expenses": "prepaidexpenses",
        "loans_and_leases": "loansandleases",
        "allowance_for_loan_and_lease_losses": "allowanceforloanandleaselosses",
        "current_deferred_refundable_income_taxes": "currentdeferredtaxassets",
        "other_current_assets": "othercurrentassets",
        "loans_and_leases_net_of_allowance": "netloansandleases",
        "other_current_nonoperating_assets": "othercurrentnonoperatingassets",
        "loans_held_for_sale": "loansheldforsale",
        "total_current_assets": "totalcurrentassets",
        "accrued_investment_income": "accruedinvestmentincome",
        "plant_property_equipment_gross": "grossppe",
        "customer_and_other_receivables": "customerandotherreceivables",
        "accumulated_depreciation": "accumulateddepreciation",
        "premises_and_equipment_net": "netpremisesandequipment",
        "plant_property_equipment_net": "netppe",
        "mortgage_servicing_rights": "mortgageservicingrights",
        "long_term_investments": "longterminvestments",
        "unearned_premiums_asset": "unearnedpremiumsdebit",
        "noncurrent_note_lease_receivables": "noncurrentnotereceivables",
        "deferred_acquisition_cost": "deferredacquisitioncost",
        "goodwill": "goodwill",
        "separate_account_business_assets": "separateaccountbusinessassets",
        "intangible_assets": "intangibleassets",
        "noncurrent_deferred_refundable_income_taxes": "noncurrentdeferredtaxassets",
        "employee_benefit_assets": "employeebenefitassets",
        "other_assets": "otherassets",
        "other_noncurrent_operating_assets": "othernoncurrentassets",
        "total_assets": "totalassets",
        "other_noncurrent_nonoperating_assets": "othernoncurrentnonoperatingassets",
        "non_interest_bearing_deposits": "noninterestbearingdeposits",
        "interest_bearing_deposits": "interestbearingdeposits",
        "total_noncurrent_assets": "totalnoncurrentassets",
        "federal_funds_purchased_and_securities_sold": "fedfundspurchased",
        "short_term_debt": "shorttermdebt",
        "bankers_acceptance_out_standing": "bankersacceptances",
        "accrued_interest_payable": "accruedinterestpayable",
        "accounts_payable": "accountspayable",
        "accrued_expenses": "accruedexpenses",
        "other_short_term_payables": "othershorttermpayables",
        "long_term_debt": "longtermdebt",
        "customer_deposits": "customerdeposits",
        "capital_lease_obligations": "capitalleaseobligations",
        "dividends_payable": "dividendspayable",
        "claims_and_claim_expense": "claimsandclaimexpenses",
        "current_deferred_revenue": "currentdeferredrevenue",
        "future_policy_benefits": "futurepolicybenefits",
        "current_deferred_payable_income_tax_liabilities": "currentdeferredtaxliabilities",
        "current_employee_benefit_liabilities": "currentemployeebenefitliabilities",
        "unearned_premiums_liability": "unearnedpremiumscredit",
        "other_taxes_payable": "othertaxespayable",
        "policy_holder_funds": "policyholderfunds",
        "other_current_liabilities": "othercurrentliabilities",
        "participating_policy_holder_equity": "participatingpolicyholderequity",
        "other_current_nonoperating_liabilities": "othercurrentnonoperatingliabilities",
        "separate_account_business_liabilities": "separateaccountbusinessliabilities",
        "total_current_liabilities": "totalcurrentliabilities",
        "other_long_term_liabilities": "otherlongtermliabilities",
        "total_liabilities": "totalliabilities",
        "commitments_contingencies": "commitmentsandcontingencies",
        "asset_retirement_reserve_litigation_obligation": "assetretirementandlitigationobligation",
        "redeemable_noncontrolling_interest": "redeemablenoncontrollinginterest",
        "noncurrent_deferred_revenue": "noncurrentdeferredrevenue",
        "preferred_stock": "totalpreferredequity",
        "common_stock": "commonequity",
        "noncurrent_deferred_payable_income_tax_liabilities": "noncurrentdeferredtaxliabilities",
        "noncurrent_employee_benefit_liabilities": "noncurrentemployeebenefitliabilities",
        "retained_earnings": "retainedearnings",
        "other_noncurrent_operating_liabilities": "othernoncurrentliabilities",
        "treasury_stock": "treasurystock",
        "accumulated_other_comprehensive_income": "aoci",
        "other_noncurrent_nonoperating_liabilities": "othernoncurrentnonoperatingliabilities",
        "other_equity_adjustments": "otherequity",
        "total_noncurrent_liabilities": "totalnoncurrentliabilities",
        "total_common_equity": "totalcommonequity",
        "total_preferred_common_equity": "totalequity",
        "noncontrolling_interest": "noncontrollinginterests",
        "total_equity_noncontrolling_interests": "totalequityandnoncontrollinginterests",
        "total_liabilities_shareholders_equity": "totalliabilitiesandequity"
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
        query: IntrinioBalanceSheetQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioBalanceSheetData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioBalanceSheetData] = []

        for item in data:
            sub_dict: Dict[str, Any] = {}

            for sub_item in item["financials"]:
                field_name = sub_item["data_tag"]["tag"]
                sub_dict[field_name] = float(sub_item["value"])

            sub_dict["period_ending"] = item["period_ending"]
            sub_dict["fiscal_year"] = item["fiscal_year"]
            sub_dict["fiscal_period"] = item["fiscal_period"]

            # Intrinio does not return Q4 data but FY data instead
            if query.period == "quarter" and item["fiscal_period"] == "FY":
                sub_dict["fiscal_period"] = "Q4"

            transformed_data.append(IntrinioBalanceSheetData(**sub_dict))

        return transformed_data
