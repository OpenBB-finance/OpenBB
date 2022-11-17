---
title: adx
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# adx

<Tabs>
<TabItem value="model" label="Model" default>

## common_ta_trend_indicators_model.adx

```python title='openbb_terminal/common/technical_analysis/trend_indicators_model.py'
def adx(data: pd.DataFrame, window: int, scalar: int, drift: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_model.py#L16)

Description: ADX technical indicator

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | None | False |
| scalar | int | Scalar variable | None | False |
| drift | int | Drift variable | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with adx indicator |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_ta_trend_indicators_view.display_adx

```python title='openbb_terminal/common/technical_analysis/trend_indicators_view.py'
def display_adx(data: pd.DataFrame, window: int, scalar: int, drift: int, symbol: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_view.py#L30)

Description: Plot ADX indicator

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | None | False |
| scalar | int | Scalar variable | None | False |
| drift | int | Drift variable | None | False |
| symbol | str | Ticker | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>