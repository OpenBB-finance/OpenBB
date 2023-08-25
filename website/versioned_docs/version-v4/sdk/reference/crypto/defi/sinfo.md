---
title: sinfo
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sinfo

<Tabs>
<TabItem value="model" label="Model" default>

Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py#L105)]

```python
openbb.crypto.defi.sinfo(address: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, str] | luna delegations and summary report for given address |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py#L32)]

```python
openbb.crypto.defi.sinfo_chart(address: str = "", limit: int = 10, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg |  | True |
| limit | int | Number of records to display | 10 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>