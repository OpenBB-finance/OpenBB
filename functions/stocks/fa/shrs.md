---
title: shrs
description: OpenBB SDK Function
---

# shrs

## stocks_fa_yahoo_finance_model.get_shareholders

```python title='openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py'
def get_shareholders(symbol: str, holder: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L75)

Description: Get shareholders from yahoo

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| holder | str | Which holder to get table for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Major holders |

## Examples

