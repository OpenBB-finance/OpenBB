---
title: dividends
description: OpenBB SDK Function
---

# dividends

## stocks_disc_nasdaq_model.get_dividend_cal

```python title='openbb_terminal/stocks/discovery/nasdaq_model.py'
def get_dividend_cal(date: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/nasdaq_model.py#L55)

Description: Gets dividend calendar for given date.  Date represents Ex-Dividend Date

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | datetime | Date to get for in format YYYY-MM-DD | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe of dividend calendar |

## Examples

