---
title: info
description: OpenBB SDK Function
---

# info

## stocks_fa_yahoo_finance_model.get_info

```python title='openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py'
def get_info(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L31)

Description: Gets ticker symbol info

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of yfinance information |

## Examples

