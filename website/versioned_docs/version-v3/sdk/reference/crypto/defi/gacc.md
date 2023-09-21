---
title: gacc
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# gacc

<Tabs>
<TabItem value="model" label="Model" default>

Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py#L263)]

```python
openbb.crypto.defi.gacc(cumulative: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| cumulative | bool | distinguish between periodical and cumulative account growth data | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | historical data of accounts growth |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py#L139)]

```python
openbb.crypto.defi.gacc_chart(kind: str = "total", cumulative: bool = False, limit: int = 90, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 90 | True |
| kind | str | display total account count or active account count. One from list [active, total] | total | True |
| cumulative | bool | Flag to show cumulative or discrete values. For active accounts only discrete value are available. | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>