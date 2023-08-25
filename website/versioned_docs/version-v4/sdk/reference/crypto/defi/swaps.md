---
title: swaps
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# swaps

<Tabs>
<TabItem value="model" label="Model" default>

Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_model.py#L296)]

```python
openbb.crypto.defi.swaps(limit: int = 100, sortby: str = "timestamp", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of swaps to return. Maximum possible number: 1000. | 100 | True |
| sortby | str | Key by which to sort data. The table can be sorted by every of its columns<br/>(see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2). | timestamp | True |
| ascend | bool | Flag to sort data descending | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Last 100 swaps on Uniswap |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing last swaps done on Uniswap

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_view.py#L218)]

```python
openbb.crypto.defi.swaps_chart(limit: int = 10, sortby: str = "timestamp", ascend: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data. The table can be sorted by every of its columns<br/>(see https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2). | timestamp | True |
| ascend | bool | Flag to sort data descending | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>