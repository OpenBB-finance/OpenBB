---
title: twitter
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# twitter

<Tabs>
<TabItem value="model" label="Model" default>

Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L23)]

```python
openbb.crypto.dd.twitter(symbol: str = "BTC", sortby: str = "date", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| sortby | str | Key by which to sort data. Every column name is valid<br/>(see for possible values:<br/>https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get). | date | True |
| ascend | bool | Flag to sort data descending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Twitter timeline for given coin.<br/>Columns: date, user_name, status, retweet_count, like_count |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L86)]

```python
openbb.crypto.dd.twitter_chart(symbol: str = "BTC", limit: int = 10, sortby: str = "date", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data. Every column name is valid<br/>(see for possible values:<br/>https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get). | date | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>