---
title: ugs
description: OpenBB SDK Function
---

# ugs

## stocks_disc_yahoofinance_model.get_ugs

```python title='openbb_terminal/stocks/discovery/yahoofinance_model.py'
def get_ugs() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/yahoofinance_model.py#L54)

Description: Get stocks with earnings growth rates better than 25% and relatively low PE and PEG ratios.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Undervalued stocks |

## Examples

