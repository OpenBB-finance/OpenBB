---
title: sidtc
description: OpenBB SDK Function
---

# sidtc

## stocks_dps_stockgrid_model.get_short_interest_days_to_cover

```python title='openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py'
def get_short_interest_days_to_cover(sortby: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py#L78)

Description: Get short interest and days to cover. [Source: Stockgrid]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Field for which to sort by, where 'float': Float Short %%,
'dtc': Days to Cover, 'si': Short Interest | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| pd.DataFrame | None | Short interest and days to cover data | None | None |

## Returns

This function does not return anything

## Examples

