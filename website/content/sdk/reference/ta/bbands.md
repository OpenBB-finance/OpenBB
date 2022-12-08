---
title: bbands
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# bbands

<Tabs>
<TabItem value="model" label="Model" default>

Calculate Bollinger Bands

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L18)]

```python
openbb.ta.bbands(data: pd.DataFrame, window: int = 15, n_std: float = 2, mamode: str = "ema")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window to calculate BB | 15 | True |
| n_std | float | Number of standard deviations to show | 2 | True |
| mamode | str | Method of calculating average | ema | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of bollinger band data |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots bollinger bands

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L27)]

```python
openbb.ta.bbands_chart(data: pd.DataFrame, symbol: str = "", window: int = 15, n_std: float = 2, mamode: str = "sma", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| symbol | str | Ticker symbol |  | True |
| window | int | Length of window to calculate BB | 15 | True |
| n_std | float | Number of standard deviations to show | 2 | True |
| mamode | str | Method of calculating average | sma | True |
| export | str | Format of export file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>