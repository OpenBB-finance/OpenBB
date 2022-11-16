---
title: toplobbying
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# toplobbying

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_gov_quiverquant_model.get_top_lobbying

```python title='openbb_terminal/stocks/government/quiverquant_model.py'
def get_top_lobbying() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L358)

Description: Corporate lobbying details

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of top corporate lobbying |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_gov_quiverquant_view.display_top_lobbying

```python title='openbb_terminal/stocks/government/quiverquant_view.py'
def display_top_lobbying(limit: int, raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L622)

Description: Top lobbying tickers based on total spent

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of tickers to show | None | False |
| raw | bool | Show raw data | None | False |
| export |  | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>