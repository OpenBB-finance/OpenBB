---
title: Stock Multiples
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `StockMultiples` | `StockMultiplesQueryParams` | `StockMultiplesData` |

### Import Statement

```python
from openbb_provider.standard_models.stock_multiples import (
StockMultiplesData,
StockMultiplesQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| limit | Union[int] | The number of data entries to return. | 100 | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| revenue_per_share_ttm | Union[float] | Revenue per share calculated as trailing twelve months. |
| net_income_per_share_ttm | Union[float] | Net income per share calculated as trailing twelve months. |
| operating_cash_flow_per_share_ttm | Union[float] | Operating cash flow per share calculated as trailing twelve months. |
| free_cash_flow_per_share_ttm | Union[float] | Free cash flow per share calculated as trailing twelve months. |
| cash_per_share_ttm | Union[float] | Cash per share calculated as trailing twelve months. |
| book_value_per_share_ttm | Union[float] | Book value per share calculated as trailing twelve months. |
| tangible_book_value_per_share_ttm | Union[float] | Tangible book value per share calculated as trailing twelve months. |
| shareholders_equity_per_share_ttm | Union[float] | Shareholders equity per share calculated as trailing twelve months. |
| interest_debt_per_share_ttm | Union[float] | Interest debt per share calculated as trailing twelve months. |
| market_cap_ttm | Union[float] | Market capitalization calculated as trailing twelve months. |
| enterprise_value_ttm | Union[float] | Enterprise value calculated as trailing twelve months. |
| pe_ratio_ttm | Union[float] | Price-to-earnings ratio (P/E ratio) calculated as trailing twelve months. |
| price_to_sales_ratio_ttm | Union[float] | Price-to-sales ratio calculated as trailing twelve months. |
| pocf_ratio_ttm | Union[float] | Price-to-operating cash flow ratio calculated as trailing twelve months. |
| pfcf_ratio_ttm | Union[float] | Price-to-free cash flow ratio calculated as trailing twelve months. |
| pb_ratio_ttm | Union[float] | Price-to-book ratio calculated as trailing twelve months. |
| ptb_ratio_ttm | Union[float] | Price-to-tangible book ratio calculated as trailing twelve months. |
| ev_to_sales_ttm | Union[float] | Enterprise value-to-sales ratio calculated as trailing twelve months. |
| enterprise_value_over_ebitda_ttm | Union[float] | Enterprise value-to-EBITDA ratio calculated as trailing twelve months. |
| ev_to_operating_cash_flow_ttm | Union[float] | Enterprise value-to-operating cash flow ratio calculated as trailing twelve months. |
| ev_to_free_cash_flow_ttm | Union[float] | Enterprise value-to-free cash flow ratio calculated as trailing twelve months. |
| earnings_yield_ttm | Union[float] | Earnings yield calculated as trailing twelve months. |
| free_cash_flow_yield_ttm | Union[float] | Free cash flow yield calculated as trailing twelve months. |
| debt_to_equity_ttm | Union[float] | Debt-to-equity ratio calculated as trailing twelve months. |
| debt_to_assets_ttm | Union[float] | Debt-to-assets ratio calculated as trailing twelve months. |
| net_debt_to_ebitda_ttm | Union[float] | Net debt-to-EBITDA ratio calculated as trailing twelve months. |
| current_ratio_ttm | Union[float] | Current ratio calculated as trailing twelve months. |
| interest_coverage_ttm | Union[float] | Interest coverage calculated as trailing twelve months. |
| income_quality_ttm | Union[float] | Income quality calculated as trailing twelve months. |
| dividend_yield_ttm | Union[float] | Dividend yield calculated as trailing twelve months. |
| dividend_yield_percentage_ttm | Union[float] | Dividend yield percentage calculated as trailing twelve months. |
| dividend_to_market_cap_ttm | Union[float] | Dividend to market capitalization ratio calculated as trailing twelve months. |
| dividend_per_share_ttm | Union[float] | Dividend per share calculated as trailing twelve months. |
| payout_ratio_ttm | Union[float] | Payout ratio calculated as trailing twelve months. |
| sales_general_and_administrative_to_revenue_ttm | Union[float] | Sales general and administrative expenses-to-revenue ratio calculated as trailing twelve months. |
| research_and_development_to_revenue_ttm | Union[float] | Research and development expenses-to-revenue ratio calculated as trailing twelve months. |
| intangibles_to_total_assets_ttm | Union[float] | Intangibles-to-total assets ratio calculated as trailing twelve months. |
| capex_to_operating_cash_flow_ttm | Union[float] | Capital expenditures-to-operating cash flow ratio calculated as trailing twelve months. |
| capex_to_revenue_ttm | Union[float] | Capital expenditures-to-revenue ratio calculated as trailing twelve months. |
| capex_to_depreciation_ttm | Union[float] | Capital expenditures-to-depreciation ratio calculated as trailing twelve months. |
| stock_based_compensation_to_revenue_ttm | Union[float] | Stock-based compensation-to-revenue ratio calculated as trailing twelve months. |
| graham_number_ttm | Union[float] | Graham number calculated as trailing twelve months. |
| roic_ttm | Union[float] | Return on invested capital calculated as trailing twelve months. |
| return_on_tangible_assets_ttm | Union[float] | Return on tangible assets calculated as trailing twelve months. |
| graham_net_net_ttm | Union[float] | Graham net-net working capital calculated as trailing twelve months. |
| working_capital_ttm | Union[float] | Working capital calculated as trailing twelve months. |
| tangible_asset_value_ttm | Union[float] | Tangible asset value calculated as trailing twelve months. |
| net_current_asset_value_ttm | Union[float] | Net current asset value calculated as trailing twelve months. |
| invested_capital_ttm | Union[float] | Invested capital calculated as trailing twelve months. |
| average_receivables_ttm | Union[float] | Average receivables calculated as trailing twelve months. |
| average_payables_ttm | Union[float] | Average payables calculated as trailing twelve months. |
| average_inventory_ttm | Union[float] | Average inventory calculated as trailing twelve months. |
| days_sales_outstanding_ttm | Union[float] | Days sales outstanding calculated as trailing twelve months. |
| days_payables_outstanding_ttm | Union[float] | Days payables outstanding calculated as trailing twelve months. |
| days_of_inventory_on_hand_ttm | Union[float] | Days of inventory on hand calculated as trailing twelve months. |
| receivables_turnover_ttm | Union[float] | Receivables turnover calculated as trailing twelve months. |
| payables_turnover_ttm | Union[float] | Payables turnover calculated as trailing twelve months. |
| inventory_turnover_ttm | Union[float] | Inventory turnover calculated as trailing twelve months. |
| roe_ttm | Union[float] | Return on equity calculated as trailing twelve months. |
| capex_per_share_ttm | Union[float] | Capital expenditures per share calculated as trailing twelve months. |
</TabItem>

</Tabs>

