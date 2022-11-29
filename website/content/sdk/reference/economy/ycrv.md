---
title: ycrv
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ycrv

<Tabs>
<TabItem value="model" label="Model" default>

Gets yield curve data from FRED

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_model.py#L257)]

```python
openbb.economy.ycrv(date: datetime.datetime = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | datetime | Date to get curve for.  If None, gets most recent date | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, datetime] | Dataframe of yields and maturities,<br/>Date for which the yield curve is obtained |
---

## Examples

```python
from openbb_terminal.sdk import openbb
ycrv_df = openbb.economy.ycrv()
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display yield curve based on US Treasury rates for a specified date.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_view.py#L187)]

```python
openbb.economy.ycrv_chart(date: datetime.datetime = None, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, raw: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | datetime | Date to get yield curve for | None | True |
| external_axes | Optional[List[plt.Axes]] | External axes to plot data on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>