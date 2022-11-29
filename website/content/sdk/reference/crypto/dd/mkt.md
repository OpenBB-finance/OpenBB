---
title: mkt
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mkt

<Tabs>
<TabItem value="model" label="Model" default>

All markets for given coin and currency [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L176)]

```python
openbb.crypto.dd.mkt(symbol: str = "BTC", quotes: str = "USD", sortby: str = "pct_volume_share", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| quotes | str | Comma separated list of quotes to return.<br/>Example: quotes=USD,BTC<br/>Allowed values:<br/>BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN,<br/>PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR,<br/>VND, BOB, COP, PEN, ARS, ISK | USD | True |
| sortby | str | Key by which to sort data. Every column name is valid (see for possible values:<br/>https://api.coinpaprika.com/v1). | pct_volume_share | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All markets for given coin and currency |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing all markets for given coin id. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L230)]

```python
openbb.crypto.dd.mkt_chart(from_symbol: str = "BTC", to_symbol: str = "USD", limit: int = 20, sortby: str = "pct_volume_share", ascend: bool = True, links: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| to_symbol | str | Quoted currency | USD | True |
| limit | int | Number of records to display | 20 | True |
| sortby | str | Key by which to sort data. Every column name is valid (see for possible values:<br/>https://api.coinpaprika.com/v1). | pct_volume_share | True |
| ascend | bool | Flag to sort data ascending | True | True |
| links | bool | Flag to display urls | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>