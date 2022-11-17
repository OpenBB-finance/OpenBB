---
title: get_binance_trading_pairs
description: OpenBB SDK Function
---

# get_binance_trading_pairs

## crypto_dd_binance_model.get_all_binance_trading_pairs

```python title='openbb_terminal/decorators.py'
def get_all_binance_trading_pairs() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L58)

Description: Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | All available pairs on Binance
Columns: symbol, baseAsset, quoteAsset |

## Examples

