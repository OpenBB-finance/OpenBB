---
title: demark
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# demark

<Tabs>
<TabItem value="model" label="Model" default>

Get the integer value for demark sequential indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L257)]

```python
openbb.ta.demark(values: pd.Series)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| values | pd.Series | Series of close values | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of UP and DOWN sequential indicators |
---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.ta.demark(df["Close"])
```

---



</TabItem>
<TabItem value="view" label="Chart">

Plot demark sequential indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L644)]

```python
openbb.ta.demark_chart(data: pd.DataFrame, symbol: str = "", min_to_show: int = 5, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame of values | None | False |
| symbol | str | Symbol that the data corresponds to |  | True |
| min_to_show | int | Minimum value to show | 5 | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.ta.demark_chart(df)
```

---



</TabItem>
</Tabs>