---
title: chart
description: Extend your technical analysis with the OpenBB crypto chart function.
  This feature allows loading of cryptocurrency data, optional title configuration
  based on Coin and Currency, and control over plot scale (linear or log). Source
  code is available.
keywords:
- Technical Analysis
- OpenBB crypto chart
- Cryptocurrency data
- matplotlib axes
- linear plot scale
- log plot scale
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.chart - Reference | OpenBB SDK Docs" />

Load data for Technical Analysis

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/cryptocurrency_helpers.py#L747)]

```python
openbb.crypto.chart(prices_df: pd.DataFrame, to_symbol: str = "", from_symbol: str = "", source: str = "", exchange: str = "", interval: str = "", external_axes: Optional[list[matplotlib.axes._axes.Axes]] = None, yscale: str = "linear")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| prices_df | pd.DataFrame | Cryptocurrency | None | False |
| to_symbol | str | Coin (only used for chart title), by default "" |  | True |
| from_symbol | str | Currency (only used for chart title), by default "" |  | True |
| yscale | str | Scale for y axis of plot Either linear or log | linear | True |


---

## Returns

This function does not return anything

---
