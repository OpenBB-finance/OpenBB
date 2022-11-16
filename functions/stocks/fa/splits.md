---
title: splits
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# splits

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_fa_yahoo_finance_model.get_splits

```python title='openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py'
def get_splits(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L308)

Description: Get splits and reverse splits events. [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get forward and reverse splits | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe of forward and reverse splits |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_fa_yahoo_finance_view.display_splits

```python title='openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py'
def display_splits(symbol: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py#L261)

Description: Display splits and reverse splits events. [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>