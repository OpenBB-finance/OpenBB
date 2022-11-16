---
title: vol_yf
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# vol_yf

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_yfinance_model.get_vol

```python title='openbb_terminal/stocks/options/yfinance_model.py'
def get_vol(symbol: str, expiry: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L534)

Description: Plot volume

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| expiry | str | expiration date for options | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_yfinance_view.plot_vol

```python title='openbb_terminal/stocks/options/yfinance_view.py'
def plot_vol(symbol: str, expiry: str, min_sp: float, max_sp: float, calls_only: bool, puts_only: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_view.py#L338)

Description: Plot volume

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| expiry | str | expiration date for options | None | False |
| min_sp | float | Min strike to consider | None | False |
| max_sp | float | Max strike to consider | None | False |
| calls_only | bool | Show calls only | None | False |
| puts_only | bool | Show puts only | None | False |
| export | str | Format to export file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>