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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Key Metrics. Key metrics for a given company.

```python wordwrap
obb.equity.fundamental.metrics(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: int = 100, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| with_ttm | bool | Include trailing twelve months (TTM) data. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[KeyMetrics]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| period | str | Period of the data. |
| revenue_per_share | float | Revenue per share |
| net_income_per_share | float | Net income per share |
| operating_cash_flow_per_share | float | Operating cash flow per share |
| free_cash_flow_per_share | float | Free cash flow per share |
| cash_per_share | float | Cash per share |
| book_value_per_share | float | Book value per share |
| tangible_book_value_per_share | float | Tangible book value per share |
| shareholders_equity_per_share | float | Shareholders equity per share |
| interest_debt_per_share | float | Interest debt per share |
| market_cap | float | Market capitalization |
| enterprise_value | float | Enterprise value |
| pe_ratio | float | Price-to-earnings ratio (P/E ratio) |
| price_to_sales_ratio | float | Price-to-sales ratio |
| pocf_ratio | float | Price-to-operating cash flow ratio |
| pfcf_ratio | float | Price-to-free cash flow ratio |
| pb_ratio | float | Price-to-book ratio |
| ptb_ratio | float | Price-to-tangible book ratio |
| ev_to_sales | float | Enterprise value-to-sales ratio |
| enterprise_value_over_ebitda | float | Enterprise value-to-EBITDA ratio |
| ev_to_operating_cash_flow | float | Enterprise value-to-operating cash flow ratio |
| ev_to_free_cash_flow | float | Enterprise value-to-free cash flow ratio |
| earnings_yield | float | Earnings yield |
| free_cash_flow_yield | float | Free cash flow yield |
| debt_to_equity | float | Debt-to-equity ratio |
| debt_to_assets | float | Debt-to-assets ratio |
| net_debt_to_ebitda | float | Net debt-to-EBITDA ratio |
| current_ratio | float | Current ratio |
| interest_coverage | float | Interest coverage |
| income_quality | float | Income quality |
| dividend_yield | float | Dividend yield |
| payout_ratio | float | Payout ratio |
| sales_general_and_administrative_to_revenue | float | Sales general and administrative expenses-to-revenue ratio |
| research_and_development_to_revenue | float | Research and development expenses-to-revenue ratio |
| intangibles_to_total_assets | float | Intangibles-to-total assets ratio |
| capex_to_operating_cash_flow | float | Capital expenditures-to-operating cash flow ratio |
| capex_to_revenue | float | Capital expenditures-to-revenue ratio |
| capex_to_depreciation | float | Capital expenditures-to-depreciation ratio |
| stock_based_compensation_to_revenue | float | Stock-based compensation-to-revenue ratio |
| graham_number | float | Graham number |
| roic | float | Return on invested capital |
| return_on_tangible_assets | float | Return on tangible assets |
| graham_net_net | float | Graham net-net working capital |
| working_capital | float | Working capital |
| tangible_asset_value | float | Tangible asset value |
| net_current_asset_value | float | Net current asset value |
| invested_capital | float | Invested capital |
| average_receivables | float | Average receivables |
| average_payables | float | Average payables |
| average_inventory | float | Average inventory |
| days_sales_outstanding | float | Days sales outstanding |
| days_payables_outstanding | float | Days payables outstanding |
| days_of_inventory_on_hand | float | Days of inventory on hand |
| receivables_turnover | float | Receivables turnover |
| payables_turnover | float | Payables turnover |
| inventory_turnover | float | Inventory turnover |
| roe | float | Return on equity |
| capex_per_share | float | Capital expenditures per share |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| period | str | Period of the data. |
| revenue_per_share | float | Revenue per share |
| net_income_per_share | float | Net income per share |
| operating_cash_flow_per_share | float | Operating cash flow per share |
| free_cash_flow_per_share | float | Free cash flow per share |
| cash_per_share | float | Cash per share |
| book_value_per_share | float | Book value per share |
| tangible_book_value_per_share | float | Tangible book value per share |
| shareholders_equity_per_share | float | Shareholders equity per share |
| interest_debt_per_share | float | Interest debt per share |
| market_cap | float | Market capitalization |
| enterprise_value | float | Enterprise value |
| pe_ratio | float | Price-to-earnings ratio (P/E ratio) |
| price_to_sales_ratio | float | Price-to-sales ratio |
| pocf_ratio | float | Price-to-operating cash flow ratio |
| pfcf_ratio | float | Price-to-free cash flow ratio |
| pb_ratio | float | Price-to-book ratio |
| ptb_ratio | float | Price-to-tangible book ratio |
| ev_to_sales | float | Enterprise value-to-sales ratio |
| enterprise_value_over_ebitda | float | Enterprise value-to-EBITDA ratio |
| ev_to_operating_cash_flow | float | Enterprise value-to-operating cash flow ratio |
| ev_to_free_cash_flow | float | Enterprise value-to-free cash flow ratio |
| earnings_yield | float | Earnings yield |
| free_cash_flow_yield | float | Free cash flow yield |
| debt_to_equity | float | Debt-to-equity ratio |
| debt_to_assets | float | Debt-to-assets ratio |
| net_debt_to_ebitda | float | Net debt-to-EBITDA ratio |
| current_ratio | float | Current ratio |
| interest_coverage | float | Interest coverage |
| income_quality | float | Income quality |
| dividend_yield | float | Dividend yield |
| payout_ratio | float | Payout ratio |
| sales_general_and_administrative_to_revenue | float | Sales general and administrative expenses-to-revenue ratio |
| research_and_development_to_revenue | float | Research and development expenses-to-revenue ratio |
| intangibles_to_total_assets | float | Intangibles-to-total assets ratio |
| capex_to_operating_cash_flow | float | Capital expenditures-to-operating cash flow ratio |
| capex_to_revenue | float | Capital expenditures-to-revenue ratio |
| capex_to_depreciation | float | Capital expenditures-to-depreciation ratio |
| stock_based_compensation_to_revenue | float | Stock-based compensation-to-revenue ratio |
| graham_number | float | Graham number |
| roic | float | Return on invested capital |
| return_on_tangible_assets | float | Return on tangible assets |
| graham_net_net | float | Graham net-net working capital |
| working_capital | float | Working capital |
| tangible_asset_value | float | Tangible asset value |
| net_current_asset_value | float | Net current asset value |
| invested_capital | float | Invested capital |
| average_receivables | float | Average receivables |
| average_payables | float | Average payables |
| average_inventory | float | Average inventory |
| days_sales_outstanding | float | Days sales outstanding |
| days_payables_outstanding | float | Days payables outstanding |
| days_of_inventory_on_hand | float | Days of inventory on hand |
| receivables_turnover | float | Receivables turnover |
| payables_turnover | float | Payables turnover |
| inventory_turnover | float | Inventory turnover |
| roe | float | Return on equity |
| capex_per_share | float | Capital expenditures per share |
| calendar_year | int | Calendar year. |
</TabItem>

</Tabs>

