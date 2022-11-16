---
title: hist
description: OpenBB SDK Function
---

# hist

## forex_av_model.get_historical

```python title='openbb_terminal/forex/av_model.py'
def get_historical(to_symbol: str, from_symbol: str, resolution: str, interval: int, start_date: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/av_model.py#L97)

Description: Get historical forex data.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| to_symbol | str | To forex symbol | None | False |
| from_symbol | str | From forex symbol | None | False |
| resolution | str | Resolution of data.  Can be "i", "d", "w", "m" for intraday, daily, weekly or monthly | None | True |
| interval | int | Interval for intraday data | None | True |
| start_date | str | Start date for data. | None | True |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Historical data for forex pair |

## Examples

