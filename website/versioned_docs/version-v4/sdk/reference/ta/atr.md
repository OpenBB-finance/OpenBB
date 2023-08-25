---
title: atr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# atr

<Tabs>
<TabItem value="model" label="Model" default>

Average True Range

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L132)]

```python
openbb.ta.atr(data: pd.DataFrame, window: int = 14, mamode: str = "ema", offset: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | 14 | True |
| mamode | str | Type of filter | ema | True |
| offset | int | Offset value | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of atr |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots ATR

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L289)]

```python
openbb.ta.atr_chart(data: pd.DataFrame, symbol: str = "", window: int = 14, mamode: str = "sma", offset: int = 0, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| symbol | str | Ticker symbol |  | True |
| window | int | Length of window to calculate upper channel | 14 | True |
| export | str | Format of export file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>