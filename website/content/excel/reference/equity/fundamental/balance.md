<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Balance Sheet. Balance sheet statement.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.BALANCE(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp, intrinio, polygon | true |
| period | string | Time period of the data to return. | true |
| limit | number | The number of data entries to return. | true |
| cik | string | Central Index Key (CIK) of the company. (provider: fmp) | true |
| filing_date | string | Filing date of the financial statement. (provider: polygon) | true |
| filing_date_lt | string | Filing date less than the given date. (provider: polygon) | true |
| filing_date_lte | string | Filing date less than or equal to the given date. (provider: polygon) | true |
| filing_date_gt | string | Filing date greater than the given date. (provider: polygon) | true |
| filing_date_gte | string | Filing date greater than or equal to the given date. (provider: polygon) | true |
| period_of_report_date | string | Period of report date of the financial statement. (provider: polygon) | true |
| period_of_report_date_lt | string | Period of report date less than the given date. (provider: polygon) | true |
| period_of_report_date_lte | string | Period of report date less than or equal to the given date. (provider: polygon) | true |
| period_of_report_date_gt | string | Period of report date greater than the given date. (provider: polygon) | true |
| period_of_report_date_gte | string | Period of report date greater than or equal to the given date. (provider: polygon) | true |
| include_sources | boolean | Whether to include the sources of the financial statement. (provider: polygon) | true |
| order | string | Order of the financial statement. (provider: polygon) | true |
| sort | string | Sort of the financial statement. (provider: polygon) | true |

## Data

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
