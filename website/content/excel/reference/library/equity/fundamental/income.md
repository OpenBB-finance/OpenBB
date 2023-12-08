---
title: income
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
=OBB.EQUITY.FUNDAMENTAL.INCOME(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio, polygon | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| cik | Text | The CIK of the company if no symbol is provided. (provider: fmp) | True |
| filing_date | Text | Filing date of the financial statement. (provider: polygon) | True |
| filing_date_lt | Text | Filing date less than the given date. (provider: polygon) | True |
| filing_date_lte | Text | Filing date less than or equal to the given date. (provider: polygon) | True |
| filing_date_gt | Text | Filing date greater than the given date. (provider: polygon) | True |
| filing_date_gte | Text | Filing date greater than or equal to the given date. (provider: polygon) | True |
| period_of_report_date | Text | Period of report date of the financial statement. (provider: polygon) | True |
| period_of_report_date_lt | Text | Period of report date less than the given date. (provider: polygon) | True |
| period_of_report_date_lte | Text | Period of report date less than or equal to the given date. (provider: polygon) | True |
| period_of_report_date_gt | Text | Period of report date greater than the given date. (provider: polygon) | True |
| period_of_report_date_gte | Text | Period of report date greater than or equal to the given date. (provider: polygon) | True |
| include_sources | Boolean | Whether to include the sources of the financial statement. (provider: polygon) | True |
| order | Text | Order of the financial statement. (provider: polygon) | True |
| sort | Text | Sort of the financial statement. (provider: polygon) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data. In this case, the date of the income statement.  |
| period | Period of the income statement.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| revenue | Revenue.  |
| cost_of_revenue | Cost of revenue.  |
| gross_profit | Gross profit.  |
| cost_and_expenses | Cost and expenses.  |
| gross_profit_ratio | Gross profit ratio.  |
| research_and_development_expenses | Research and development expenses.  |
| general_and_administrative_expenses | General and administrative expenses.  |
| selling_and_marketing_expenses | Selling and marketing expenses.  |
| selling_general_and_administrative_expenses | Selling, general and administrative expenses.  |
| other_expenses | Other expenses.  |
| operating_expenses | Operating expenses.  |
| depreciation_and_amortization | Depreciation and amortization.  |
| ebit | Earnings before interest, and taxes.  |
| ebitda | Earnings before interest, taxes, depreciation and amortization.  |
| ebitda_ratio | Earnings before interest, taxes, depreciation and amortization ratio.  |
| operating_income | Operating income.  |
| operating_income_ratio | Operating income ratio.  |
| interest_income | Interest income.  |
| interest_expense | Interest expense.  |
| total_other_income_expenses_net | Total other income expenses net.  |
| income_before_tax | Income before tax.  |
| income_before_tax_ratio | Income before tax ratio.  |
| income_tax_expense | Income tax expense.  |
| net_income | Net income.  |
| net_income_ratio | Net income ratio.  |
| eps | Earnings per share.  |
| eps_diluted | Earnings per share diluted.  |
| weighted_average_shares_outstanding | Weighted average shares outstanding.  |
| weighted_average_shares_outstanding_dil | Weighted average shares outstanding diluted.  |
| link | Link to the income statement.  |
| final_link | Final link to the income statement.  |
| reportedCurrency | Reporting currency. (provider: fmp) |
| fillingDate | Filling date. (provider: fmp) |
| accepted_date | Accepted date. (provider: fmp) |
| calendar_year | Calendar year. (provider: fmp) |
| operating_revenue | Operating revenue. (provider: intrinio) |
| operating_cost_of_revenue | Operating cost of revenue. (provider: intrinio) |
| net_income_continuing | Net income from continuing operations. (provider: intrinio) |
| net_income_to_common | Net income to common shareholders. (provider: intrinio) |
| cash_dividends_per_share | Cash dividends per share. (provider: intrinio) |
| other_income | Other income. (provider: intrinio) |
| weighted_ave_basic_diluted_shares_os | Weighted average basic and diluted shares outstanding. (provider: intrinio) |
| income_loss_from_continuing_operations_before_tax | Income/Loss From Continuing Operations After Tax (provider: polygon) |
| income_loss_from_continuing_operations_after_tax | Income (loss) from continuing operations after tax (provider: polygon) |
| benefits_costs_expenses | Benefits, costs and expenses (provider: polygon) |
| net_income_loss_attributable_to_noncontrolling_interest | Net income (loss) attributable to noncontrolling interest (provider: polygon) |
| net_income_loss_attributable_to_parent | Net income (loss) attributable to parent (provider: polygon) |
| net_income_loss_available_to_common_stockholders_basic | Net Income/Loss Available To Common Stockholders Basic (provider: polygon) |
| participating_securities_distributed_and_undistributed_earnings_loss_basic | Participating Securities Distributed And Undistributed Earnings Loss Basic (provider: polygon) |
| nonoperating_income_loss | Nonoperating Income Loss (provider: polygon) |
| preferred_stock_dividends_and_other_adjustments | Preferred stock dividends and other adjustments (provider: polygon) |
