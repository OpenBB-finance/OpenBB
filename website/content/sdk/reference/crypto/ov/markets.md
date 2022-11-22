---
title: markets
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# markets

<Tabs>
<TabItem value="model" label="Model" default>

Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L223)]

```python
openbb.crypto.ov.markets(symbols: str = "USD", sortby: str = "rank", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Comma separated quotes to return e.g quotes=USD,BTC | USD | True |
| sortby | str | Key by which to sort data | rank | True |
| ascend | bool | Flag to sort data ascend | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | rank, name, symbol, price, volume_24h, mcap_change_24h,<br/>pct_change_1h, pct_change_24h, ath_price, pct_from_ath, |
---



</TabItem>
<TabItem value="view" label="Chart">

Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L105)]

```python
openbb.crypto.ov.markets_chart(symbol: str, sortby: str = "rank", ascend: bool = True, limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Quoted currency | None | False |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | rank | True |
| ascend | bool | Flag to sort data ascending | True | True |
| links | bool | Flag to display urls | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>