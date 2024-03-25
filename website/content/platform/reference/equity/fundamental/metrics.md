---
title: "metrics"
description: "Learn about key metrics for a given company using the `obb.equity.fundamental.metrics`  Python function. This API endpoint provides data such as revenue per share, net  income per share, market capitalization, price-to-earnings ratio, and more. Explore  the available parameters and returned data to analyze financial performance. Full  documentation and usage examples available."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/metrics - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get fundamental metrics for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.metrics(symbol='AAPL', provider='fmp')
obb.equity.fundamental.metrics(symbol='AAPL', period='annual', limit=100, provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, yfinance. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['finviz', 'fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, yfinance. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['finviz', 'fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, yfinance. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['finviz', 'fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
| with_ttm | bool | Include trailing twelve months (TTM) data. | False | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, yfinance. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['finviz', 'fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, yfinance. |  | False |
| period | Literal['annual', 'quarter'] | Time period of the data to return. | annual | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['finviz', 'fmp', 'intrinio', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : KeyMetrics
        Serializable results.
    provider : Literal['finviz', 'fmp', 'intrinio', 'yfinance']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| market_cap | float | Market capitalization |
| pe_ratio | float | Price-to-earnings ratio (P/E ratio) |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| market_cap | float | Market capitalization |
| pe_ratio | float | Price-to-earnings ratio (P/E ratio) |
| foward_pe | float | Forward price-to-earnings ratio (forward P/E) |
| eps | float | Earnings per share (EPS) |
| price_to_sales | float | Price-to-sales ratio (P/S) |
| price_to_book | float | Price-to-book ratio (P/B) |
| book_value_per_share | float | Book value per share (Book/sh) |
| price_to_cash | float | Price-to-cash ratio (P/C) |
| cash_per_share | float | Cash per share (Cash/sh) |
| price_to_free_cash_flow | float | Price-to-free cash flow ratio (P/FCF) |
| debt_to_equity | float | Debt-to-equity ratio (Debt/Eq) |
| long_term_debt_to_equity | float | Long-term debt-to-equity ratio (LT Debt/Eq) |
| quick_ratio | float | Quick ratio |
| current_ratio | float | Current ratio |
| gross_margin | float | Gross margin, as a normalized percent. |
| profit_margin | float | Profit margin, as a normalized percent. |
| operating_margin | float | Operating margin, as a normalized percent. |
| return_on_assets | float | Return on assets (ROA), as a normalized percent. |
| return_on_investment | float | Return on investment (ROI), as a normalized percent. |
| return_on_equity | float | Return on equity (ROE), as a normalized percent. |
| payout_ratio | float | Payout ratio, as a normalized percent. |
| dividend_yield | float | Dividend yield, as a normalized percent. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| market_cap | float | Market capitalization |
| pe_ratio | float | Price-to-earnings ratio (P/E ratio) |
| date | date | The date of the data. |
| period | str | Period of the data. |
| calendar_year | int | Calendar year. |
| revenue_per_share | float | Revenue per share |
| net_income_per_share | float | Net income per share |
| operating_cash_flow_per_share | float | Operating cash flow per share |
| free_cash_flow_per_share | float | Free cash flow per share |
| cash_per_share | float | Cash per share |
| book_value_per_share | float | Book value per share |
| tangible_book_value_per_share | float | Tangible book value per share |
| shareholders_equity_per_share | float | Shareholders equity per share |
| interest_debt_per_share | float | Interest debt per share |
| enterprise_value | float | Enterprise value |
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
| dividend_yield | float | Dividend yield, as a normalized percent. |
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

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| market_cap | float | Market capitalization |
| pe_ratio | float | Price-to-earnings ratio (P/E ratio) |
| price_to_book | float | Price to book ratio. |
| price_to_tangible_book | float | Price to tangible book ratio. |
| price_to_revenue | float | Price to revenue ratio. |
| quick_ratio | float | Quick ratio. |
| gross_margin | float | Gross margin, as a normalized percent. |
| ebit_margin | float | EBIT margin, as a normalized percent. |
| profit_margin | float | Profit margin, as a normalized percent. |
| eps | float | Basic earnings per share. |
| eps_growth | float | EPS growth, as a normalized percent. |
| revenue_growth | float | Revenue growth, as a normalized percent. |
| ebitda_growth | float | EBITDA growth, as a normalized percent. |
| ebit_growth | float | EBIT growth, as a normalized percent. |
| net_income_growth | float | Net income growth, as a normalized percent. |
| free_cash_flow_to_firm_growth | float | Free cash flow to firm growth, as a normalized percent. |
| invested_capital_growth | float | Invested capital growth, as a normalized percent. |
| return_on_assets | float | Return on assets, as a normalized percent. |
| return_on_equity | float | Return on equity, as a normalized percent. |
| return_on_invested_capital | float | Return on invested capital, as a normalized percent. |
| ebitda | int | Earnings before interest, taxes, depreciation, and amortization. |
| ebit | int | Earnings before interest and taxes. |
| long_term_debt | int | Long-term debt. |
| total_debt | int | Total debt. |
| total_capital | int | The sum of long-term debt and total shareholder equity. |
| enterprise_value | int | Enterprise value. |
| free_cash_flow_to_firm | int | Free cash flow to firm. |
| altman_z_score | float | Altman Z-score. |
| beta | float | Beta relative to the broad market (rolling three-year). |
| dividend_yield | float | Dividend yield, as a normalized percent. |
| earnings_yield | float | Earnings yield, as a normalized percent. |
| last_price | float | Last price of the stock. |
| year_high | float | 52 week high |
| year_low | float | 52 week low |
| volume_avg | int | Average daily volume. |
| short_interest | int | Number of shares reported as sold short. |
| shares_outstanding | int | Weighted average shares outstanding (TTM). |
| days_to_cover | float | Days to cover short interest, based on average daily volume. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| market_cap | float | Market capitalization |
| pe_ratio | float | Price-to-earnings ratio (P/E ratio) |
| forward_pe | float | Forward price-to-earnings ratio. |
| peg_ratio | float | PEG ratio (5-year expected). |
| peg_ratio_ttm | float | PEG ratio (TTM). |
| eps_ttm | float | Earnings per share (TTM). |
| eps_forward | float | Forward earnings per share. |
| enterprise_to_ebitda | float | Enterprise value to EBITDA ratio. |
| earnings_growth | float | Earnings growth (Year Over Year), as a normalized percent. |
| earnings_growth_quarterly | float | Quarterly earnings growth (Year Over Year), as a normalized percent. |
| revenue_per_share | float | Revenue per share (TTM). |
| revenue_growth | float | Revenue growth (Year Over Year), as a normalized percent. |
| enterprise_to_revenue | float | Enterprise value to revenue ratio. |
| cash_per_share | float | Cash per share. |
| quick_ratio | float | Quick ratio. |
| current_ratio | float | Current ratio. |
| debt_to_equity | float | Debt-to-equity ratio. |
| gross_margin | float | Gross margin, as a normalized percent. |
| operating_margin | float | Operating margin, as a normalized percent. |
| ebitda_margin | float | EBITDA margin, as a normalized percent. |
| profit_margin | float | Profit margin, as a normalized percent. |
| return_on_assets | float | Return on assets, as a normalized percent. |
| return_on_equity | float | Return on equity, as a normalized percent. |
| dividend_yield | float | Dividend yield, as a normalized percent. |
| dividend_yield_5y_avg | float | 5-year average dividend yield, as a normalized percent. |
| payout_ratio | float | Payout ratio. |
| book_value | float | Book value per share. |
| price_to_book | float | Price-to-book ratio. |
| enterprise_value | int | Enterprise value. |
| overall_risk | float | Overall risk score. |
| audit_risk | float | Audit risk score. |
| board_risk | float | Board risk score. |
| compensation_risk | float | Compensation risk score. |
| shareholder_rights_risk | float | Shareholder rights risk score. |
| beta | float | Beta relative to the broad market (5-year monthly). |
| price_return_1y | float | One-year price return, as a normalized percent. |
| currency | str | Currency in which the data is presented. |
</TabItem>

</Tabs>

