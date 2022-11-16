---
title: histcont
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# histcont

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_gov_quiverquant_model.get_hist_contracts

```python title='openbb_terminal/stocks/government/quiverquant_model.py'
def get_hist_contracts(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L139)

Description: Get historical quarterly government contracts [Source: quiverquant.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get congress trading data from | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Historical quarterly government contracts |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_gov_quiverquant_view.display_hist_contracts

```python title='openbb_terminal/stocks/government/quiverquant_view.py'
def display_hist_contracts(symbol: str, raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L547)

Description: Show historical quarterly government contracts [Source: quiverquant.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get congress trading data from | None | False |
| raw | bool | Flag to display raw data | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>