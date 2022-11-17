---
title: coin_list
description: OpenBB SDK Function
---

# coin_list

## crypto_disc_pycoingecko_model.get_coin_list

```python title='openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py'
def get_coin_list() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L331)

Description: Get list of coins available on CoinGecko [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | Coins available on CoinGecko
Columns: id, symbol, name |

## Examples

