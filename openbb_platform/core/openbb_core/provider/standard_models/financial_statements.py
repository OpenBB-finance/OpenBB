"""Financial Statements Models."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    QUERY_DESCRIPTIONS,
)


class FinancialStatementsQueryParams(QueryParams):
    """Financial Statement Query Params."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(default="annual", description="The reporting period.")
    limit: Optional[int] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        return v.upper()


class BalanceSheetData(Data):
    """Balance Sheet Data"""

    report_date: Optional[dateType] = Field(
        description="The date of the report.", default=None
    )
    period_ending: Optional[dateType] = Field(
        description="Reporting period ending.", default=None
    )
    fiscal_year: Optional[int] = Field(
        description="Fiscal year of the report.", default=None
    )
    fiscal_period: Optional[str] = Field(
        description="Fiscal period of the report.", default=None
    )
    cash_and_equivalents: Optional[float] = Field(
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
    other_current_nonoperating_assets: Optional[float] = Field(
        description="Other current nonoperating assets.", default=None
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

    long_term_investments: Optional[float] = Field(
        description="Long term investments.", default=None
    )
    accrued_investment_income: Optional[float] = Field(
        description="Accrued investment income.", default=None
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
    mortgage_servicing_rights: Optional[float] = Field(
        description="Mortgage servicing rights.", default=None
    )
    unearned_premiums_asset: Optional[float] = Field(
        description="Unearned premiums asset.", default=None
    )
    noncurrent_note_lease_receivables: Optional[float] = Field(
        description="Noncurrent note lease receivables.", default=None
    )
    deferred_acquisition_cost: Optional[float] = Field(
        description="Deferred acquisition cost.", default=None
    )
    goodwill: Optional[float] = Field(description="Goodwill.", default=None)
    separate_account_business_assets: Optional[float] = Field(
        description="Separate account business assets.", default=None
    )
    noncurrent_deferred_refundable_income_taxes: Optional[float] = Field(
        description="Noncurrent deferred refundable income taxes.", default=None
    )
    intangible_assets: Optional[float] = Field(
        description="Intangible assets.", default=None
    )
    employee_benefit_assets: Optional[float] = Field(
        description="Employee benefit assets.", default=None
    )
    other_assets: Optional[float] = Field(description="Other assets.", default=None)
    other_noncurrent_operating_assets: Optional[float] = Field(
        description="Other noncurrent operating assets.", default=None
    )
    other_noncurrent_nonoperating_assets: Optional[float] = Field(
        description="Other noncurrent nonoperating assets.", default=None
    )
    non_interest_bearing_deposits: Optional[float] = Field(
        description="Non interest bearing deposits.", default=None
    )
    interest_bearing_deposits: Optional[float] = Field(
        description="Interest bearing deposits.", default=None
    )
    total_noncurrent_assets: Optional[float] = Field(
        description="Total noncurrent assets.", default=None
    )
    federal_funds_purchased_and_securities_sold: Optional[float] = Field(
        description="Federal funds purchased and securities sold.", default=None
    )
    total_assets: Optional[float] = Field(description="Total assets.", default=None)
    bankers_acceptance_outstanding: Optional[float] = Field(
        description="Bankers acceptance outstanding.", default=None
    )
    short_term_debt: Optional[float] = Field(
        description="Short term debt.", default=None
    )
    accrued_interest_payable: Optional[float] = Field(
        description="Accrued interest payable.", default=None
    )
    accounts_payable: Optional[float] = Field(
        description="Accounts payable.", default=None
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
    current_deferred_payable_income_tax_liabilities: Optional[float] = Field(
        description="Current deferred payable income tax liabilities.", default=None
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
    current_deferred_revenue: Optional[float] = Field(
        description="Current deferred revenue.", default=None
    )
    participating_policy_holder_equity: Optional[float] = Field(
        description="Participating policy holder equity.", default=None
    )
    other_current_nonoperating_liabilities: Optional[float] = Field(
        description="Other current nonoperating liabilities.", default=None
    )
    separate_account_business_liabilities: Optional[float] = Field(
        description="Separate account business liabilities.", default=None
    )
    total_current_liabilities: Optional[float] = Field(
        description="Total current liabilities.", default=None
    )
    other_long_term_liabilities: Optional[float] = Field(
        description="Other long term liabilities.", default=None
    )
    long_term_debt: Optional[float] = Field(description="Long term debt.", default=None)
    capital_lease_obligations: Optional[float] = Field(
        description="Capital lease obligations.", default=None
    )
    asset_retirement_reserve_litigation_obligation: Optional[float] = Field(
        description="Asset retirement reserve litigation obligation.", default=None
    )
    noncurrent_deferred_revenue: Optional[float] = Field(
        description="Noncurrent deferred revenue.", default=None
    )
    noncurrent_deferred_payable_income_tax_liabilities: Optional[float] = Field(
        description="Noncurrent deferred payable income tax liabilities.", default=None
    )
    noncurrent_employee_benefit_liabilities: Optional[float] = Field(
        description="Noncurrent employee benefit liabilities.", default=None
    )
    other_noncurrent_operating_liabilities: Optional[float] = Field(
        description="Other noncurrent operating liabilities.", default=None
    )
    other_noncurrent_nonoperating_liabilities: Optional[float] = Field(
        description="Other noncurrent nonoperating liabilities.", default=None
    )
    total_noncurrent_liabilities: Optional[float] = Field(
        description="Total noncurrent liabilities.", default=None
    )
    total_liabilities: Optional[float] = Field(
        description="Total liabilities.", default=None
    )
    commitments_contingencies: Optional[float] = Field(
        description="Commitments contingencies.", default=None
    )
    redeemable_noncontrolling_interest: Optional[float] = Field(
        description="Redeemable noncontrolling interest.", default=None
    )
    preferred_stock: Optional[float] = Field(
        description="Preferred stock.", default=None
    )
    common_stock: Optional[float] = Field(description="Common stock.", default=None)
    treasury_stock: Optional[float] = Field(description="Treasury stock.", default=None)
    retained_earnings: Optional[float] = Field(
        description="Retained earnings.", default=None
    )
    accumulated_other_comprehensive_income: Optional[float] = Field(
        description="Accumulated other comprehensive income.", default=None
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
    noncontrolling_interest: Optional[float] = Field(
        description="Noncontrolling interest.", default=None
    )
    total_equity_noncontrolling_interests: Optional[float] = Field(
        description="Total equity noncontrolling interests.", default=None
    )
    total_liabilities_shareholders_equity: Optional[float] = Field(
        description="Total liabilities and shareholders equity.", default=None
    )


class CashFlowStatementData(Data):
    """Cash Flow Statement Data."""

    report_date: Optional[dateType] = Field(
        description="The date of the report.", default=None
    )
    period_ending: Optional[dateType] = Field(
        description="Reporting period ending.", default=None
    )
    fiscal_year: Optional[int] = Field(
        description="Fiscal year of the report.", default=None
    )
    fiscal_period: Optional[str] = Field(
        description="Fiscal period of the report.", default=None
    )
    net_income_continuing_operations: Optional[float] = Field(
        default=None, description="Net Income (Continuing Operations)"
    )
    net_income_discontinued_operations: Optional[float] = Field(
        default=None, description="Net Income (Discontinued Operations)"
    )
    consolidated_net_income: Optional[float] = Field(
        default=None, description="Consolidated Net Income"
    )
    acquisitions: Optional[float] = Field(default=None, description="Acquisitions")
    divestitures: Optional[float] = Field(default=None, description="Divestitures")

    issuance_of_common_equity: Optional[float] = Field(
        default=None, description="Issuance of Common Equity"
    )
    issuance_of_preferred_equity: Optional[float] = Field(
        default=None, description="Issuance of Preferred Equity"
    )

    non_cash_adjustments_to_reconcile_net_income: Optional[float] = Field(
        default=None, description="Non-Cash Adjustments to Reconcile Net Income"
    )
    amortization_expense: Optional[float] = Field(
        default=None, description="Amortization Expense"
    )
    depreciation_expense: Optional[float] = Field(
        default=None, description="Depreciation Expense"
    )

    changes_in_operating_assets_and_liabilities: Optional[float] = Field(
        default=None, description="Changes in Operating Assets and Liabilities (Net)"
    )
    net_cash_from_continuing_operating_activities: Optional[float] = Field(
        default=None, description="Net Cash from Continuing Operating Activities"
    )
    net_cash_from_discontinued_operating_activities: Optional[float] = Field(
        default=None, description="Net Cash from Discontinued Operating Activities"
    )
    net_cash_from_operating_activities: Optional[float] = Field(
        default=None, description="Net Cash from Operating Activities"
    )

    loans_held_for_sale: Optional[float] = Field(
        default=None, description="Loans Held for Sale (Net)"
    )
    net_cash_from_continuing_financing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Continuing Financing Activities"
    )
    net_cash_from_continuing_investing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Continuing Investing Activities"
    )

    issuance_of_debt: Optional[float] = Field(
        default=None, description="Issuance of Debt"
    )

    net_cash_from_discontinued_financing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Discontinued Financing Activities"
    )
    net_cash_from_discontinued_investing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Discontinued Investing Activities"
    )
    net_cash_from_financing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Financing Activities"
    )
    net_cash_from_investing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Investing Activities"
    )

    payment_of_dividends: Optional[float] = Field(
        default=None, description="Payment of Dividends"
    )

    net_increase_in_fed_funds_sold: Optional[float] = Field(
        default=None, description="Net Increase in Fed Funds Sold"
    )
    other_financing_activities: Optional[float] = Field(
        default=None, description="Other Financing Activities (Net)"
    )
    other_investing_activities: Optional[float] = Field(
        default=None, description="Other Investing Activities (Net)"
    )
    provision_for_loan_losses: Optional[float] = Field(
        default=None, description="Provision for Loan Losses"
    )
    purchase_of_investments: Optional[float] = Field(
        default=None, description="Purchase of Investments"
    )
    purchase_of_investment_securities: Optional[float] = Field(
        default=None, description="Purchase of Investment Securities"
    )
    purchase_of_property_plant_and_equipment: Optional[float] = Field(
        default=None, description="Purchase of Property, Plant, and Equipment"
    )
    cash_interest_received: Optional[float] = Field(
        default=None, description="Cash Interest Received"
    )
    repayment_of_debt: Optional[float] = Field(
        default=None, description="Repayment of Debt"
    )
    repurchase_of_common_equity: Optional[float] = Field(
        default=None, description="Repurchase of Common Equity"
    )
    repurchase_of_preferred_equity: Optional[float] = Field(
        default=None, description="Repurchase of Preferred Equity"
    )
    sale_and_maturity_of_investments: Optional[float] = Field(
        default=None, description="Sale and Maturity of Investments"
    )
    sale_of_property_plant_and_equipment: Optional[float] = Field(
        default=None, description="Sale of Property, Plant, and Equipment"
    )

    effect_of_exchange_rate_changes: Optional[float] = Field(
        default=None, description="Effect of Exchange Rate Changes"
    )

    net_change_in_deposits: Optional[float] = Field(
        default=None, description="Net Change in Deposits"
    )
    other_net_changes_in_cash: Optional[float] = Field(
        default=None, description="Other Net Changes in Cash"
    )
    net_change_in_cash_and_equivalents: Optional[float] = Field(
        default=None, description="Net Change in Cash and Equivalents"
    )

    cash_income_taxes_paid: Optional[float] = Field(
        default=None, description="Cash Income Taxes Paid"
    )
    cash_interest_paid: Optional[float] = Field(
        default=None, description="Cash Interest Paid"
    )


