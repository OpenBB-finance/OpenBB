---
title: dapp_metrics
description: Get dapp metrics [Source https//dappradar
keywords:
- crypto
- disc
- dapp_metrics
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.disc.dapp_metrics - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get dapp metrics [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L280)]

```python wordwrap
openbb.crypto.disc.dapp_metrics(dappId: int, chain: str = "", time_range: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dappId | int | Dapp ID | None | False |
| chain | str | Name of the chain if the dapp is multi-chain |  | True |
| range | str | Time range for the metrics. Can be 24h, 7d, 30d | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Columns: Transactions, Transactions Change [%], Users, UAW, UAW Change [%],<br/>Volume [$], Volume Change [%], Balance [$], Balance Change [%] |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing dapp metrics [Source: https://dappradar.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L229)]

```python wordwrap
openbb.crypto.disc.dapp_metrics_chart(dappId: int, chain: str = "", time_range: str = "", export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dappId | int | Dapp id | None | False |
| chain | str | Name of the chain |  | True |
| range | str | Range of data to display (24h, 7d, 30d) | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| sheet_name | str | Name of the sheet in excel or csv file | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>