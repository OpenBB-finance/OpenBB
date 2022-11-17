---
title: gainers_or_losers
description: OpenBB SDK Function
---

# gainers_or_losers

## crypto_disc_pycoingecko_model.get_gainers_or_losers

```python title='openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py'
def get_gainers_or_losers(limit: int, interval: str, typ: str, sortby: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L189)

Description: Returns data about top gainers - coins which gain the most in given period and

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Num of coins to get | None | False |
| sortby | str | Key to sort data. The table can be sorted by every of its columns. Refer to
API documentation (see /coins/markets in https://www.coingecko.com/en/api/documentation) | None | False |
| interval | str | One from {14d,1h,1y,200d,24h,30d,7d} | None | False |
| typ | str | Either "gainers" or "losers" | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | Top Gainers / Top Losers - coins which gain/lost most in price in given period of time.
Columns: Symbol, Name, Volume, Price, %Change_{interval}, Url |

## Examples

