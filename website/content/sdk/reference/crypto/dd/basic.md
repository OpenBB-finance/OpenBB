---
title: basic
description: This documentation page provides insights into how to use basic functions
  of the OpenBB terminal for cryptocurrency tracking and analysis. It also provides
  source code links and parameters information for two of its functions - 'coinpaprika_model'
  and 'coinpaprika_view', dealing with basic information retrieval and chart generation
  for cryptocurrencies respectively.
keywords:
- OpenBB terminal
- cryptocurrency analysis
- coinpaprika_model
- basic coin information
- coinpaprika_view
- cryptocurrency chart generation
- cryptocurrency tracking
- cryptocurrency parameters
- BTC
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.basic - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Basic coin information [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L379)]

```python
openbb.crypto.dd.basic(symbol: str = "BTC")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Metric, Value |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing basic information for coin. Like:

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L325)]

```python
openbb.crypto.dd.basic_chart(symbol: str = "BTC", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | BTC | True |
| export | str | Export dataframe data to csv,json,xlsx |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
