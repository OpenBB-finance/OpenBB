---
title: tokens
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# tokens

<Tabs>
<TabItem value="model" label="Model" default>

Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_model.py#L81)]

```python
openbb.crypto.defi.tokens(skip: int = 0, limit: int = 100, sortby: str = "index", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| skip | int | Skip n number of records. | 0 | True |
| limit | int | Show n number of records. | 100 | True |
| sortby | str | The column to sort by | index | True |
| ascend | bool | Whether to sort in ascending order | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Uniswap tokens with trading volume, transaction count, liquidity. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing tokens trade-able on Uniswap DEX.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_view.py#L18)]

```python
openbb.crypto.defi.tokens_chart(skip: int = 0, limit: int = 20, sortby: str = "index", ascend: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| skip | int | Number of records to skip | 0 | True |
| limit | int | Number of records to display | 20 | True |
| sortby | str | Key by which to sort data | index | True |
| ascend | bool | Flag to sort data descending | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>