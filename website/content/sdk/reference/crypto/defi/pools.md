---
title: pools
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pools

<Tabs>
<TabItem value="model" label="Model" default>

Get uniswap pools by volume. [Source: https://thegraph.com/en/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_model.py#L253)]

```python
openbb.crypto.defi.pools()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Trade-able pairs listed on Uniswap by top volume. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing uniswap pools by volume.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_view.py#L170)]

```python
openbb.crypto.defi.pools_chart(limit: int = 20, sortby: str = "volumeUSD", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 20 | True |
| sortby | str | Key by which to sort data. The table can be sorted by every of its columns<br/>(see https://bit.ly/3ORagr1 then press ctrl-enter or execute the query). | volumeUSD | True |
| ascend | bool | Flag to sort data descending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>