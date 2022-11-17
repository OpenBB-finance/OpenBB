---
title: candle
description: OpenBB SDK Function
---

# candle

## forex_helpers.display_candle

```python title='openbb_terminal/forex/forex_helper.py'
def display_candle(data: pd.DataFrame, to_symbol: str, from_symbol: str, ma: Optional[Iterable[int]], external_axes: Optional[List[matplotlib.axes._axes.Axes]], use_matplotlib: bool, add_trend: bool, yscale: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/forex_helper.py#L227)

Description: Show candle plot for fx data.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Loaded fx historical data | None | False |
| to_symbol | str | To forex symbol | None | False |
| from_symbol | str | From forex symbol | None | False |
| ma | Optional[Iterable[int]] | Moving averages | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | False |

## Returns

This function does not return anything

## Examples

