---
title: kc
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# kc

<Tabs>
<TabItem value="model" label="Model" default>

## common_ta_volatility_model.kc

```python title='openbb_terminal/common/technical_analysis/volatility_model.py'
def kc(data: pd.DataFrame, window: int, scalar: float, mamode: str, offset: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L88)

Description: Keltner Channels

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | None | False |
| scalar | float | Scalar value | None | False |
| mamode | str | Type of filter | None | False |
| offset | int | Offset value | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of rolling kc |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_ta_volatility_view.view_kc

```python title='openbb_terminal/common/technical_analysis/volatility_view.py'
def view_kc(data: pd.DataFrame, window: int, scalar: float, mamode: str, offset: int, symbol: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L194)

Description: View Keltner Channels Indicator

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | None | False |
| scalar | float | Scalar value | None | False |
| mamode | str | Type of filter | None | False |
| offset | int | Offset value | None | False |
| symbol | str | Ticker symbol | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>