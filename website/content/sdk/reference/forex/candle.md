---
title: candle
description: Discover how to implement candle plotting for forex data using the OpenBB
  platform. The page includes necessary parameters for creating a candle plot and
  source code for reference.
keywords:
- forex
- candle
- fx data
- moving averages
- matplotlib
- OpenBB.finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex.candle - Reference | OpenBB SDK Docs" />

Show candle plot for fx data.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/forex_helper.py#L244)]

```python wordwrap
openbb.forex.candle(data: pd.DataFrame, to_symbol: str = "", from_symbol: str = "", ma: Optional[Iterable[int]] = None, external_axes: bool = False, add_trend: bool = False, yscale: str = "linear")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Loaded fx historical data | None | False |
| to_symbol | str | To forex symbol |  | True |
| from_symbol | str | From forex symbol |  | True |
| ma | Optional[Iterable[int]] | Moving averages | None | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---

