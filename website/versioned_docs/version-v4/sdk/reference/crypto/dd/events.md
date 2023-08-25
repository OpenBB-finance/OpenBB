---
title: events
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# events

<Tabs>
<TabItem value="model" label="Model" default>

Get all events related to given coin like conferences, start date of futures trading etc.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L74)]

```python
openbb.crypto.dd.events(symbol: str = "BTC", sortby: str = "date", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| sortby | str | Key by which to sort data. Every column name is valid<br/>(see for possible values:<br/>https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1events/get). | date | True |
| ascend | bool | Flag to sort data ascending | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Events found for given coin<br/>Columns: id, date , date_to, name, description, is_conference, link, proof_image_link |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing all events for given coin id. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L132)]

```python
openbb.crypto.dd.events_chart(symbol: str = "BTC", limit: int = 10, sortby: str = "date", ascend: bool = False, links: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data. Every column name is valid<br/>(see for possible values:<br/>https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1events/get). | date | True |
| ascend | bool | Flag to sort data ascending | False | True |
| links | bool | Flag to display urls | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>