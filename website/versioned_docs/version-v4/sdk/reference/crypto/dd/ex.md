---
title: ex
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ex

<Tabs>
<TabItem value="model" label="Model" default>

Get all exchanges for given coin id. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L137)]

```python
openbb.crypto.dd.ex(symbol: str = "BTC", sortby: str = "adjusted_volume_24h_share", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| sortby | str | Key by which to sort data. Every column name is valid (see for possible values:<br/>https://api.coinpaprika.com/v1). | adjusted_volume_24h_share | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All exchanges for given coin<br/>Columns: id, name, adjusted_volume_24h_share, fiats |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing all exchanges for given coin id. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L185)]

```python
openbb.crypto.dd.ex_chart(symbol: str = "btc", limit: int = 10, sortby: str = "adjusted_volume_24h_share", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | btc | True |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data. Every column name is valid (see for possible values:<br/>https://api.coinpaprika.com/v1). | adjusted_volume_24h_share | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>