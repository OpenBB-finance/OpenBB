---
title: find
description: OpenBB SDK Function
---

# find

## crypto_helpers.find

```python title='openbb_terminal/cryptocurrency/cryptocurrency_helpers.py'
def find(query: str, source: str, key: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/cryptocurrency_helpers.py#L997)

Description: Find similar coin by coin name,symbol or id.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Cryptocurrency | None | False |
| source | str | Data source of coins.  CoinGecko (cg) or CoinPaprika (cp) or Binance (bin), Coinbase (cb) | None | False |
| key | str | Searching key (symbol, id, name) | None | False |
| limit | int | Number of records to display | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples

