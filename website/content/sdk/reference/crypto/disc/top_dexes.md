---
title: top_dexes
description: The 'top_dexes' page contains information and source code for obtaining
  and viewing decentralized exchange data, including daily volume and users. The first
  tab shows a model for getting top dexes by specified parameters, while the second
  tab displays a function that prints this data in tabular format.
keywords:
- dexes
- decetralized exchange
- daily volume
- data model
- data view
- dappradar
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.top_dexes - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get top dexes by daily volume and users [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L124)]

```python
openbb.crypto.disc.top_dexes(sortby: str = "", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Top decentralized exchanges. Columns: Name, Daily Users, Daily Volume [$] |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing top decentralized exchanges [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L97)]

```python
openbb.crypto.disc.top_dexes_chart(limit: int = 10, export: str = "", sortby: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data |  | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
