---
title: crypto_hacks
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# crypto_hacks

<Tabs>
<TabItem value="model" label="Model" default>

Get major crypto-related hacks

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/rekt_model.py#L93)]

```python
openbb.crypto.ov.crypto_hacks(sortby: str = "Platform", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL} | Platform | True |
| ascend | bool | Flag to sort data ascending | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Hacks with columns {Platform,Date,Amount [$],Audited,Slug,URL} |
---



</TabItem>
<TabItem value="view" label="Chart">

Display list of major crypto-related hacks. If slug is passed

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/rekt_view.py#L18)]

```python
openbb.crypto.ov.crypto_hacks_chart(limit: int = 15, sortby: str = "Platform", ascend: bool = False, slug: str = "polyntwork-rekt", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | Crypto hack slug to check (e.g., polynetwork-rekt) | polyntwork-rekt | True |
| limit | int | Number of hacks to search | 15 | True |
| sortby | str | Key by which to sort data {Platform,Date,Amount [$],Audit,Slug,URL} | Platform | True |
| ascend | bool | Flag to sort data ascending | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>