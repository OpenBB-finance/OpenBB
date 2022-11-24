---
title: products
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# products

<Tabs>
<TabItem value="model" label="Model" default>

Get list of financial products from CoinGecko API

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L317)]

```python
openbb.crypto.ov.products(sortby: str = "Name", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | Name | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate |
---



</TabItem>
<TabItem value="view" label="Chart">

Shows list of financial products. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L570)]

```python
openbb.crypto.ov.products_chart(sortby: str = "Platform", ascend: bool = False, limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | Platform | True |
| ascend | bool | Flag to sort data descending | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>