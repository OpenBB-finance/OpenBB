---
title: analysis
description: OpenBB SDK Function
---

# analysis

## stocks_fa_eclect_us_model.get_filings_analysis

```python title='openbb_terminal/stocks/fundamental_analysis/eclect_us_model.py'
def get_filings_analysis(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/eclect_us_model.py#L18)

Description: Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to see analysis of filings | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| str | Analysis of filings text |

## Examples

