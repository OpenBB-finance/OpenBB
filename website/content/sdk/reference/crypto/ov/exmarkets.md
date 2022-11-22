---
title: exmarkets
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# exmarkets

<Tabs>
<TabItem value="model" label="Model" default>

List markets by exchange ID [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L328)]

```python
openbb.crypto.ov.exmarkets(exchange_id: str = "binance", symbols: str = "USD", sortby: str = "pair", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange_id | str | identifier of exchange e.g for Binance Exchange -> binance | binance | True |
| symbols | str | Comma separated quotes to return e.g quotes=USD,BTC | USD | True |
| sortby | str | Key by which to sort data | pair | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | pair, base_currency_name, quote_currency_name, market_url,<br/>category, reported_volume_24h_share, trust_score, |
---



</TabItem>
<TabItem value="view" label="Chart">

Get all markets for given exchange [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L267)]

```python
openbb.crypto.ov.exmarkets_chart(exchange: str = "binance", sortby: str = "pair", ascend: bool = True, limit: int = 15, links: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange | str | Exchange identifier e.g Binance | binance | True |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | pair | True |
| ascend | bool | Flag to sort data descending | True | True |
| links | bool | Flag to display urls | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>