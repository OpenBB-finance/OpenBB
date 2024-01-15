---
title: INCOME
description: Get income statement and financial performance data for a company. Parameters
  include symbol, period, limit, provider, and more. Data includes revenue, gross
  profit, operating expenses, net income, and more.
keywords: 
- income statement
- financial performance
- get income data
- period
- limit
- provider
- symbol
- cik
- filing date
- period of report date
- include sources
- order
- sort
- revenue
- cost of revenue
- gross profit
- cost and expenses
- research and development expenses
- general and administrative expenses
- selling and marketing expenses
- other expenses
- operating expenses
- depreciation and amortization
- ebitda
- operating income
- interest income
- interest expense
- income before tax
- income tax expense
- net income
- eps
- weighted average shares outstanding
- link
- reported currency
- filling date
- accepted date
- calendar year
---

<!-- markdownlint-disable MD041 -->

Income Statement. Report on a company's financial performance.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.INCOME(symbol;[period];[limit];[provider];[fiscal_year];[filing_date];[filing_date_lt];[filing_date_lte];[filing_date_gt];[filing_date_gte];[period_of_report_date];[period_of_report_date_lt];[period_of_report_date_lte];[period_of_report_date_gt];[period_of_report_date_gte];[include_sources];[order];[sort])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.INCOME("AAPL")
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
| period_ending | The end date of the reporting period.  |
| fiscal_period | The fiscal period of the report.  |
| fiscal_year | The fiscal year of the fiscal period.  |
| symbol | Symbol representing the entity requested in the data. (provider: fmp);     Symbol of the company. (provider: intrinio) |
| filing_date | The date when the filing was made. (provider: fmp) |
| accepted_date | The date and time when the filing was accepted. (provider: fmp) |
| reported_currency | The currency in which the balance sheet was reported. (provider: fmp, intrinio) |
| revenue | Total revenue. (provider: fmp, intrinio, polygon) |
| cost_of_revenue | Cost of revenue. (provider: fmp, intrinio, polygon) |
| gross_profit | Gross profit. (provider: fmp, intrinio, polygon) |
| gross_profit_margin | Gross profit margin. (provider: fmp);     Gross margin ratio. (provider: intrinio) |
| general_and_admin_expense | General and administrative expenses. (provider: fmp) |
| research_and_development_expense | Research and development expenses. (provider: fmp, intrinio) |
| selling_and_marketing_expense | Selling and marketing expenses. (provider: fmp) |
| selling_general_and_admin_expense | Selling, general and administrative expenses. (provider: fmp, intrinio) |
| other_expenses | Other expenses. (provider: fmp) |
| total_operating_expenses | Total operating expenses. (provider: fmp, intrinio) |
| cost_and_expenses | Cost and expenses. (provider: fmp) |
| interest_income | Interest income. (provider: fmp) |
| total_interest_expense | Total interest expenses. (provider: fmp, intrinio);     Interest Expense (provider: polygon) |
| depreciation_and_amortization | Depreciation and amortization. (provider: fmp, polygon) |
| ebitda | EBITDA. (provider: fmp);     Earnings Before Interest, Taxes, Depreciation and Amortization. (provider: intrinio) |
| ebitda_margin | EBITDA margin. (provider: fmp);     Margin on Earnings Before Interest, Taxes, Depreciation and Amortization. (provider: intrinio) |
| total_operating_income | Total operating income. (provider: fmp, intrinio) |
| operating_income_margin | Operating income margin. (provider: fmp) |
| total_other_income_expenses | Total other income and expenses. (provider: fmp) |
| total_pre_tax_income | Total pre-tax income. (provider: fmp, intrinio);     Income Before Tax (provider: polygon) |
| pre_tax_income_margin | Pre-tax income margin. (provider: fmp, intrinio) |
| income_tax_expense | Income tax expense. (provider: fmp, intrinio, polygon) |
| consolidated_net_income | Consolidated net income. (provider: fmp, intrinio);     Net Income/Loss (provider: polygon) |
| net_income_margin | Net income margin. (provider: fmp) |
| basic_earnings_per_share | Basic earnings per share. (provider: fmp, intrinio);     Earnings Per Share (provider: polygon) |
| diluted_earnings_per_share | Diluted earnings per share. (provider: fmp, intrinio, polygon) |
| weighted_average_basic_shares_outstanding | Weighted average basic shares outstanding. (provider: fmp, intrinio);     Basic Average Shares (provider: polygon) |
| weighted_average_diluted_shares_outstanding | Weighted average diluted shares outstanding. (provider: fmp, intrinio);     Diluted Average Shares (provider: polygon) |
| link | Link to the filing. (provider: fmp) |
| final_link | Link to the filing document. (provider: fmp) |
| operating_revenue | Total operating revenue (provider: intrinio) |
| operating_cost_of_revenue | Total operating cost of revenue (provider: intrinio) |
| provision_for_credit_losses | Provision for credit losses (provider: intrinio) |
| salaries_and_employee_benefits | Salaries and employee benefits (provider: intrinio) |
| marketing_expense | Marketing expense (provider: intrinio) |
| net_occupancy_and_equipment_expense | Net occupancy and equipment expense (provider: intrinio) |
| other_operating_expenses | Other operating expenses (provider: intrinio, polygon) |
| depreciation_expense | Depreciation expense (provider: intrinio) |
| amortization_expense | Amortization expense (provider: intrinio) |
| amortization_of_deferred_policy_acquisition_costs | Amortization of deferred policy acquisition costs (provider: intrinio) |
| exploration_expense | Exploration expense (provider: intrinio) |
| depletion_expense | Depletion expense (provider: intrinio) |
| deposits_and_money_market_investments_interest_income | Deposits and money market investments interest income (provider: intrinio) |
| federal_funds_sold_and_securities_borrowed_interest_income | Federal funds sold and securities borrowed interest income (provider: intrinio) |
| investment_securities_interest_income | Investment securities interest income (provider: intrinio) |
| loans_and_leases_interest_income | Loans and leases interest income (provider: intrinio) |
| trading_account_interest_income | Trading account interest income (provider: intrinio) |
| other_interest_income | Other interest income (provider: intrinio) |
| total_non_interest_income | Total non-interest income (provider: intrinio) |
| interest_and_investment_income | Interest and investment income (provider: intrinio) |
| short_term_borrowings_interest_expense | Short-term borrowings interest expense (provider: intrinio) |
| long_term_debt_interest_expense | Long-term debt interest expense (provider: intrinio) |
| capitalized_lease_obligations_interest_expense | Capitalized lease obligations interest expense (provider: intrinio) |
| deposits_interest_expense | Deposits interest expense (provider: intrinio) |
| federal_funds_purchased_and_securities_sold_interest_expense | Federal funds purchased and securities sold interest expense (provider: intrinio) |
| other_interest_expense | Other interest expense (provider: intrinio) |
| net_interest_income | Net interest income (provider: intrinio);     Interest Income Net (provider: polygon) |
| other_non_interest_income | Other non-interest income (provider: intrinio) |
| investment_banking_income | Investment banking income (provider: intrinio) |
| trust_fees_by_commissions | Trust fees by commissions (provider: intrinio) |
| premiums_earned | Premiums earned (provider: intrinio) |
| insurance_policy_acquisition_costs | Insurance policy acquisition costs (provider: intrinio) |
| current_and_future_benefits | Current and future benefits (provider: intrinio) |
| property_and_liability_insurance_claims | Property and liability insurance claims (provider: intrinio) |
| total_non_interest_expense | Total non-interest expense (provider: intrinio) |
| net_realized_and_unrealized_capital_gains_on_investments | Net realized and unrealized capital gains on investments (provider: intrinio) |
| other_gains | Other gains (provider: intrinio) |
| non_operating_income | Non-operating income (provider: intrinio);     Non Operating Income/Loss (provider: polygon) |
| other_income | Other income (provider: intrinio) |
| other_revenue | Other revenue (provider: intrinio) |
| extraordinary_income | Extraordinary income (provider: intrinio) |
| total_other_income | Total other income (provider: intrinio) |
| ebit | Earnings Before Interest and Taxes. (provider: intrinio) |
| impairment_charge | Impairment charge (provider: intrinio) |
| restructuring_charge | Restructuring charge (provider: intrinio) |
| service_charges_on_deposit_accounts | Service charges on deposit accounts (provider: intrinio) |
| other_service_charges | Other service charges (provider: intrinio) |
| other_special_charges | Other special charges (provider: intrinio) |
| other_cost_of_revenue | Other cost of revenue (provider: intrinio) |
| net_income_continuing_operations | Net income (continuing operations) (provider: intrinio) |
| net_income_discontinued_operations | Net income (discontinued operations) (provider: intrinio) |
| other_adjustments_to_consolidated_net_income | Other adjustments to consolidated net income (provider: intrinio) |
| other_adjustment_to_net_income_attributable_to_common_shareholders | Other adjustment to net income attributable to common shareholders (provider: intrinio) |
| net_income_attributable_to_noncontrolling_interest | Net income attributable to noncontrolling interest (provider: intrinio) |
| net_income_attributable_to_common_shareholders | Net income attributable to common shareholders (provider: intrinio);     Net Income/Loss Available To Common Stockholders Basic (provider: polygon) |
| basic_and_diluted_earnings_per_share | Basic and diluted earnings per share (provider: intrinio) |
| cash_dividends_to_common_per_share | Cash dividends to common per share (provider: intrinio) |
| preferred_stock_dividends_declared | Preferred stock dividends declared (provider: intrinio) |
| weighted_average_basic_and_diluted_shares_outstanding | Weighted average basic and diluted shares outstanding (provider: intrinio) |
| cost_of_revenue_goods | Cost of Revenue - Goods (provider: polygon) |
| cost_of_revenue_services | Cost of Revenue - Services (provider: polygon) |
| provisions_for_loan_lease_and_other_losses | Provisions for loan lease and other losses (provider: polygon) |
| income_tax_expense_benefit_current | Income tax expense benefit current (provider: polygon) |
| deferred_tax_benefit | Deferred tax benefit (provider: polygon) |
| benefits_costs_expenses | Benefits, costs and expenses (provider: polygon) |
| selling_general_and_administrative_expense | Selling, general and administrative expense (provider: polygon) |
| research_and_development | Research and development (provider: polygon) |
| costs_and_expenses | Costs and expenses (provider: polygon) |
| operating_expenses | Operating expenses (provider: polygon) |
| operating_income | Operating Income/Loss (provider: polygon) |
| interest_and_dividend_income | Interest and Dividend Income (provider: polygon) |
| interest_and_debt_expense | Interest and Debt Expense (provider: polygon) |
| interest_income_after_provision_for_losses | Interest Income After Provision for Losses (provider: polygon) |
| non_interest_expense | Non-Interest Expense (provider: polygon) |
| non_interest_income | Non-Interest Income (provider: polygon) |
| income_from_discontinued_operations_net_of_tax_on_disposal | Income From Discontinued Operations Net of Tax on Disposal (provider: polygon) |
| income_from_discontinued_operations_net_of_tax | Income From Discontinued Operations Net of Tax (provider: polygon) |
| income_before_equity_method_investments | Income Before Equity Method Investments (provider: polygon) |
| income_from_equity_method_investments | Income From Equity Method Investments (provider: polygon) |
| income_after_tax | Income After Tax (provider: polygon) |
| net_income_attributable_noncontrolling_interest | Net income (loss) attributable to noncontrolling interest (provider: polygon) |
| net_income_attributable_to_parent | Net income (loss) attributable to parent (provider: polygon) |
| participating_securities_earnings | Participating Securities Distributed And Undistributed Earnings Loss Basic (provider: polygon) |
| undistributed_earnings_allocated_to_participating_securities | Undistributed Earnings Allocated To Participating Securities (provider: polygon) |
| common_stock_dividends | Common Stock Dividends (provider: polygon) |
| preferred_stock_dividends_and_other_adjustments | Preferred stock dividends and other adjustments (provider: polygon) |
