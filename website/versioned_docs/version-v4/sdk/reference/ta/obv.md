---
title: obv
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# obv

<Tabs>
<TabItem value="model" label="Model" default>

On Balance Volume

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_model.py#L90)]

```python
openbb.ta.obv(data: pd.DataFrame)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots OBV technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_view.py#L249)]

```python
openbb.ta.obv_chart(data: pd.DataFrame, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| symbol | str | Ticker |  | True |
| export | str | Format to export data as |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>