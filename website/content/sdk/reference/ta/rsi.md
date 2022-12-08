---
title: rsi
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rsi

<Tabs>
<TabItem value="model" label="Model" default>

Relative strength index

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L93)]

```python
openbb.ta.rsi(data: pd.Series, window: int = 14, scalar: float = 100, drift: int = 1)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Dataframe of prices | None | False |
| window | int | Length of window | 14 | True |
| scalar | float | Scalar variable | 100 | True |
| drift | int | Drift variable | 1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots RSI Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L219)]

```python
openbb.ta.rsi_chart(data: pd.Series, window: int = 14, scalar: float = 100.0, drift: int = 1, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Values to input | None | False |
| window | int | Length of window | 14 | True |
| scalar | float | Scalar variable | 100.0 | True |
| drift | int | Drift variable | 1 | True |
| symbol | str | Stock ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>