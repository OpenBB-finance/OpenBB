---
title: info
description: This page provides detailed documentation on retrieving and visualizing
  cryptocurrency data from the CoinPaprika API using methods from the OpenBB crypto
  module. The page includes parameters and return values, data sorting, and export
  options. Source codes are also linked for better understanding.
keywords:
- CoinPaprika API
- crypto coin data
- cryptocurrency information
- openbb.crypto.ov.info
- data modeling
- data sorting
- ascending and descending sorting
- data visualization
- data export formats
- python coding
- coin market cap
- coin volume
- price chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.info - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L183)]

```python
openbb.crypto.ov.info(symbols: str = "USD", sortby: str = "rank", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Comma separated quotes to return e.g quotes=USD,BTC | USD | True |
| sortby | str | Key by which to sort data | rank | True |
| ascend | bool | Flag to sort data descending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | rank, name, symbol, price, volume_24h, circulating_supply, total_supply,<br/>max_supply, market_cap, beta_value, ath_price, |
---

</TabItem>
<TabItem value="view" label="Chart">

Displays basic coin information for all coins from CoinPaprika API. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L159)]

```python
openbb.crypto.ov.info_chart(symbol: str, sortby: str = "rank", ascend: bool = True, limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Quoted currency | None | False |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | rank | True |
| ascend | bool | Flag to sort data descending | True | True |
| links | bool | Flag to display urls | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
