---
title: mktcap
description: OpenBB SDK Function
---

# mktcap

## stocks_fa_yahoo_finance_model.get_mktcap

```python title='openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py'
def get_mktcap(symbol: str, start_date: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L273)

Description: Get market cap over time for ticker. [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get market cap over time | None | False |
| start_date | str | Start date to display market cap | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe of estimated market cap over time |

## Examples

