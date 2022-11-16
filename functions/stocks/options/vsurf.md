---
title: vsurf
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# vsurf

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_yfinance_model.get_iv_surface

```python title='openbb_terminal/stocks/options/yfinance_model.py'
def get_iv_surface(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L321)

Description: Gets IV surface for calls and puts for ticker

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol to get | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of DTE, Strike and IV |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_yfinance_view.display_vol_surface

```python title='openbb_terminal/stocks/options/yfinance_view.py'
def display_vol_surface(symbol: str, export: str, z: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_view.py#L1128)

Description: Display vol surface

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get surface for | None | False |
| export | str | Format to export data | None | False |
| z | str | The variable for the Z axis | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>