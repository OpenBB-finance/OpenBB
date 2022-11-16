---
title: adosc
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# adosc

<Tabs>
<TabItem value="model" label="Model" default>

## common_ta_volume_model.adosc

```python title='openbb_terminal/common/technical_analysis/volume_model.py'
def adosc(data: pd.DataFrame, use_open: bool, fast: int, slow: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_model.py#L46)

Description: Calculate AD oscillator technical indicator

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| use_open | bool | Whether to use open prices | None | False |
| fast | int | Fast value | None | False |
| slow | int | Slow value | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with technical indicator |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_ta_volume_view.display_adosc

```python title='openbb_terminal/common/technical_analysis/volume_view.py'
def display_adosc(data: pd.DataFrame, fast: int, slow: int, use_open: bool, symbol: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_view.py#L141)

Description: Display AD Osc Indicator

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| use_open | bool | Whether to use open prices in calculation | None | False |
| fast | int | Length of fast window | None | False |
| slow | int | Length of slow window | None | False |
| symbol | str | Stock ticker | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>