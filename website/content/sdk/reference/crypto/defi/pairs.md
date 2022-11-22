---
title: pairs
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pairs

<Tabs>
<TabItem value="model" label="Model" default>

Get lastly added trade-able pairs on Uniswap with parameters like:

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_model.py#L164)]

```python
openbb.crypto.defi.pairs(last_days: int = 14, min_volume: int = 100, min_liquidity: int = 0, min_tx: int = 100)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| last_days | int | How many days back to look for added pairs. | 14 | True |
| min_volume | int | Minimum volume | 100 | True |
| min_liquidity | int | Minimum liquidity | 0 | True |
| min_tx | int | Minimum number of transactions done in given pool. | 100 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Lastly added pairs on Uniswap DEX. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing Lastly added pairs on Uniswap DEX.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_view.py#L102)]

```python
openbb.crypto.defi.pairs_chart(limit: int = 20, days: int = 7, min_volume: int = 20, min_liquidity: int = 0, min_tx: int = 100, sortby: str = "created", ascend: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 20 | True |
| days | int | Number of days the pair has been active, | 7 | True |
| min_volume | int | Minimum trading volume, | 20 | True |
| min_liquidity | int | Minimum liquidity | 0 | True |
| min_tx | int | Minimum number of transactions | 100 | True |
| sortby | str | Key by which to sort data | created | True |
| ascend | bool | Flag to sort data descending | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>