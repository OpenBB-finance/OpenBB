---
title: ps
description: This page includes an overview of the OpenBB Terminal cryptocurrency
  functions ps and ps_chart. The ps function obtains ticker-related information for
  a given cryptocurrency and the ps_chart function visualizes trading data for a particular
  cryptocurrency. The documentation is inclusive of source code, input parameters,
  and expected returns.
keywords:
- Cryptocurrency
- CoinPaprika API
- Python programming
- Market ticker related information
- Cryptocurrency symbols
- Crypto trading data
- Cryptocurrency chart
- Data export
- CSV
- JSON
- XSLX
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.ps - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get all most important ticker related information for given coin id [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L290)]

```python
openbb.crypto.dd.ps(symbol: str = "BTC", quotes: str = "USD")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| quotes | str | Comma separated quotes to return e.g quotes = USD, BTC | USD | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most important ticker related information<br/>Columns: Metric, Value |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing ticker information for single coin [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L287)]

```python
openbb.crypto.dd.ps_chart(from_symbol: str = "BTC", to_symbol: str = "USD", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| to_symbol | str | Quoted currency | USD | True |
| export | str | Export dataframe data to csv,json,xlsx |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
