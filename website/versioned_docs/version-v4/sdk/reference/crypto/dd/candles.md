---
title: candles
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# candles

<Tabs>
<TabItem value="model" label="Model" default>

Get candles for chosen trading pair and time interval. [Source: Coinbase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py#L143)]

```python
openbb.crypto.dd.candles(symbol: str, interval: str = "24h")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| interval | str | Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour | 24h | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Candles for chosen trading pair. |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing candles for chosen trading pair and time interval. [Source: Coinbase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py#L76)]

```python
openbb.crypto.dd.candles_chart(symbol: str, interval: str = "24h", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| interval | str | Time interval. One from 1m, 5m ,15m, 1h, 6h, 24h | 24h | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>