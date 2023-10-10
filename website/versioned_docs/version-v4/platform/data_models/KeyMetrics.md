---
title: KeyMetrics
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
| period | Union[Literal['annual', 'quarter']] | Period of the data to return. | annual | True |
| limit | Union[int] | The number of data entries to return. | 100 | True |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| period | Union[Literal['annual', 'quarter']] | Period of the data to return. | annual | True |
| limit | Union[int] | The number of data entries to return. | 100 | True |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| with_ttm | Union[bool] | Include trailing twelve months (TTM) data. | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | Union[str] | Symbol to get data for. |
| date | date | The date of the data. |
| period | str | Period of the data. |
| revenue_per_share | Union[float] | Revenue per share |
| net_income_per_share | Union[float] | Net income per share |
| operating_cash_flow_per_share | Union[float] | Operating cash flow per share |
| free_cash_flow_per_share | Union[float] | Free cash flow per share |
| cash_per_share | Union[float] | Cash per share |
| book_value_per_share | Union[float] | Book value per share |
| tangible_book_value_per_share | Union[float] | Tangible book value per share |
| shareholders_equity_per_share | Union[float] | Shareholders equity per share |
| interest_debt_per_share | Union[float] | Interest debt per share |
| market_cap | Union[float] | Market capitalization |
| enterprise_value | Union[float] | Enterprise value |
| pe_ratio | Union[float] | Price-to-earnings ratio (P/E ratio) |
| price_to_sales_ratio | Union[float] | Price-to-sales ratio |
| pocf_ratio | Union[float] | Price-to-operating cash flow ratio |
| pfcf_ratio | Union[float] | Price-to-free cash flow ratio |
| pb_ratio | Union[float] | Price-to-book ratio |
| ptb_ratio | Union[float] | Price-to-tangible book ratio |
| ev_to_sales | Union[float] | Enterprise value-to-sales ratio |
| enterprise_value_over_ebitda | Union[float] | Enterprise value-to-EBITDA ratio |
| ev_to_operating_cash_flow | Union[float] | Enterprise value-to-operating cash flow ratio |
| ev_to_free_cash_flow | Union[float] | Enterprise value-to-free cash flow ratio |
| earnings_yield | Union[float] | Earnings yield |
| free_cash_flow_yield | Union[float] | Free cash flow yield |
| debt_to_equity | Union[float] | Debt-to-equity ratio |
| debt_to_assets | Union[float] | Debt-to-assets ratio |
| net_debt_to_ebitda | Union[float] | Net debt-to-EBITDA ratio |
| current_ratio | Union[float] | Current ratio |
| interest_coverage | Union[float] | Interest coverage |
| income_quality | Union[float] | Income quality |
| dividend_yield | Union[float] | Dividend yield |
| payout_ratio | Union[float] | Payout ratio |
| sales_general_and_administrative_to_revenue | Union[float] | Sales general and administrative expenses-to-revenue ratio |
| research_and_development_to_revenue | Union[float] | Research and development expenses-to-revenue ratio |
| intangibles_to_total_assets | Union[float] | Intangibles-to-total assets ratio |
| capex_to_operating_cash_flow | Union[float] | Capital expenditures-to-operating cash flow ratio |
| capex_to_revenue | Union[float] | Capital expenditures-to-revenue ratio |
| capex_to_depreciation | Union[float] | Capital expenditures-to-depreciation ratio |
| stock_based_compensation_to_revenue | Union[float] | Stock-based compensation-to-revenue ratio |
| graham_number | Union[float] | Graham number |
| roic | Union[float] | Return on invested capital |
| return_on_tangible_assets | Union[float] | Return on tangible assets |
| graham_net_net | Union[float] | Graham net-net working capital |
| working_capital | Union[float] | Working capital |
| tangible_asset_value | Union[float] | Tangible asset value |
| net_current_asset_value | Union[float] | Net current asset value |
| invested_capital | Union[float] | Invested capital |
| average_receivables | Union[float] | Average receivables |
| average_payables | Union[float] | Average payables |
| average_inventory | Union[float] | Average inventory |
| days_sales_outstanding | Union[float] | Days sales outstanding |
| days_payables_outstanding | Union[float] | Days payables outstanding |
| days_of_inventory_on_hand | Union[float] | Days of inventory on hand |
| receivables_turnover | Union[float] | Receivables turnover |
| payables_turnover | Union[float] | Payables turnover |
| inventory_turnover | Union[float] | Inventory turnover |
| roe | Union[float] | Return on equity |
| capex_per_share | Union[float] | Capital expenditures per share |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | Union[str] | Symbol to get data for. |
| date | date | The date of the data. |
| period | str | Period of the data. |
| revenue_per_share | Union[float] | Revenue per share |
| net_income_per_share | Union[float] | Net income per share |
| operating_cash_flow_per_share | Union[float] | Operating cash flow per share |
| free_cash_flow_per_share | Union[float] | Free cash flow per share |
| cash_per_share | Union[float] | Cash per share |
| book_value_per_share | Union[float] | Book value per share |
| tangible_book_value_per_share | Union[float] | Tangible book value per share |
| shareholders_equity_per_share | Union[float] | Shareholders equity per share |
| interest_debt_per_share | Union[float] | Interest debt per share |
| market_cap | Union[float] | Market capitalization |
| enterprise_value | Union[float] | Enterprise value |
| pe_ratio | Union[float] | Price-to-earnings ratio (P/E ratio) |
| price_to_sales_ratio | Union[float] | Price-to-sales ratio |
| pocf_ratio | Union[float] | Price-to-operating cash flow ratio |
| pfcf_ratio | Union[float] | Price-to-free cash flow ratio |
| pb_ratio | Union[float] | Price-to-book ratio |
| ptb_ratio | Union[float] | Price-to-tangible book ratio |
| ev_to_sales | Union[float] | Enterprise value-to-sales ratio |
| enterprise_value_over_ebitda | Union[float] | Enterprise value-to-EBITDA ratio |
| ev_to_operating_cash_flow | Union[float] | Enterprise value-to-operating cash flow ratio |
| ev_to_free_cash_flow | Union[float] | Enterprise value-to-free cash flow ratio |
| earnings_yield | Union[float] | Earnings yield |
| free_cash_flow_yield | Union[float] | Free cash flow yield |
| debt_to_equity | Union[float] | Debt-to-equity ratio |
| debt_to_assets | Union[float] | Debt-to-assets ratio |
| net_debt_to_ebitda | Union[float] | Net debt-to-EBITDA ratio |
| current_ratio | Union[float] | Current ratio |
| interest_coverage | Union[float] | Interest coverage |
| income_quality | Union[float] | Income quality |
| dividend_yield | Union[float] | Dividend yield |
| payout_ratio | Union[float] | Payout ratio |
| sales_general_and_administrative_to_revenue | Union[float] | Sales general and administrative expenses-to-revenue ratio |
| research_and_development_to_revenue | Union[float] | Research and development expenses-to-revenue ratio |
| intangibles_to_total_assets | Union[float] | Intangibles-to-total assets ratio |
| capex_to_operating_cash_flow | Union[float] | Capital expenditures-to-operating cash flow ratio |
| capex_to_revenue | Union[float] | Capital expenditures-to-revenue ratio |
| capex_to_depreciation | Union[float] | Capital expenditures-to-depreciation ratio |
| stock_based_compensation_to_revenue | Union[float] | Stock-based compensation-to-revenue ratio |
| graham_number | Union[float] | Graham number |
| roic | Union[float] | Return on invested capital |
| return_on_tangible_assets | Union[float] | Return on tangible assets |
| graham_net_net | Union[float] | Graham net-net working capital |
| working_capital | Union[float] | Working capital |
| tangible_asset_value | Union[float] | Tangible asset value |
| net_current_asset_value | Union[float] | Net current asset value |
| invested_capital | Union[float] | Invested capital |
| average_receivables | Union[float] | Average receivables |
| average_payables | Union[float] | Average payables |
| average_inventory | Union[float] | Average inventory |
| days_sales_outstanding | Union[float] | Days sales outstanding |
| days_payables_outstanding | Union[float] | Days payables outstanding |
| days_of_inventory_on_hand | Union[float] | Days of inventory on hand |
| receivables_turnover | Union[float] | Receivables turnover |
| payables_turnover | Union[float] | Payables turnover |
| inventory_turnover | Union[float] | Inventory turnover |
| roe | Union[float] | Return on equity |
| capex_per_share | Union[float] | Capital expenditures per share |
| calendar_year | Union[typing_extensions.Annotated[int, BeforeValidator(func=<function check_int at 0x7f9523f183a0>)]] | Calendar year. |
</TabItem>

</Tabs>

