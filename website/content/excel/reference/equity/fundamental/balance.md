---
title: BALANCE
description: Learn how to use the balance sheet function in Python to retrieve financial
  statement data. This documentation provides details about the function parameters,
  return values, and available data types.
keywords: 
- balance sheet statement
- balance sheet function
- python function
- financial statement function
- balance sheet data parameters
- balance sheet data returns
- balance sheet data types
---

<!-- markdownlint-disable MD041 -->

Balance Sheet. Balance sheet statement.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.BALANCE(symbol;[period];[limit];[provider];[fiscal_year];[filing_date];[filing_date_lt];[filing_date_lte];[filing_date_gt];[filing_date_gte];[period_of_report_date];[period_of_report_date_lt];[period_of_report_date_lte];[period_of_report_date_gt];[period_of_report_date_gte];[include_sources];[order];[sort])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.BALANCE("AAPL")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| period | Text | Time period of the data to return. | False |
| limit | Number | The number of data entries to return. | False |
| provider | Text | Options: fmp, intrinio, polygon, defaults to fmp. | False |
| fiscal_year | Number | The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio) | False |
| filing_date | Text | Filing date of the financial statement. (provider: polygon) | False |
| filing_date_lt | Text | Filing date less than the given date. (provider: polygon) | False |
| filing_date_lte | Text | Filing date less than or equal to the given date. (provider: polygon) | False |
| filing_date_gt | Text | Filing date greater than the given date. (provider: polygon) | False |
| filing_date_gte | Text | Filing date greater than or equal to the given date. (provider: polygon) | False |
| period_of_report_date | Text | Period of report date of the financial statement. (provider: polygon) | False |
| period_of_report_date_lt | Text | Period of report date less than the given date. (provider: polygon) | False |
| period_of_report_date_lte | Text | Period of report date less than or equal to the given date. (provider: polygon) | False |
| period_of_report_date_gt | Text | Period of report date greater than the given date. (provider: polygon) | False |
| period_of_report_date_gte | Text | Period of report date greater than or equal to the given date. (provider: polygon) | False |
| include_sources | Boolean | Whether to include the sources of the financial statement. (provider: polygon) | False |
| order | Text | Order of the financial statement. (provider: polygon) | False |
| sort | Text | Sort of the financial statement. (provider: polygon) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| period_ending | The end date of the reporting period.  |
| fiscal_period | The fiscal period of the report.  |
| fiscal_year | The fiscal year of the fiscal period.  |
| filing_date | The date when the filing was made. (provider: fmp) |
| accepted_date | The date and time when the filing was accepted. (provider: fmp) |
| reported_currency | The currency in which the balance sheet was reported. (provider: fmp, intrinio) |
| cash_and_cash_equivalents | Cash and cash equivalents. (provider: fmp, intrinio) |
| short_term_investments | Short term investments. (provider: fmp, intrinio) |
| cash_and_short_term_investments | Cash and short term investments. (provider: fmp) |
| net_receivables | Net receivables. (provider: fmp) |
| inventory | Inventory. (provider: fmp, polygon) |
| other_current_assets | Other current assets. (provider: fmp, intrinio, polygon) |
| total_current_assets | Total current assets. (provider: fmp, intrinio, polygon) |
| plant_property_equipment_net | Plant property equipment net. (provider: fmp, intrinio) |
| goodwill | Goodwill. (provider: fmp, intrinio) |
| intangible_assets | Intangible assets. (provider: fmp, intrinio, polygon) |
| goodwill_and_intangible_assets | Goodwill and intangible assets. (provider: fmp) |
| long_term_investments | Long term investments. (provider: fmp, intrinio) |
| tax_assets | Tax assets. (provider: fmp) |
| other_non_current_assets | Other non current assets. (provider: fmp, polygon) |
| non_current_assets | Total non current assets. (provider: fmp) |
| other_assets | Other assets. (provider: fmp, intrinio) |
| total_assets | Total assets. (provider: fmp, intrinio, polygon) |
| accounts_payable | Accounts payable. (provider: fmp, intrinio, polygon) |
| short_term_debt | Short term debt. (provider: fmp, intrinio) |
| tax_payables | Tax payables. (provider: fmp) |
| current_deferred_revenue | Current deferred revenue. (provider: fmp, intrinio) |
| other_current_liabilities | Other current liabilities. (provider: fmp, intrinio, polygon) |
| total_current_liabilities | Total current liabilities. (provider: fmp, intrinio, polygon) |
| long_term_debt | Long term debt. (provider: fmp, intrinio, polygon) |
| deferred_revenue_non_current | Non current deferred revenue. (provider: fmp) |
| deferred_tax_liabilities_non_current | Deferred tax liabilities non current. (provider: fmp) |
| other_non_current_liabilities | Other non current liabilities. (provider: fmp, polygon) |
| total_non_current_liabilities | Total non current liabilities. (provider: fmp, intrinio, polygon) |
| other_liabilities | Other liabilities. (provider: fmp) |
| capital_lease_obligations | Capital lease obligations. (provider: fmp, intrinio) |
| total_liabilities | Total liabilities. (provider: fmp, intrinio, polygon) |
| preferred_stock | Preferred stock. (provider: fmp, intrinio, polygon) |
| common_stock | Common stock. (provider: fmp, intrinio) |
| retained_earnings | Retained earnings. (provider: fmp, intrinio) |
| accumulated_other_comprehensive_income | Accumulated other comprehensive income (loss). (provider: fmp, intrinio) |
| other_shareholders_equity | Other shareholders equity. (provider: fmp) |
| other_total_shareholders_equity | Other total shareholders equity. (provider: fmp) |
| total_common_equity | Total common equity. (provider: fmp, intrinio) |
| total_equity_non_controlling_interests | Total equity non controlling interests. (provider: fmp, intrinio) |
| total_liabilities_and_shareholders_equity | Total liabilities and shareholders equity. (provider: fmp) |
| minority_interest | Minority interest. (provider: fmp, polygon) |
| total_liabilities_and_total_equity | Total liabilities and total equity. (provider: fmp) |
| total_investments | Total investments. (provider: fmp) |
| total_debt | Total debt. (provider: fmp) |
| net_debt | Net debt. (provider: fmp) |
| link | Link to the filing. (provider: fmp) |
| final_link | Link to the filing document. (provider: fmp) |
| cash_and_due_from_banks | Cash and due from banks. (provider: intrinio) |
| restricted_cash | Restricted cash. (provider: intrinio) |
| federal_funds_sold | Federal funds sold. (provider: intrinio) |
| accounts_receivable | Accounts receivable. (provider: intrinio, polygon) |
| note_and_lease_receivable | Note and lease receivable. (Vendor non-trade receivables) (provider: intrinio) |
| inventories | Net Inventories. (provider: intrinio) |
| customer_and_other_receivables | Customer and other receivables. (provider: intrinio) |
| interest_bearing_deposits_at_other_banks | Interest bearing deposits at other banks. (provider: intrinio) |
| time_deposits_placed_and_other_short_term_investments | Time deposits placed and other short term investments. (provider: intrinio) |
| trading_account_securities | Trading account securities. (provider: intrinio) |
| loans_and_leases | Loans and leases. (provider: intrinio) |
| allowance_for_loan_and_lease_losses | Allowance for loan and lease losses. (provider: intrinio) |
| current_deferred_refundable_income_taxes | Current deferred refundable income taxes. (provider: intrinio) |
| loans_and_leases_net_of_allowance | Loans and leases net of allowance. (provider: intrinio) |
| accrued_investment_income | Accrued investment income. (provider: intrinio) |
| other_current_non_operating_assets | Other current non-operating assets. (provider: intrinio) |
| loans_held_for_sale | Loans held for sale. (provider: intrinio) |
| prepaid_expenses | Prepaid expenses. (provider: intrinio, polygon) |
| plant_property_equipment_gross | Plant property equipment gross. (provider: intrinio) |
| accumulated_depreciation | Accumulated depreciation. (provider: intrinio) |
| premises_and_equipment_net | Net premises and equipment. (provider: intrinio) |
| mortgage_servicing_rights | Mortgage servicing rights. (provider: intrinio) |
| unearned_premiums_asset | Unearned premiums asset. (provider: intrinio) |
| non_current_note_lease_receivables | Non-current note lease receivables. (provider: intrinio) |
| deferred_acquisition_cost | Deferred acquisition cost. (provider: intrinio) |
| separate_account_business_assets | Separate account business assets. (provider: intrinio) |
| non_current_deferred_refundable_income_taxes | Noncurrent deferred refundable income taxes. (provider: intrinio) |
| employee_benefit_assets | Employee benefit assets. (provider: intrinio) |
| other_non_current_operating_assets | Other noncurrent operating assets. (provider: intrinio) |
| other_non_current_non_operating_assets | Other noncurrent non-operating assets. (provider: intrinio) |
| interest_bearing_deposits | Interest bearing deposits. (provider: intrinio) |
| total_non_current_assets | Total noncurrent assets. (provider: intrinio, polygon) |
| non_interest_bearing_deposits | Non interest bearing deposits. (provider: intrinio) |
| federal_funds_purchased_and_securities_sold | Federal funds purchased and securities sold. (provider: intrinio) |
| bankers_acceptance_outstanding | Bankers acceptance outstanding. (provider: intrinio) |
| current_deferred_payable_income_tax_liabilities | Current deferred payable income tax liabilities. (provider: intrinio) |
| accrued_interest_payable | Accrued interest payable. (provider: intrinio) |
| accrued_expenses | Accrued expenses. (provider: intrinio) |
| other_short_term_payables | Other short term payables. (provider: intrinio) |
| customer_deposits | Customer deposits. (provider: intrinio) |
| dividends_payable | Dividends payable. (provider: intrinio) |
| claims_and_claim_expense | Claims and claim expense. (provider: intrinio) |
| future_policy_benefits | Future policy benefits. (provider: intrinio) |
| current_employee_benefit_liabilities | Current employee benefit liabilities. (provider: intrinio) |
| unearned_premiums_liability | Unearned premiums liability. (provider: intrinio) |
| other_taxes_payable | Other taxes payable. (provider: intrinio) |
| policy_holder_funds | Policy holder funds. (provider: intrinio) |
| other_current_non_operating_liabilities | Other current non-operating liabilities. (provider: intrinio) |
| separate_account_business_liabilities | Separate account business liabilities. (provider: intrinio) |
| other_long_term_liabilities | Other long term liabilities. (provider: intrinio) |
| non_current_deferred_revenue | Non-current deferred revenue. (provider: intrinio) |
| non_current_deferred_payable_income_tax_liabilities | Non-current deferred payable income tax liabilities. (provider: intrinio) |
| non_current_employee_benefit_liabilities | Non-current employee benefit liabilities. (provider: intrinio) |
| other_non_current_operating_liabilities | Other non-current operating liabilities. (provider: intrinio) |
| other_non_current_non_operating_liabilities | Other non-current, non-operating liabilities. (provider: intrinio) |
| asset_retirement_reserve_litigation_obligation | Asset retirement reserve litigation obligation. (provider: intrinio) |
| commitments_contingencies | Commitments contingencies. (provider: intrinio) |
| redeemable_non_controlling_interest | Redeemable non-controlling interest. (provider: intrinio, polygon) |
| treasury_stock | Treasury stock. (provider: intrinio) |
| participating_policy_holder_equity | Participating policy holder equity. (provider: intrinio) |
| other_equity_adjustments | Other equity adjustments. (provider: intrinio) |
| total_preferred_common_equity | Total preferred common equity. (provider: intrinio) |
| non_controlling_interest | Non-controlling interest. (provider: intrinio) |
| total_liabilities_shareholders_equity | Total liabilities and shareholders equity. (provider: intrinio) |
| marketable_securities | Marketable securities (provider: polygon) |
| property_plant_equipment_net | Property plant and equipment net (provider: polygon) |
| employee_wages | Employee wages (provider: polygon) |
| temporary_equity_attributable_to_parent | Temporary equity attributable to parent (provider: polygon) |
| equity_attributable_to_parent | Equity attributable to parent (provider: polygon) |
| temporary_equity | Temporary equity (provider: polygon) |
| redeemable_non_controlling_interest_other | Redeemable non-controlling interest other (provider: polygon) |
| total_stock_holders_equity | Total stock holders equity (provider: polygon) |
| total_liabilities_and_stock_holders_equity | Total liabilities and stockholders equity (provider: polygon) |
| total_equity | Total equity (provider: polygon) |
