---
title: topledger
description: Returns Topledger's Data for the given Organization's Slug[org_slug] based
keywords:
- crypto
- onchain
- topledger
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.topledger - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns Topledger's Data for the given Organization's Slug[org_slug] based

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/topledger_model.py#L277)]

```python wordwrap
openbb.crypto.onchain.topledger(org_slug: str, query_slug: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| org_slug | str | Organization Slug | None | False |
| query_slug | str | Query Slug | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Topledger Data |
---



</TabItem>
<TabItem value="view" label="Chart">

Display on-chain data from Topledger. [Source: Topledger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/topledger_view.py#L20)]

```python wordwrap
openbb.crypto.onchain.topledger_chart(org_slug: str, query_slug: str, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| org_slug | str | Organization Slug | None | False |
| query_slug | str | Query Slug | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>