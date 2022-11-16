---
title: voi_yf
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# voi_yf

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_yfinance_model.get_volume_open_interest

```python title='openbb_terminal/stocks/options/yfinance_model.py'
def get_volume_open_interest(symbol: str, expiry: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L553)

Description: Plot volume and open interest

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| expiry | str | Option expiration | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_yfinance_view.plot_volume_open_interest

```python title='openbb_terminal/stocks/options/yfinance_view.py'
def plot_volume_open_interest(symbol: str, expiry: str, min_sp: float, max_sp: float, min_vol: float, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_view.py#L429)

Description: Plot volume and open interest

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| expiry | str | Option expiration | None | False |
| min_sp | float | Min strike price | None | False |
| max_sp | float | Max strike price | None | False |
| min_vol | float | Min volume to consider | None | False |
| export | str | Format for exporting data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>