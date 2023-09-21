---
title: luna_supply
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# luna_supply

<Tabs>
<TabItem value="model" label="Model" default>

Get supply history of the Terra ecosystem

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/smartstake_model.py#L14)]

```python
openbb.crypto.defi.luna_supply(supply_type: str = "lunaSupplyChallengeStats", days: int = 30)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| supply_type | str | Supply type to unpack json | lunaSupplyChallengeStats | True |
| days | int | Day count to fetch data | 30 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of supply history data |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots and prints table showing Luna circulating supply stats

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/smartstake_view.py#L29)]

```python
openbb.crypto.defi.luna_supply_chart(days: int = 30, export: str = "", supply_type: str = "lunaSupplyChallengeStats", limit: int = 5, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| days | int | Number of days | 30 | True |
| supply_type | str | Supply type to unpack json | lunaSupplyChallengeStats | True |
| export | str | Export type |  | True |
| limit | int | Number of results display on the terminal<br/>Default: 5 | 5 | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>