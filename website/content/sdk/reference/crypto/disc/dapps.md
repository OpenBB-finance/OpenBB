---
title: dapps
description: Get dapps [Source https//dappradar
keywords:
- crypto
- disc
- dapps
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.dapps - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get dapps [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L166)]

```python wordwrap
openbb.crypto.disc.dapps(chain: str = "", page: int = 1, resultPerPage: int = 15)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| chain | str | Name of the chain |  | True |
| page | int | Page number | 1 | True |
| resultPerPage | int | Number of records to display | 15 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Columns: Dapp ID, Name, Description, Full Description, Logo, Link, Website,<br/>Chains, Categories |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing dapps [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L122)]

```python wordwrap
openbb.crypto.disc.dapps_chart(chain: str = "", page: int = 1, resultPerPage: int = 15, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| chain | str | Name of the chain |  | True |
| page | int | Page number | 1 | True |
| resultPerPage | int | Number of records per page | 15 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| sheet_name | str | Name of the sheet in excel or csv file | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>