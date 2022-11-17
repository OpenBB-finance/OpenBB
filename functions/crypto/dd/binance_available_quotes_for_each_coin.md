---
title: binance_available_quotes_for_each_coin
description: OpenBB SDK Function
---

# binance_available_quotes_for_each_coin

## crypto_dd_binance_model.get_binance_available_quotes_for_each_coin

```python title='openbb_terminal/decorators.py'
def get_binance_available_quotes_for_each_coin() -> dict:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L77)

Description: Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
|  | All quote assets for given coin
{'ETH' : ['BTC', 'USDT' ...], 'UNI' : ['ETH', 'BTC','BUSD', ...] |

## Examples

