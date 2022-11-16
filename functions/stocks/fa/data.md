---
title: data
description: OpenBB SDK Function
---

# data

## stocks_fa_finviz_model.get_data

```python title='openbb_terminal/stocks/fundamental_analysis/finviz_model.py'
def get_data(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/finviz_model.py#L15)

Description: Get fundamental data from finviz

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of fundamental data |

## Examples

