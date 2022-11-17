---
title: candles
description: OpenBB SDK Function
---

# candles

## crypto_helpers.plot_candles

```python title='openbb_terminal/cryptocurrency/cryptocurrency_helpers.py'
def plot_candles(candles_df: pd.DataFrame, volume: bool, ylabel: str, title: str, external_axes: list[plt.Axes] | None, yscale: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/cryptocurrency_helpers.py#L1469)

Description: Plot candle chart from dataframe. [Source: Binance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| candles_df | pd.DataFrame | Dataframe containing time and OHLCV | None | False |
| volume | bool | If volume data shall be plotted, by default True | True | False |
| ylabel | str | Y-label of the graph, by default "" | None | False |
| title | str | Title of graph, by default "" | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |
| yscale | str | Scaling for y axis.  Either linear or log | None | False |

## Returns

This function does not return anything

## Examples

