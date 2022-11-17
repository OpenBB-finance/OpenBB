---
title: vwap
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# vwap

<Tabs>
<TabItem value="model" label="Model" default>

## common_ta_overlap_model.vwap

```python title='openbb_terminal/common/technical_analysis/overlap_model.py'
def vwap(data: pd.Series, offset: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L139)

Description: Gets volume weighted average price (VWAP)

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of dates and prices | None | False |
| offset | int | Length of offset | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with VWAP data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_ta_overlap_view.view_vwap

```python title='openbb_terminal/common/technical_analysis/overlap_view.py'
def view_vwap(data: pd.DataFrame, symbol: str, start_date: str, end_date: str, offset: int, interval: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_view.py#L121)

Description: Plots VWMA technical indicator

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| symbol | str | Ticker | None | False |
| offset | int | Offset variable | None | False |
| start_date | datetime | Start date to get data from with | None | False |
| end_date | datetime | End date to get data from with | None | False |
| interval | str | Interval of data | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>