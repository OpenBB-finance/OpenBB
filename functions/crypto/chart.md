---
title: chart
description: OpenBB SDK Function
---

# chart

## crypto_helpers.plot_chart

```python title='openbb_terminal/cryptocurrency/cryptocurrency_helpers.py'
def plot_chart(prices_df: pd.DataFrame, to_symbol: str, from_symbol: str, source: str, exchange: str, interval: str, external_axes: list[plt.Axes] | None, yscale: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/cryptocurrency_helpers.py#L1417)

Description: Load data for Technical Analysis

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| prices_df | pd.DataFrame | Cryptocurrency | None | False |
| to_symbol | str | Coin (only used for chart title), by default "" | None | False |
| from_symbol | str | Currency (only used for chart title), by default "" | None | False |
| yscale | str | Scale for y axis of plot Either linear or log | None | False |

## Returns

This function does not return anything

## Examples

