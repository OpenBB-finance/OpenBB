---
title: top_dapps
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# top_dapps

<Tabs>
<TabItem value="model" label="Model" default>

Get top decentralized applications by daily volume and users [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L209)]

```python
openbb.crypto.disc.top_dapps(sortby: str = "", limit: int = 10)
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
| pd.DataFrame | Top decentralized exchanges.<br/>Columns: Name, Category, Protocols, Daily Users, Daily Volume [$] |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing top decentralized exchanges [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L133)]

```python
openbb.crypto.disc.top_dapps_chart(limit: int = 10, export: str = "", sortby: str = "")
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