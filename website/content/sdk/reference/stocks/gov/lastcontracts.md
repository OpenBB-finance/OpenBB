---
title: lastcontracts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# lastcontracts

<Tabs>
<TabItem value="model" label="Model" default>

Get last government contracts [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L377)]

```python
openbb.stocks.gov.lastcontracts(past_transaction_days: int = 2)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| past_transaction_days | int | Number of days to look back | 2 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of government contracts |
---



</TabItem>
<TabItem value="view" label="Chart">

Last government contracts [Source: quiverquant.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L225)]

```python
openbb.stocks.gov.lastcontracts_chart(past_transaction_days: int = 2, limit: int = 20, sum_contracts: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| past_transaction_days | int | Number of days to look back | 2 | True |
| limit | int | Number of contracts to show | 20 | True |
| sum_contracts | bool | Flag to show total amount of contracts given out. | False | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>