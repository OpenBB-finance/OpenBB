---
title: print_insider_data
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# print_insider_data

<Tabs>
<TabItem value="model" label="Model" default>

Print insider data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/openinsider_model.py#L1437)]

```python
openbb.stocks.ins.print_insider_data(type_insider: str = "lcb", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| type_insider | str | Insider type of data. Available types can be accessed through get_insider_types(). | lcb | True |
| limit | int | Limit of data rows to display | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Open insider filtered data |
---



</TabItem>
<TabItem value="view" label="Chart">

Print insider data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/openinsider_view.py#L108)]

```python
openbb.stocks.ins.print_insider_data_chart(type_insider: str = "lcb", limit: int = 10, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| type_insider | str | Insider type of data. Available types can be accessed through get_insider_types(). | lcb | True |
| limit | int | Limit of data rows to display | 10 | True |
| export | str | Export data format |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>