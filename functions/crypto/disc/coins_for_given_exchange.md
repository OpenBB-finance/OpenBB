---
title: coins_for_given_exchange
description: OpenBB SDK Function
---

# coins_for_given_exchange

## crypto_disc_pycoingecko_model.get_coins_for_given_exchange

```python title='openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py'
def get_coins_for_given_exchange(exchange_id: str, page: int) -> dict:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L349)

Description: Helper method to get all coins available on binance exchange [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange_id | str | id of exchange | None | False |
| page | int | number of page. One page contains 100 records | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| dict | dictionary with all trading pairs on binance |

## Examples

