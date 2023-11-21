---
title: hm
description: The page provides detailed documentation for OpenBB crypto functions
  that interact with CoinGecko to retrieve and visualise cryptocurrency data. It includes
  code examples, a list of parameters and their descriptions for each function, and
  source code links.
keywords:
- cryptocurrency
- CoinGecko
- heatmap
- docusaurus
- dataframe
- metadata
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.hm - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get N coins from CoinGecko [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L130)]

```python wordwrap
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L78)]

```python wordwrap
openbb.crypto.ov.hm_chart(category: str = "", limit: int = 15, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| caterogy | str | Category (e.g., stablecoins). Empty for no category (default: ) | None | True |
| limit | int | Number of top cryptocurrencies to display | 15 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Export dataframe data to csv,json,xlsx |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>