---
title: candles
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# candles

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_coinbase_model.get_candles

```python title='openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py'
def get_candles(symbol: str, interval: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py#L130)

Description: Get candles for chosen trading pair and time interval. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| interval | str | Time interval. One from 1min, 5min ,15min, 1hour, 6hour, 24hour | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Candles for chosen trading pair. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_coinbase_view.display_candles

```python title='openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py'
def display_candles(symbol: str, interval: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py#L76)

Description: Get candles for chosen trading pair and time interval. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| interval | str | Time interval. One from 1m, 5m ,15m, 1h, 6h, 24h | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>