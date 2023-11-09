---
title: candles
description: The page provides documentation for the 'candles' function in the OpenBB
  crypto module. It describes how a candle chart can be plotted from a provided DataFrame,
  and the various parameters that can be adjusted.
keywords:
- crypto.candles
- candle chart
- Binance source
- Python script
- data visualization
- OpenBB crypto module
- matplotlib
- OHLCV
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.candles - Reference | OpenBB SDK Docs" />

Plot candle chart from dataframe. [Source: Binance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/cryptocurrency_helpers.py#L799)]

```python
openbb.crypto.candles(candles_df: pd.DataFrame, volume: bool = True, ylabel: str = "", title: str = "", external_axes: Optional[list[matplotlib.axes._axes.Axes]] = None, yscale: str = "linear")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| candles_df | pd.DataFrame | Dataframe containing time and OHLCV | None | False |
| volume | bool | If volume data shall be plotted, by default True | True | True |
| ylabel | str | Y-label of the graph, by default "" |  | True |
| title | str | Title of graph, by default "" |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |
| yscale | str | Scaling for y axis.  Either linear or log | linear | True |


---

## Returns

This function does not return anything

---
