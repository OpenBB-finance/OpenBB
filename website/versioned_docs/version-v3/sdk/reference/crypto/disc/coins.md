---
title: coins
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# coins

<Tabs>
<TabItem value="model" label="Model" default>

Get N coins from CoinGecko [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L128)]

```python
openbb.crypto.disc.coins(limit: int = 250, category: str = "", sortby: str = "Symbol", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of top coins to grab from CoinGecko | 250 | True |
| category | str | Category of the coins we want to retrieve |  | True |
| sortby | str | Key to sort data | Symbol | True |
| ascend | bool | Sort data in ascending order | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | N coins |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing top coins [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_view.py#L35)]

```python
openbb.crypto.disc.coins_chart(category: str, limit: int = 250, sortby: str = "Symbol", export: str = "", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| category | str | If no category is passed it will search for all coins. (E.g., smart-contract-platform) | None | False |
| limit | int | Number of records to display | 250 | True |
| sortby | str | Key to sort data | Symbol | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| ascend | bool | Sort data in ascending order | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>