<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Income Statement. Report on a company's financial performance.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.INCOME(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp, intrinio, polygon | true |
| period | string | Time period of the data to return. | true |
| limit | number | The number of data entries to return. | true |
| cik | string | The CIK of the company if no symbol is provided. (provider: fmp) | true |
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
| income_loss_from_continuing_operations_before_tax | Income/Loss From Continuing Operations After Tax (provider: polygon) |
| income_loss_from_continuing_operations_after_tax | Income (loss) from continuing operations after tax (provider: polygon) |
| benefits_costs_expenses | Benefits, costs and expenses (provider: polygon) |
| net_income_loss_attributable_to_noncontrolling_interest | Net income (loss) attributable to noncontrolling interest (provider: polygon) |
| net_income_loss_attributable_to_parent | Net income (loss) attributable to parent (provider: polygon) |
| net_income_loss_available_to_common_stockholders_basic | Net Income/Loss Available To Common Stockholders Basic (provider: polygon) |
| participating_securities_distributed_and_undistributed_earnings_loss_basic | Participating Securities Distributed And Undistributed Earnings Loss Basic (provider: polygon) |
| nonoperating_income_loss | Nonoperating Income Loss (provider: polygon) |
| preferred_stock_dividends_and_other_adjustments | Preferred stock dividends and other adjustments (provider: polygon) |
