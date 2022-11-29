---
title: hm
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hm

<Tabs>
<TabItem value="model" label="Model" default>

Get N coins from CoinGecko [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L128)]

```python
openbb.crypto.ov.hm(limit: int = 250, category: str = "", sortby: str = "Symbol", ascend: bool = False)
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

Shows cryptocurrencies heatmap [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L36)]

```python
openbb.crypto.ov.hm_chart(category: str = "", limit: int = 15, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| caterogy | str | Category (e.g., stablecoins). Empty for no category (default: ) | None | True |
| limit | int | Number of top cryptocurrencies to display | 15 | True |
| export | str | Export dataframe data to csv,json,xlsx |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>