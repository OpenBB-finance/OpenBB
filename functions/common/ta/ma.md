---
title: ma
description: OpenBB SDK Function
---

# ma

## common_ta_overlap_view.view_ma

```python title='openbb_terminal/common/technical_analysis/overlap_view.py'
def view_ma(data: pd.Series, window: List[int], offset: int, ma_type: str, symbol: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_view.py#L32)

Description: Plots MA technical indicator

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of prices | None | False |
| window | List[int] | Length of EMA window | None | False |
| offset | int | Offset variable | None | False |
| ma_type | str | Type of moving average.  Either "EMA" "ZLMA" or "SMA" | None | False |
| symbol | str | Ticker | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples

