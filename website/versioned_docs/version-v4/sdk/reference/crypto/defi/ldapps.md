---
title: ldapps
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ldapps

<Tabs>
<TabItem value="model" label="Model" default>

Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_model.py#L35)]

```python
openbb.crypto.defi.ldapps(limit: int = 100, sortby: str = "", ascend: bool = False, description: bool = False, drop_chain: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | The number of dApps to display | 100 | True |
| sortby | str | Key by which to sort data |  | True |
| ascend | bool | Flag to sort data descending | False | True |
| description | bool | Flag to display description of protocol | False | True |
| drop_chain | bool | Whether to drop the chain column | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Information about DeFi protocols |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing information about listed DeFi protocols, their current TVL and changes to it in

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_view.py#L94)]

```python
openbb.crypto.defi.ldapps_chart(sortby: str, limit: int = 20, ascend: bool = False, description: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 20 | True |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data descending | False | True |
| description | bool | Flag to display description of protocol | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>