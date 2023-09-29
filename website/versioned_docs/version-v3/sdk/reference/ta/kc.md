---
title: kc
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# kc

<Tabs>
<TabItem value="model" label="Model" default>

Keltner Channels

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L88)]

```python
openbb.ta.kc(data: pd.DataFrame, window: int = 20, scalar: float = 2, mamode: str = "ema", offset: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | 20 | True |
| scalar | float | Scalar value | 2 | True |
| mamode | str | Type of filter | ema | True |
| offset | int | Offset value | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of rolling kc |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots Keltner Channels Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L194)]

```python
openbb.ta.kc_chart(data: pd.DataFrame, window: int = 20, scalar: float = 2, mamode: str = "ema", offset: int = 0, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| window | int | Length of window | 20 | True |
| scalar | float | Scalar value | 2 | True |
| mamode | str | Type of filter | ema | True |
| offset | int | Offset value | 0 | True |
| symbol | str | Ticker symbol |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>