class IncomeStatementData(Data):
    """Income Statement Data."""

    report_date: Optional[dateType] = Field(
        description="The date of the report.", default=None
    )
    period_ending: Optional[dateType] = Field(
        description="Reporting period ending.", default=None
    )
    fiscal_year: Optional[int] = Field(
        description="Fiscal year of the report.", default=None
    )
    fiscal_period: Optional[str] = Field(
        description="Fiscal period of the report.", default=None
    )
    revenue: Optional[float] = Field(default=None, description="Total revenue")
    cost_of_revenue: Optional[float] = Field(
        default=None, description="Total cost of revenue"
    )
    gross_profit: Optional[float] = Field(
        default=None, description="Total gross profit"
    )
    gross_margin: Optional[float] = Field(
        default=None, description="Gross margin"
    )
    research_and_development_expense: Optional[float] = Field(
        default=None, description="Research and development expense"
    )
    selling_general_and_admin_expense: Optional[float] = Field(
        default=None, description="Selling, general, and admin expense"
    )
    salaries_and_employee_benefits: Optional[float] = Field(
        default=None, description="Salaries and employee benefits"
    )
    marketing_expense: Optional[float] = Field(
        default=None, description="Marketing expense"
    )
    net_occupancy_and_equipment_expense: Optional[float] = Field(
        default=None, description="Net occupancy and equipment expense"
    )
    other_operating_expenses: Optional[float] = Field(
        default=None, description="Other operating expenses"
    )
    depreciation_expense: Optional[float] = Field(
        default=None, description="Depreciation expense"
    )
    amortization_expense: Optional[float] = Field(
        default=None, description="Amortization expense"
    )
    amortization_of_deferred_policy_acquisition_costs: Optional[float] = Field(
        default=None, description="Amortization of deferred policy acquisition costs"
    )
    exploration_expense: Optional[float] = Field(
        default=None, description="Exploration expense"
    )
    depletion_expense: Optional[float] = Field(
        default=None, description="Depletion expense"
    )
    total_operating_expenses: Optional[float] = Field(
        default=None, description="Total operating expenses"
    )
    total_operating_income: Optional[float] = Field(
        default=None, description="Total operating income"
    )
    deposits_and_money_market_investments_interest_income: Optional[float] = Field(
        default=None,
        description="Deposits and money market investments interest income",
    )
    federal_funds_sold_and_securities_borrowed_interest_income: Optional[float] = Field(
        default=None,
        description="Federal funds sold and securities borrowed interest income",
    )
    investment_securities_interest_income: Optional[float] = Field(
        default=None, description="Investment securities interest income"
    )
    loans_and_leases_interest_income: Optional[float] = Field(
        default=None, description="Loans and leases interest income"
    )
    trading_account_interest_income: Optional[float] = Field(
        default=None, description="Trading account interest income"
    )
    other_interest_income: Optional[float] = Field(
        default=None, description="Other interest income"
    )
    total_non_interest_income: Optional[float] = Field(
        default=None, description="Total non-interest income"
    )
    interest_and_investment_income: Optional[float] = Field(
        default=None, description="Interest and investment income"
    )
    short_term_borrowings_interest_expense: Optional[float] = Field(
        default=None, description="Short-term borrowings interest expense"
    )
    long_term_debt_interest_expense: Optional[float] = Field(
        default=None, description="Long-term debt interest expense"
    )
    capitalized_lease_obligations_interest_expense: Optional[float] = Field(
        default=None, description="Capitalized lease obligations interest expense"
    )
    deposits_interest_expense: Optional[float] = Field(
        default=None, description="Deposits interest expense"
    )
    federal_funds_purchased_and_securities_sold_interest_expense: Optional[
        float
    ] = Field(
        default=None,
        description="Federal funds purchased and securities sold interest expense",
    )
    other_interest_expense: Optional[float] = Field(
        default=None, description="Other interest expense"
    )
    total_interest_expense: Optional[float] = Field(
        default=None, description="Total interest expense"
    )
    net_interest_income: Optional[float] = Field(
        default=None, description="Net interest income"
    )
    other_non_interest_income: Optional[float] = Field(
        default=None, description="Other non-interest income"
    )
    service_charges_on_deposit_accounts: Optional[float] = Field(
        default=None, description="Service charges on deposit accounts"
    )
    investment_banking_income: Optional[float] = Field(
        default=None, description="Investment banking income"
    )
    trust_fees_by_commissions: Optional[float] = Field(
        default=None, description="Trust fees by commissions"
    )
    premiums_earned: Optional[float] = Field(
        default=None, description="Premiums earned"
    )
    insurance_policy_acquisition_costs: Optional[float] = Field(
        default=None, description="Insurance policy acquisition costs"
    )
    current_and_future_benefits: Optional[float] = Field(
        default=None, description="Current and future benefits"
    )
    property_and_liability_insurance_claims: Optional[float] = Field(
        default=None, description="Property and liability insurance claims"
    )
    total_non_interest_expense: Optional[float] = Field(
        default=None, description="Total non-interest expense"
    )
    net_realized_and_unrealized_capital_gains_on_investments: Optional[float] = Field(
        default=None,
        description="Net realized and unrealized capital gains on investments",
    )
    other_gains: Optional[float] = Field(default=None, description="Other gains")
    non_operating_income: Optional[float] = Field(
        default=None, description="Non-operating income"
    )
    other_income: Optional[float] = Field(default=None, description="Other income")
    other_revenue: Optional[float] = Field(default=None, description="Other revenue")

    extraordinary_income: Optional[float] = Field(
        default=None, description="Extraordinary income"
    )
    total_other_income: Optional[float] = Field(
        default=None, description="Total other income"
    )
    total_pre_tax_income: Optional[float] = Field(
        default=None, description="Total pre-tax income"
    )
    pre_tax_income_margin: Optional[float] = Field(
        default=None, description="Pre-Tax Income Margin."
    )
    income_tax_expense: Optional[float] = Field(
        default=None, description="Income tax expense"
    )
    other_cost_of_revenue: Optional[float] = Field(
        default=None, description="Other cost of revenue"
    )
    net_income_continuing_operations: Optional[float] = Field(
        default=None, description="Net income (continuing operations)"
    )
    net_income_discontinued_operations: Optional[float] = Field(
        default=None, description="Net income (discontinued operations)"
    )
    consolidated_net_income: Optional[float] = Field(
        default=None, description="Consolidated net income"
    )
    impairment_charge: Optional[float] = Field(
        default=None, description="Impairment charge"
    )
    restructuring_charge: Optional[float] = Field(
        default=None, description="Restructuring charge"
    )
    other_service_charges: Optional[float] = Field(
        default=None, description="Other service charges"
    )
    other_special_charges: Optional[float] = Field(
        default=None, description="Other special charges"
    )
    provision_for_credit_losses: Optional[float] = Field(
        default=None, description="Provision for credit losses"
    )
    other_adjustments_to_consolidated_net_income: Optional[float] = Field(
        default=None, description="Other adjustments to consolidated net income"
    )
    other_adjustment_to_net_income_attributable_to_common_shareholders: Optional[
        float
    ] = Field(
        default=None,
        description="Other adjustment to net income attributable to common shareholders",
    )
    net_income_attributable_to_noncontrolling_interest: Optional[float] = Field(
        default=None, description="Net income attributable to noncontrolling interest"
    )
    net_income_attributable_to_common_shareholders: Optional[float] = Field(
        default=None, description="Net income attributable to common shareholders"
    )
    ebit: Optional[float] = Field(
        default=None, description="Earnings Before Interest and Taxes."
    )
    ebitda: Optional[float] = Field(
        default=None,
        description="Earnings Before Interest, Taxes, Depreciation and Amortization.",
    )
    ebitda_margin: Optional[float] = Field(
        default=None,
        description="Margin on Earnings Before Interest, Taxes, Depreciation and Amortization.",
    )
    basic_earnings_per_share: Optional[float] = Field(
        default=None, description="Basic earnings per share"
    )
    diluted_earnings_per_share: Optional[float] = Field(
        default=None, description="Diluted earnings per share"
    )
    basic_and_diluted_earnings_per_share: Optional[float] = Field(
        default=None, description="Basic and diluted earnings per share"
    )
    cash_dividends_to_common_per_share: Optional[float] = Field(
        default=None, description="Cash dividends to common per share"
    )
    preferred_stock_dividends_declared: Optional[float] = Field(
        default=None, description="Preferred stock dividends declared"
    )
    weighted_average_basic_shares_outstanding: Optional[float] = Field(
        default=None, description="Weighted average basic shares outstanding"
    )
    weighted_average_diluted_shares_outstanding: Optional[float] = Field(
        default=None, description="Weighted average diluted shares outstanding"
    )
    weighted_average_basic_and_diluted_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Weighted average basic and diluted shares outstanding",
    )
