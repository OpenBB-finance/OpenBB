---
title: atr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# atr

<Tabs>
<TabItem value="model" label="Model" default>

## common_ta_volatility_model.atr

```python title='openbb_terminal/common/technical_analysis/volatility_model.py'
def atr(data: pd.DataFrame, window: int, mamode: str, offset: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L132)

Description: Average True Range

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | None | False |
| mamode | str | Type of filter | None | False |
| offset | int | Offset value | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of atr |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_ta_volatility_view.display_atr

```python title='openbb_terminal/common/technical_analysis/volatility_view.py'
def display_atr(data: pd.DataFrame, symbol: str, window: int, mamode: str, offset: int, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L289)

Description: Show ATR

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| symbol | str | Ticker symbol | None | False |
| window | int | Length of window to calculate upper channel | None | False |
| export | str | Format of export file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>