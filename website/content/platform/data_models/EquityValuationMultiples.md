---
title: Equity Valuation Multiples
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EquityValuationMultiples` | `EquityValuationMultiplesQueryParams` | `EquityValuationMultiplesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.equity_valuation_multiples import (
EquityValuationMultiplesData,
EquityValuationMultiplesQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 100 | True |
| chart | bool | Whether to create a chart or not, by default False. | False | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| revenue_per_share_ttm | float | Revenue per share calculated as trailing twelve months. |
| net_income_per_share_ttm | float | Net income per share calculated as trailing twelve months. |
| operating_cash_flow_per_share_ttm | float | Operating cash flow per share calculated as trailing twelve months. |
| free_cash_flow_per_share_ttm | float | Free cash flow per share calculated as trailing twelve months. |
| cash_per_share_ttm | float | Cash per share calculated as trailing twelve months. |
| book_value_per_share_ttm | float | Book value per share calculated as trailing twelve months. |
| tangible_book_value_per_share_ttm | float | Tangible book value per share calculated as trailing twelve months. |
| shareholders_equity_per_share_ttm | float | Shareholders equity per share calculated as trailing twelve months. |
| interest_debt_per_share_ttm | float | Interest debt per share calculated as trailing twelve months. |
| market_cap_ttm | float | Market capitalization calculated as trailing twelve months. |
| enterprise_value_ttm | float | Enterprise value calculated as trailing twelve months. |
| pe_ratio_ttm | float | Price-to-earnings ratio (P/E ratio) calculated as trailing twelve months. |
| price_to_sales_ratio_ttm | float | Price-to-sales ratio calculated as trailing twelve months. |
| pocf_ratio_ttm | float | Price-to-operating cash flow ratio calculated as trailing twelve months. |
| pfcf_ratio_ttm | float | Price-to-free cash flow ratio calculated as trailing twelve months. |
| pb_ratio_ttm | float | Price-to-book ratio calculated as trailing twelve months. |
| ptb_ratio_ttm | float | Price-to-tangible book ratio calculated as trailing twelve months. |
| ev_to_sales_ttm | float | Enterprise value-to-sales ratio calculated as trailing twelve months. |
| enterprise_value_over_ebitda_ttm | float | Enterprise value-to-EBITDA ratio calculated as trailing twelve months. |
| ev_to_operating_cash_flow_ttm | float | Enterprise value-to-operating cash flow ratio calculated as trailing twelve months. |
| ev_to_free_cash_flow_ttm | float | Enterprise value-to-free cash flow ratio calculated as trailing twelve months. |
| earnings_yield_ttm | float | Earnings yield calculated as trailing twelve months. |
| free_cash_flow_yield_ttm | float | Free cash flow yield calculated as trailing twelve months. |
| debt_to_equity_ttm | float | Debt-to-equity ratio calculated as trailing twelve months. |
| debt_to_assets_ttm | float | Debt-to-assets ratio calculated as trailing twelve months. |
| net_debt_to_ebitda_ttm | float | Net debt-to-EBITDA ratio calculated as trailing twelve months. |
| current_ratio_ttm | float | Current ratio calculated as trailing twelve months. |
| interest_coverage_ttm | float | Interest coverage calculated as trailing twelve months. |
| income_quality_ttm | float | Income quality calculated as trailing twelve months. |
| dividend_yield_ttm | float | Dividend yield calculated as trailing twelve months. |
| dividend_yield_percentage_ttm | float | Dividend yield percentage calculated as trailing twelve months. |
| dividend_to_market_cap_ttm | float | Dividend to market capitalization ratio calculated as trailing twelve months. |
| dividend_per_share_ttm | float | Dividend per share calculated as trailing twelve months. |
| payout_ratio_ttm | float | Payout ratio calculated as trailing twelve months. |
| sales_general_and_administrative_to_revenue_ttm | float | Sales general and administrative expenses-to-revenue ratio calculated as trailing twelve months. |
| research_and_development_to_revenue_ttm | float | Research and development expenses-to-revenue ratio calculated as trailing twelve months. |
| intangibles_to_total_assets_ttm | float | Intangibles-to-total assets ratio calculated as trailing twelve months. |
| capex_to_operating_cash_flow_ttm | float | Capital expenditures-to-operating cash flow ratio calculated as trailing twelve months. |
| capex_to_revenue_ttm | float | Capital expenditures-to-revenue ratio calculated as trailing twelve months. |
| capex_to_depreciation_ttm | float | Capital expenditures-to-depreciation ratio calculated as trailing twelve months. |
| stock_based_compensation_to_revenue_ttm | float | Stock-based compensation-to-revenue ratio calculated as trailing twelve months. |
| graham_number_ttm | float | Graham number calculated as trailing twelve months. |
| roic_ttm | float | Return on invested capital calculated as trailing twelve months. |
| return_on_tangible_assets_ttm | float | Return on tangible assets calculated as trailing twelve months. |
| graham_net_net_ttm | float | Graham net-net working capital calculated as trailing twelve months. |
| working_capital_ttm | float | Working capital calculated as trailing twelve months. |
| tangible_asset_value_ttm | float | Tangible asset value calculated as trailing twelve months. |
| net_current_asset_value_ttm | float | Net current asset value calculated as trailing twelve months. |
| invested_capital_ttm | float | Invested capital calculated as trailing twelve months. |
| average_receivables_ttm | float | Average receivables calculated as trailing twelve months. |
| average_payables_ttm | float | Average payables calculated as trailing twelve months. |
| average_inventory_ttm | float | Average inventory calculated as trailing twelve months. |
| days_sales_outstanding_ttm | float | Days sales outstanding calculated as trailing twelve months. |
| days_payables_outstanding_ttm | float | Days payables outstanding calculated as trailing twelve months. |
| days_of_inventory_on_hand_ttm | float | Days of inventory on hand calculated as trailing twelve months. |
| receivables_turnover_ttm | float | Receivables turnover calculated as trailing twelve months. |
| payables_turnover_ttm | float | Payables turnover calculated as trailing twelve months. |
| inventory_turnover_ttm | float | Inventory turnover calculated as trailing twelve months. |
| roe_ttm | float | Return on equity calculated as trailing twelve months. |
| capex_per_share_ttm | float | Capital expenditures per share calculated as trailing twelve months. |
</TabItem>

</Tabs>
