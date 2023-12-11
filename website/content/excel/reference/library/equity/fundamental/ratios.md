---
title: ratios
description: Learn about financial ratios for a given company over time. Explore various
  equity ratios, such as current ratio, quick ratio, and cash conversion cycle. Understand
  key profitability metrics like return on equity and profit margin. Analyze debt
  ratios, inventory turnover, and operating and free cash flows. Evaluate the price
  to earnings ratio and dividend yield.
keywords: 
- financial ratios
- company ratios
- ratios over time
- equity ratios
- current ratio
- quick ratio
- cash conversion cycle
- return on equity
- profit margin
- debt ratio
- inventory turnover
- operating cash flow
- free cash flow
- price to earnings ratio
- dividend yield
---

<!-- markdownlint-disable MD041 -->

Extensive set of ratios over time. Financial ratios for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.RATIOS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| with_ttm | Boolean | Include trailing twelve months (TTM) data. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| period | Period of the financial ratios.  |
| current_ratio | Current ratio.  |
| quick_ratio | Quick ratio.  |
| cash_ratio | Cash ratio.  |
| days_of_sales_outstanding | Days of sales outstanding.  |
| days_of_inventory_outstanding | Days of inventory outstanding.  |
| operating_cycle | Operating cycle.  |
| days_of_payables_outstanding | Days of payables outstanding.  |
| cash_conversion_cycle | Cash conversion cycle.  |
| gross_profit_margin | Gross profit margin.  |
| operating_profit_margin | Operating profit margin.  |
| pretax_profit_margin | Pretax profit margin.  |
| net_profit_margin | Net profit margin.  |
| effective_tax_rate | Effective tax rate.  |
| return_on_assets | Return on assets.  |
| return_on_equity | Return on equity.  |
| return_on_capital_employed | Return on capital employed.  |
| net_income_per_ebt | Net income per EBT.  |
| ebt_per_ebit | EBT per EBIT.  |
| ebit_per_revenue | EBIT per revenue.  |
| debt_ratio | Debt ratio.  |
| debt_equity_ratio | Debt equity ratio.  |
| long_term_debt_to_capitalization | Long term debt to capitalization.  |
| total_debt_to_capitalization | Total debt to capitalization.  |
| interest_coverage | Interest coverage.  |
| cash_flow_to_debt_ratio | Cash flow to debt ratio.  |
| company_equity_multiplier | Company equity multiplier.  |
| receivables_turnover | Receivables turnover.  |
| payables_turnover | Payables turnover.  |
| inventory_turnover | Inventory turnover.  |
| fixed_asset_turnover | Fixed asset turnover.  |
| asset_turnover | Asset turnover.  |
| operating_cash_flow_per_share | Operating cash flow per share.  |
| free_cash_flow_per_share | Free cash flow per share.  |
| cash_per_share | Cash per share.  |
| payout_ratio | Payout ratio.  |
| operating_cash_flow_sales_ratio | Operating cash flow sales ratio.  |
| free_cash_flow_operating_cash_flow_ratio | Free cash flow operating cash flow ratio.  |
| cash_flow_coverage_ratios | Cash flow coverage ratios.  |
| short_term_coverage_ratios | Short term coverage ratios.  |
| capital_expenditure_coverage_ratio | Capital expenditure coverage ratio.  |
| dividend_paid_and_capex_coverage_ratio | Dividend paid and capex coverage ratio.  |
| dividend_payout_ratio | Dividend payout ratio.  |
| price_book_value_ratio | Price book value ratio.  |
| price_to_book_ratio | Price to book ratio.  |
| price_to_sales_ratio | Price to sales ratio.  |
| price_earnings_ratio | Price earnings ratio.  |
| price_to_free_cash_flows_ratio | Price to free cash flows ratio.  |
| price_to_operating_cash_flows_ratio | Price to operating cash flows ratio.  |
| price_cash_flow_ratio | Price cash flow ratio.  |
| price_earnings_to_growth_ratio | Price earnings to growth ratio.  |
| price_sales_ratio | Price sales ratio.  |
| dividend_yield | Dividend yield.  |
| dividend_yield_percentage | Dividend yield percentage.  |
| dividend_per_share | Dividend per share.  |
| enterprise_value_multiple | Enterprise value multiple.  |
| price_fair_value | Price fair value.  |
