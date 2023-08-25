---
title: categories
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# categories

<Tabs>
<TabItem value="model" label="Model" default>

Returns top crypto categories [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L157)]

```python
openbb.crypto.ov.categories(sort_filter: str = "market_cap_desc")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort_filter | str | Can be one of - "market_cap_desc", "market_cap_asc", "name_desc", "name_asc",<br/>"market_cap_change_24h_desc", "market_cap_change_24h_asc" | market_cap_desc | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rank, Name, Change_1h, Change_7d, Market_Cap, Volume_24h,Coins, Url |
---



</TabItem>
<TabItem value="view" label="Chart">

Shows top cryptocurrency categories by market capitalization

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L416)]

```python
openbb.crypto.ov.categories_chart(sortby: str = "market_cap_desc", limit: int = 15, export: str = "", pie: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | market_cap_desc | True |
| limit | int | Number of records to display | 15 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| pie | bool | Whether to show the pie chart | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>