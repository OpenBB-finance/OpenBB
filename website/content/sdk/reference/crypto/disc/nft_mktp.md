---
title: nft_mktp
description: Get top nft collections [Source https//dappradar
keywords:
- crypto
- disc
- nft_mktp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.nft_mktp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get top nft collections [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L71)]

```python wordwrap
openbb.crypto.disc.nft_mktp(chain: str = "", sortby: str = "", order: str = "", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| chain | str | Name of the chain |  | True |
| sortby | str | Key by which to sort data |  | True |
| order | str | Order of sorting |  | True |
| limit | int | Number of records to display | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Columns: Name, Dapp ID, Logo, Chains, Avg Price [$], Avg Price Change [%],<br/>Volume [$], Volume Change [%], Traders, Traders Change [%] |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing nft marketplaces [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L23)]

```python wordwrap
openbb.crypto.disc.nft_mktp_chart(limit: int = 10, sortby: str = "", order: str = "", chain: str = "", export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| chain | str | Name of the chain |  | True |
| order | str | Order of sorting (asc/desc) |  | True |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data |  | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| sheet_name | str | Name of the sheet in excel or csv file | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>