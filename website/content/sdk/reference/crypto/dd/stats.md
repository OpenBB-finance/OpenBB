---
title: stats
description: Discover the statistics module of openbb.crypto.dd using symbol trading
  pair and explore the possibility of exporting data to desired file format. Find
  detailed parameters and return values to improve your experience.
keywords:
- crypto stats
- coinbase trading
- data export
- API parameters
- dataframe
- crypto trading
- base currency
- ETH-USDT
- UNI-ETH
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.stats - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get 24 hr stats for the product. Volume is in base currency units.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py#L202)]

```python
openbb.crypto.dd.stats(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | 24h stats for chosen trading pair |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing 24 hr stats for the product. Volume is in base currency units.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py#L99)]

```python
openbb.crypto.dd.stats_chart(symbol: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
