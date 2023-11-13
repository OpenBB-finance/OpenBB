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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Extensive set of ratios over time. Financial ratios for a given company.

```python wordwrap
obb.equity.fundamental.ratios(symbol: Union[str, List[str]], period: Literal[str] = annual, limit: int = 12, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| with_ttm | bool | Include trailing twelve months (TTM) data. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[FinancialRatios]
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
| date | str | The date of the data. |
| period | str | Period of the financial ratios. |
| current_ratio | float | Current ratio. |
| quick_ratio | float | Quick ratio. |
| cash_ratio | float | Cash ratio. |
| days_of_sales_outstanding | float | Days of sales outstanding. |
| days_of_inventory_outstanding | float | Days of inventory outstanding. |
| operating_cycle | float | Operating cycle. |
| days_of_payables_outstanding | float | Days of payables outstanding. |
| cash_conversion_cycle | float | Cash conversion cycle. |
| gross_profit_margin | float | Gross profit margin. |
| operating_profit_margin | float | Operating profit margin. |
| pretax_profit_margin | float | Pretax profit margin. |
| net_profit_margin | float | Net profit margin. |
| effective_tax_rate | float | Effective tax rate. |
| return_on_assets | float | Return on assets. |
| return_on_equity | float | Return on equity. |
| return_on_capital_employed | float | Return on capital employed. |
| net_income_per_ebt | float | Net income per EBT. |
| ebt_per_ebit | float | EBT per EBIT. |
| ebit_per_revenue | float | EBIT per revenue. |
| debt_ratio | float | Debt ratio. |
| debt_equity_ratio | float | Debt equity ratio. |
| long_term_debt_to_capitalization | float | Long term debt to capitalization. |
| total_debt_to_capitalization | float | Total debt to capitalization. |
| interest_coverage | float | Interest coverage. |
| cash_flow_to_debt_ratio | float | Cash flow to debt ratio. |
| company_equity_multiplier | float | Company equity multiplier. |
| receivables_turnover | float | Receivables turnover. |
| payables_turnover | float | Payables turnover. |
| inventory_turnover | float | Inventory turnover. |
| fixed_asset_turnover | float | Fixed asset turnover. |
| asset_turnover | float | Asset turnover. |
| operating_cash_flow_per_share | float | Operating cash flow per share. |
| free_cash_flow_per_share | float | Free cash flow per share. |
| cash_per_share | float | Cash per share. |
| payout_ratio | float | Payout ratio. |
| operating_cash_flow_sales_ratio | float | Operating cash flow sales ratio. |
| free_cash_flow_operating_cash_flow_ratio | float | Free cash flow operating cash flow ratio. |
| cash_flow_coverage_ratios | float | Cash flow coverage ratios. |
| short_term_coverage_ratios | float | Short term coverage ratios. |
| capital_expenditure_coverage_ratio | float | Capital expenditure coverage ratio. |
| dividend_paid_and_capex_coverage_ratio | float | Dividend paid and capex coverage ratio. |
| dividend_payout_ratio | float | Dividend payout ratio. |
| price_book_value_ratio | float | Price book value ratio. |
| price_to_book_ratio | float | Price to book ratio. |
| price_to_sales_ratio | float | Price to sales ratio. |
| price_earnings_ratio | float | Price earnings ratio. |
| price_to_free_cash_flows_ratio | float | Price to free cash flows ratio. |
| price_to_operating_cash_flows_ratio | float | Price to operating cash flows ratio. |
| price_cash_flow_ratio | float | Price cash flow ratio. |
| price_earnings_to_growth_ratio | float | Price earnings to growth ratio. |
| price_sales_ratio | float | Price sales ratio. |
| dividend_yield | float | Dividend yield. |
| enterprise_value_multiple | float | Enterprise value multiple. |
| price_fair_value | float | Price fair value. |
</TabItem>

</Tabs>

