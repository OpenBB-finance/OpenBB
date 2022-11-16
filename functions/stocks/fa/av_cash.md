---
title: av_cash
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# av_cash

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_fa_av_model.get_cash_flow

```python title='openbb_terminal/stocks/fundamental_analysis/av_model.py'
def get_cash_flow(symbol: str, limit: int, quarterly: bool, ratios: bool, plot: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L340)

Description: Get cash flows for company

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of past to get | None | False |
| quarterly | bool | Flag to get quarterly instead of annual, by default False | False | True |
| ratios | bool | Shows percentage change, by default False | False | False |
| plot | bool | If the data shall be formatted ready to plot | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of cash flow statements |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_fa_av_view.display_cash_flow

```python title='openbb_terminal/decorators.py'
def display_cash_flow() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L245)

Description: Alpha Vantage income statement

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Fundamental analysis ticker symbol | None | False |
| limit | int | Number of past statements, by default 5 | 5 | False |
| quarterly | bool | Flag to get quarterly instead of annual, by default False | False | False |
| ratios | bool | Shows percentage change, by default False | False | False |
| plot | list | List of row labels to plot | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>