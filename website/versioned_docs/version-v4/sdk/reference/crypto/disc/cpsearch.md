---
title: cpsearch
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpsearch

<Tabs>
<TabItem value="model" label="Model" default>

Search CoinPaprika. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/coinpaprika_model.py#L27)]

```python
openbb.crypto.disc.cpsearch(query: str, category: Optional[Any] = None, modifier: Optional[Any] = None, sortby: str = "id", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | phrase for search | None | False |
| category | Optional[Any] | one or more categories (comma separated) to search.<br/>Available options: currencies|exchanges|icos|people|tags<br/>Default: currencies,exchanges,icos,people,tags | None | True |
| modifier | Optional[Any] | set modifier for search results. Available options: symbol_search -<br/>search only by symbol (works for currencies only) | None | True |
| sortby | str | Key to sort data. The table can be sorted by every of its columns. Refer to<br/>API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get) | id | True |
| ascend | bool | Flag to sort data descending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Search Results<br/>Columns: Metric, Value |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing Search over CoinPaprika. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/coinpaprika_view.py#L16)]

```python
openbb.crypto.disc.cpsearch_chart(query: str, category: str = "all", limit: int = 10, sortby: str = "id", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query | None | False |
| category | str | Categories to search: currencies|exchanges|icos|people|tags|all. Default: all | all | True |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key to sort data. The table can be sorted by every of its columns. Refer to<br/>API documentation (see https://api.coinpaprika.com/docs#tag/Tools/paths/~1search/get) | id | True |
| ascend | bool | Flag to sort data descending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>