---
title: av_overview
description: OpenBB SDK Function
---

# av_overview

## stocks_fa_av_model.get_overview

```python title='openbb_terminal/stocks/fundamental_analysis/av_model.py'
def get_overview(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L36)

Description: Get alpha vantage company overview

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of fundamentals |

## Examples

