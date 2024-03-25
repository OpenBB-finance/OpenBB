---
title: "balance"
description: "Learn how to use the balance sheet function in Python to retrieve financial  statement data. This documentation provides details about the function parameters,  return values, and available data types."
keywords:
- balance sheet statement
- balance sheet function
- python function
- financial statement function
- balance sheet data parameters
- balance sheet data returns
- balance sheet data types
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/balance - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the balance sheet for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.balance(symbol='AAPL', provider='fmp')
obb.equity.fundamental.balance(symbol='AAPL', period='annual', limit=5, provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| fiscal_year | int | The specific fiscal year. Reports do not go beyond 2008. | None | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| filing_date | date | Filing date of the financial statement. | None | True |
| filing_date_lt | date | Filing date less than the given date. | None | True |
| filing_date_lte | date | Filing date less than or equal to the given date. | None | True |
| filing_date_gt | date | Filing date greater than the given date. | None | True |
| filing_date_gte | date | Filing date greater than or equal to the given date. | None | True |
| period_of_report_date | date | Period of report date of the financial statement. | None | True |
| period_of_report_date_lt | date | Period of report date less than the given date. | None | True |
| period_of_report_date_lte | date | Period of report date less than or equal to the given date. | None | True |
| period_of_report_date_gt | date | Period of report date greater than the given date. | None | True |
| period_of_report_date_gte | date | Period of report date greater than or equal to the given date. | None | True |
| include_sources | bool | Whether to include the sources of the financial statement. | True | True |
| order | Literal['asc', 'desc'] | Order of the financial statement. | None | True |
| sort | Literal['filing_date', 'period_of_report_date'] | Sort of the financial statement. | None | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| period | str | Time period of the data to return. | annual | True |
| limit | int, Ge(ge=0) | The number of data entries to return. | 5 | True |
| provider | Literal['fmp', 'intrinio', 'polygon', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : BalanceSheet
        Serializable results.
    provider : Literal['fmp', 'intrinio', 'polygon', 'yfinance']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
| filing_date | date | The date when the filing was made. |
| accepted_date | datetime | The date and time when the filing was accepted. |
| reported_currency | str | The currency in which the balance sheet was reported. |
| cash_and_cash_equivalents | float | Cash and cash equivalents. |
| short_term_investments | float | Short term investments. |
| cash_and_short_term_investments | float | Cash and short term investments. |
| net_receivables | float | Net receivables. |
| inventory | float | Inventory. |
| other_current_assets | float | Other current assets. |
| total_current_assets | float | Total current assets. |
| plant_property_equipment_net | float | Plant property equipment net. |
| goodwill | float | Goodwill. |
| intangible_assets | float | Intangible assets. |
| goodwill_and_intangible_assets | float | Goodwill and intangible assets. |
| long_term_investments | float | Long term investments. |
| tax_assets | float | Tax assets. |
| other_non_current_assets | float | Other non current assets. |
| non_current_assets | float | Total non current assets. |
| other_assets | float | Other assets. |
| total_assets | float | Total assets. |
| accounts_payable | float | Accounts payable. |
| short_term_debt | float | Short term debt. |
| tax_payables | float | Tax payables. |
| current_deferred_revenue | float | Current deferred revenue. |
| other_current_liabilities | float | Other current liabilities. |
| total_current_liabilities | float | Total current liabilities. |
| long_term_debt | float | Long term debt. |
| deferred_revenue_non_current | float | Non current deferred revenue. |
| deferred_tax_liabilities_non_current | float | Deferred tax liabilities non current. |
| other_non_current_liabilities | float | Other non current liabilities. |
| total_non_current_liabilities | float | Total non current liabilities. |
| other_liabilities | float | Other liabilities. |
| capital_lease_obligations | float | Capital lease obligations. |
| total_liabilities | float | Total liabilities. |
| preferred_stock | float | Preferred stock. |
| common_stock | float | Common stock. |
| retained_earnings | float | Retained earnings. |
| accumulated_other_comprehensive_income | float | Accumulated other comprehensive income (loss). |
| other_shareholders_equity | float | Other shareholders equity. |
| other_total_shareholders_equity | float | Other total shareholders equity. |
| total_common_equity | float | Total common equity. |
| total_equity_non_controlling_interests | float | Total equity non controlling interests. |
| total_liabilities_and_shareholders_equity | float | Total liabilities and shareholders equity. |
| minority_interest | float | Minority interest. |
| total_liabilities_and_total_equity | float | Total liabilities and total equity. |
| total_investments | float | Total investments. |
| total_debt | float | Total debt. |
| net_debt | float | Net debt. |
| link | str | Link to the filing. |
| final_link | str | Link to the filing document. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
| reported_currency | str | The currency in which the balance sheet is reported. |
| cash_and_cash_equivalents | float | Cash and cash equivalents. |
| cash_and_due_from_banks | float | Cash and due from banks. |
| restricted_cash | float | Restricted cash. |
| short_term_investments | float | Short term investments. |
| federal_funds_sold | float | Federal funds sold. |
| accounts_receivable | float | Accounts receivable. |
| note_and_lease_receivable | float | Note and lease receivable. (Vendor non-trade receivables) |
| inventories | float | Net Inventories. |
| customer_and_other_receivables | float | Customer and other receivables. |
| interest_bearing_deposits_at_other_banks | float | Interest bearing deposits at other banks. |
| time_deposits_placed_and_other_short_term_investments | float | Time deposits placed and other short term investments. |
| trading_account_securities | float | Trading account securities. |
| loans_and_leases | float | Loans and leases. |
| allowance_for_loan_and_lease_losses | float | Allowance for loan and lease losses. |
| current_deferred_refundable_income_taxes | float | Current deferred refundable income taxes. |
| other_current_assets | float | Other current assets. |
| loans_and_leases_net_of_allowance | float | Loans and leases net of allowance. |
| accrued_investment_income | float | Accrued investment income. |
| other_current_non_operating_assets | float | Other current non-operating assets. |
| loans_held_for_sale | float | Loans held for sale. |
| prepaid_expenses | float | Prepaid expenses. |
| total_current_assets | float | Total current assets. |
| plant_property_equipment_gross | float | Plant property equipment gross. |
| accumulated_depreciation | float | Accumulated depreciation. |
| premises_and_equipment_net | float | Net premises and equipment. |
| plant_property_equipment_net | float | Net plant property equipment. |
| long_term_investments | float | Long term investments. |
| mortgage_servicing_rights | float | Mortgage servicing rights. |
| unearned_premiums_asset | float | Unearned premiums asset. |
| non_current_note_lease_receivables | float | Non-current note lease receivables. |
| deferred_acquisition_cost | float | Deferred acquisition cost. |
| goodwill | float | Goodwill. |
| separate_account_business_assets | float | Separate account business assets. |
| non_current_deferred_refundable_income_taxes | float | Noncurrent deferred refundable income taxes. |
| intangible_assets | float | Intangible assets. |
| employee_benefit_assets | float | Employee benefit assets. |
| other_assets | float | Other assets. |
| other_non_current_operating_assets | float | Other noncurrent operating assets. |
| other_non_current_non_operating_assets | float | Other noncurrent non-operating assets. |
| interest_bearing_deposits | float | Interest bearing deposits. |
| total_non_current_assets | float | Total noncurrent assets. |
| total_assets | float | Total assets. |
| non_interest_bearing_deposits | float | Non interest bearing deposits. |
| federal_funds_purchased_and_securities_sold | float | Federal funds purchased and securities sold. |
| bankers_acceptance_outstanding | float | Bankers acceptance outstanding. |
| short_term_debt | float | Short term debt. |
| accounts_payable | float | Accounts payable. |
| current_deferred_revenue | float | Current deferred revenue. |
| current_deferred_payable_income_tax_liabilities | float | Current deferred payable income tax liabilities. |
| accrued_interest_payable | float | Accrued interest payable. |
| accrued_expenses | float | Accrued expenses. |
| other_short_term_payables | float | Other short term payables. |
| customer_deposits | float | Customer deposits. |
| dividends_payable | float | Dividends payable. |
| claims_and_claim_expense | float | Claims and claim expense. |
| future_policy_benefits | float | Future policy benefits. |
| current_employee_benefit_liabilities | float | Current employee benefit liabilities. |
| unearned_premiums_liability | float | Unearned premiums liability. |
| other_taxes_payable | float | Other taxes payable. |
| policy_holder_funds | float | Policy holder funds. |
| other_current_liabilities | float | Other current liabilities. |
| other_current_non_operating_liabilities | float | Other current non-operating liabilities. |
| separate_account_business_liabilities | float | Separate account business liabilities. |
| total_current_liabilities | float | Total current liabilities. |
| long_term_debt | float | Long term debt. |
| other_long_term_liabilities | float | Other long term liabilities. |
| non_current_deferred_revenue | float | Non-current deferred revenue. |
| non_current_deferred_payable_income_tax_liabilities | float | Non-current deferred payable income tax liabilities. |
| non_current_employee_benefit_liabilities | float | Non-current employee benefit liabilities. |
| other_non_current_operating_liabilities | float | Other non-current operating liabilities. |
| other_non_current_non_operating_liabilities | float | Other non-current, non-operating liabilities. |
| total_non_current_liabilities | float | Total non-current liabilities. |
| capital_lease_obligations | float | Capital lease obligations. |
| asset_retirement_reserve_litigation_obligation | float | Asset retirement reserve litigation obligation. |
| total_liabilities | float | Total liabilities. |
| commitments_contingencies | float | Commitments contingencies. |
| redeemable_non_controlling_interest | float | Redeemable non-controlling interest. |
| preferred_stock | float | Preferred stock. |
| common_stock | float | Common stock. |
| retained_earnings | float | Retained earnings. |
| treasury_stock | float | Treasury stock. |
| accumulated_other_comprehensive_income | float | Accumulated other comprehensive income. |
| participating_policy_holder_equity | float | Participating policy holder equity. |
| other_equity_adjustments | float | Other equity adjustments. |
| total_common_equity | float | Total common equity. |
| total_preferred_common_equity | float | Total preferred common equity. |
| non_controlling_interest | float | Non-controlling interest. |
| total_equity_non_controlling_interests | float | Total equity non-controlling interests. |
| total_liabilities_shareholders_equity | float | Total liabilities and shareholders equity. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
| accounts_receivable | int | Accounts receivable |
| marketable_securities | int | Marketable securities |
| prepaid_expenses | int | Prepaid expenses |
| other_current_assets | int | Other current assets |
| total_current_assets | int | Total current assets |
| property_plant_equipment_net | int | Property plant and equipment net |
| inventory | int | Inventory |
| other_non_current_assets | int | Other non-current assets |
| total_non_current_assets | int | Total non-current assets |
| intangible_assets | int | Intangible assets |
| total_assets | int | Total assets |
| accounts_payable | int | Accounts payable |
| employee_wages | int | Employee wages |
| other_current_liabilities | int | Other current liabilities |
| total_current_liabilities | int | Total current liabilities |
| other_non_current_liabilities | int | Other non-current liabilities |
| total_non_current_liabilities | int | Total non-current liabilities |
| long_term_debt | int | Long term debt |
| total_liabilities | int | Total liabilities |
| minority_interest | int | Minority interest |
| temporary_equity_attributable_to_parent | int | Temporary equity attributable to parent |
| equity_attributable_to_parent | int | Equity attributable to parent |
| temporary_equity | int | Temporary equity |
| preferred_stock | int | Preferred stock |
| redeemable_non_controlling_interest | int | Redeemable non-controlling interest |
| redeemable_non_controlling_interest_other | int | Redeemable non-controlling interest other |
| total_stock_holders_equity | int | Total stock holders equity |
| total_liabilities_and_stock_holders_equity | int | Total liabilities and stockholders equity |
| total_equity | int | Total equity |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| period_ending | date | The end date of the reporting period. |
| fiscal_period | str | The fiscal period of the report. |
| fiscal_year | int | The fiscal year of the fiscal period. |
</TabItem>

</Tabs>

