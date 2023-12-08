---
title: metrics
description: Learn about key metrics for a given company using the `obb.equity.fundamental.metrics`
  Python function. This API endpoint provides data such as revenue per share, net
  income per share, market capitalization, price-to-earnings ratio, and more. Explore
  the available parameters and returned data to analyze financial performance. Full
  documentation and usage examples available.
keywords: 
- key metrics
- python function
- documentation
- API
- parameters
- returns
- data
- symbol
- period
- limit
- provider
- with_ttm
- revenue per share
- net income per share
- operating cash flow per share
- free cash flow per share
- cash per share
- book value per share
- tangible book value per share
- shareholders equity per share
- interest debt per share
- market capitalization
- enterprise value
- price-to-earnings ratio
- price-to-sales ratio
- price-to-operating cash flow ratio
- price-to-free cash flow ratio
- price-to-book ratio
- price-to-tangible book ratio
- earnings yield
- free cash flow yield
- debt-to-equity ratio
- debt-to-assets ratio
- net debt-to-EBITDA ratio
- current ratio
- interest coverage
- income quality
- dividend yield
- payout ratio
- sales general and administrative expenses-to-revenue ratio
- research and development expenses-to-revenue ratio
- intangibles-to-total assets ratio
- capital expenditures-to-operating cash flow ratio
- capital expenditures-to-revenue ratio
- capital expenditures-to-depreciation ratio
- stock-based compensation-to-revenue ratio
- Graham number
- return on invested capital
- return on tangible assets
- Graham net-net working capital
- working capital
- tangible asset value
- net current asset value
- invested capital
- average receivables
- average payables
- average inventory
- days sales outstanding
- days payables outstanding
- days of inventory on hand
- receivables turnover
- payables turnover
- inventory turnover
- return on equity
- capital expenditures per share
- calendar year
---

<!-- markdownlint-disable MD041 -->

Key Metrics. Key metrics for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.METRICS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio | True |
| period | Text | Time period of the data to return. | True |
| limit | Number | The number of data entries to return. | True |
| with_ttm | Boolean | Include trailing twelve months (TTM) data. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| market_cap | Market capitalization  |
| pe_ratio | Price-to-earnings ratio (P/E ratio)  |
| date | The date of the data. (provider: fmp) |
| period | Period of the data. (provider: fmp) |
| calendar_year | Calendar year. (provider: fmp) |
| revenue_per_share | Revenue per share (provider: fmp) |
| net_income_per_share | Net income per share (provider: fmp) |
| operating_cash_flow_per_share | Operating cash flow per share (provider: fmp) |
| free_cash_flow_per_share | Free cash flow per share (provider: fmp) |
| cash_per_share | Cash per share (provider: fmp) |
| book_value_per_share | Book value per share (provider: fmp) |
| tangible_book_value_per_share | Tangible book value per share (provider: fmp) |
| shareholders_equity_per_share | Shareholders equity per share (provider: fmp) |
| interest_debt_per_share | Interest debt per share (provider: fmp) |
| enterprise_value | Enterprise value (provider: fmp) |
| price_to_sales_ratio | Price-to-sales ratio (provider: fmp) |
| pocf_ratio | Price-to-operating cash flow ratio (provider: fmp) |
| pfcf_ratio | Price-to-free cash flow ratio (provider: fmp) |
| pb_ratio | Price-to-book ratio (provider: fmp) |
| ptb_ratio | Price-to-tangible book ratio (provider: fmp) |
| ev_to_sales | Enterprise value-to-sales ratio (provider: fmp) |
| enterprise_value_over_ebitda | Enterprise value-to-EBITDA ratio (provider: fmp) |
| ev_to_operating_cash_flow | Enterprise value-to-operating cash flow ratio (provider: fmp) |
| ev_to_free_cash_flow | Enterprise value-to-free cash flow ratio (provider: fmp) |
| earnings_yield | Earnings yield (provider: fmp) |
| free_cash_flow_yield | Free cash flow yield (provider: fmp) |
| debt_to_equity | Debt-to-equity ratio (provider: fmp) |
| debt_to_assets | Debt-to-assets ratio (provider: fmp) |
| net_debt_to_ebitda | Net debt-to-EBITDA ratio (provider: fmp) |
| current_ratio | Current ratio (provider: fmp) |
| interest_coverage | Interest coverage (provider: fmp) |
| income_quality | Income quality (provider: fmp) |
| dividend_yield | Dividend yield (provider: fmp, intrinio) |
| payout_ratio | Payout ratio (provider: fmp) |
| sales_general_and_administrative_to_revenue | Sales general and administrative expenses-to-revenue ratio (provider: fmp) |
| research_and_development_to_revenue | Research and development expenses-to-revenue ratio (provider: fmp) |
| intangibles_to_total_assets | Intangibles-to-total assets ratio (provider: fmp) |
| capex_to_operating_cash_flow | Capital expenditures-to-operating cash flow ratio (provider: fmp) |
| capex_to_revenue | Capital expenditures-to-revenue ratio (provider: fmp) |
| capex_to_depreciation | Capital expenditures-to-depreciation ratio (provider: fmp) |
| stock_based_compensation_to_revenue | Stock-based compensation-to-revenue ratio (provider: fmp) |
| graham_number | Graham number (provider: fmp) |
| roic | Return on invested capital (provider: fmp) |
| return_on_tangible_assets | Return on tangible assets (provider: fmp) |
| graham_net_net | Graham net-net working capital (provider: fmp) |
| working_capital | Working capital (provider: fmp) |
| tangible_asset_value | Tangible asset value (provider: fmp) |
| net_current_asset_value | Net current asset value (provider: fmp) |
| invested_capital | Invested capital (provider: fmp) |
| average_receivables | Average receivables (provider: fmp) |
| average_payables | Average payables (provider: fmp) |
| average_inventory | Average inventory (provider: fmp) |
| days_sales_outstanding | Days sales outstanding (provider: fmp) |
| days_payables_outstanding | Days payables outstanding (provider: fmp) |
| days_of_inventory_on_hand | Days of inventory on hand (provider: fmp) |
| receivables_turnover | Receivables turnover (provider: fmp) |
| payables_turnover | Payables turnover (provider: fmp) |
| inventory_turnover | Inventory turnover (provider: fmp) |
| roe | Return on equity (provider: fmp) |
| capex_per_share | Capital expenditures per share (provider: fmp) |
| beta | Beta (provider: intrinio) |
| volume | Volume (provider: intrinio) |
| fifty_two_week_high | 52 week high (provider: intrinio) |
| fifty_two_week_low | 52 week low (provider: intrinio) |
