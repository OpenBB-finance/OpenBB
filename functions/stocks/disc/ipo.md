---
title: ipo
description: OpenBB SDK Function
---

# ipo

## stocks_disc_finnhub_model.get_ipo_calendar

```python title='openbb_terminal/decorators.py'
def get_ipo_calendar() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L16)

Description: Get IPO calendar

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | start date (%Y-%m-%d) to get IPO calendar | None | False |
| end_date | str | end date (%Y-%m-%d) to get IPO calendar | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Get dataframe with economic calendar events |

## Examples

