---
title: bbands
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# bbands

<Tabs>
<TabItem value="model" label="Model" default>

## common_ta_volatility_model.bbands

```python title='openbb_terminal/common/technical_analysis/volatility_model.py'
def bbands(data: pd.DataFrame, window: int, n_std: float, mamode: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L18)

Description: Calculate Bollinger Bands

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window to calculate BB | None | False |
| n_std | float | Number of standard deviations to show | None | False |
| mamode | str | Method of calculating average | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of bollinger band data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_ta_volatility_view.display_bbands

```python title='openbb_terminal/common/technical_analysis/volatility_view.py'
def display_bbands(data: pd.DataFrame, symbol: str, window: int, n_std: float, mamode: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L27)

Description: Show bollinger bands

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| symbol | str | Ticker symbol | None | False |
| window | int | Length of window to calculate BB | None | False |
| n_std | float | Number of standard deviations to show | None | False |
| mamode | str | Method of calculating average | None | False |
| export | str | Format of export file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>