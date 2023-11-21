---
title: sinfo
description: Learn how to get staking info for a given Terra account using OpenBB's
  API. Explore functionality like viewing luna delegations and summary reports for
  the chosen address, displaying staking info for the provided Terra account address,
  and exporting dataframe data to csv, json, or xlsx file.
keywords:
- Terra blockchain
- staking info
- luna delegations
- summary report
- export to csv
- export to json
- export to xlsx
- defi
- cryptocurrency
- dataframe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.defi.sinfo - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

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
