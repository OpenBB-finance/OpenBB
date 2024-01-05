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
=OBB.EQUITY.FUNDAMENTAL.RATIOS(symbol;[provider];[period];[limit];[with_ttm];[fiscal_year])
```

---

## Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.RATIOS("AAPL")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **False** |
| provider | Text | Options: fmp, intrinio, defaults to fmp. | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| with_ttm | Boolean | Include trailing twelve months (TTM) data. (provider: fmp, intrinio) | True |
| fiscal_year | Number | The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| period_ending | The date of the data.  |
| fiscal_period | Period of the financial ratios.  |
| fiscal_year | Fiscal year.  |
| current_ratio | Current ratio. (provider: fmp) |
| quick_ratio | Quick ratio. (provider: fmp) |
| cash_ratio | Cash ratio. (provider: fmp) |
| days_of_sales_outstanding | Days of sales outstanding. (provider: fmp) |
| days_of_inventory_outstanding | Days of inventory outstanding. (provider: fmp) |
| operating_cycle | Operating cycle. (provider: fmp) |
| days_of_payables_outstanding | Days of payables outstanding. (provider: fmp) |
| cash_conversion_cycle | Cash conversion cycle. (provider: fmp) |
| gross_profit_margin | Gross profit margin. (provider: fmp) |
| operating_profit_margin | Operating profit margin. (provider: fmp) |
| pretax_profit_margin | Pretax profit margin. (provider: fmp) |
| net_profit_margin | Net profit margin. (provider: fmp) |
| effective_tax_rate | Effective tax rate. (provider: fmp) |
| return_on_assets | Return on assets. (provider: fmp) |
| return_on_equity | Return on equity. (provider: fmp) |
| return_on_capital_employed | Return on capital employed. (provider: fmp) |
| net_income_per_ebt | Net income per EBT. (provider: fmp) |
| ebt_per_ebit | EBT per EBIT. (provider: fmp) |
| ebit_per_revenue | EBIT per revenue. (provider: fmp) |
| debt_ratio | Debt ratio. (provider: fmp) |
| debt_equity_ratio | Debt equity ratio. (provider: fmp) |
| long_term_debt_to_capitalization | Long term debt to capitalization. (provider: fmp) |
| total_debt_to_capitalization | Total debt to capitalization. (provider: fmp) |
| interest_coverage | Interest coverage. (provider: fmp) |
| cash_flow_to_debt_ratio | Cash flow to debt ratio. (provider: fmp) |
| company_equity_multiplier | Company equity multiplier. (provider: fmp) |
| receivables_turnover | Receivables turnover. (provider: fmp) |
| payables_turnover | Payables turnover. (provider: fmp) |
| inventory_turnover | Inventory turnover. (provider: fmp) |
| fixed_asset_turnover | Fixed asset turnover. (provider: fmp) |
| asset_turnover | Asset turnover. (provider: fmp) |
| operating_cash_flow_per_share | Operating cash flow per share. (provider: fmp) |
| free_cash_flow_per_share | Free cash flow per share. (provider: fmp) |
| cash_per_share | Cash per share. (provider: fmp) |
| payout_ratio | Payout ratio. (provider: fmp) |
| operating_cash_flow_sales_ratio | Operating cash flow sales ratio. (provider: fmp) |
| free_cash_flow_operating_cash_flow_ratio | Free cash flow operating cash flow ratio. (provider: fmp) |
| cash_flow_coverage_ratios | Cash flow coverage ratios. (provider: fmp) |
| short_term_coverage_ratios | Short term coverage ratios. (provider: fmp) |
| capital_expenditure_coverage_ratio | Capital expenditure coverage ratio. (provider: fmp) |
| dividend_paid_and_capex_coverage_ratio | Dividend paid and capex coverage ratio. (provider: fmp) |
| dividend_payout_ratio | Dividend payout ratio. (provider: fmp) |
| price_book_value_ratio | Price book value ratio. (provider: fmp) |
| price_to_book_ratio | Price to book ratio. (provider: fmp) |
| price_to_sales_ratio | Price to sales ratio. (provider: fmp) |
| price_earnings_ratio | Price earnings ratio. (provider: fmp) |
| price_to_free_cash_flows_ratio | Price to free cash flows ratio. (provider: fmp) |
| price_to_operating_cash_flows_ratio | Price to operating cash flows ratio. (provider: fmp) |
| price_cash_flow_ratio | Price cash flow ratio. (provider: fmp) |
| price_earnings_to_growth_ratio | Price earnings to growth ratio. (provider: fmp) |
| price_sales_ratio | Price sales ratio. (provider: fmp) |
| dividend_yield | Dividend yield. (provider: fmp) |
| dividend_yield_percentage | Dividend yield percentage. (provider: fmp) |
| dividend_per_share | Dividend per share. (provider: fmp) |
| enterprise_value_multiple | Enterprise value multiple. (provider: fmp) |
| price_fair_value | Price fair value. (provider: fmp) |
