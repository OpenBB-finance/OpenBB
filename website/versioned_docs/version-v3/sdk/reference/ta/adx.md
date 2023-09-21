---
title: adx
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# adx

<Tabs>
<TabItem value="model" label="Model" default>

ADX technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_model.py#L16)]

```python
openbb.ta.adx(data: pd.DataFrame, window: int = 14, scalar: int = 100, drift: int = 1)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | 14 | True |
| scalar | int | Scalar variable | 100 | True |
| drift | int | Drift variable | 1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with adx indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots ADX indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_view.py#L30)]

```python
openbb.ta.adx_chart(data: pd.DataFrame, window: int = 14, scalar: int = 100, drift: int = 1, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | 14 | True |
| scalar | int | Scalar variable | 100 | True |
| drift | int | Drift variable | 1 | True |
| symbol | str | Ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>