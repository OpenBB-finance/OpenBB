---
title: cg
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cg

<Tabs>
<TabItem value="model" label="Model" default>

Center of gravity

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L189)]

```python
openbb.ta.cg(values: pd.Series, window: int)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| values | pd.DataFrame | Data to use with close being titled values | None | False |
| window | int | Length for indicator window | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots center of gravity Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L499)]

```python
openbb.ta.cg_chart(data: pd.Series, window: int = 14, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of values | None | False |
| window | int | Length of window | 14 | True |
| symbol | str | Stock ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>