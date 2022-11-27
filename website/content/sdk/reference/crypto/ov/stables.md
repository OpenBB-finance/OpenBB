---
title: stables
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# stables

<Tabs>
<TabItem value="model" label="Model" default>

Returns top stable coins [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L191)]

```python
openbb.crypto.ov.stables(limit: int = 15, sortby: str = "Market_Cap_[$]", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | How many rows to show | 15 | True |
| sortby | str | Key by which to sort data, default is Market_Cap_[$] | Market_Cap_[$] | True |
| ascend | bool | Flag to sort data ascending | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with stable coins data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.crypto.ov.stables(sortby="Volume_[$]", ascend=True, limit=10)
```

---



</TabItem>
<TabItem value="view" label="Chart">

Shows stablecoins data [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L331)]

```python
openbb.crypto.ov.stables_chart(limit: int = 15, export: str = "", sortby: str = "Market_Cap_[$]", ascend: bool = False, pie: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data, default is Market_Cap_[$] | Market_Cap_[$] | True |
| ascend | bool | Flag to sort data ascending | False | True |
| pie | bool | Whether to show a pie chart, default is True | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| pie | bool | Whether to show a pie chart | True | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.crypto.ov.stables_chart(sortby="Volume_[$]", ascend=True, limit=10)
```

---



</TabItem>
</Tabs>