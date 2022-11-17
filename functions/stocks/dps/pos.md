---
title: pos
description: OpenBB SDK Function
---

# pos

## stocks_dps_stockgrid_model.get_dark_pool_short_positions

```python title='openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py'
def get_dark_pool_short_positions(sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py#L20)

Description: Get dark pool short positions. [Source: Stockgrid]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Field for which to sort by, where 'sv': Short Vol. [1M],
'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],
'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],
'dpp_dollar': DP Position ($1B) | None | False |
| ascend | bool | Data in ascending order | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dark pool short position data |

## Examples

