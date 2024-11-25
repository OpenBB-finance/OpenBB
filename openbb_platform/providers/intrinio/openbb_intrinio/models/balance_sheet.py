"""Intrinio Balance Sheet Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import ClientResponse, amake_requests
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field, field_validator, model_validator


class IntrinioBalanceSheetQueryParams(BalanceSheetQueryParams):
    """Intrinio Balance Sheet Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    fiscal_year: Optional[int] = Field(
        default=None,
        description="The specific fiscal year.  Reports do not go beyond 2008.",
    )

    @field_validator("symbol", mode="after", check_fields=False)
    @classmethod
    def handle_symbol(cls, v) -> str:
        """Handle symbols with a dash and replace it with a dot for Intrinio."""
        return v.replace("-", ".")


class IntrinioBalanceSheetData(BalanceSheetData):
    """Intrinio Balance Sheet Data."""

    __alias_dict__ = {
        "cash_and_cash_equivalents": "cashandequivalents",
        "restricted_cash": "restrictedcash",
        "short_term_investments": "shortterminvestments",
        "federal_funds_sold": "fedfundssold",
        "note_and_lease_receivable": "notereceivable",
        "interest_bearing_deposits_at_other_banks": "interestbearingdepositsatotherbanks",
        "accounts_receivable": "accountsreceivable",
        "time_deposits_placed_and_other_short_term_investments": "timedepositsplaced",
        "inventories": "netinventory",
        "trading_account_securities": "tradingaccountsecurities",
        "prepaid_expenses": "prepaidexpenses",
        "loans_and_leases": "loansandleases",
        "allowance_for_loan_and_lease_losses": "allowanceforloanandleaselosses",
        "current_deferred_refundable_income_taxes": "currentdeferredtaxassets",
        "other_current_assets": "othercurrentassets",
        "loans_and_leases_net_of_allowance": "netloansandleases",
        "other_current_non_operating_assets": "othercurrentnonoperatingassets",
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
        "non_current_note_lease_receivables": "noncurrentnotereceivables",
        "deferred_acquisition_cost": "deferredacquisitioncost",
        "goodwill": "goodwill",
        "separate_account_business_assets": "separateaccountbusinessassets",
        "intangible_assets": "intangibleassets",
        "non_current_deferred_refundable_income_taxes": "noncurrentdeferredtaxassets",
        "employee_benefit_assets": "employeebenefitassets",
        "other_assets": "otherassets",
        "other_non_current_operating_assets": "othernoncurrentassets",
        "total_assets": "totalassets",
        "other_non_current_non_operating_assets": "othernoncurrentnonoperatingassets",
        "non_interest_bearing_deposits": "noninterestbearingdeposits",
        "interest_bearing_deposits": "interestbearingdeposits",
        "total_non_current_assets": "totalnoncurrentassets",
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
        "other_current_non_operating_liabilities": "othercurrentnonoperatingliabilities",
        "separate_account_business_liabilities": "separateaccountbusinessliabilities",
        "total_current_liabilities": "totalcurrentliabilities",
        "other_long_term_liabilities": "otherlongtermliabilities",
        "total_liabilities": "totalliabilities",
        "commitments_contingencies": "commitmentsandcontingencies",
        "asset_retirement_reserve_litigation_obligation": "assetretirementandlitigationobligation",
        "redeemable_non_controlling_interest": "redeemablenoncontrollinginterest",
        "non_current_deferred_revenue": "noncurrentdeferredrevenue",
        "preferred_stock": "totalpreferredequity",
        "common_stock": "commonequity",
        "non_current_deferred_payable_income_tax_liabilities": "noncurrentdeferredtaxliabilities",
        "non_current_employee_benefit_liabilities": "noncurrentemployeebenefitliabilities",
        "retained_earnings": "retainedearnings",
        "other_non_current_operating_liabilities": "othernoncurrentliabilities",
        "treasury_stock": "treasurystock",
        "accumulated_other_comprehensive_income": "aoci",
        "other_non_current_non_operating_liabilities": "othernoncurrentnonoperatingliabilities",
        "other_equity_adjustments": "otherequity",
        "total_non_current_liabilities": "totalnoncurrentliabilities",
        "total_common_equity": "totalcommonequity",
        "total_preferred_common_equity": "totalequity",
        "non_controlling_interest": "noncontrollinginterests",
        "total_equity_non_controlling_interests": "totalequityandnoncontrollinginterests",
        "total_liabilities_shareholders_equity": "totalliabilitiesandequity",
    }
    reported_currency: Optional[str] = Field(
        description="The currency in which the balance sheet is reported.",
        default=None,
    )
    cash_and_cash_equivalents: Optional[float] = Field(
        description="Cash and cash equivalents.", default=None
    )
    cash_and_due_from_banks: Optional[float] = Field(
        description="Cash and due from banks.", default=None
    )
    restricted_cash: Optional[float] = Field(
        description="Restricted cash.", default=None
    )
    short_term_investments: Optional[float] = Field(
        description="Short term investments.", default=None
    )
    federal_funds_sold: Optional[float] = Field(
        description="Federal funds sold.", default=None
    )
    accounts_receivable: Optional[float] = Field(
        description="Accounts receivable.", default=None
    )
    note_and_lease_receivable: Optional[float] = Field(
        description="Note and lease receivable. (Vendor non-trade receivables)",
        default=None,
    )
    inventories: Optional[float] = Field(description="Net Inventories.", default=None)
    customer_and_other_receivables: Optional[float] = Field(
        description="Customer and other receivables.", default=None
    )
    interest_bearing_deposits_at_other_banks: Optional[float] = Field(
        description="Interest bearing deposits at other banks.", default=None
    )
    time_deposits_placed_and_other_short_term_investments: Optional[float] = Field(
        description="Time deposits placed and other short term investments.",
        default=None,
    )
    trading_account_securities: Optional[float] = Field(
        description="Trading account securities.", default=None
    )
    loans_and_leases: Optional[float] = Field(
        description="Loans and leases.", default=None
    )
    allowance_for_loan_and_lease_losses: Optional[float] = Field(
        description="Allowance for loan and lease losses.", default=None
    )
    current_deferred_refundable_income_taxes: Optional[float] = Field(
        description="Current deferred refundable income taxes.", default=None
    )
    other_current_assets: Optional[float] = Field(
        description="Other current assets.", default=None
    )
    loans_and_leases_net_of_allowance: Optional[float] = Field(
        description="Loans and leases net of allowance.", default=None
    )
    accrued_investment_income: Optional[float] = Field(
        description="Accrued investment income.", default=None
    )
    other_current_non_operating_assets: Optional[float] = Field(
        description="Other current non-operating assets.", default=None
    )
    loans_held_for_sale: Optional[float] = Field(
        description="Loans held for sale.", default=None
    )
    prepaid_expenses: Optional[float] = Field(
        description="Prepaid expenses.", default=None
    )
    total_current_assets: Optional[float] = Field(
        description="Total current assets.", default=None
    )
    plant_property_equipment_gross: Optional[float] = Field(
        description="Plant property equipment gross.", default=None
    )
    accumulated_depreciation: Optional[float] = Field(
        description="Accumulated depreciation.", default=None
    )
    premises_and_equipment_net: Optional[float] = Field(
        description="Net premises and equipment.", default=None
    )
    plant_property_equipment_net: Optional[float] = Field(
        description="Net plant property equipment.", default=None
    )
    long_term_investments: Optional[float] = Field(
        description="Long term investments.", default=None
    )
    mortgage_servicing_rights: Optional[float] = Field(
        description="Mortgage servicing rights.", default=None
    )
    unearned_premiums_asset: Optional[float] = Field(
        description="Unearned premiums asset.", default=None
    )
    non_current_note_lease_receivables: Optional[float] = Field(
        description="Non-current note lease receivables.", default=None
    )
    deferred_acquisition_cost: Optional[float] = Field(
        description="Deferred acquisition cost.", default=None
    )
    goodwill: Optional[float] = Field(description="Goodwill.", default=None)
    separate_account_business_assets: Optional[float] = Field(
        description="Separate account business assets.", default=None
    )
    non_current_deferred_refundable_income_taxes: Optional[float] = Field(
        description="Noncurrent deferred refundable income taxes.", default=None
    )
    intangible_assets: Optional[float] = Field(
        description="Intangible assets.", default=None
    )
    employee_benefit_assets: Optional[float] = Field(
        description="Employee benefit assets.", default=None
    )
    other_assets: Optional[float] = Field(description="Other assets.", default=None)
    other_non_current_operating_assets: Optional[float] = Field(
        description="Other noncurrent operating assets.", default=None
    )
    other_non_current_non_operating_assets: Optional[float] = Field(
        description="Other noncurrent non-operating assets.", default=None
    )
    interest_bearing_deposits: Optional[float] = Field(
        description="Interest bearing deposits.", default=None
    )
    total_non_current_assets: Optional[float] = Field(
        description="Total noncurrent assets.", default=None
    )
    total_assets: Optional[float] = Field(description="Total assets.", default=None)
    non_interest_bearing_deposits: Optional[float] = Field(
        description="Non interest bearing deposits.", default=None
    )
    federal_funds_purchased_and_securities_sold: Optional[float] = Field(
        description="Federal funds purchased and securities sold.", default=None
    )
    bankers_acceptance_outstanding: Optional[float] = Field(
        description="Bankers acceptance outstanding.", default=None
    )
    short_term_debt: Optional[float] = Field(
        description="Short term debt.", default=None
    )
    accounts_payable: Optional[float] = Field(
        description="Accounts payable.", default=None
    )
    current_deferred_revenue: Optional[float] = Field(
        description="Current deferred revenue.", default=None
    )
    current_deferred_payable_income_tax_liabilities: Optional[float] = Field(
        description="Current deferred payable income tax liabilities.", default=None
    )
    accrued_interest_payable: Optional[float] = Field(
        description="Accrued interest payable.", default=None
    )
    accrued_expenses: Optional[float] = Field(
        description="Accrued expenses.", default=None
    )
    other_short_term_payables: Optional[float] = Field(
        description="Other short term payables.", default=None
    )
    customer_deposits: Optional[float] = Field(
        description="Customer deposits.", default=None
    )
    dividends_payable: Optional[float] = Field(
        description="Dividends payable.", default=None
    )
    claims_and_claim_expense: Optional[float] = Field(
        description="Claims and claim expense.", default=None
    )
    future_policy_benefits: Optional[float] = Field(
        description="Future policy benefits.", default=None
    )
    current_employee_benefit_liabilities: Optional[float] = Field(
        description="Current employee benefit liabilities.", default=None
    )
    unearned_premiums_liability: Optional[float] = Field(
        description="Unearned premiums liability.", default=None
    )
    other_taxes_payable: Optional[float] = Field(
        description="Other taxes payable.", default=None
    )
    policy_holder_funds: Optional[float] = Field(
        description="Policy holder funds.", default=None
    )
    other_current_liabilities: Optional[float] = Field(
        description="Other current liabilities.", default=None
    )
    other_current_non_operating_liabilities: Optional[float] = Field(
        description="Other current non-operating liabilities.", default=None
    )
    separate_account_business_liabilities: Optional[float] = Field(
        description="Separate account business liabilities.", default=None
    )
    total_current_liabilities: Optional[float] = Field(
        description="Total current liabilities.", default=None
    )
    long_term_debt: Optional[float] = Field(description="Long term debt.", default=None)
    other_long_term_liabilities: Optional[float] = Field(
        description="Other long term liabilities.", default=None
    )
    non_current_deferred_revenue: Optional[float] = Field(
        description="Non-current deferred revenue.", default=None
    )
    non_current_deferred_payable_income_tax_liabilities: Optional[float] = Field(
        description="Non-current deferred payable income tax liabilities.", default=None
    )
    non_current_employee_benefit_liabilities: Optional[float] = Field(
        description="Non-current employee benefit liabilities.", default=None
    )
    other_non_current_operating_liabilities: Optional[float] = Field(
        description="Other non-current operating liabilities.", default=None
    )
    other_non_current_non_operating_liabilities: Optional[float] = Field(
        description="Other non-current, non-operating liabilities.", default=None
    )
    total_non_current_liabilities: Optional[float] = Field(
        description="Total non-current liabilities.", default=None
    )
    capital_lease_obligations: Optional[float] = Field(
        description="Capital lease obligations.", default=None
    )
    asset_retirement_reserve_litigation_obligation: Optional[float] = Field(
        description="Asset retirement reserve litigation obligation.", default=None
    )
    total_liabilities: Optional[float] = Field(
        description="Total liabilities.", default=None
    )
    commitments_contingencies: Optional[float] = Field(
        description="Commitments contingencies.", default=None
    )
    redeemable_non_controlling_interest: Optional[float] = Field(
        description="Redeemable non-controlling interest.", default=None
    )
    preferred_stock: Optional[float] = Field(
        description="Preferred stock.", default=None
    )
    common_stock: Optional[float] = Field(description="Common stock.", default=None)
    retained_earnings: Optional[float] = Field(
        description="Retained earnings.", default=None
    )
    treasury_stock: Optional[float] = Field(description="Treasury stock.", default=None)
    accumulated_other_comprehensive_income: Optional[float] = Field(
        description="Accumulated other comprehensive income.", default=None
    )
    participating_policy_holder_equity: Optional[float] = Field(
        description="Participating policy holder equity.", default=None
    )
    other_equity_adjustments: Optional[float] = Field(
        description="Other equity adjustments.", default=None
    )
    total_common_equity: Optional[float] = Field(
        description="Total common equity.", default=None
    )
    total_preferred_common_equity: Optional[float] = Field(
        description="Total preferred common equity.", default=None
    )
    non_controlling_interest: Optional[float] = Field(
        description="Non-controlling interest.", default=None
    )
    total_equity_non_controlling_interests: Optional[float] = Field(
        description="Total equity non-controlling interests.", default=None
    )
    total_liabilities_shareholders_equity: Optional[float] = Field(
        description="Total liabilities and shareholders equity.", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
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
    async def aextract_data(
        query: IntrinioBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "balance_sheet_statement"
        fundamentals_data: Dict = {}
        base_url = "https://api-v2.intrinio.com"
        period = "FY" if query.period == "annual" else "QTR"
        fundamentals_url = (
            f"{base_url}/companies/{query.symbol}/fundamentals?"
            f"statement_code={statement_code}&type={period}"
        )
        if query.fiscal_year is not None:
            if query.fiscal_year < 2008:
                warn("Financials data is only available from 2008 and later.")
                query.fiscal_year = 2008
            fundamentals_url = fundamentals_url + f"&fiscal_year={query.fiscal_year}"
        fundamentals_url = fundamentals_url + f"&api_key={api_key}"
        fundamentals_data = (await get_data_one(fundamentals_url, **kwargs)).get(
            "fundamentals", []
        )
        fiscal_periods = [
            f"{item['fiscal_year']}-{item['fiscal_period']}"
            for item in fundamentals_data
        ]
        fiscal_periods = fiscal_periods[: query.limit]

        async def callback(response: ClientResponse, _: Any) -> Dict:
            """Return the response."""
            statement_data = await response.json()  # type: ignore
            return {
                "period_ending": statement_data["fundamental"]["end_date"],  # type: ignore
                "fiscal_year": statement_data["fundamental"]["fiscal_year"],  # type: ignore
                "fiscal_period": statement_data["fundamental"]["fiscal_period"],  # type: ignore
                "financials": statement_data["standardized_financials"],  # type: ignore
            }

        urls = [
            f"{base_url}/fundamentals/{query.symbol}-{statement_code}-{p}/standardized_financials?api_key={api_key}"
            for p in fiscal_periods
        ]

        return await amake_requests(urls, callback, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: IntrinioBalanceSheetQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioBalanceSheetData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioBalanceSheetData] = []
        period = "FY" if query.period == "annual" else "QTR"
        units = []
        for item in data:
            sub_dict: Dict[str, Any] = {}

            for sub_item in item["financials"]:
                field_name = sub_item["data_tag"]["tag"]
                unit = sub_item["data_tag"].get("unit", "")
                if unit and len(unit) == 3:
                    units.append(unit)
                sub_dict[field_name] = (
                    float(sub_item["value"])
                    if sub_item["value"] and sub_item["value"] != 0
                    else None
                )

            sub_dict["period_ending"] = item["period_ending"]
            sub_dict["fiscal_year"] = item["fiscal_year"]
            sub_dict["fiscal_period"] = item["fiscal_period"]
            sub_dict["reported_currency"] = list(set(units))[0]

            # Intrinio does not return Q4 data but FY data instead
            if period == "QTR" and item["fiscal_period"] == "FY":
                sub_dict["fiscal_period"] = "Q4"

            transformed_data.append(IntrinioBalanceSheetData(**sub_dict))

        return transformed_data
