---
title: hsi
description: OpenBB SDK Function
---

# hsi

## stocks_dps_shortinterest_model.get_high_short_interest

```python title='openbb_terminal/stocks/dark_pool_shorts/shortinterest_model.py'
def get_high_short_interest() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/shortinterest_model.py#L18)

Description: Returns a high short interest DataFrame

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | High short interest Dataframe with the following columns:
Ticker, Company, Exchange, ShortInt, Float, Outstd, Industry |

## Examples

