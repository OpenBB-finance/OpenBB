---
title: FinancialRatios
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Literal['annual', 'quarter'] | Period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 12 | True |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| with_ttm | Union[bool] | Include trailing twelve months (TTM) data. | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the company. |
| date | str | Date of the financial ratios. |
| period | str | Period of the financial ratios. |
| current_ratio | Union[float] | Current ratio. |
| quick_ratio | Union[float] | Quick ratio. |
| cash_ratio | Union[float] | Cash ratio. |
| days_of_sales_outstanding | Union[float] | Days of sales outstanding. |
| days_of_inventory_outstanding | Union[float] | Days of inventory outstanding. |
| operating_cycle | Union[float] | Operating cycle. |
| days_of_payables_outstanding | Union[float] | Days of payables outstanding. |
| cash_conversion_cycle | Union[float] | Cash conversion cycle. |
| gross_profit_margin | Union[float] | Gross profit margin. |
| operating_profit_margin | Union[float] | Operating profit margin. |
| pretax_profit_margin | Union[float] | Pretax profit margin. |
| net_profit_margin | Union[float] | Net profit margin. |
| effective_tax_rate | Union[float] | Effective tax rate. |
| return_on_assets | Union[float] | Return on assets. |
| return_on_equity | Union[float] | Return on equity. |
| return_on_capital_employed | Union[float] | Return on capital employed. |
| net_income_per_ebt | Union[float] | Net income per EBT. |
| ebt_per_ebit | Union[float] | EBT per EBIT. |
| ebit_per_revenue | Union[float] | EBIT per revenue. |
| debt_ratio | Union[float] | Debt ratio. |
| debt_equity_ratio | Union[float] | Debt equity ratio. |
| long_term_debt_to_capitalization | Union[float] | Long term debt to capitalization. |
| total_debt_to_capitalization | Union[float] | Total debt to capitalization. |
| interest_coverage | Union[float] | Interest coverage. |
| cash_flow_to_debt_ratio | Union[float] | Cash flow to debt ratio. |
| company_equity_multiplier | Union[float] | Company equity multiplier. |
| receivables_turnover | Union[float] | Receivables turnover. |
| payables_turnover | Union[float] | Payables turnover. |
| inventory_turnover | Union[float] | Inventory turnover. |
| fixed_asset_turnover | Union[float] | Fixed asset turnover. |
| asset_turnover | Union[float] | Asset turnover. |
| operating_cash_flow_per_share | Union[float] | Operating cash flow per share. |
| free_cash_flow_per_share | Union[float] | Free cash flow per share. |
| cash_per_share | Union[float] | Cash per share. |
| payout_ratio | Union[float] | Payout ratio. |
| operating_cash_flow_sales_ratio | Union[float] | Operating cash flow sales ratio. |
| free_cash_flow_operating_cash_flow_ratio | Union[float] | Free cash flow operating cash flow ratio. |
| cash_flow_coverage_ratios | Union[float] | Cash flow coverage ratios. |
| short_term_coverage_ratios | Union[float] | Short term coverage ratios. |
| capital_expenditure_coverage_ratio | Union[float] | Capital expenditure coverage ratio. |
| dividend_paid_and_capex_coverage_ratio | Union[float] | Dividend paid and capex coverage ratio. |
| dividend_payout_ratio | Union[float] | Dividend payout ratio. |
| price_book_value_ratio | Union[float] | Price book value ratio. |
| price_to_book_ratio | Union[float] | Price to book ratio. |
| price_to_sales_ratio | Union[float] | Price to sales ratio. |
| price_earnings_ratio | Union[float] | Price earnings ratio. |
| price_to_free_cash_flows_ratio | Union[float] | Price to free cash flows ratio. |
| price_to_operating_cash_flows_ratio | Union[float] | Price to operating cash flows ratio. |
| price_cash_flow_ratio | Union[float] | Price cash flow ratio. |
| price_earnings_to_growth_ratio | Union[float] | Price earnings to growth ratio. |
| price_sales_ratio | Union[float] | Price sales ratio. |
| dividend_yield | Union[float] | Dividend yield. |
| enterprise_value_multiple | Union[float] | Enterprise value multiple. |
| price_fair_value | Union[float] | Price fair value. |
</TabItem>

</Tabs>

