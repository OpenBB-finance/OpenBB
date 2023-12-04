---
title: balance
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
=OBB.EQUITY.FUNDAMENTAL.BALANCE(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio, polygon | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| cik | Text | Central Index Key (CIK) of the company. (provider: fmp) | True |
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
| date | The date of the data.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| currency | Reporting currency.  |
| filling_date | Filling date.  |
| accepted_date | Accepted date.  |
| period | Reporting period of the statement.  |
| cash_and_cash_equivalents | Cash and cash equivalents  |
| short_term_investments | Short-term investments  |
| long_term_investments | Long-term investments  |
| inventory | Inventory  |
| net_receivables | Receivables, net  |
| marketable_securities | Marketable securities  |
| property_plant_equipment_net | Property, plant and equipment, net  |
| goodwill | Goodwill  |
| assets | Total assets  |
| current_assets | Total current assets  |
| other_current_assets | Other current assets  |
| intangible_assets | Intangible assets  |
| tax_assets | Accrued income taxes  |
| non_current_assets | Total non-current assets  |
| other_non_current_assets | Other non-current assets  |
| account_payables | Accounts payable  |
| tax_payables | Accrued income taxes  |
| deferred_revenue | Accrued income taxes, other deferred revenue  |
| other_assets | Other assets  |
| total_assets | Total assets  |
| long_term_debt | Long-term debt, Operating lease obligations, Long-term finance lease obligations  |
| short_term_debt | Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year  |
| liabilities | Total liabilities  |
| other_current_liabilities | Other current liabilities  |
| current_liabilities | Total current liabilities  |
| total_liabilities_and_total_equity | Total liabilities and total equity  |
| other_non_current_liabilities | Other non-current liabilities  |
| non_current_liabilities | Total non-current liabilities  |
| total_liabilities_and_stockholders_equity | Total liabilities and stockholders' equity  |
| other_stockholder_equity | Other stockholders equity  |
| total_stockholders_equity | Total stockholders' equity  |
| other_liabilities | Other liabilities  |
| total_liabilities | Total liabilities  |
| common_stock | Common stock  |
| preferred_stock | Preferred stock  |
| accumulated_other_comprehensive_income_loss | Accumulated other comprehensive income (loss)  |
| retained_earnings | Retained earnings  |
| minority_interest | Minority interest  |
| total_equity | Total equity  |
| calendar_year | Calendar Year (provider: fmp) |
| cash_and_short_term_investments | Cash and Short Term Investments (provider: fmp) |
| goodwill_and_intangible_assets | Goodwill and Intangible Assets (provider: fmp) |
| deferred_revenue_non_current | Deferred Revenue Non Current (provider: fmp) |
| total_investments | Total investments (provider: fmp) |
| capital_lease_obligations | Capital lease obligations (provider: fmp) |
| deferred_tax_liabilities_non_current | Deferred Tax Liabilities Non Current (provider: fmp) |
| total_debt | Total Debt (provider: fmp) |
| net_debt | Net Debt (provider: fmp) |
| link | Link to the statement. (provider: fmp) |
| final_link | Link to the final statement. (provider: fmp) |
| note_receivable | Notes and lease receivable. (provider: intrinio) |
| net_ppe | Plant, property, and equipment, net. (provider: intrinio) |
| total_noncurrent_assets | Total noncurrent assets. (provider: intrinio) |
| current_deferred_revenue | Current deferred revenue. (provider: intrinio) |
| other_noncurrent_liabilities | Other noncurrent operating liabilities. (provider: intrinio) |
| total_noncurrent_liabilities | Total noncurrent liabilities. (provider: intrinio) |
| commitments_and_contingencies | Commitments and contingencies. (provider: intrinio) |
| aoci | Accumulated other comprehensive income / (loss). (provider: intrinio) |
| total_common_equity | Total common equity. (provider: intrinio) |
| total_equity_and_noncontrolling_interests | Total equity & noncontrolling interests. (provider: intrinio) |
| total_liabilities_and_equity | Total liabilities & shareholders' equity. (provider: intrinio) |
