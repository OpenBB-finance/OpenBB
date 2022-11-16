---
title: ohlc_historical
description: OpenBB SDK Function
---

# ohlc_historical

## crypto_dd_coinpaprika_model.get_ohlc_historical

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py'
def get_ohlc_historical(symbol: str, quotes: str, days: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L247)

Description: Open/High/Low/Close values with volume and market_cap. [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Paprika coin identifier e.g. eth-ethereum | None | False |
| quotes | str | returned data quote (available values: usd btc) | None | False |
| days | int | time range for chart in days. Maximum 365 | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | Open/High/Low/Close values with volume and market_cap. |

## Examples

