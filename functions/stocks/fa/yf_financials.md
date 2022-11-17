---
title: yf_financials
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# yf_financials

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_fa_yahoo_finance_model.get_financials

```python title='openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py'
def get_financials(symbol: str, statement: str, ratios: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L328)

Description: Get cashflow statement for company

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| statement | str | can be:

- cash-flow
- financials for Income
- balance-sheet | None | False |
| ratios | bool | Shows percentage change | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of Financial statement |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_fa_yahoo_finance_view.display_fundamentals

```python title='openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py'
def display_fundamentals(symbol: str, statement: str, limit: int, ratios: bool, plot: list, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py#L383)

Description: Display tickers balance sheet, income statement or cash-flow

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| statement | str | Possible values are:

- cash-flow
- financials for Income
- balance-sheet | None | False |
| limit | int | Number of periods to show | None | False |
| ratios | bool | Shows percentage change | None | False |
| plot | list | List of row labels to plot | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>